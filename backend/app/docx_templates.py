from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from email_validator import EmailNotValidError, validate_email
from lxml import etree

MAX_DOCX_BYTES = 20 * 1024 * 1024
MAX_UNPACKED_BYTES = 40 * 1024 * 1024
MAX_CANDIDATES = 400
MAX_CATALOG_CHARACTERS = 100_000
DRAFT_NOTICE = "BOZZA NON VERIFICATA - NON FIRMARE O INVIARE SENZA REVISIONE"
PLACEHOLDER = re.compile(r"[\s_.\-\u2026\u2013\u2014]*\Z")
INLINE_PLACEHOLDER = re.compile(
    r"_(?:[ \u00a0]*_){1,}|[.\u2026](?:[ \u00a0]*[.\u2026])*"
    r"|\{\{[^{}\n]{1,80}\}\}"
    r"|\[(?:DA COMPILARE|INSERIRE|INDICARE)\b[^\]\n]{0,80}\]",
    re.IGNORECASE,
)
EMAIL_LABEL = re.compile(
    r"(?<!\w)(?:e[ -]?mail|p\.?[ \u00a0]*e\.?[ \u00a0]*c\.?"
    r"|posta\s+elettronica(?:\s+certificata)?)"
    r"(?:\s+(?:aziendale|personale|istituzionale))?"
    r"(?:\s*\([^()\n]{1,60}\))?[\s:.-]*\Z",
    re.IGNORECASE,
)
SIGNATURE_LABEL = re.compile(r"\b(?:firma|firmato|signature|sottoscrizione)\b", re.IGNORECASE)
COMPLEX_CONTENT = {
    qn(f"w:{tag}")
    for tag in (
        "fldChar",
        "instrText",
        "fldSimple",
        "sdt",
        "drawing",
        "pict",
        "sym",
        "object",
        "hyperlink",
        "footnoteReference",
        "endnoteReference",
    )
}
PARAGRAPH_CHILDREN = {
    qn(f"w:{tag}") for tag in ("pPr", "r", "bookmarkStart", "bookmarkEnd", "proofErr")
}


class DocumentInputError(ValueError):
    pass


class DocxTooLargeError(DocumentInputError):
    pass


def text_of(element) -> str:
    return "".join(node.text or "" for node in element.iter(qn("w:t")))


def normalized(value: str) -> str:
    return " ".join(value.split()).casefold()


def is_email_label(value: str) -> bool:
    return bool(EMAIL_LABEL.search(value.replace("_", " ")))


def _placeholder_matches(text: str) -> list[re.Match]:
    matches = []
    for match in INLINE_PLACEHOLDER.finditer(text):
        if match.group().startswith("_") and match.group().count("_") == 2:
            # Short fields such as (__) are explicit blanks. Keep bare double
            # underscores in identifiers or prose outside the writable catalog.
            before = text[:match.start()].rstrip(" \u00a0")
            after = text[match.end():].lstrip(" \u00a0")
            if not before.endswith("(") or not after.startswith(")"):
                continue
        if match.group()[0] in ".\u2026":
            # Preserve the abbreviation and its space in e.g. "prov. ........".
            if (
                match.group().startswith(".")
                and match.start() > 0
                and text[match.start() - 1].isalnum()
                and len(match.group()) > 1
                and match.group()[1] in " \u00a0"
            ):
                start = match.start() + 1
                while text[start] in " \u00a0":
                    start += 1
                match = INLINE_PLACEHOLDER.match(text, start)
            if match.group().count(".") + 3 * match.group().count("\u2026") < 4:
                continue
        matches.append(match)
    return matches


