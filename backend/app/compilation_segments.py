"""Backend-owned FORM segments for a global proposal split across calls (P3).

Every call keeps the complete FORM, SOURCE and USER context: only the
responsibility for proposals is partitioned. Blocks are never split and an
option clause stays with the table that follows it. The merged envelope is
re-serialized and validated by the unchanged V12 validator; a failed segment
leaves its destinations visibly unanalyzed, never partially recovered.
"""

import json
import math
import re
from copy import deepcopy

from app.compilation_factual_recovery import canonical_property

GENERATION_REVISION = 1
MAX_SEGMENT_CANDIDATES = 60
MAX_SEGMENTS = 6
MAX_CONCURRENT_SEGMENTS = 3
LIMITS = {"facts": 128, "conditions": 128, "bindings": 128, "choice_groups": 64,
          "clarifications": 16}
CONFLICT_REASON = "Valori SOURCE diversi proposti in sezioni diverse del modulo"


def _block_of(catalog):
    owner = {}
    for block in catalog["blocks"]:
        for paragraph in block["paragraphs"]:
            owner[paragraph["id"]] = block["id"]
    result = {}
    for cid, candidate in catalog["candidates"].items():
        block = candidate.get("location", {}).get("block_id") or owner.get(
            candidate.get("context_id"))
        if block is None:
            raise ValueError("Candidate senza blocco FORM: partizione non dimostrabile")
        result[cid] = block
    return result


def partition(catalog):
    """Contiguous block units in document order, balanced by candidate count."""
    from app.compilation_option_regions import option_regions

    order = [block["id"] for block in catalog["blocks"]]
    position = {bid: i for i, bid in enumerate(order)}
    block_of = _block_of(catalog)
    # Union of block ranges that must stay together (an option clause and its table).
    joined = list(range(len(order)))

    def root(i):
        while joined[i] != i:
            joined[i] = joined[joined[i]]
            i = joined[i]
        return i

    for region in option_regions(catalog):
        blocks = {block_of[cid] for cid in region["field_ids"] if cid in block_of}
        anchor = next((b["id"] for b in catalog["blocks"]
                       if any(p["id"] == region["paragraph_id"] for p in b["paragraphs"])), None)
        if anchor:
            blocks.add(anchor)
        if blocks:
            first, last = min(position[b] for b in blocks), max(position[b] for b in blocks)
            for i in range(first, last + 1):
                joined[root(i)] = root(first)
    units = []
    for i, bid in enumerate(order):
        if units and root(i) == root(units[-1][-1]):
            units[-1].append(i)
        else:
            units.append([i])
    by_block = {}
    for cid, bid in block_of.items():
        by_block.setdefault(bid, []).append(cid)
    total = len(catalog["candidates"])
    target = max(MAX_SEGMENT_CANDIDATES, math.ceil(total / MAX_SEGMENTS))
    segments, current = [], {"block_ids": [], "candidate_ids": []}
    for unit in units:
        ids = [cid for i in unit for cid in by_block.get(order[i], [])]
        if current["candidate_ids"] and ids and len(current["candidate_ids"]) + len(ids) > target:
            segments.append(current)
            current = {"block_ids": [], "candidate_ids": []}
        current["block_ids"].extend(order[i] for i in unit)
        current["candidate_ids"].extend(ids)
    if current["candidate_ids"] or not segments:
        segments.append(current)
    else:
        segments[-1]["block_ids"].extend(current["block_ids"])
    for index, segment in enumerate(segments, start=1):
        segment["index"] = index
    return segments


def instruction(segment, count):
    ids = ",".join(segment["candidate_ids"])
    return (f"SEGMENTO {segment['index']} DI {count}. Questa chiamata copre SOLTANTO i candidate "
            f"in segment_candidate_ids. Leggi comunque l'intero FORM e tutte le SOURCE per "
            "interpretare soggetti, ruoli, condizioni e valori, anche quando sono in altre "
            "sezioni. fields, clarifications e coverage contengono SOLO candidate di questo "
            "segmento: non scrivere nulla sugli altri, che sono assegnati ad altre chiamate. "
            "Puoi definire facts, bindings, conditions e choice_groups necessari a questi "
            "candidate anche se la clausola FORM citata è in un'altra sezione. Le regole di "
            "coverage valgono soltanto per le posizioni di questo segmento.\n"
            f"segment_candidate_ids: [{ids}]")


