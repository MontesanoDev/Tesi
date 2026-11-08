"""Bounded FORM label edges, derived from the original physical Word grid.

This backend projection never enters the model input. Edges prove location,
not property entailment, SOURCE identity, role, applicability or permission.
Unmatched spans, competing labels and interrupted column schemas have no edge.
"""

from docx.oxml.ns import qn


def _number(element, path, default):
    node = element.find(path)
    value = node.get(qn("w:val"), "") if node is not None else str(default)
    return int(value) if value.isdigit() else None


def relations(layout, catalog):
    """Use catalog IDs, checking offsets/merges against their original XML nodes."""
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    occupied = {c["context_id"] for c in catalog["candidates"].values()}
    tables = list(layout.document.element.body.iter(qn("w:tbl")))
    result = {}
    for block in catalog["blocks"]:
        for table in block.get("tables", []):
            xml = tables[int(table["id"].split(":")[1])]
            grid = xml.find(qn("w:tblGrid"))
            width = len(grid) if grid is not None else 0
            rows, active = [], {}
            for records, tr in zip(table["rows"], xml.findall(qn("w:tr")), strict=True):
                offset = _number(tr, f'{qn("w:trPr")}/{qn("w:gridBefore")}', 0)
                after = _number(tr, f'{qn("w:trPr")}/{qn("w:gridAfter")}', 0)
                row, next_active = [], {}
                for cell, tc in zip(records, tr.findall(qn("w:tc")), strict=True):
                    span = _number(tc, f'{qn("w:tcPr")}/{qn("w:gridSpan")}', 1)
                    valid = offset is not None and span is not None and span > 0
                    interval = (offset, offset + span) if valid else None
                    proofs = [{"paragraph_id": p, "quote": paragraphs[p]["text"], "role": "form"}
                              for p in cell["paragraph_ids"] if paragraphs[p]["text"].strip()]
                    complex_cell = (bool(cell.get("table_ids")) or
                                    tc.find(f'{qn("w:tcPr")}/{qn("w:hMerge")}') is not None or
                                    any(paragraphs[p].get("controls")
                                        for p in cell["paragraph_ids"]))
                    fixed = bool(proofs) and not complex_cell and not (
                        {cell["id"], *cell["paragraph_ids"]} & occupied)
                    candidate = catalog["candidates"].get(cell["id"], {})
                    # The existing parser owns blank/placeholder eligibility,
                    # including underscore/dot cells; do not invent another parser.
                    target = candidate.get("type") == "text" and not complex_cell
                    entry = {"id": cell["id"], "interval": interval, "proofs": proofs,
                             "paragraph_ids": cell["paragraph_ids"], "fixed": fixed,
                             "target": target, "start_row": len(rows), "end_row": len(rows)}
                    merge = cell.get("vertical_merge")
                    if merge == "continue":
                        origin = active.get(interval)
                        entry.update(fixed=False, target=False)
                        if origin is not None and not proofs and not complex_cell:
                            origin["end_row"] = len(rows)
                            next_active[interval] = origin
                    elif merge == "restart":
                        next_active[interval] = entry
                    elif merge is not None:
                        entry.update(fixed=False, target=False)
                    row.append(entry)
                    offset = interval[1] if interval else None
                if not width or offset is None or after is None or offset + after != width:
                    for entry in row:
                        entry.update(fixed=False, target=False)
                rows.append(row)
                active = next_active

            for ri, row in enumerate(rows):
                # Alternating physical label/value cells give a unique orientation.
                pairs = []
                column_schema = len(rows[0]) > 1 and all(c["fixed"] for c in rows[0])
                for direction in (() if ri and column_schema else (0, 1)):
                    if len(row) % 2 == 0 and row and all(
                        c["fixed" if i % 2 == direction else "target"]
                        for i, c in enumerate(row)
                    ):
                        pairs = [(row[i + direction], row[i + 1 - direction])
                                 for i in range(0, len(row), 2)]
                adjacent = {target["id"]: label for label, target in pairs
                            if (label["start_row"], label["end_row"]) ==
                               (target["start_row"], target["end_row"])}
                for target in row:
                    if not target["target"]:
                        continue
                    labels = []
                    if target["id"] in adjacent:
                        labels.append(("adjacent_cell", adjacent[target["id"]]))
                    if ri and all(c["target"] for c in row):
                        previous = rows[ri - 1]
                        if previous and all(c["fixed"] and c["end_row"] == ri - 1
                                            for c in previous):
                            labels.extend(("previous_row", c) for c in previous
                                          if c["interval"] == target["interval"])
                        # A first row is a column schema only along uninterrupted
                        # blank data rows. No repeated-header flag or text keywords.
                        header = rows[0]
                        if (header and all(c["fixed"] and c["end_row"] == 0 for c in header)
                                and all(all(c["target"] for c in r) for r in rows[1:ri + 1])):
                            labels.extend(("first_row_column", c) for c in header
                                          if c["interval"] == target["interval"])
                    unique = {label["id"] for _, label in labels}
                    record = {"candidate_id": target["id"], "table_id": table["id"],
                              "target_cell_id": target["id"], "row_index": ri,
                              "grid_interval": list(target["interval"]),
                              "original_sha256": layout.sha256, "role": "form",
                              "semantic_review_required": True}
                    if len(unique) != 1:
                        result[target["id"]] = {**record, "result": "not_demonstrated",
                                                "reason": "competing_or_missing_labels"}
                        continue
                    method, label = labels[-1]
                    record.update(result="structural_match", method=method,
                                  label_cell_id=label["id"], form_evidence=label["proofs"],
                                  label_grid_interval=list(label["interval"]),
                                  vertical_extent=[target["start_row"], target["end_row"]])
                    if method in {"previous_row", "first_row_column"}:
                        label_row = rows[label["start_row"]]
                        record["schema_evidence"] = [p for c in label_row for p in c["proofs"]]
                    result[target["id"]] = record
            # Unsupported/continued cells cannot fall back to a broad row/header
            # merely because another label happens to be present there.
            for row in rows:
                for cell in row:
                    if catalog["candidates"].get(cell["id"], {}).get("type") == "text":
                        result.setdefault(cell["id"], {
                            "candidate_id": cell["id"], "table_id": table["id"],
                            "result": "not_demonstrated", "role": "form",
                            "original_sha256": layout.sha256,
                            "reason": "unsupported_or_ambiguous_geometry"})
    return result


