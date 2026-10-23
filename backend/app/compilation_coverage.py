"""Account for omissions without authorizing values, applicability or user questions.

An anchored model explanation is not proof of a failed search or of semantic
completeness. Missing/invalid explanations remain visibly unexplained. A local
coverage failure must not discard independent, validated SOURCE proposals.
"""

from collections import Counter, defaultdict

from app.compilation_global_contract import UnfilledExplanation


def attach_coverage(result, payload, catalog, paragraphs, contexts):
    from app.compilation_global import _form_quote

    fields = {f["candidate_id"]: f for f in result["fields"]}
    accounted = {}
    for cid, field in fields.items():
        if field.get("proposal") is not None:
            rejected = field["validation"] == "REJECTED" or bool(field["validation_errors"])
            accounted[cid] = {"state": "REJECTED_PROPOSAL" if rejected else "PROPOSED",
                "origin": "BACKEND", "reason": "; ".join(field["validation_errors"])
                if rejected else "Proposta presente, soggetta ai gate SOURCE e di applicabilità"}
        request = result.get("clarifications", {}).get(cid)
        if cid not in accounted and request:
            accepted = request["validation"] == "GROUNDED_REQUEST"
            accounted[cid] = {"state": "CLARIFICATION" if accepted else "REJECTED_PROPOSAL",
                "origin": "BACKEND", "reason": field.get("reason", "") if accepted else
                "; ".join(request["validation_errors"])}

    records, groups, errors, claims = payload.get("coverage"), [], [], defaultdict(list)
    if not isinstance(records, list) or len(records) > 400:
        errors.append("Resoconto coverage assente, non valido o oltre il budget di400 gruppi")
        records = []
    marked = {p["id"]: p.get("text_with_fields", p["text"]) for b in catalog["blocks"]
              for p in b["paragraphs"]}
    tables = {t["id"]: {pid for row in t["rows"] for cell in row for pid in cell["paragraph_ids"]}
              for b in catalog["blocks"] for t in b.get("tables", [])}
    for block in catalog["blocks"]:
        for table in block.get("tables", []):
            tables[table["id"]].update(block.get("preceding_body_paragraph_ids", []))
    rejected = defaultdict(list)
    for index, record in enumerate(records):
        group = {"index": index, "proposal": record, "validation": "REJECTED",
                 "accepted_ids": [], "validation_errors": []}
        groups.append(group)
        try:
            item = UnfilledExplanation.model_validate(record)
            if len(item.conditions) != len(set(item.conditions)):
                raise ValueError("Condizioni duplicate nel resoconto")
            evidence = None
            if item.form is not None:
                pid = item.form.paragraph_id
                if pid not in paragraphs:
                    raise ValueError("Estratto del resoconto fuori dal FORM")
                text = marked[pid] if "[[" in item.form.quote else paragraphs[pid]
                evidence = {"paragraph_id": pid, "quote": _form_quote(text, item.form.quote),
                            "role": "form"}
            elif item.outcome != "unassessed":
                raise ValueError("Una motivazione richiede un estratto FORM verificabile")
            group.update(outcome=item.outcome, reason=item.reason, form_evidence=evidence,
                         candidate_ids=item.candidate_ids)
            shared = {catalog["candidates"][cid]["location"].get("table_id")
                      for cid in item.candidate_ids if cid in fields}
            table_context = (tables.get(next(iter(shared)), set()) if len(shared) == 1
                             and len(set(item.candidate_ids) & fields.keys()) > 1 else set())
            duplicates = {cid for cid, count in Counter(item.candidate_ids).items() if count > 1}
            for cid in dict.fromkeys(item.candidate_ids):
                problems = []
                if cid not in fields:
                    group["validation_errors"].append("Destinazione fuori dal catalogo: " + cid)
                    continue
                if cid in accounted:
                    group["validation_errors"].append(
                        "Esclusione sovrapposta a una proposta: " + cid)
                    continue
                if cid in duplicates:
                    problems.append("Posizione ripetuta nello stesso gruppo")
                conditions = set(item.conditions) | set(fields[cid].get("conditions", []))
                checks = [result["conditions"].get(c, {}) for c in conditions]
                allowed = set(contexts[cid]) | table_context
                allowed.update(c["form_evidence"]["paragraph_id"] for c in checks
                    if c.get("validation") == "GROUNDED_PROPOSAL" and
                    cid in c.get("applies_to", []) and c.get("form_evidence"))
                allowed.update(g["form_evidence"]["paragraph_id"] for g in result.get(
                    "choice_groups", {}).values() if g.get("validation") == "GROUNDED_GROUP"
                    and cid in g["options"] and g.get("form_evidence"))
                if evidence and evidence["paragraph_id"] not in allowed:
                    problems.append("Estratto non appartenente al contesto della posizione")
                if any(c.get("validation") != "GROUNDED_PROPOSAL" for c in checks):
                    problems.append("Condizione del resoconto assente o non valida")
                if item.outcome in {"condition_unknown", "not_applicable"}:
                    expected = "unknown" if item.outcome == "condition_unknown" else "false"
                    if not checks or not any(c.get("result") == expected and cid in c.get(
                        "applies_to", []) for c in checks):
                        problems.append("Applicabilità dichiarata senza una condizione locale "
                                        + expected)
                claims[cid].append((index, item, evidence, problems))
        except ValueError as exc:
            group["validation_errors"].append(str(exc))
        # Distinguish no decision from a returned but invalid explanation.
        raw_ids = record.get("candidate_ids") if isinstance(record, dict) else None
        if isinstance(raw_ids, list) and len(raw_ids) <= 400:
            for cid in raw_ids:
                if isinstance(cid, str) and cid in fields and cid not in accounted:
                    rejected[cid].append(index)

    for cid, candidates in claims.items():
        if len(candidates) != 1:
            for index, _, _, _ in candidates:
                groups[index]["validation_errors"].append("Esiti sovrapposti per " + cid)
            continue
        index, item, evidence, problems = candidates[0]
        if problems:
            groups[index]["validation_errors"].extend(cid + ": " + p for p in problems)
            continue
        accounted[cid] = {"state": "UNASSESSED" if item.outcome == "unassessed" else
                          "EXPLAINED_UNFILLED", "origin": "MODEL", "outcome": item.outcome,
                          "reason": item.reason, "group_index": index,
                          "form_evidence": evidence, "semantic_review_required": True}
        groups[index]["accepted_ids"].append(cid)
    for group in groups:
        if group["accepted_ids"]:
            group["validation"] = "PARTIAL" if group["validation_errors"] else "FORM_ANCHORED"
    for cid, field in fields.items():
        rejected_reason = ({"state": "REJECTED_EXPLANATION", "origin": "BACKEND",
            "reason": "Motivazione restituita ma non validata: consultare gli errori dei gruppi",
            "group_indices": sorted(set(rejected[cid]))} if cid in rejected else None)
        field["coverage"] = accounted.get(cid, rejected_reason or {
            "state": "UNEXPLAINED", "origin": "BACKEND",
            "reason": "Nessuna decisione o motivazione restituita per questa posizione"})
    counts = Counter(f["coverage"]["state"] for f in fields.values())
    result.update(coverage_groups=groups, coverage_errors=errors, coverage_summary={
        "total": len(fields), "proposed": counts["PROPOSED"],
        "clarifications": counts["CLARIFICATION"], "rejected": counts["REJECTED_PROPOSAL"],
        "explained_unfilled": counts["EXPLAINED_UNFILLED"],
        "explicitly_unassessed": counts["UNASSESSED"], "unexplained": counts["UNEXPLAINED"],
        "rejected_explanations": counts["REJECTED_EXPLANATION"],
        "explicit_decisions_complete": counts["UNEXPLAINED"] == 0,
        "coverage_checks_passed": not any(counts[k] for k in (
            "UNEXPLAINED", "REJECTED_EXPLANATION", "REJECTED_PROPOSAL", "UNASSESSED")),
        "semantic_completeness_verified": False,
        "outcomes": dict(Counter(f["coverage"]["outcome"] for f in fields.values()
                                 if "outcome" in f["coverage"]))})