def parse(raw):
    """Literal control characters inside strings are accepted; nothing is repaired."""
    from app.compilation_global import _unique_object
    from app.compilation_json import checked_json

    payload = checked_json(raw, object_pairs_hook=_unique_object, strict=False)
    if not isinstance(payload, dict) or payload.get("version") != 12:
        raise ValueError("Segmento senza envelope V12")
    return payload


def _rename(value, mapping):
    return mapping.get(value, value) if isinstance(value, str) else value


def merge(segments, payloads):
    """Merge successful segment payloads into one V12 envelope; return (payload, report)."""
    merged = {"version": 12, "uncertain_paragraph_ids": [], "conditions": {}, "bindings": {},
              "choice_groups": {}, "fields": {}, "facts": {}, "clarifications": {},
              "coverage": []}
    seen = {kind: {} for kind in LIMITS}
    report = {"dropped_out_of_segment": [], "deduplicated": dict.fromkeys(LIMITS, 0),
              "conflicts": [], "dropped_unreferenced_facts": 0}
    by_index = {segment["index"]: segment for segment in segments}

    for index in sorted(payloads):
        payload, allowed = payloads[index], set(by_index[index]["candidate_ids"])
        names = {kind: {} for kind in LIMITS}

        def intern(kind, old, value, index=index, names=names):
            key = json.dumps(value, sort_keys=True, ensure_ascii=False)
            if key in seen[kind]:
                report["deduplicated"][kind] += 1
                new = seen[kind][key]
            else:
                # A single segment is the whole FORM: identifiers stay unchanged.
                new = f"s{index}_{old}"[:80] if len(segments) > 1 else old
                while new in merged[kind]:
                    new = new[:76] + f"_{len(merged[kind])}"
                seen[kind][key] = new
                merged[kind][new] = value
            names[kind][old] = new

        for old, fact in (payload.get("facts") or {}).items():
            intern("facts", old, deepcopy(fact))
        for old, binding in (payload.get("bindings") or {}).items():
            intern("bindings", old, deepcopy(binding))
        for old, condition in (payload.get("conditions") or {}).items():
            condition = deepcopy(condition)
            if isinstance(condition, dict) and isinstance(condition.get("fact_ids"), list):
                condition["fact_ids"] = [_rename(f, names["facts"]) for f in condition["fact_ids"]]
            intern("conditions", old, condition)
        conditions = names["conditions"]
        for old, group in (payload.get("choice_groups") or {}).items():
            group = deepcopy(group)
            if isinstance(group, dict) and isinstance(group.get("conditions"), list):
                group["conditions"] = [_rename(c, conditions) for c in group["conditions"]]
            intern("choice_groups", old, group)
        for cid, field in (payload.get("fields") or {}).items():
            if cid not in allowed or cid in merged["fields"]:
                report["dropped_out_of_segment"].append({"segment": index, "candidate_id": cid})
                continue
            field = deepcopy(field)
            if isinstance(field, dict):
                if field.get("fact_id") is not None:
                    field["fact_id"] = _rename(field["fact_id"], names["facts"])
                if field.get("binding_id") is not None:
                    field["binding_id"] = _rename(field["binding_id"], names["bindings"])
                if isinstance(field.get("conditions"), list):
                    field["conditions"] = [_rename(c, conditions) for c in field["conditions"]]
                if isinstance(field.get("alternative_fact_ids"), list):
                    field["alternative_fact_ids"] = [_rename(f, names["facts"])
                                                     for f in field["alternative_fact_ids"]]
                if field.get("choice_group_id") is not None:
                    field["choice_group_id"] = _rename(field["choice_group_id"],
                                                       names["choice_groups"])
            merged["fields"][cid] = field
        for cid, request in (payload.get("clarifications") or {}).items():
            if cid not in allowed or cid in merged["clarifications"]:
                report["dropped_out_of_segment"].append({"segment": index, "candidate_id": cid})
                continue
            request = deepcopy(request)
            if isinstance(request, dict) and isinstance(request.get("conditions"), list):
                request["conditions"] = [_rename(c, conditions) for c in request["conditions"]]
            merged["clarifications"][cid] = request
        for record in payload.get("coverage") or []:
            if not isinstance(record, dict) or not isinstance(record.get("candidate_ids"), list):
                merged["coverage"].append(deepcopy(record))
                continue
            kept = [cid for cid in record["candidate_ids"] if cid in allowed]
            dropped = [cid for cid in record["candidate_ids"] if cid not in allowed]
            report["dropped_out_of_segment"].extend(
                {"segment": index, "candidate_id": cid, "coverage": True} for cid in dropped)
            if kept:
                record = {**deepcopy(record), "candidate_ids": kept}
                if isinstance(record.get("conditions"), list):
                    record["conditions"] = [_rename(c, conditions) for c in record["conditions"]]
                merged["coverage"].append(record)
        for pid in payload.get("uncertain_paragraph_ids") or []:
            if pid not in merged["uncertain_paragraph_ids"]:
                merged["uncertain_paragraph_ids"].append(pid)
    _mark_conflicts(merged, report)
    if len(merged["facts"]) > LIMITS["facts"]:
        used = {f.get("fact_id") for f in merged["fields"].values() if isinstance(f, dict)}
        used |= {a for f in merged["fields"].values() if isinstance(f, dict)
                 for a in f.get("alternative_fact_ids") or []}
        used |= {a for c in merged["conditions"].values() if isinstance(c, dict)
                 for a in c.get("fact_ids") or []}
        unused = [k for k in merged["facts"] if k not in used]
        for key in unused[:len(merged["facts"]) - LIMITS["facts"]]:
            del merged["facts"][key]
            report["dropped_unreferenced_facts"] += 1
    report["over_limits"] = {k: len(merged[k]) for k, limit in LIMITS.items()
                             if len(merged[k]) > limit}
    return merged, report


