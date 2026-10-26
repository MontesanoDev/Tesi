"""Write only native body controls already located by the structural catalog."""

from docx.oxml.ns import qn
from lxml import etree

from app.docx_templates import DocumentInputError

W14 = "http://schemas.microsoft.com/office/word/2010/wordml"


def native_controls(layout):
    # Reuse exactly the reader/IDs that the global catalog exposes.
    from app.compilation_catalog import _checkboxes

    body = layout.document.element.body
    positions = {p: i for i, p in enumerate(body.iter(qn("w:p")))}
    return {record["id"]: node for controls in _checkboxes(body, positions).values()
            for node, record in controls}


def _content_control(node, checked):
    wrapper = next(node.iterancestors(qn("w:sdt")), None)
    properties = wrapper.find(qn("w:sdtPr")) if wrapper is not None else None
    lock = properties.find(qn("w:lock")) if properties is not None else None
    if lock is not None and lock.get(qn("w:val")) in {"contentLocked", "sdtContentLocked"}:
        raise DocumentInputError("Checkbox con contenuto protetto")
    content = wrapper.find(qn("w:sdtContent")) if wrapper is not None else None
    texts = list(content.iter(qn("w:t"))) if content is not None else []
    # A native checkbox's cache is one glyph, never its label or arbitrary text.
    if len(texts) != 1 or len((texts[0].text or "").strip()) != 1:
        raise DocumentInputError("Rappresentazione visiva checkbox non supportata")
    states = [node.find(f"{{{W14}}}{name}State") for name in ("checked", "unchecked")]
    glyphs = {"☐", "☑", "☒"}
    for state in states:
        if state is not None:
            try:
                glyphs.add(chr(int(state.get(f"{{{W14}}}val"), 16)))
            except (TypeError, ValueError, OverflowError) as exc:
                raise DocumentInputError("Simbolo checkbox Word non valido") from exc
    if texts[0].text.strip() not in glyphs:
        raise DocumentInputError("Simbolo checkbox Word non riconosciuto")
    state = states[0 if checked else 1]
    glyph = chr(int(state.get(f"{{{W14}}}val"), 16)) if state is not None else (
        "☒" if checked else "☐")
    texts[0].text = glyph
    font = state.get(f"{{{W14}}}font") if state is not None else None
    if font:
        run = texts[0].getparent()
        props = run.find(qn("w:rPr"))
        if props is None:
            props = etree.Element(qn("w:rPr"))
            run.insert(0, props)
        fonts = props.find(qn("w:rFonts"))
        if fonts is None:
            fonts = etree.SubElement(props, qn("w:rFonts"))
        for key in ("ascii", "hAnsi"):
            fonts.set(qn("w:" + key), font)
    return f"{{{W14}}}checked", f"{{{W14}}}val"


def write_checkboxes(layout, values, *, text_positions=None):
    from app.docx_text_checkboxes import controls as text_controls
    from app.docx_text_checkboxes import write as write_text

    controls = native_controls(layout)
    text = text_controls(layout) if text_positions is None else text_positions
    if any(key not in controls.keys() | text.keys() or type(value) is not bool
           for key, value in values.items()):
        raise DocumentInputError("Checkbox o valore non autorizzato")
    for key, checked in values.items():
        if key in text:
            write_text(text[key], checked)
            continue
        node = controls[key]
        if node.tag == qn("w:checkBox"):
            begin = next(node.iterancestors(qn("w:fldChar")), None)
            if begin is None or begin.get(qn("w:fldCharType")) != "begin":
                raise DocumentInputError("Struttura checkbox legacy non supportata")
            begin.set(qn("w:dirty"), "true")
            tag, attribute = qn("w:checked"), qn("w:val")
        else:
            tag, attribute = _content_control(node, checked)
        state = node.find(tag)
        if state is None:
            state = etree.SubElement(node, tag)
        state.set(attribute, str(int(checked)))
