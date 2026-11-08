"""Experimental E1 input projection. Production catalog/validators stay canonical.

No AI, database, gold or semantic labels: only share candidate metadata already
present in the catalog. All ordered text, markers and table topology stay exact.
"""

from copy import deepcopy

VIEW_VERSION = "compact-v1"
_SHARED = ("section_ids", "anchor_paragraph_ids", "continuation_origin_paragraph_id")
_BACKEND = {"location", "range", "slot_context"}
_KNOWN = _BACKEND | set(_SHARED) | {
    "type", "context_id", "value_type", "write_protected", "control_type", "initial_checked",
}

VIEW_INSTRUCTIONS = """
FORM: VISTA COMPATTA compact-v1.
Solo la rappresentazione di ingresso cambia; schema di risposta e prove restano
quelli sopra. form.blocks conserva testo originale, text_with_fields,
text_with_choices, ordine, tabelle e riferimenti identici al catalogo completo.
L'inventario logico form.candidates è serializzato in form.contexts: ogni chiave
è un context_id originale (paragraph:N o ID di cella). fields elenca gli ID
compilabili di quel contesto; usa SOLO questi ID nella risposta. defaults contiene
sezioni/ancore/continuazione condivise; field_options contiene eccezioni per ID
e proprietà individuali (tipo, formato, protezione, stato iniziale del controllo).
Per un campo eredita defaults e applica field_options[id]. Default assenti:
type=text, section_ids=[], anchor_paragraph_ids=[]; nessuna continuazione.
type=checkbox identifica un controllo nativo e conserva initial_checked. Le
celle testuali delle tabelle restano text, non convertirle in checkbox native.
Contesto, sezioni, ancore e continuazioni sono riferimenti strutturali, non fatti
SOURCE o decisioni USER. Coordinate XML e range sono conservati dal backend.
Per citazioni/condizioni/ruoli usa ancora i testi letterali in form.blocks;
per destinazioni inline usa i marker esistenti, senza ricostruire placeholder.
""".strip()


def _logical(candidate):
    result = {k: deepcopy(v) for k, v in candidate.items() if k not in _BACKEND}
    result.setdefault("type", "text")
    result.setdefault("section_ids", [])
    result.setdefault("anchor_paragraph_ids", [])
    return result


def compact_form(catalog):
    """Produce a new view without mutating the caller's canonical catalog."""
    if "view_version" in catalog or "contexts" in catalog:
        raise ValueError("Expected a canonical catalog, not an existing view")
    contexts = {}
    for cid, candidate in catalog["candidates"].items():
        if extra := candidate.keys() - _KNOWN:
            raise ValueError(f"Unsupported candidate properties: {sorted(extra)}")
        if candidate["type"] not in {"text", "checkbox"}:
            raise ValueError("Unsupported candidate type")
        contexts.setdefault(candidate["context_id"], {})[cid] = candidate
    view = {k: deepcopy(v) for k, v in catalog.items() if k != "candidates"}
    view.update(view_version=VIEW_VERSION, contexts={})
    for context_id, fields in contexts.items():
        logical = {cid: _logical(field) for cid, field in fields.items()}
        records = list(logical.values())
        common = {k: records[0][k] for k in _SHARED
                  if k in records[0] and records[0][k]
                  and all(r.get(k) == records[0][k] for r in records)}
        options = {}
        for cid, record in logical.items():
            individual = {k: v for k, v in record.items()
                          if k != "context_id" and k not in common
                          and not (k == "type" and v == "text")
                          and not (k in {"section_ids", "anchor_paragraph_ids"} and v == [])}
            if individual:
                options[cid] = individual
        group = {"fields": list(fields)}
        if common:
            group["defaults"] = deepcopy(common)
        if options:
            group["field_options"] = options
        view["contexts"][context_id] = group
    validate_form_view(catalog, view)
    return view


def validate_form_view(catalog, view):
    """Check meaning/relationships independently of compact_form's grouping.

    Exact blocks equality covers table rows, merges, nested parent relationships,
    marker text, heading/bold observations and read-only instructions, not just IDs.
    """
    if view.get("view_version") != VIEW_VERSION or "candidates" in view:
        raise ValueError("Unexpected FORM view contract")
    metadata = {k: v for k, v in catalog.items() if k != "candidates"}
    if {k: v for k, v in view.items() if k not in {"contexts", "view_version"}} != metadata:
        raise ValueError("FORM text, topology or metadata changed")
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    cells = {c["id"] for b in catalog["blocks"] for t in b.get("tables", [])
             for row in t["rows"] for c in row}
    resolved = {}
    for context_id, group in view["contexts"].items():
        if context_id not in paragraphs and context_id not in cells:
            raise ValueError("Unresolved context")
        if group.keys() - {"fields", "defaults", "field_options"}:
            raise ValueError("Unknown context properties")
        defaults = group.get("defaults", {})
        if defaults.keys() - set(_SHARED):
            raise ValueError("Invalid shared defaults")
        if group.get("field_options", {}).keys() - set(group["fields"]):
            raise ValueError("Options for unknown field")
        for cid in group["fields"]:
            if cid in resolved:
                raise ValueError("Duplicate candidate")
            record = {"context_id": context_id, "type": "text",
                      "section_ids": [], "anchor_paragraph_ids": [], **defaults,
                      **group.get("field_options", {}).get(cid, {})}
            if record != _logical(catalog["candidates"].get(cid, {})):
                raise ValueError(f"Changed candidate semantics: {cid}")
            refs = record["section_ids"] + record["anchor_paragraph_ids"]
            if continuation := record.get("continuation_origin_paragraph_id"):
                refs += [continuation]
            if any(ref not in paragraphs for ref in refs):
                raise ValueError("Unresolved paragraph reference")
            if cid.startswith("p") and record["type"] == "text":
                if paragraphs[context_id].get("text_with_fields", "").count(f"[[{cid}]]") != 1:
                    raise ValueError("Inline field marker missing or duplicated")
            resolved[cid] = record
    if resolved.keys() != catalog["candidates"].keys():
        raise ValueError("Candidate inventory changed")
    return {"view_version": VIEW_VERSION, "candidate_count": len(resolved),
            "context_count": len(view["contexts"]), "ordered_blocks_exact": True,
            "candidate_semantics_exact": True, "references_resolve": True,
            "backend_only_properties": sorted(_BACKEND)}