def _norm(value):
    return " ".join(str(value).casefold().split())


def _mark_conflicts(merged, report):
    """Different values for one subject/property from different segments become a review."""
    groups = {}
    for key, fact in merged["facts"].items():
        if not isinstance(fact, dict) or not re.match(r"s\d+_", key):
            continue
        signature = (_norm(fact.get("subject", "")), fact.get("entity"),
                     canonical_property(fact.get("property", "")))
        groups.setdefault(signature, []).append(key)
    conflicting = {}
    for signature, keys in groups.items():
        values = {_norm(merged["facts"][k].get("value", "")) for k in keys}
        segments = {k.split("_", 1)[0] for k in keys}
        if len(values) > 1 and len(segments) > 1:
            for key in keys:
                conflicting[key] = keys
            report["conflicts"].append({"subject": signature[0], "entity": signature[1],
                                        "property": signature[2], "fact_ids": keys})
    for cid, field in merged["fields"].items():
        if (not isinstance(field, dict) or field.get("fact_id") not in conflicting
                or field.get("kind") != "data"):
            continue
        keys = conflicting[field["fact_id"]][:4]
        merged["fields"][cid] = {
            "label": field.get("label", cid), "kind": "data", "disposition": "review",
            "form": field.get("form"), "conditions": field.get("conditions", []),
            "property": field.get("property") or "valore", "review_kind": "conflicting",
            "alternative_fact_ids": keys,
            "reason": CONFLICT_REASON}


def attach_status(audit, report):
    """Unanalyzed destinations are explicit BACKEND coverage, never a MODEL explanation."""
    failed = {cid: segment for segment in report.get("segments", [])
              if segment["status"] != "analyzed" for cid in segment["candidate_ids"]}
    for field in audit.get("fields", []):
        segment = failed.get(field["candidate_id"])
        if segment and not field.get("proposal"):
            field["coverage"] = {"state": "UNASSESSED", "origin": "BACKEND",
                                 "reason": "Sezione del modulo non analizzata: "
                                 + segment["error"], "segment": segment["index"]}
    audit["generation_segments"] = {
        "revision": GENERATION_REVISION,
        "segments": [{k: s[k] for k in ("index", "status", "candidate_count", "error")}
                     for s in report.get("segments", [])],
        "unanalyzed_candidate_ids": sorted(failed),
        "dropped_out_of_segment": len(report.get("dropped_out_of_segment", [])),
        "conflicts": report.get("conflicts", []),
    }
    if "coverage_summary" in audit:
        from collections import Counter

        counts = Counter(f["coverage"]["state"] for f in audit["fields"] if f.get("coverage"))
        audit["coverage_summary"]["explicitly_unassessed"] = counts["UNASSESSED"]
        audit["coverage_summary"]["unexplained"] = counts["UNEXPLAINED"]
    return audit


