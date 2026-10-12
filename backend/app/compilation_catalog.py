"""One deterministic FORM catalog, shared context instead of per-field copies.

This is document structure, not a semantic plan or evidence of applicant facts.
Native checkbox positions are catalogued for the next resolver; the existing
session/writer still supports only its original text candidates.
"""

from __future__ import annotations

import json
from io import BytesIO
from zipfile import ZipFile

from docx.oxml.ns import qn
from lxml import etree

from app.docx_templates import MAX_CANDIDATES, DocumentInputError, is_signature_target, text_of

W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
CATALOG_VERSION = 4
MAX_CATALOG_CHARACTERS = 200_000
MAX_PRECEDING_PARAGRAPHS = 6
MAX_SLOT_CONTEXT_CHARACTERS = 120


def _regions(layout):
    paragraphs = list(layout.document.element.body.iter(qn("w:p")))
    positions = {p: i for i, p in enumerate(paragraphs)}
    regions = []
    for element in layout.document.element.body:
        contained = list(element.iter(qn("w:p")))
        if contained:
            regions.append((f"paragraph:{positions[contained[0]]}", element, contained))
    return positions, regions


def document_blocks(layout):
    """Compatibility projection for the current reviewed document map."""
    _, regions = _regions(layout)
    locations, blocks = {}, []
    for block_id, _, paragraphs in regions:
        for paragraph in paragraphs:
            locations[paragraph] = block_id
        blocks.append({"id": block_id,
                       "text": "\n".join(text_of(p) for p in paragraphs if text_of(p).strip()),
                       "candidate_ids": []})
    by_id = {block["id"]: block for block in blocks}
    for candidate_id in sorted(layout.candidate_ids):
        element = (layout.slots[candidate_id].paragraph if candidate_id in layout.slots
                   else layout.cells[candidate_id])
        first = next(element.iter(qn("w:p")))
        by_id[locations[first]]["candidate_ids"].append(candidate_id)
    return blocks


def _outline_level(paragraph, styles):
    """Only explicit Word hierarchy; never infer section meaning from keywords."""
    properties = paragraph.find(qn("w:pPr"))
    visited = set()
    while properties is not None:
        level = properties.find(qn("w:outlineLvl"))
        if level is not None:
            value = level.get(qn("w:val"), "")
            return int(value) if value.isdigit() and 0 <= int(value) <= 8 else None
        style = properties.find(qn("w:pStyle"))
        style_id = style.get(qn("w:val")) if style is not None else None
        if style_id is None or style_id in visited or style_id not in styles:
            return None
        visited.add(style_id)
        definition = styles[style_id]
        properties = definition.find(qn("w:pPr"))
        if properties is not None and properties.find(qn("w:outlineLvl")) is not None:
            continue
        parent = definition.find(qn("w:basedOn"))
        if parent is None:
            return None
        # Continue through based-on styles without relying on localized names.
        properties = etree.Element(qn("w:pPr"))
        reference = etree.SubElement(properties, qn("w:pStyle"))
        reference.set(qn("w:val"), parent.get(qn("w:val"), ""))
    return None


def _boolean(element, attribute, *, absent=False):
    if element is None:
        return absent
    value = element.get(attribute)
    if value is None:
        return True
    if value in {"1", "true", "on"}:
        return True
    if value in {"0", "false", "off"}:
        return False
    raise DocumentInputError("Stato checkbox Word non riconosciuto")


def _checkboxes(body, positions):
    by_paragraph = {}
    for node in body.iter():
        if node.tag not in {qn("w:checkBox"), f"{{{W14}}}checkbox"}:
            continue
        paragraph = next(node.iterancestors(qn("w:p")), None)
        if paragraph is None:
            wrapper = next(node.iterancestors(qn("w:sdt")), None)
            content = wrapper.find(qn("w:sdtContent")) if wrapper is not None else None
            paragraph = next(content.iter(qn("w:p")), None) if content is not None else None
        if paragraph not in positions:
            raise DocumentInputError("Checkbox senza un contesto strutturale supportato")
        legacy = node.tag == qn("w:checkBox")
        state_tag = qn("w:checked") if legacy else f"{{{W14}}}checked"
        attribute = qn("w:val") if legacy else f"{{{W14}}}val"
        default = _boolean(node.find(qn("w:default")), qn("w:val")) if legacy else False
        controls = by_paragraph.setdefault(paragraph, [])
        controls.append((node, {
            "id": f"p{positions[paragraph]}.cb{len(controls)}", "offset": 0,
            "control_type": "legacy" if legacy else "content_control",
            "initial_checked": _boolean(node.find(state_tag), attribute, absent=default),
        }))
    return by_paragraph


