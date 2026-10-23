"""Ground individual user questions without inventing values or broad conditions."""

from app.compilation_global_contract import UserFieldRequest
from app.docx_templates import is_signature_target

REASON_LIMIT = UserFieldRequest.model_json_schema()["properties"]["reason"]["maxLength"]


def _request_record(record, checked):
    """Quarantine only oversized descriptive text; validate every structural property."""
    reason = record.get("reason") if isinstance(record, dict) else None
    if not isinstance(reason, str) or len(reason.strip()) <= REASON_LIMIT:
        return record
    checked["metadata_warnings"] = [{
        "field": "reason", "code": "descriptive_text_over_limit",
        "original_characters": len(reason), "schema_max_characters": REASON_LIMIT,
        "preserved_in": "proposal.reason", "effect": "operational_reason_replaced",
    }]
    return {**record, "reason": (
        "Chiarimento richiesto dal modello; motivazione integrale conservata nella proposta.")}


def attach_user_requests(result, records, raw_fields, layout, catalog, paragraphs, local):
    from app.compilation_global import _slot_destination

    marked = {p["id"]: p["text_with_fields"] for b in catalog["blocks"]
              for p in b["paragraphs"] if "text_with_fields" in p}
    fields = {f["candidate_id"]: f for f in result["fields"]}
    requests = {}
    for cid, record in records.items():
        checked = {"validation": "REJECTED", "proposal": record, "validation_errors": []}
        try:
            request = UserFieldRequest.model_validate(_request_record(record, checked))
            if cid not in fields or cid in raw_fields:
                raise ValueError("Domanda senza posizione autonoma o già proposta dalle SOURCE")
            candidate = catalog["candidates"][cid]
            if candidate["type"] != "text" or is_signature_target(layout, cid):
                raise ValueError("Domanda ammessa soltanto su un campo testuale non firma")
            enriched = {**candidate, "anchor_paragraph_ids": local[candidate["context_id"]]}
            form, destination = _slot_destination(cid, enriched, request.form, paragraphs,
                                                  marked, layout)
            conditions = set(request.conditions) | set(fields[cid].get("conditions", []))
            if len(request.conditions) != len(set(request.conditions)) or any(
                result["conditions"].get(c, {}).get("validation") != "GROUNDED_PROPOSAL"
                for c in conditions
            ):
                raise ValueError("Domanda con condizioni assenti o non validate")
            checked.update(validation="GROUNDED_REQUEST", label=request.label,
                           form_evidence=form.model_dump(), conditions=sorted(conditions))
            fields[cid].update(label=request.label, kind="data", disposition="missing",
                               form_evidence=form.model_dump(), conditions=sorted(conditions),
                               reason=request.reason, destination_check=destination,
                               value=None, fact_id=None, source_evidence=[],
                               validation="REVIEW_REQUIRED", semantic_review_required=True)
        except ValueError as exc:
            checked["validation_errors"].append(str(exc))
        requests[cid] = checked
    result["clarifications"] = requests
    accepted = sum(r["validation"] == "GROUNDED_REQUEST" for r in requests.values())
    result["unassigned_count"] -= accepted