# Resilient segments (generation_revision 2, candidate, not adopted). Ownership follows the
# dependencies the backend already knows (FORM block, local paragraphs that scope conditions,
# V14 option regions); size is a secondary criterion. Each segment receives only its FORM
# context, is validated on its own and cached by request digest for resumption.

RESILIENT_REVISION = 2
TARGET_CANDIDATES = 60
MAX_RESILIENT_SEGMENTS = 8
MAX_RETRIES_PER_SEGMENT = 1
MAX_RETRIES_PER_ANALYSIS = 2
UNASSESSED_REASON = "Sezione del modulo non analizzata: applicabilità non accertata"


def _document_rank(catalog):
    """Candidate order in the document (catalog keys are not ordered by position)."""
    block_of = _block_of(catalog)
    blocks = {block["id"]: i for i, block in enumerate(catalog["blocks"])}
    paragraphs = {p["id"]: i for block in catalog["blocks"]
                  for i, p in enumerate(block["paragraphs"])}
    return {cid: (blocks[block_of[cid]], paragraphs.get(candidate["context_id"], 0),
                  (candidate.get("range") or [0])[0], cid)
            for cid, candidate in catalog["candidates"].items()}


def dependency_units(catalog):
    """Destinations that must share an owner, in document order."""
    from app.compilation_option_regions import option_regions

    block_of = _block_of(catalog)
    rank = _document_rank(catalog)
    parent = {cid: cid for cid in catalog["candidates"]}

    def find(cid):
        while parent[cid] != cid:
            parent[cid] = parent[parent[cid]]
            cid = parent[cid]
        return cid

    groups = {}
    for cid, candidate in catalog["candidates"].items():
        groups.setdefault(("block", block_of[cid]), []).append(cid)
        for paragraph in candidate.get("anchor_paragraph_ids", []):
            groups.setdefault(("paragraph", paragraph), []).append(cid)
    for region in option_regions(catalog):
        groups.setdefault(("region", region["paragraph_id"]), []).extend(
            cid for cid in region["field_ids"] if cid in parent)
    for members in groups.values():
        for cid in members[1:]:
            parent[find(cid)] = find(members[0])
    units = {}
    for cid in catalog["candidates"]:
        units.setdefault(find(cid), []).append(cid)
    return sorted((sorted(ids, key=rank.get) for ids in units.values()),
                  key=lambda ids: rank[ids[0]])


def resilient_partition(catalog, target=TARGET_CANDIDATES):
    """Pack whole dependency units; prefer a cut before a bold heading paragraph."""
    block_of = _block_of(catalog)
    position = {block["id"]: i for i, block in enumerate(catalog["blocks"])}
    paragraph_block = {p["id"]: block["id"] for block in catalog["blocks"]
                       for p in block["paragraphs"]}
    with_fields = {c["context_id"] for c in catalog["candidates"].values()}
    headings = sorted({position[block["id"]] for block in catalog["blocks"]
                       for p in block["paragraphs"]
                       if p.get("all_text_direct_bold") and p["text"].strip()
                       and p["id"] not in with_fields})
    target = max(target, math.ceil(len(catalog["candidates"]) / MAX_RESILIENT_SEGMENTS))
    packs, current, last = [], [], -1
    for unit in dependency_units(catalog):
        first = min(position[block_of[c]] for c in unit)
        heading = any(last < h < first for h in headings)
        if current and (len(current) + len(unit) > target
                        or (heading and len(current) >= target / 2)):
            packs.append(current)
            current = []
        current.extend(unit)
        last = max(last, max(position[block_of[c]] for c in unit))
    if current or not packs:
        packs.append(current)
    # Quantity stays secondary but a tiny section is not worth a call of its own: it joins the
    # previous pack when the union stays within the target (whole units, order unchanged).
    merged_packs = []
    for pack in packs:
        if (merged_packs and len(pack) < target / 4
                and len(merged_packs[-1]) + len(pack) <= target):
            merged_packs[-1] = merged_packs[-1] + pack
        else:
            merged_packs.append(pack)
    packs = merged_packs
    from app.compilation_global import _condition_bindings
    from app.compilation_option_regions import option_regions

    # Every paragraph whose conditions the validator would scope over a destination, the
    # lead-in a continuation depends on and an option clause are shown to the owner.
    clauses = _condition_bindings(catalog)
    for region in option_regions(catalog):
        for cid in region["field_ids"]:
            if cid in catalog["candidates"]:
                key = catalog["candidates"][cid]["context_id"]
                clauses[key] = {*clauses[key], region["paragraph_id"]}
    segments = []
    for index, ids in enumerate(packs, start=1):
        own = {block_of[c] for c in ids}
        context = set(own) | {paragraph_block[p] for c in ids
                              for p in [*catalog["candidates"][c].get("anchor_paragraph_ids", []),
                                        *clauses[catalog["candidates"][c]["context_id"]],
                                        catalog["candidates"][c].get(
                                            "continuation_origin_paragraph_id")]
                              if p in paragraph_block}
        first = min((position[b] for b in own), default=0)
        previous = [h for h in headings if h < first]
        if previous:
            context.add(catalog["blocks"][previous[-1]]["id"])
        segments.append({"index": index, "candidate_ids": ids,
                         "block_ids": sorted(own, key=position.get),
                         "context_block_ids": sorted(context, key=position.get)})
    return segments


