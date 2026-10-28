"""Observe the actual HTTPX transport boundary; never equate dispatch with delivery.

No payload/header/URL/timeout mutation. The client continues to own redirects,
cookies, hooks and response reading. Each additional hop gets its own reservation.
The adapter is verified against the locked HTTPX 0.28.1 implementation.

Budget waits have no fixed limit: a request waits only while live reservations can still
settle, and a segment of a planned analysis waits when its HTTP client opens, before the
compiler starts the model timeout. Queue time therefore never becomes a provider timeout.
"""
from __future__ import annotations

import asyncio
import contextlib
import contextvars
import functools
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx

from . import budget

ACTIVE = contextvars.ContextVar('audited_http_exchange', default=None)
PLAN = contextvars.ContextVar('segment_admission_plan', default=None)
TICKET = contextvars.ContextVar('segment_admission_ticket', default=None)
POLL_SECONDS = .1


def utc():
    return datetime.now(UTC).isoformat()


def usage_of(response):
    if response is None or not response.is_stream_consumed:
        return None
    try:
        payload = response.json()
    except (ValueError, httpx.ResponseNotRead):
        return None
    usage = payload.get('usage') if isinstance(payload, dict) else None
    if not isinstance(usage, dict) or not all(type(usage.get(k)) is int and usage[k] >= 0
            for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')):
        return None
    if usage['total_tokens'] != usage['prompt_tokens'] + usage['completion_tokens']:
        return None
    details = usage.get('completion_tokens_details') or {}
    if not isinstance(details, dict):
        return None
    reasoning = details.get('reasoning_tokens')
    if reasoning is not None and (type(reasoning) is not int or not 0 <= reasoning <= usage['completion_tokens']):
        return None
    return usage


def cost(usage, rates):
    if usage is None or not isinstance(rates, dict) or not all(
            type(rates.get(k)) in (int, float) and rates[k] >= 0
            for k in ('cache_hit', 'cache_miss', 'output')):
        return None
    hit, miss = usage.get('prompt_cache_hit_tokens'), usage.get('prompt_cache_miss_tokens')
    if (type(hit) is not int or type(miss) is not int or min(hit, miss) < 0
            or hit + miss != usage['prompt_tokens']):
        return None
    return (hit * rates['cache_hit'] + miss * rates['cache_miss']
            + usage['completion_tokens'] * rates['output']) / 1_000_000


class Exchange:
    def __init__(self, root, body, secret='', context=None, rates=None, simulated=False,
                 limit=budget.LIMIT, before_dispatch=None, reserve_tokens=0, analysis=False):
        self.root, self.body, self.secret = Path(root), body, secret
        self.reserve_tokens, self.analysis = reserve_tokens, analysis
        self.key = uuid4().hex
        self.folder = self.root / 'provider-calls' / self.key
        self.folder.mkdir(parents=True, exist_ok=False)
        self.ledger = self.root / 'budget-ledger.json'
        self.rates, self.limit, self.before_dispatch = rates, limit, before_dispatch
        self.responses = []
        self.start = time.perf_counter()
        self.record = {'id': self.key, 'context': context or {}, 'simulated': simulated,
                       'prepared_UTC': utc(), 'events': [], 'transports': [],
                       'reserved_tokens': 0, 'analysis_call': analysis, 'transport_started': False,
                       'provider_usage': None, 'estimated_cost_USD': None}
        self.save('request.json', body)
        self.event('request_prepared')

    def save(self, name, data):
        text = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        if self.secret:
            text = text.replace(self.secret, '[REDACTED]')
        (self.folder / name).write_text(text)

    def event(self, name, **values):
        self.record['events'].append({'event': name, 'UTC': utc(),
                                     'elapsed_seconds': time.perf_counter() - self.start, **values})
        self.save('metrics.json', self.record)

    def reserve(self):
        """Immediate reservation or refusal (synchronous calls)."""
        try:
            amount = budget.reserve(self.ledger, self.key, self.body, self.limit,
                                    reserve_tokens=self.reserve_tokens, analysis=self.analysis)
        except (AssertionError, RuntimeError) as exc:
            self.refuse(exc)
            raise
        self.reserved(amount, 0, 'immediate')

    async def admit(self, wait_check=None):
        """Exact reservation: in place of the segment's ticket when it has one, else in the
        FIFO line (immediate or refused without wait_check)."""
        ticket = TICKET.get()
        try:
            amount = budget.bound(self.body)
            if ticket is not None and not ticket['used']:
                ticket['used'] = True
                if budget.convert(self.ledger, ticket['key'], self.key, self.body) is not None:
                    return self.reserved(amount, ticket['waited'], 'before_client_open',
                                         ticket['key'])
                budget.release(self.ledger, ticket['key'])
            if wait_check is None:
                budget.reserve(self.ledger, self.key, self.body, self.limit,
                               reserve_tokens=self.reserve_tokens, analysis=self.analysis)
                return self.reserved(amount, 0, 'immediate')
            waited = await wait_in_line(self.ledger, self.key, amount, limit=self.limit,
                reserve_tokens=self.reserve_tokens, analysis=self.analysis,
                wait_check=wait_check, on_queue=lambda: self.queued(amount))
            self.reserved(amount, waited, 'inside_request')
        except asyncio.CancelledError as exc:
            self.refuse(exc, 'cancelled_while_queued')
            raise
        except BaseException as exc:
            self.refuse(exc)
            raise

    def queued(self, amount):
        self.record['queued_UTC'] = utc()
        self.event('queued_for_budget', tokens=amount)

    def reserved(self, amount, waited, where, ticket=None):
        # Where the wait happened: before_client_open is outside any application timeout.
        self.record['reserved_tokens'] = amount
        self.record['reservation_wait_seconds'] = time.perf_counter() - self.start
        self.record['budget_wait'] = {'seconds': waited, 'where': where, 'ticket': ticket}
        self.event('tokens_reserved', tokens=amount)

    def refuse(self, exc, outcome='refused_before_dispatch'):
        budget.withdraw(self.ledger, self.key)
        self.record.update(outcome=outcome, error=type(exc).__name__,
                           refusal=getattr(exc, 'kind', None), billing='not_dispatched',
                           measured_tokens=0, estimated_cost_USD=0)
        self.event('reservation_refused', reason=str(exc))

    def start_transport(self, request):
        if self.before_dispatch:
            self.before_dispatch(request)
        number = len(self.record['transports']) + 1
        key = self.key if number == 1 else f'{self.key}/hop-{number}'
        if number > 1:
            # Even an intermediate redirect might have been billed. Never assume zero.
            amount = budget.reserve(self.ledger, key, self.body, self.limit,
                reserve_tokens=self.reserve_tokens, analysis=self.analysis)
            self.record['reserved_tokens'] += amount
            self.event('tokens_reserved_additional_hop', tokens=amount, hop=number)
        try:
            payload_digest = hashlib.sha256(request.content).hexdigest()
        except httpx.RequestNotRead:
            payload_digest = None  # Do not consume or replace a stream to observe it.
        item = {'hop': number, 'ledger_key': key, 'url': str(request.url),
                'method': request.method, 'payload_sha256': payload_digest,
                'timeout': request.extensions.get('timeout'),
                'authorization_present': 'authorization' in request.headers,
                'transport_started_UTC': utc(), 'response_received': False}
        self.record['transports'].append(item)
        self.responses.append(None)
        self.record['transport_started'] = True
        self.event('transport_started', hop=number)
        return item, time.perf_counter()

    def transport_response(self, item, started, response):
        self.responses[item['hop'] - 1] = response
        item.update(response_received=True, status=response.status_code,
                    response_headers_UTC=utc(), transport_seconds=time.perf_counter() - started)
        self.event('response_headers_received', hop=item['hop'], status=response.status_code)

    def transport_error(self, item, started, exc):
        item.update(error=type(exc).__name__, transport_seconds=time.perf_counter() - started)
        self.event('transport_error_or_uncertain_outcome', hop=item['hop'], error=type(exc).__name__)

    def finish(self, error=None):
        self.record['elapsed_seconds'] = time.perf_counter() - self.start
        if error is not None:
            self.record['error'] = type(error).__name__
            if self.record['transport_started']:
                # A provider timeout is a transport timeout after dispatch, never queue time.
                self.record['interruption'] = (
                    'provider_timeout' if isinstance(error, httpx.TimeoutException) else
                    'cancelled_after_dispatch' if isinstance(error, (asyncio.CancelledError,
                                                                     TimeoutError)) else
                    'transport_error')
        if not self.record['transport_started']:
            if self.record['reserved_tokens']:
                budget.cancel_unstarted(self.ledger, self.key)
            self.record.update(outcome='not_dispatched', measured_tokens=0,
                               billing='not_dispatched', estimated_cost_USD=0)
        else:
            usages, costs = [], []
            for item, response in zip(self.record['transports'], self.responses):
                usage = usage_of(response)
                budget.settle(self.ledger, item['ledger_key'], usage)
                item['provider_usage'] = usage
                item['estimated_cost_USD'] = cost(usage, self.rates)
                usages.append(usage)
                costs.append(item['estimated_cost_USD'])
                if response is not None and response.is_stream_consumed:
                    try:
                        content = response.text
                    except httpx.ResponseNotRead:
                        content = None  # Stream interrupted: no fabricated partial response.
                    self.save(f'response-{item["hop"]}.json', {'status': response.status_code,
                              'text': content})
            known = all(u is not None for u in usages)
            self.record.update(outcome='transport_error_or_uncertain' if error else 'response_received',
                provider_usage=usages, measured_tokens=sum(u['total_tokens'] for u in usages) if known else None,
                billing='provider_usage_reported' if known else 'unknown',
                estimated_cost_USD=sum(costs) if all(c is not None for c in costs) else None)
        self.record['budget'] = budget.totals(self.ledger)
        self.event('exchange_finished', billing=self.record['billing'])


class TrackedAsync(httpx.AsyncBaseTransport):
    def __init__(self, transport, exchange):
        self.transport, self.exchange = transport, exchange

    async def handle_async_request(self, request):
        item, start = self.exchange.start_transport(request)
        try:
            response = await self.transport.handle_async_request(request)
        except BaseException as exc:
            self.exchange.transport_error(item, start, exc)
            raise
        self.exchange.transport_response(item, start, response)
        return response


class TrackedSync(httpx.BaseTransport):
    def __init__(self, transport, exchange):
        self.transport, self.exchange = transport, exchange

    def handle_request(self, request):
        item, start = self.exchange.start_transport(request)
        try:
            response = self.transport.handle_request(request)
        except BaseException as exc:
            self.exchange.transport_error(item, start, exc)
            raise
        self.exchange.transport_response(item, start, response)
        return response


def install_transport_observer():
    """Wrap selected transports, including redirect hops, without changing client options."""
    if getattr(httpx.AsyncClient, '_narrator_observer', False):
        return
    if httpx.__version__ != '0.28.1':
        raise RuntimeError('Revalidate audit adapter against this HTTPX version before use')
    real_async = httpx.AsyncClient._transport_for_url
    real_sync = httpx.Client._transport_for_url
    def async_transport(client, url):
        original = real_async(client, url)
        return TrackedAsync(original, ACTIVE.get()) if ACTIVE.get() else original
    def sync_transport(client, url):
        original = real_sync(client, url)
        return TrackedSync(original, ACTIVE.get()) if ACTIVE.get() else original
    httpx.AsyncClient._transport_for_url = async_transport
    httpx.Client._transport_for_url = sync_transport
    httpx.AsyncClient._narrator_observer = True


async def wait_in_line(ledger, key, amount, *, limit, reserve_tokens, analysis, wait_check,
                       ticket=False, on_queue=None):
    """Seconds waited; None for a ticket that can never fit. No time limit: budget.enqueue
    refuses as soon as no live reservation could make room, and wait_check (gate, stop)
    lets the operator end any wait. A waiter that leaves for any reason leaves the line."""
    started = time.perf_counter()
    try:
        while (done := budget.enqueue(ledger, key, amount, limit=limit,
                                      reserve_tokens=reserve_tokens, analysis=analysis,
                                      ticket=ticket)) is False:
            if on_queue:
                on_queue()
                on_queue = None
            wait_check()
            await asyncio.sleep(POLL_SECONDS)
    except BaseException:
        budget.withdraw(ledger, key)
        raise
    return None if done is None else time.perf_counter() - started


def install_admission_hook():
    """A segment of a planned analysis gets its ticket when its HTTP client opens: the
    compiler holds its own concurrency slot, but its model timeout has not started yet.
    Clients outside a plan, and the requests themselves, are untouched."""
    if getattr(httpx.AsyncClient, '_narrator_admission', False):
        return
    if httpx.__version__ != '0.28.1':
        raise RuntimeError('Revalidate audit adapter against this HTTPX version before use')
    real_enter, real_exit = httpx.AsyncClient.__aenter__, httpx.AsyncClient.__aexit__

    async def enter(client):
        plan = PLAN.get()
        if plan is None or not plan['amounts'] or TICKET.get() is not None:
            return await real_enter(client)
        key, amount = 'ticket-' + uuid4().hex, max(plan['amounts'])
        waited = await wait_in_line(plan['ledger'], key, amount, limit=plan['limit'],
                                    reserve_tokens=plan['reserve_tokens'], analysis=True,
                                    wait_check=plan['wait_check'], ticket=True)
        if waited is None:  # The largest segment can never fit: let the exact request decide.
            return await real_enter(client)
        token = TICKET.set({'key': key, 'waited': waited, 'used': False})
        try:
            result = await real_enter(client)
        except BaseException:
            TICKET.reset(token)
            budget.release(plan['ledger'], key)
            raise
        client._narrator_ticket = token, plan['ledger'], key
        return result

    async def exit_(client, *args):
        try:
            return await real_exit(client, *args)
        finally:
            if held := client.__dict__.pop('_narrator_ticket', None):
                TICKET.reset(held[0])
                budget.release(held[1], held[2])

    httpx.AsyncClient.__aenter__, httpx.AsyncClient.__aexit__ = enter, exit_
    httpx.AsyncClient._narrator_admission = True


def plan_segments(proposal, build, *, ledger, limit=budget.LIMIT, reserve_tokens=0,
                  wait_check=None):
    """Wrap the compiler's segmented analysis and its request builder, unchanged in
    arguments and results: bodies built during the analysis size its tickets."""
    @functools.wraps(proposal)
    async def planned(*args, **kwargs):
        token = PLAN.set({'ledger': Path(ledger), 'limit': limit, 'amounts': [],
                          'reserve_tokens': reserve_tokens, 'wait_check': wait_check or (
                              lambda: None)})
        try:
            return await proposal(*args, **kwargs)
        finally:
            PLAN.reset(token)

    @functools.wraps(build)
    def built(*args, **kwargs):
        body = build(*args, **kwargs)
        if (plan := PLAN.get()) is not None:
            with contextlib.suppress(AssertionError):  # Unbounded: refused at its reservation.
                plan['amounts'].append(budget.bound(body))
        return body

    return planned, built


async def observe(original, client, settings, body, root, *, context=None, rates=None,
                  simulated=False, limit=budget.LIMIT, reserve_tokens=0, analysis=False,
                  before_dispatch=None, wait_check=None, **kwargs):
    exchange = Exchange(root, body, settings.api_key or '', context, rates, simulated, limit,
                        before_dispatch, reserve_tokens, analysis or PLAN.get() is not None)
    await exchange.admit(wait_check)
    token = ACTIVE.set(exchange)
    error = None
    try:
        return await original(client, settings, body, **kwargs)
    except BaseException as exc:
        error = exc
        raise
    finally:
        ACTIVE.reset(token)
        exchange.finish(error)


def observe_sync(operation, body, root, *, rates=None, limit=budget.LIMIT, before_dispatch=None,
                 simulated=False):
    exchange = Exchange(root, body, rates=rates, limit=limit, before_dispatch=before_dispatch,
                        simulated=simulated)
    exchange.reserve()
    token = ACTIVE.set(exchange)
    error = None
    try:
        return operation()
    except BaseException as exc:
        error = exc
        raise
    finally:
        ACTIVE.reset(token)
        exchange.finish(error)
