"""Observe the actual HTTPX transport boundary; never equate dispatch with delivery.

No payload/header/URL/timeout mutation. The client continues to own redirects,
cookies, hooks and response reading. Each additional hop gets its own reservation.
The adapter is verified against the locked HTTPX 0.28.1 implementation.
"""
from __future__ import annotations

import contextvars
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx

from . import budget

ACTIVE = contextvars.ContextVar('audited_http_exchange', default=None)


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
                 limit=budget.LIMIT, before_dispatch=None):
        self.root, self.body, self.secret = Path(root), body, secret
        self.key = uuid4().hex
        self.folder = self.root / 'provider-calls' / self.key
        self.folder.mkdir(parents=True, exist_ok=False)
        self.ledger = self.root / 'budget-ledger.json'
        self.rates, self.limit, self.before_dispatch = rates, limit, before_dispatch
        self.responses = []
        self.start = time.perf_counter()
        self.record = {'id': self.key, 'context': context or {}, 'simulated': simulated,
                       'prepared_UTC': utc(), 'events': [], 'transports': [],
                       'reserved_tokens': 0, 'transport_started': False,
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
        try:
            amount = budget.reserve(self.ledger, self.key, self.body, self.limit)
        except (AssertionError, RuntimeError) as exc:
            self.record.update(outcome='refused_before_dispatch', error=type(exc).__name__,
                               billing='not_dispatched', measured_tokens=0, estimated_cost_USD=0)
            self.event('reservation_refused')
            raise
        for field in ('outcome', 'error', 'billing', 'measured_tokens'):
            self.record.pop(field, None)
        self.record['estimated_cost_USD'] = None
        self.record['reserved_tokens'] = amount
        self.record['reservation_wait_seconds'] = time.perf_counter() - self.start
        self.event('tokens_reserved', tokens=amount)

    def start_transport(self, request):
        if self.before_dispatch:
            self.before_dispatch(request)
        number = len(self.record['transports']) + 1
        key = self.key if number == 1 else f'{self.key}/hop-{number}'
        if number > 1:
            # Even an intermediate redirect might have been billed. Never assume zero.
            amount = budget.reserve(self.ledger, key, self.body, self.limit)
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


async def observe(original, client, settings, body, root, *, context=None, rates=None,
                  simulated=False, limit=budget.LIMIT, before_dispatch=None, wait_check=None, **kwargs):
    exchange = Exchange(root, body, settings.api_key or '', context, rates, simulated, limit,
                        before_dispatch)
    while True:
        try:
            exchange.reserve()
            break
        except RuntimeError:
            if not wait_check:
                raise
            with budget.locked(exchange.ledger) as state:
                pending = not state.get('stop') and any(c['status'] == 'pending' for c in state['calls'].values())
            if not pending:
                raise
            wait_check()
            if time.perf_counter() - exchange.start > 120:
                raise RuntimeError('Pending reservation unresolved; operator review required')
            import asyncio
            await asyncio.sleep(.1)
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