def segment_input(model_input, segment, *, revision=2):
    """Rev 2 local FORM; rev 3 full FORM before segment-specific destinations and plan."""
    own = set(segment["candidate_ids"])
    keep = set(segment["context_block_ids"])
    if revision == 3:
        keep = {b["id"] for b in model_input["form"]["blocks"]}
    form = model_input["form"]
    plan = deepcopy(model_input.get("reading_plan") or {})
    for key in ("units", "source_role_targets"):
        if isinstance(plan.get(key), list):
            plan[key] = [{**item, "candidate_ids": [c for c in item["candidate_ids"] if c in own]}
                         for item in plan[key] if own & set(item.get("candidate_ids", []))]
    data = {key: model_input[key] for key in (
        "proposal_stage", "project_id", "sources", "schema_output", "source_coverage",
        "user_values", "user_context", "reference_date") if key in model_input}
    data.update({key: value for key, value in model_input.items()
                 if key not in data and key not in {"form", "reading_plan"}})
    # SOURCE-derived parts of the plan are the same for every segment: they stay in the
    # cacheable prefix, before this segment's units and role targets.
    data["reading_plan"] = {**{k: v for k, v in plan.items()
                               if k not in {"units", "source_role_targets"}},
                            **{k: plan[k] for k in ("units", "source_role_targets") if k in plan}}
    data["form"] = {**form, "blocks": [b for b in form["blocks"] if b["id"] in keep],
                    "candidates": {c: form["candidates"][c] for c in segment["candidate_ids"]}}
    if revision == 3:
        # Keep the entire shared FORM in the identical input prefix. Local reading-plan
        # units must not precede it and invalidate provider prefix caching for every segment.
        complete_form = {**{k: v for k, v in form.items() if k != "candidates"},
                         "candidates": data["form"]["candidates"]}
        return {**{k: v for k, v in data.items() if k not in {"form", "reading_plan"}},
                "form": complete_form, "reading_plan": data["reading_plan"]}
    return data


def resilient_instruction(segment, count, *, revision=2):
    if revision == 3:
        return instruction(segment, count).replace(
            "\nsegment_candidate_ids:",
            " Ogni opzione di choice_groups deve appartenere a questo segmento.\n"
            "segment_candidate_ids:")
    ids = ",".join(segment["candidate_ids"])
    return (f"SEGMENTO {segment['index']} DI {count}. Il FORM ricevuto contiene soltanto i blocchi "
            "di questo segmento, i paragrafi del loro contesto locale e l'intestazione che li "
            "precede: le altre parti del modulo sono assegnate ad altre chiamate. fields, "
            "clarifications e coverage contengono SOLO candidate in segment_candidate_ids. "
            "facts, bindings, conditions e choice_groups citano soltanto paragrafi FORM e SOURCE "
            "ricevuti. Le regole di coverage valgono soltanto per le posizioni di questo "
            f"segmento.\nsegment_candidate_ids: [{ids}]")


def request_digest(body):
    import hashlib

    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()
                          ).hexdigest()