def apply_bindings(local, catalog):
    """Restrict whole-cell proofs to their own cell and explicit label edges.

    Inline slots and checkbox groups retain their independent historical gates.
    No role context is extended by these property edges.
    """
    cells = {c["id"]: c for b in catalog["blocks"] for t in b.get("tables", [])
             for row in t["rows"] for c in row}
    for cid, edge in catalog.get("_table_form_links", {}).items():
        candidate = catalog["candidates"][cid]
        own = cells[cid]["paragraph_ids"]
        local[candidate["context_id"]] = set(own) | {
            p["paragraph_id"] for p in edge.get("form_evidence", [])}


def source_conflicts(edge, fact, fields, facts, links):
    """Necessary negative checks only; never establish a new SOURCE binding."""
    from app.compilation_attribution import COMPANY, PERSON

    text = " ".join(p["quote"] for p in edge.get("schema_evidence", edge["form_evidence"]))
    entities = {entity for entity, pattern in [("person", PERSON), ("company", COMPANY)]
                if pattern.search(text)}
    if entities and entities != {fact.get("entity")}:
        return "Tipo di soggetto SOURCE incompatibile con le etichette FORM collegate"
    if "schema_evidence" in edge:
        identities = set()
        for cid, field in fields.items():
            other = links.get(cid, {})
            if ((other.get("table_id"), other.get("row_index")) !=
                    (edge["table_id"], edge["row_index"])):
                continue
            source = facts.get(field.get("fact_id"), {}) if isinstance(field, dict) else {}
            if source.get("validation") == "GROUNDED_PROPOSAL":
                identities.add((source["entity"], " ".join(source["subject"].casefold().split())))
        if len(identities) > 1:
            return "Riga FORM con valori SOURCE attribuiti a soggetti diversi"
    return None


def authorization_required(edge, kind):
    """A newly linked declaration cannot acquire consent from a SOURCE value.

    Markerless table declarations have no existing bounded USER receipt flow;
    keep their previous no-write result rather than inventing one here.
    """
    from app.compilation_procedural_consent import COMMITMENT

    return kind == "declaration" or any(COMMITMENT.search(p["quote"])
                                         for p in edge["form_evidence"])