def compact_input(data):
    """Change only FORM; SOURCE, reading plan, USER and output schema are exact."""
    return {**deepcopy(data), "form": compact_form(data["form"])}


INDEXED_VIEW_VERSION = "compact-index-v2"
INDEXED_VIEW_INSTRUCTIONS = """
FORM: VISTA COMPATTA compact-index-v2.
Solo il formato di ingresso cambia; schema di risposta e prove restano quelli
sopra. form.blocks conserva testo originale, text_with_fields, text_with_choices,
ordine, tabelle e riferimenti identici al catalogo completo.
form.candidates conserva l'indice DIRETTO per ID: ogni record espone type e
context_id originali, oltre alle proprietà individuali quando presenti.
Per leggere sezioni/ancore/continuazione di un candidate, eredita le proprietà
di form.contexts[candidate.context_id] e applica gli override nel suo record.
Default assenti: section_ids=[], anchor_paragraph_ids=[], nessuna continuazione.
I riferimenti sono strutturali, non fatti SOURCE o decisioni USER. Non dedurre
ruoli o condizioni da un ID. Le celle text restano distinte dai controlli nativi
type=checkbox, con stato iniziale e tipo di controllo espliciti.
Coordinate XML, range e copie before/after restano nel backend. Un ID presente
in text_with_fields è sempre una destinazione INLINE: anche senza range nel
payload, cita un estratto contiguo con il marker e testo prestampato utile.
Per condizioni/ruoli e celle di tabella usa ancora gli estratti originali;
per opzioni native usa text_with_choices. Nessun criterio di prova è rilassato.
""".strip()


def indexed_form(catalog):
    """Same canonical information as v1, with direct ID lookup and explicit types."""
    grouped = compact_form(catalog)
    view = {k: deepcopy(v) for k, v in catalog.items() if k != "candidates"}
    view.update(view_version=INDEXED_VIEW_VERSION, candidates={}, contexts={})
    for context_id, group in grouped["contexts"].items():
        view["contexts"][context_id] = deepcopy(group.get("defaults", {}))
        for cid in group["fields"]:
            view["candidates"][cid] = {
                "type": catalog["candidates"][cid]["type"], "context_id": context_id,
                **deepcopy(group.get("field_options", {}).get(cid, {})),
            }
    validate_indexed_form(catalog, view)
    return view


def validate_indexed_form(catalog, view):
    """Verify the flat index against canonical fields, not against v1 expansion."""
    if view.get("view_version") != INDEXED_VIEW_VERSION:
        raise ValueError("Unexpected indexed FORM view contract")
    metadata = {k: v for k, v in catalog.items() if k != "candidates"}
    if {k: v for k, v in view.items()
            if k not in {"contexts", "candidates", "view_version"}} != metadata:
        raise ValueError("FORM text, topology or metadata changed")
    candidates = view["candidates"]
    if candidates.keys() != catalog["candidates"].keys():
        raise ValueError("Candidate inventory changed")
    expected_contexts = {c["context_id"] for c in catalog["candidates"].values()}
    if view["contexts"].keys() != expected_contexts:
        raise ValueError("Context inventory changed")
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    cells = {c["id"] for b in catalog["blocks"] for t in b.get("tables", [])
             for row in t["rows"] for c in row}
    for context_id, defaults in view["contexts"].items():
        if context_id not in paragraphs and context_id not in cells:
            raise ValueError("Unresolved context")
        if defaults.keys() - set(_SHARED):
            raise ValueError("Invalid shared context properties")
    for cid, candidate in candidates.items():
        if candidate.keys() - (_KNOWN - _BACKEND):
            raise ValueError("Unknown or backend-only candidate property")
        if not {"type", "context_id"} <= candidate.keys():
            raise ValueError("Direct index needs explicit type and context_id")
        context_id = candidate["context_id"]
        if context_id not in view["contexts"]:
            raise ValueError("Unresolved candidate context")
        record = {"section_ids": [], "anchor_paragraph_ids": [],
                  **view["contexts"][context_id], **candidate}
        if record != _logical(catalog["candidates"][cid]):
            raise ValueError(f"Changed candidate semantics: {cid}")
        refs = record["section_ids"] + record["anchor_paragraph_ids"]
        if continuation := record.get("continuation_origin_paragraph_id"):
            refs += [continuation]
        if any(ref not in paragraphs for ref in refs):
            raise ValueError("Unresolved paragraph reference")
        if cid.startswith("p") and candidate["type"] == "text":
            if paragraphs[context_id].get("text_with_fields", "").count(f"[[{cid}]]") != 1:
                raise ValueError("Inline field marker missing or duplicated")
    return {"view_version": INDEXED_VIEW_VERSION, "candidate_count": len(candidates),
            "context_count": len(view["contexts"]), "direct_candidate_index": True,
            "explicit_candidate_types": True, "ordered_blocks_exact": True,
            "candidate_semantics_exact": True, "references_resolve": True,
            "backend_only_properties": sorted(_BACKEND)}


def indexed_input(data):
    """Change only FORM, preserving other input components and original objects."""
    return {**deepcopy(data), "form": indexed_form(data["form"])}