def unify_shared_conditions(merged, report):
    """Same FORM clause and structure from different segments: one condition, scopes united.

    One USER answer then settles every scope. Different structures on the same paragraph stay
    separate and are reported, never chosen implicitly.
    """
    def signature(condition):
        form = condition.get("form") or {}
        facts = sorted(json.dumps(merged["facts"].get(f), sort_keys=True, ensure_ascii=False)
                       for f in condition.get("fact_ids") or [])
        return (form.get("paragraph_id"), _norm(form.get("quote", "")), condition.get("aspect"),
                condition.get("operator"), tuple(facts))

    groups, by_paragraph = {}, {}
    for key, condition in merged["conditions"].items():
        if isinstance(condition, dict) and re.match(r"s\d+_", key):
            groups.setdefault(signature(condition), []).append(key)
            by_paragraph.setdefault((condition.get("form") or {}).get("paragraph_id"),
                                    set()).add(signature(condition))
    alias = {}
    report["unified_conditions"] = []
    for keys in groups.values():
        if len({k.split("_", 1)[0] for k in keys}) < 2:
            continue
        kept = merged["conditions"][keys[0]]
        scope = list(kept.get("scope") or [])
        for other in keys[1:]:
            scope += [s for s in merged["conditions"][other].get("scope") or [] if s not in scope]
            alias[other] = keys[0]
            del merged["conditions"][other]
        if scope:
            kept["scope"] = scope
        report["unified_conditions"].append({"kept": keys[0], "merged": keys[1:]})
    report["shared_conditions_not_unified"] = sorted(
        str(p) for p, signatures in by_paragraph.items() if len(signatures) > 1)

    def renamed(values):
        out = []
        for value in values:
            value = alias.get(value, value)
            if value not in out:
                out.append(value)
        return out

    for container in (merged["fields"], merged["clarifications"], merged["choice_groups"]):
        for record in container.values():
            if isinstance(record, dict) and isinstance(record.get("conditions"), list):
                record["conditions"] = renamed(record["conditions"])
    for record in merged["coverage"]:
        if isinstance(record, dict) and isinstance(record.get("conditions"), list):
            record["conditions"] = renamed(record["conditions"])
    return merged


def resilient_merge(segments, payloads, *, revision=2):
    """P3 merge (ownership, renaming, exact dedup, value conflicts) plus shared conditions."""
    merged, report = merge(segments, payloads)
    return (merged if revision == 3 else unify_shared_conditions(merged, report)), report


def attach_resilient_status(audit, report):
    """Unanalyzed destinations: BACKEND coverage and NON ACCERTATA applicability."""
    failed = {cid: segment for segment in report.get("segments", [])
              if segment["status"] != "analyzed" for cid in segment["candidate_ids"]}
    for field in audit.get("fields", []):
        segment = failed.get(field["candidate_id"])
        if segment and not field.get("proposal"):
            field["coverage"] = {"state": "UNASSESSED", "origin": "BACKEND",
                                 "reason": UNASSESSED_REASON + " (" + str(segment["error"]) + ")",
                                 "segment": segment["index"]}
    audit["generation_segments"] = {
        "revision": report.get("revision", RESILIENT_REVISION),
        "segments": [{**{k: s.get(k) for k in ("index", "status", "candidate_count", "error",
                                               "source", "digest")},
                      "attempts": len(s.get("attempts") or [])}
                     for s in report.get("segments", [])],
        "unanalyzed_candidate_ids": sorted(failed),
        "dropped_out_of_segment": len(report.get("dropped_out_of_segment", [])),
        "conflicts": report.get("conflicts", []),
        "unified_conditions": report.get("unified_conditions", []),
        "shared_conditions_not_unified": report.get("shared_conditions_not_unified", []),
        "retries": report.get("retries", 0)}
    if "coverage_summary" in audit:
        from collections import Counter

        counts = Counter(f["coverage"]["state"] for f in audit["fields"] if f.get("coverage"))
        audit["coverage_summary"]["explicitly_unassessed"] = counts["UNASSESSED"]
        audit["coverage_summary"]["unexplained"] = counts["UNEXPLAINED"]
    return audit


def unassessed_fields(data):
    """Destinations owned by a segment that was not analyzed (applicability NON ACCERTATA).

    A SOURCE proposal or reuse there lacks the owner's assessment of conditions; only a USER
    value given for that same destination keeps an independent FORM/USER chain.
    """
    if data.get("generation_revision") not in {RESILIENT_REVISION, 3}:
        return set()
    segments = (data.get("audit") or {}).get("generation_segments") or {}
    return set(segments.get("unanalyzed_candidate_ids", []))