def _check_package(data: bytes) -> None:
    if len(data) > MAX_DOCX_BYTES:
        raise DocxTooLargeError("Il modello supera il limite di 20 MB")
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 2048 or sum(e.file_size for e in entries) > MAX_UNPACKED_BYTES:
                raise DocxTooLargeError("Il DOCX decompresso supera i limiti supportati")
            names = [entry.filename for entry in entries]
            if len(names) != len(set(names)):
                raise DocumentInputError("Il DOCX contiene parti duplicate")
            if "word/document.xml" not in names:
                raise DocumentInputError("Il file non contiene un documento Word DOCX")
            for entry in entries:
                path = PurePosixPath(entry.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in entry.filename:
                    raise DocumentInputError("Il DOCX contiene percorsi non validi")
                lower = entry.filename.lower()
                if entry.flag_bits & 1 or any(
                    part in lower
                    for part in ("vbaproject", "activex/", "embeddings/", "_xmlsignatures/")
                ):
                    raise DocumentInputError(
                        "Modelli cifrati, firmati, con macro o oggetti incorporati non supportati"
                    )
                content = archive.read(entry)
                if lower.endswith((".xml", ".rels")):
                    parser = etree.XMLParser(resolve_entities=False, no_network=True)
                    root = etree.fromstring(content, parser)
                    if root.getroottree().docinfo.doctype:
                        raise DocumentInputError("Dichiarazioni DTD non ammesse nel DOCX")
                    if lower.endswith(".rels"):
                        for relation in root:
                            if relation.get("TargetMode") == "External" and not relation.get(
                                "Type", ""
                            ).endswith("/hyperlink"):
                                raise DocumentInputError(
                                    "Il modello contiene risorse esterne non supportate"
                                )
    except (BadZipFile, etree.XMLSyntaxError, OSError, KeyError, RuntimeError) as exc:
        raise DocumentInputError("Il DOCX non e leggibile o risulta danneggiato") from exc


def _writable(cell) -> bool:
    # A visually empty cell may contain a form control, a drawing or a merge continuation.
    if not PLACEHOLDER.fullmatch(text_of(cell)):
        return False
    paragraphs = list(cell.iter(qn("w:p")))
    if not paragraphs or any(
        paragraph.getparent() is not cell
        or any(child.tag not in PARAGRAPH_CHILDREN for child in paragraph)
        for paragraph in paragraphs
    ):
        return False
    forbidden = (
        "tbl",
        "fldChar",
        "instrText",
        "fldSimple",
        "sdt",
        "drawing",
        "pict",
        "sym",
        "object",
        "footnoteReference",
        "endnoteReference",
    )
    if any(list(cell.iter(qn(f"w:{tag}"))) for tag in forbidden):
        return False
    merge = cell.find("./" + qn("w:tcPr") + "/" + qn("w:vMerge"))
    if merge is not None and merge.get(qn("w:val")) != "restart":
        return False
    return True


@dataclass
class ParagraphSlot:
    paragraph: object
    paragraph_index: int
    slot_index: int
    start: int
    end: int
    placeholder: str
    signature: bool


def _paragraph_text(paragraph) -> tuple[str, list[tuple[object, int, int]]]:
    parts, nodes = [], []
    offset = 0
    for run in paragraph.findall(qn("w:r")):
        for node in run:
            if node.tag == qn("w:t"):
                value = node.text or ""
                nodes.append((node, offset, offset + len(value)))
            elif node.tag in {qn("w:br"), qn("w:cr")}:
                value = "\n"
            elif node.tag == qn("w:tab"):
                value = "\t"
            elif node.tag == qn("w:rPr"):
                continue
            else:
                # Non-text objects must not join two otherwise separate placeholders.
                value = "\ufffc"
            parts.append(value)
            offset += len(value)
    return "".join(parts), nodes


def _unsafe_paragraphs(body) -> set:
    unsafe = set()
    field_depth = 0
    for node in body.iter():
        field_kind = node.get(qn("w:fldCharType")) if node.tag == qn("w:fldChar") else None
        if field_kind == "begin":
            field_depth += 1
        if field_depth or node.tag in COMPLEX_CONTENT:
            paragraph = node if node.tag == qn("w:p") else next(node.iterancestors(qn("w:p")), None)
            if paragraph is not None:
                unsafe.add(paragraph)
        if field_kind == "end":
            field_depth = max(0, field_depth - 1)
    return unsafe


def _adjacent_text(paragraph, *, following=False) -> str:
    sibling = paragraph.getnext() if following else paragraph.getprevious()
    while sibling is not None and sibling.tag == qn("w:p"):
        text = text_of(sibling).strip()
        if text:
            return text
        sibling = sibling.getnext() if following else sibling.getprevious()
    return ""


def _paragraph_slots(paragraphs, cells, unsafe) -> tuple[dict, list, list]:
    slots, catalog, unsupported = {}, [], []
    whole_cells = set(cells.values())
    for pi, paragraph in enumerate(paragraphs):
        parent = paragraph.getparent()
        if parent in whole_cells:
            continue
        text, _ = _paragraph_text(paragraph)
        matches = _placeholder_matches(text)
        ancestors = set(paragraph.iterancestors())
        complex_ancestor = any(node.tag in COMPLEX_CONTENT for node in ancestors)
        complex_children = any(child.tag not in PARAGRAPH_CHILDREN for child in paragraph)
        merge = parent.find("./" + qn("w:tcPr") + "/" + qn("w:vMerge"))
        continuation = merge is not None and merge.get(qn("w:val")) != "restart"
        if (
            paragraph in unsafe
            or complex_ancestor
            or complex_children
            or parent.tag not in {qn("w:body"), qn("w:tc")}
            or continuation
        ):
            if matches or paragraph in unsafe or complex_ancestor or complex_children:
                unsupported.append(
                    {
                        "paragraph": pi + 1,
                        "reason": "Contenuto complesso o controllo Word non modificato",
                    }
                )
            continue
        if not matches:
            continue
        before, after = _adjacent_text(paragraph), _adjacent_text(paragraph, following=True)
        fields, annotated = [], []
        previous_end = 0
        for si, match in enumerate(matches):
            target_id = f"p{pi}.s{si}"
            prefix = text[previous_end : match.start()]
            suffix = text[
                match.end() : matches[si + 1].start() if si + 1 < len(matches) else len(text)
            ]
            signature = bool(
                SIGNATURE_LABEL.search(prefix + " " + match.group().replace("_", " "))
                or _signature_cell(parent)
                or (not prefix.strip() and si == 0 and SIGNATURE_LABEL.search(before))
                or (re.match(r"\s*\(", suffix) and SIGNATURE_LABEL.search(suffix))
                or (
                    len(matches) == 1
                    and not (text[:match.start()] + text[match.end():]).strip()
                    and SIGNATURE_LABEL.search(after)
                )
            )
            slots[target_id] = ParagraphSlot(
                paragraph, pi, si, match.start(), match.end(), match.group(), signature
            )
            fields.append(
                {
                    "id": target_id,
                    "placeholder": match.group(),
                    "writable": True,
                    "signature": signature,
                    "value_type": (
                        "email" if is_email_label(
                            before if si == 0 and not prefix.strip() else prefix
                        )
                        or is_email_label(match.group().strip("{}[]")) else None
                    ),
                }
            )
            annotated.extend([prefix, f"[[{target_id}]]"])
            previous_end = match.end()
        annotated.append(text[previous_end:])
        # Explicitly partitioned addresses (___@___.___) need a different writer.
        # Block the entire connected group rather than writing complete addresses into parts.
        group = []
        for si in range(len(matches)):
            prefix = text[:matches[si].start()]
            suffix = text[matches[si].end():]
            if re.search(r"[^\s]*@[^\s]*$", prefix) or re.match(r"[^\s]*@[^\s]*", suffix):
                fields[si]["value_type"] = "email_parts"
            if group and not re.fullmatch(
                r"[ \u00a0]*[@.][ \u00a0]*", text[matches[si - 1].end():matches[si].start()]
            ):
                group = []
            group.append(si)
            if len(group) > 1 and (
                any(fields[index]["value_type"] in {"email", "email_parts"} for index in group)
                or "@" in text[matches[group[0]].end():matches[si].start()]
            ):
                for index in group:
                    fields[index]["value_type"] = "email_parts"
        catalog.append(
            {
                "paragraph": pi,
                "text": text,
                "text_with_fields": "".join(annotated),
                "preceding_context": before,
                "following_context": after,
                "fields": fields,
            }
        )
    return slots, catalog, unsupported


@dataclass
class DocxLayout:
    original: bytes
    sha256: str
    document: object
    cells: dict
    catalog: list[dict]
    slots: dict[str, ParagraphSlot]
    paragraph_catalog: list[dict]
    unsupported_locations: list[dict]
    field_types: dict[str, str]

    @property
    def candidate_ids(self) -> set[str]:
        return set(self.cells) | set(self.slots)

    def location(self, target_id: str) -> dict:
        if target_id in self.slots:
            slot = self.slots[target_id]
            return {
                "kind": "paragraph",
                "paragraph": slot.paragraph_index + 1,
                "slot": slot.slot_index + 1,
                "placeholder": slot.placeholder,
            }
        return {"kind": "table_cell"}


def inspect_docx(data: bytes) -> DocxLayout:
    _check_package(data)
    try:
        document = Document(BytesIO(data))
    except (ValueError, KeyError, TypeError, etree.LxmlError) as exc:
        raise DocumentInputError("Il modello DOCX non e supportato") from exc
    if DRAFT_NOTICE in text_of(document.element):
        raise DocumentInputError("Carica il modello vuoto, non una bozza gia generata")
    if len(text_of(document.element.body)) > 60_000:
        raise DocumentInputError("Il testo del modello supera il limite di 60.000 caratteri")
    if document.settings.element.find(qn("w:documentProtection")) is not None:
        raise DocumentInputError("Rimuovi la protezione del modello prima di compilarlo")
    if any(list(document.element.iter(qn(f"w:{tag}"))) for tag in ("ins", "del", "altChunk")):
        raise DocumentInputError(
            "Modelli con revisioni pendenti o contenuti importati non supportati"
        )

    paragraphs = list(document.element.body.iter(qn("w:p")))
    unsafe = _unsafe_paragraphs(document.element.body)
    tables = list(document.element.body.iter(qn("w:tbl")))
    cells = {}
    catalog = []
    for ti, table in enumerate(tables):
        context = []
        sibling = table.getprevious()
        while sibling is not None and len(context) < 3:
            text = text_of(sibling).strip()
            if text:
                context.insert(0, text)
            sibling = sibling.getprevious()
        rows = []
        for ri, row in enumerate(table.findall(qn("w:tr"))):
            row_cells = []
            # Physical XML cells, not python-docx's expanded grid of merged cells.
            for ci, cell in enumerate(row.findall(qn("w:tc"))):
                cell_id = f"t{ti}.r{ri}.c{ci}"
                writable = _writable(cell) and not any(p in unsafe for p in cell.iter(qn("w:p")))
                if any(node.tag in COMPLEX_CONTENT for node in cell.iterancestors()):
                    writable = False
                if writable:
                    cells[cell_id] = cell
                row_cells.append(
                    {
                        "id": cell_id,
                        "text": text_of(cell),
                        "writable": writable,
                        "signature": _signature_cell(cell),
                    }
                )
            rows.append(row_cells)
        catalog.append({"table": ti, "preceding_context": context, "rows": rows})
    slots, paragraph_catalog, unsupported = _paragraph_slots(paragraphs, cells, unsafe)
    if not cells and not slots:
        raise DocumentInputError(
            "Nessun campo supportato: servono celle vuote o segnaposti nei paragrafi "
            "(___, ...., {{campo}}). Controlli Word e spazi senza segnaposto non sono supportati"
        )
    if len(cells) + len(slots) > MAX_CANDIDATES:
        raise DocumentInputError("Il modello contiene troppi campi: limite 400 elementi candidati")
    # Reject oversized context instead of silently hiding part of a form from the model.
    if len(json.dumps([catalog, paragraph_catalog], ensure_ascii=False)) > MAX_CATALOG_CHARACTERS:
        raise DocumentInputError("Il contenuto del modello supera il limite supportato")
    field_types = {
        field["id"]: field["value_type"]
        for paragraph in paragraph_catalog for field in paragraph["fields"]
        if field["value_type"] is not None
    }
    for table in catalog:
        header = table["rows"][0] if table["rows"] else []
        has_header = header and all(not cell["writable"] for cell in header)
        for ri, row in enumerate(table["rows"]):
            for ci, cell in enumerate(row):
                if not cell["writable"]:
                    continue
                label = next((c["text"] for c in reversed(row[:ci]) if c["text"].strip()), "")
                if is_email_label(label) or (
                    has_header and ri > 0 and len(row) == len(header)
                    and is_email_label(header[ci]["text"])
                ):
                    cell["value_type"] = field_types[cell["id"]] = "email"
    return DocxLayout(
        data,
        hashlib.sha256(data).hexdigest(),
        document,
        cells,
        catalog,
        slots,
        paragraph_catalog,
        unsupported,
        field_types,
    )


def field_value_error(
    layout: DocxLayout, target_id: str, value: str, *, label: str = ""
) -> tuple[str, str] | None:
    value_type = layout.field_types.get(target_id)
    if value_type == "email_parts":
        return (
            "unsupported_email_layout",
            "Recapito diviso in parti con separatori prestampati: compilazione manuale richiesta",
        )
    if value_type != "email" and not is_email_label(label):
        return None
    try:
        # Do not normalize/repair the source value, contact DNS or assert PEC ownership.
        validate_email(value, check_deliverability=False, allow_display_name=False)
    except EmailNotValidError:
        return "invalid_email", "Email/PEC non completa o con sintassi non valida"
    return None


def _signature_cell(cell) -> bool:
    if cell.tag != qn("w:tc"):
        return False
    row = cell.getparent()
    row_cells = row.findall(qn("w:tc"))
    column = row_cells.index(cell)
    labels = [text_of(part) for part in row_cells[:column]]
    first_row = row.getparent().find(qn("w:tr"))
    if first_row is not None and first_row is not row:
        header_cells = first_row.findall(qn("w:tc"))
        if column < len(header_cells):
            labels.append(text_of(header_cells[column]))
    return any(SIGNATURE_LABEL.search(label) for label in labels)


def is_signature_target(layout: DocxLayout, cell_id: str) -> bool:
    if cell_id in layout.slots:
        slot = layout.slots[cell_id]
        return slot.signature or _signature_cell(slot.paragraph.getparent())
    return _signature_cell(layout.cells[cell_id]) if cell_id in layout.cells else False


def _expand_row(element) -> None:
    row = next(element.iterancestors(qn("w:tr")), None)
    properties = row.find(qn("w:trPr")) if row is not None else None
    if properties is not None:
        for height in properties.findall(qn("w:trHeight")):
            if height.get(qn("w:hRule")) == "exact":
                height.set(qn("w:hRule"), "atLeast")


def _replace_slot(slot: ParagraphSlot, value: str) -> None:
    text, nodes = _paragraph_text(slot.paragraph)
    if text[slot.start : slot.end] != slot.placeholder:
        raise DocumentInputError("Il segnaposto del paragrafo non coincide con il modello")
    affected = [
        (node, start, end) for node, start, end in nodes if start < slot.end and end > slot.start
    ]
    if not affected:
        raise DocumentInputError("Segnaposto privo di testo scrivibile")
    first = affected[0][0]
    for node, start, end in affected:
        original = node.text or ""
        prefix = original[: max(0, slot.start - start)]
        suffix = original[max(0, slot.end - start) :]
        node.text = prefix + (value if node is first else "") + suffix
        node.set(qn("xml:space"), "preserve")
    # Insert proper Word line breaks/tabs, keeping the placeholder run's formatting.
    if "\n" in first.text or "\t" in first.text:
        pieces = re.split(r"([\n\t])", first.text)
        first.text = pieces[0]
        previous = first
        for piece in pieces[1:]:
            node = OxmlElement("w:br" if piece == "\n" else "w:tab" if piece == "\t" else "w:t")
            if piece not in {"\n", "\t"}:
                node.text = piece
                node.set(qn("xml:space"), "preserve")
            previous.addnext(node)
            previous = node
    _expand_row(slot.paragraph)


def fill_docx(layout: DocxLayout, values: dict[str, str]) -> bytes:
    if hashlib.sha256(layout.original).hexdigest() != layout.sha256:
        raise DocumentInputError("Il modello e cambiato durante la compilazione")
    # Reopen the original so repeated exports cannot accumulate edits or draft notices.
    fresh = inspect_docx(layout.original)
    for cell_id, value in values.items():
        if cell_id not in fresh.candidate_ids or not isinstance(value, str) or not value.strip():
            raise DocumentInputError("Tentativo di scrittura su un campo non autorizzato")
        if is_signature_target(fresh, cell_id):
            raise DocumentInputError("Le firme non vengono compilate automaticamente")
        if len(value) > 1500 or any(ord(c) < 32 and c not in "\n\t\r" for c in value):
            raise DocumentInputError("Il valore contiene caratteri o dimensioni non supportati")
        if error := field_value_error(fresh, cell_id, value):
            raise DocumentInputError(error[1])
    # Work from right to left so replacements never invalidate earlier slot offsets.
    for cell_id in sorted(fresh.slots, key=lambda key: fresh.slots[key].start, reverse=True):
        if cell_id in values:
            _replace_slot(
                fresh.slots[cell_id], values[cell_id].replace("\r\n", "\n").replace("\r", "\n")
            )
    for cell_id, value in values.items():
        if cell_id not in fresh.cells:
            continue
        cell = fresh.cells[cell_id]
        paragraphs = cell.findall(qn("w:p"))
        if not paragraphs:
            raise DocumentInputError("Struttura della cella non supportata")
        first_run = cell.find(".//" + qn("w:rPr"))
        style = deepcopy(first_run) if first_run is not None else None
        for node in cell.iter(qn("w:t")):
            node.text = ""
        run = OxmlElement("w:r")
        if style is not None:
            run.append(style)
        for index, line in enumerate(value.replace("\r\n", "\n").replace("\r", "\n").split("\n")):
            if index:
                run.append(OxmlElement("w:br"))
            text = OxmlElement("w:t")
            text.set(qn("xml:space"), "preserve")
            text.text = line
            run.append(text)
        paragraphs[0].append(run)
        # Fixed row heights otherwise clip longer values without warning in Word.
        _expand_row(cell)

    notice = OxmlElement("w:p")
    run = OxmlElement("w:r")
    properties = OxmlElement("w:rPr")
    properties.append(OxmlElement("w:b"))
    run.append(properties)
    text = OxmlElement("w:t")
    text.text = DRAFT_NOTICE
    run.append(text)
    notice.append(run)
    fresh.document.element.body.insert(0, notice)

    # Only the body part changes; preserve images, footnotes, headers and relationships verbatim.
    output = BytesIO()
    with (
        ZipFile(BytesIO(layout.original)) as original,
        ZipFile(output, "w", ZIP_DEFLATED) as result,
    ):
        for entry in original.infolist():
            content = original.read(entry)
            if entry.filename == "word/document.xml":
                content = etree.tostring(
                    fresh.document.element, xml_declaration=True, encoding="UTF-8", standalone=True
                )
            result.writestr(entry, content)
    return output.getvalue()