def narration_coverage(audit, handled_ids=()):
    """Bounded human context, no technical recipients or invented absence claims."""
    summary = audit.get("coverage_summary")
    if summary is None:
        return {"recorded": False, "positions_without_proposal": audit.get("unassigned_count", 0),
                "meaning": "Omissioni dell'output precedente, non prova che non siano state lette"}
    handled = set(handled_ids) | {f["candidate_id"] for f in audit.get("fields", [])
                                 if f.get("source_reuse")}
    groups = [{**g, "accepted_ids": [cid for cid in g["accepted_ids"] if cid not in handled]}
              for g in audit["coverage_groups"]]
    groups = [g for g in groups if g["accepted_ids"]]
    return {"recorded": True, **summary,
            "groups": [{"outcome": g["outcome"], "reason": g["reason"],
                        "positions": len(g["accepted_ids"]),
                        "form_context": (g.get("form_evidence") or {}).get("quote", "")}
                       for g in groups[:24]], "omitted_groups": max(0, len(groups) - 24),
            "meaning": "Motivazioni MODEL ancorate al FORM; non prova di assenza nelle SOURCE "
                       "e non autorizzazione a scrivere o a dichiarare la non applicabilità"}


def source_availability_context(audit, sources, answers=None):
    """Literal input records are reading hints, never new accepted facts.

    We cannot certify exhaustive absence or successful retrieval from a model
    coverage explanation. Expose those unknowns rather than inventing a search.
    """
    from app.compilation_role_records import _subject_records

    fields, answers = audit.get("fields", []), answers or {}
    used = [e.get("quote", "") for f in fields for e in f.get("source_evidence", [])]
    records, seen = [], set()
    for source in sources:
        if source.get("role") != "source" or source.get("category") == "general":
            continue
        for record in _subject_records(source["content"], None):
            quote = record["record"]
            key = (source["file_id"], record.get("subject"), quote)
            if key in seen:
                continue
            seen.add(key)
            records.append({"subject": record.get("subject", ""),
                "source_name": source["source_name"], "quote": quote[:800],
                "truncated": len(quote) > 800,
                "table_title": record.get("title", ""),
                "used_by_proposal": any(quote in q or q in quote for q in used if q)})
    return {"absent_from_sources": {"verified": False,
                "meaning": "Nessuna verifica esaustiva di assenza disponibile"},
            "not_retrieved": {"verified": False,
                "meaning": "Non deducibile da un'omissione del modello"},
            "present_not_proposed": {"meaning": "Record dell'input non citati da proposte; "
                "non provano da soli la pertinenza a ogni campo", "records": [
                    r for r in records if not r["used_by_proposal"]][:24]},
            "rejected_proposals": sum(bool(f.get("validation_errors")) for f in fields),
            "conditional_or_waiting": sum(any(
                check.get("result") == "unknown" and answers.get(
                    "condition:" + key, {}).get("applies") is None
                for key, check in f.get("condition_checks", {}).items()) for f in fields),
            "meaning": "Indizi SOURCE distinti da decisioni USER e fatti validati; "
                       "non dichiarare un dato assente soltanto perché non è proposto"}


def coverage_notice(audit):
    """A truthful initial notice cannot depend on the narrator remembering omissions."""
    summary = audit.get("coverage_summary") or {}
    if summary.get("unexplained") or summary.get("explicitly_unassessed"):
        invalid = ("Altre motivazioni non sono state validate nel contesto del modulo. "
                   if summary.get("rejected_explanations") else "")
        return ("Per alcune posizioni manca ancora un esito esplicito. " + invalid
                + "La copertura del modulo resta incompleta.")
    if summary.get("rejected_explanations"):
        return ("Alcune motivazioni non sono state validate nel contesto del modulo "
                "e richiedono una verifica.")
    return ""