def uncertain_fields(data):
    """Rev 2: destinations whose local FORM paragraphs the model declared uncertain.

    The model could not determine their conditions: a SOURCE value there stays CONDIZIONATA.
    """
    if data.get("generation_revision") not in {RESILIENT_REVISION, 3}:
        return set()
    uncertain = set((data.get("audit") or {}).get("uncertain_paragraph_ids") or [])
    return {cid for cid, candidate in ((data.get("catalog") or {}).get("candidates") or {}).items()
            if uncertain & {candidate.get("context_id"), *candidate.get(
                "anchor_paragraph_ids", [])}} if uncertain else set()


def unverified_fields(data):
    """Rev 2 SOURCE writes not VERIFICATA beyond the existing gates (USER values unaffected)."""
    from app.compilation_scope_review import blocked_source_fields

    return unassessed_fields(data) | uncertain_fields(data) | blocked_source_fields(data)


def applicability_states(data):
    """VERIFICATA / CONDIZIONATA / NON_ACCERTATA with the checks that assigned them.

    VERIFICATA means only that no recognized dependency is pending: owner segment analyzed,
    conditions attached by the model or by the validator's local scope resolved, no pending V14
    authorization or FORM predicate. A clause the model omitted outside the local paragraphs and
    unknown to V14 or to the FORM predicate grammar is not detected.
    """
    from app.compilation_branch_evidence import effective_user_values
    from app.compilation_form_applicability import blocked_fields as predicates
    from app.compilation_procedural_consent import blocked_fields as authorizations

    audit = data.get("audit") or {}
    answers = (data.get("dialogue") or {}).get("answers", {})
    users = effective_user_values(data)
    from app.compilation_form_option_scope import uncovered_fields as option_uncovered
    from app.compilation_table_scope import blocked_fields as table_scope_blocked

    table_unknown = table_scope_blocked(data)
    option_unknown = option_uncovered(data)
    unassessed = unassessed_fields(data)
    pending = {"predicato_FORM": predicates(data), "autorizzazione_V14": authorizations(data),
               "paragrafo_locale_incerto": uncertain_fields(data)}
    from app.compilation_scope_review import blocked_source_fields, blocked_user_fields, enabled

    user_blocked = blocked_user_fields(data)
    independent_users = set(users) - user_blocked if enabled(data) else set()
    pending["condizione_intestazione_FORM_non_accertata"] = table_unknown
    pending["condizione_opzione_FORM_non_accertata"] = option_unknown
    pending["ambito_USER_non_verificato"] = blocked_source_fields(data) | user_blocked
    pending["paragrafo_locale_incerto"] -= independent_users
    states = {}
    for field in audit.get("fields", []):
        cid = field["candidate_id"]
        grounded = "GROUNDED_PROPOSAL" in {field.get("validation"),
                                           field.get("proposal_grounding")}
        # Rejected proposals are not writes: they have no applicability to assess.
        if not (grounded or cid in users):
            continue
        reasons = [name for name, ids in pending.items() if cid in ids]
        for key in field.get("conditions", []):
            result = (audit.get("conditions", {}).get(key) or {}).get("result", "unknown")
            receipt = answers.get("condition:" + key, {})
            if receipt.get("applies") is False or (result == "false" and receipt.get(
                    "applies") is not True):
                reasons.append("condizione_falsa:" + key)
            elif result != "true" and receipt.get("applies") is not True:
                reasons.append("condizione_aperta:" + key)
        user_only = cid in users and not grounded
        if enabled(data):
            user_only = cid in independent_users
        if cid in unassessed and not user_only:
            states[cid] = {"state": "NON_ACCERTATA", "reasons": ["segmento_non_analizzato"]
                           + reasons}
        elif cid in table_unknown or cid in option_unknown:
            states[cid] = {"state": "NON_ACCERTATA", "reasons": reasons}
        elif reasons:
            states[cid] = {"state": "CONDIZIONATA", "reasons": reasons}
        else:
            states[cid] = {"state": "VERIFICATA", "reasons": ["controlli_disponibili_superati"]}
    return states