def _paragraph_content(paragraph, paragraph_controls):
    text, references = [], []
    controls = {node: {**control} for node, control in paragraph_controls}
    length = 0
    for node in paragraph.iter():
        if next(node.iterancestors(qn("w:p")), None) is not paragraph:
            continue
        if node in controls:
            controls[node]["offset"] = length
        if node.tag in {qn("w:footnoteReference"), qn("w:endnoteReference")}:
            part = "footnotes" if node.tag == qn("w:footnoteReference") else "endnotes"
            references.append({"part": f"word/{part}.xml", "id": node.get(qn("w:id")),
                               "offset": length})
        run_child = node.getparent().tag == qn("w:r")
        value = (node.text or "") if node.tag == qn("w:t") else (
            "\n" if run_child and node.tag in {qn("w:br"), qn("w:cr")} else
            "\t" if run_child and node.tag == qn("w:tab") else ""
        )
        text.append(value)
        length += len(value)
    return "".join(text), list(controls.values()), references


def _all_text_direct_bold(paragraph):
    """A visual observation, never a heading/section or an applicability rule."""
    runs = {node.getparent() for node in paragraph.iter(qn("w:t"))
            if (node.text or "").strip()
            and next(node.iterancestors(qn("w:p")), None) is paragraph}
    return bool(runs) and all(
        _boolean(run.find(f"{qn('w:rPr')}/{qn('w:b')}"), qn("w:val"))
        for run in runs
    )


def _table_rows(table, ti, positions, tables):
    rows = []
    for ri, row in enumerate(table.findall(qn("w:tr"))):
        cells = []
        for ci, cell in enumerate(row.findall(qn("w:tc"))):
            record = {"id": f"t{ti}.r{ri}.c{ci}", "paragraph_ids": [
                f"paragraph:{positions[p]}" for p in cell.iter(qn("w:p"))
                if next(p.iterancestors(qn("w:tc")), None) is cell
            ]}
            nested = [f"table:{tables[t]}" for t in cell.iter(qn("w:tbl"))
                      if next(t.iterancestors(qn("w:tc")), None) is cell]
            if nested:
                record["table_ids"] = nested
            properties = cell.find(qn("w:tcPr"))
            if properties is not None:
                for tag, key, default in [("gridSpan", "grid_span", "1"),
                                          ("vMerge", "vertical_merge", "continue")]:
                    merged = properties.find(qn(f"w:{tag}"))
                    if merged is not None:
                        record[key] = merged.get(qn("w:val"), default)
            cells.append(record)
        rows.append(cells)
    return rows


def _read_only_parts(original):
    """Preserve textual instructions outside the body, without writable IDs."""
    parts = []
    with ZipFile(BytesIO(original)) as package:
        for name in sorted(package.namelist()):
            if not (name.startswith(("word/header", "word/footer")) and name.endswith(".xml")
                    or name in {"word/footnotes.xml", "word/endnotes.xml"}):
                continue
            root = etree.fromstring(package.read(name), etree.XMLParser(
                resolve_entities=False, no_network=True,
            ))
            paragraphs = [text_of(p) for p in root.iter(qn("w:p")) if text_of(p).strip()]
            controls = sum(node.tag in {qn("w:checkBox"), f"{{{W14}}}checkbox"}
                           for node in root.iter())
            if paragraphs or controls:
                part = {"part": name, "read_only_checkbox_count": controls}
                if name in {"word/footnotes.xml", "word/endnotes.xml"}:
                    part["notes"] = [{"id": note.get(qn("w:id")), "paragraphs": [
                        text_of(p) for p in note.iter(qn("w:p")) if text_of(p).strip()
                    ]} for note in root if text_of(note).strip()]
                else:
                    part["paragraphs"] = paragraphs
                parts.append(part)
    return parts


def _bind_locations(blocks, candidates):
    """Point directly into the canonical structure, without a second row map."""
    locations = {}
    for block in blocks:
        for paragraph in block["paragraphs"]:
            locations[paragraph["id"]] = {"block_id": block["id"]}
        tables = {table["id"]: table for table in block.get("tables", [])}
        for table in tables.values():
            for index, row in enumerate(table["rows"]):
                location = {"block_id": block["id"], "table_id": table["id"],
                            "row_index": index}
                for cell in row:
                    locations[cell["id"]] = location
                    for p in cell["paragraph_ids"]:
                        locations[p] = location
                    for nested in cell.get("table_ids", []):
                        tables[nested]["parent_cell_id"] = cell["id"]
    for candidate in candidates.values():
        candidate["location"] = locations[candidate["context_id"]]
    return {candidate["location"]["block_id"] for candidate in candidates.values()}


