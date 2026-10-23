"""FORM option regions for the declaration-authorization gate (catalog only).

An option is a native checkbox of the catalog or a box glyph in the paragraph text.
Its region is the paragraph from the first marker onwards and, for a body option,
the table that immediately follows it. An option inside a table cell governs only
its own paragraph. The option's own controls are the decision, never governed.

A region proves nothing: it only says which writes need an explicit authorization
of the whole printed clause. A branch selection or condition receipt is not one.
Not recognized (left to the existing gates): symbol fonts, «[ ]», private-use
glyphs, continuations in later paragraphs and conditions expressed only in words.
"""

from __future__ import annotations

import re

BOX_GLYPHS = re.compile("[☐□❏❑◻☑☒]")


def _cells(catalog):
    cells, tables = {}, {}
    for block in catalog["blocks"]:
        for table in block.get("tables", []):
            for row in table["rows"]:
                for cell in row:
                    for paragraph_id in cell["paragraph_ids"]:
                        cells[paragraph_id] = cell["id"]
            tables[table["id"]] = table
    return cells, tables


def _adjacent_tables(catalog, block_index):
    """Tables of the next non-empty block, if that block starts with a table."""
    for block in catalog["blocks"][block_index + 1:]:
        if block.get("tables"):
            return [table["id"] for table in block["tables"]]
        if any(p["text"].strip() for p in block["paragraphs"]):
            return []
    return []


def _marked(text, start, fields):
    """Original text from start, with each governed inline slot shown as its marker."""
    parts, cursor = [], start
    for begin, end, cid in sorted(fields):
        parts.extend([text[cursor:begin], f"[[{cid}]]"])
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts).strip()


def _table_text(table, paragraphs, governed):
    rows = []
    for row in table["rows"]:
        cells = []
        for cell in row:
            if cell["id"] in governed:
                cells.append(f"[[{cell['id']}]]")
            else:
                cells.append(" ".join(paragraphs[p].strip() for p in cell["paragraph_ids"]
                                      if paragraphs[p].strip()))
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def option_regions(catalog):
    candidates = catalog["candidates"]
    cells, tables = _cells(catalog)
    paragraphs = {p["id"]: p["text"] for b in catalog["blocks"] for p in b["paragraphs"]}
    regions = []
    for index, block in enumerate(catalog["blocks"]):
        for paragraph in block["paragraphs"]:
            text = paragraph["text"]
            own = [c["id"] for c in paragraph.get("controls", [])]
            cuts = [c["offset"] for c in paragraph.get("controls", [])]
            cuts += [m.start() for m in BOX_GLYPHS.finditer(text)]
            if not cuts:
                continue
            start = min(cuts)
            inline = [(c["range"][0], c["range"][1], cid) for cid, c in candidates.items()
                      if c.get("context_id") == paragraph["id"] and c["type"] == "text"
                      and "range" in c and c["range"][0] >= start]
            governed = [cid for _, _, cid in sorted(inline)]
            # Show the whole printed paragraph: inline alternatives share its subject.
            clause = _marked(text, 0, inline)
            in_cell = paragraph["id"] in cells
            last_in_block = paragraph["id"] == block["paragraphs"][-1]["id"]
            if not in_cell and last_in_block:
                for table_id in _adjacent_tables(catalog, index):
                    table_ids = [cid for cid, c in candidates.items()
                                 if c.get("location", {}).get("table_id") == table_id
                                 and cid not in own]
                    governed += table_ids
                    clause += "\n" + _table_text(tables[table_id], paragraphs, set(table_ids))
            governed = [cid for cid in dict.fromkeys(governed) if cid not in own]
            if governed:
                regions.append({"paragraph_id": paragraph["id"], "text": text,
                                "marked_clause": clause, "field_ids": governed,
                                "own_controls": own, "in_table_cell": in_cell})
    return regions