def _bind_slot_context(layout, paragraphs, candidates):
    """Expose the parser's exact slot map without guessing labels or direction.

    Surrounding snippets stop at the next/previous placeholder. Full original
    text is retained independently; markers are a structural projection only.
    """
    for entry in layout.paragraph_catalog:
        slots = [(field["id"], layout.slots[field["id"]]) for field in entry["fields"]]
        paragraph = paragraphs[slots[0][1].paragraph]
        # Parser coordinates include non-text object sentinels; visible text can
        # differ. Never recalculate slot offsets against the visible projection.
        if any(f"[[{key}]]" in entry["text"] for key in candidates):
            raise DocumentInputError("Marker candidate già presente nel testo originale")
        paragraph["text_with_fields"] = entry["text_with_fields"]
        for index, (key, slot) in enumerate(slots):
            previous_end = slots[index - 1][1].end if index else 0
            next_start = slots[index + 1][1].start if index + 1 < len(slots) else len(entry["text"])
            candidates[key]["slot_context"] = {
                "before": entry["text"][previous_end:slot.start][-MAX_SLOT_CONTEXT_CHARACTERS:],
                "after": entry["text"][slot.end:next_start][:MAX_SLOT_CONTEXT_CHARACTERS],
            }


def build_compilation_catalog(layout):
    """Catalog every supported body position and literal context, without AI/DB."""
    positions, regions = _regions(layout)
    tables = {element: index for index, element in enumerate(
        layout.document.element.body.iter(qn("w:tbl")),
    )}
    styles = {style.get(qn("w:styleId")): style for style in layout.document.styles.element}
    native_controls = _checkboxes(layout.document.element.body, positions)
    sections, stack, paragraphs = {}, [], {}
    controls = {}
    for paragraph, index in positions.items():
        paragraph_id = f"paragraph:{index}"
        text, paragraph_controls, references = _paragraph_content(
            paragraph, native_controls.get(paragraph, []),
        )
        level = _outline_level(paragraph, styles)
        if level is not None:
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, paragraph_id))
        sections[paragraph] = [section_id for _, section_id in stack]
        record = {"id": paragraph_id, "text": text}
        if _all_text_direct_bold(paragraph):
            record["all_text_direct_bold"] = True
        if level is not None:
            record["outline_level"] = level
        if paragraph_controls:
            record["controls"] = [{"id": c["id"], "offset": c["offset"]}
                                  for c in paragraph_controls]
        if references:
            record["references"] = references
        paragraphs[paragraph] = record
        for control in paragraph_controls:
            controls[control["id"]] = {"type": "checkbox", "context_id": paragraph_id,
                                       "section_ids": sections[paragraph],
                                       **{k: v for k, v in control.items()
                                          if k not in {"id", "offset"}}}
    blocks, preceding = [], []
    for block_id, element, contained in regions:
        block = {"id": block_id, "paragraphs": [paragraphs[p] for p in contained]}
        if preceding:
            block["preceding_body_paragraph_ids"] = preceding[-MAX_PRECEDING_PARAGRAPHS:]
        structure = []
        for table in element.iter(qn("w:tbl")):
            ti = tables[table]
            record = {"id": f"table:{ti}",
                      "rows": _table_rows(table, ti, positions, tables)}
            headers = [index for index, row in enumerate(table.findall(qn("w:tr")))
                       if _boolean(row.find(f"{qn('w:trPr')}/{qn('w:tblHeader')}"),
                                   qn("w:val"))]
            if headers:
                record["repeat_header_rows"] = headers
            structure.append(record)
        if structure:
            block["tables"] = structure
        blocks.append(block)
        if element.tag == qn("w:p") and paragraphs[element]["text"].strip():
            preceding.append(block_id)
    candidates = {}
    for candidate_id in sorted(layout.candidate_ids):
        slot = layout.slots.get(candidate_id)
        paragraph = slot.paragraph if slot else next(layout.cells[candidate_id].iter(qn("w:p")))
        candidate = {"type": "text", "context_id": f"paragraph:{positions[paragraph]}"
                     if slot else candidate_id, "section_ids": sections[paragraph]}
        if slot:
            candidate["range"] = [slot.start, slot.end]
        if candidate_id in layout.field_types:
            candidate["value_type"] = layout.field_types[candidate_id]
        if is_signature_target(layout, candidate_id):
            candidate["write_protected"] = True
        candidates[candidate_id] = candidate
    if set(candidates) & set(controls):
        raise DocumentInputError("ID candidate duplicato nel catalogo")
    candidates.update(controls)
    if len(candidates) > MAX_CANDIDATES:
        raise DocumentInputError("Il catalogo supera 400 candidate inclusi i controlli Word")
    _bind_slot_context(layout, paragraphs, candidates)
    candidate_blocks = _bind_locations(blocks, candidates)
    for block in blocks:
        if block["id"] not in candidate_blocks:
            # The full ordered text stays; nearby references help only targets.
            block.pop("preceding_body_paragraph_ids", None)
    catalog = {"version": CATALOG_VERSION, "role": "form", "template_sha256": layout.sha256,
               "candidate_scope": "document_body", "checkbox_write_supported": False,
               "blocks": blocks, "candidates": candidates,
               "read_only_parts": _read_only_parts(layout.original)}
    if len(json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))) > MAX_CATALOG_CHARACTERS:
        raise DocumentInputError("Catalogo completo oltre 200.000 caratteri: nessun testo omesso")
    return catalog
