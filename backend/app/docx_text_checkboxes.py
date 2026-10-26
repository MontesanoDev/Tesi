"""Opt-in structural adapter for a single leading ASCII checkbox in plain text.

This locates a writable marker, never an applicable clause or a USER decision.
Native Word controls and symbol elements are deliberately outside this adapter.
"""
import re

from docx.oxml.ns import qn

from app.docx_templates import PARAGRAPH_CHILDREN, ParagraphSlot, _paragraph_text, _replace_slot

PREFIX = re.compile(r'^[ \t\u00a0]*(\[(?: |[xX])?\])(?=\s+\S)')


def controls(layout):
    if layout.text_checkbox_revision != 1:
        return {}
    result = {}
    for index, paragraph in enumerate(layout.document.element.body.iter(qn('w:p'))):
        if (next(paragraph.iterancestors(qn('w:sdt')), None) is not None
                or any(c.tag not in PARAGRAPH_CHILDREN for c in paragraph)
                or any(c.tag not in {qn('w:rPr'), qn('w:t')}
                       for r in paragraph.findall(qn('w:r')) for c in r)):
            continue
        fonts = paragraph.findall('.//' + qn('w:rFonts'))
        if any('wingdings' in v.casefold() or v.casefold() in {'symbol', 'webdings'}
               for font in fonts for v in font.attrib.values()):
            continue
        text, _ = _paragraph_text(paragraph)
        match = PREFIX.match(text)
        if not match or any(c in text[match.end():] for c in '[]☐☑☒□'):
            continue
        slot = ParagraphSlot(paragraph, index, 0, match.start(1), match.end(1),
                             match[1], False)
        result[f'p{index}.txcb0'] = slot
    return result


def paragraph_records(layout):
    result = {}
    for cid, slot in controls(layout).items():
        result[slot.paragraph] = [{
            'id': cid, 'offset': slot.start, 'control_type': 'text_ascii',
            'initial_checked': slot.placeholder.casefold() == '[x]',
        }]
    return result


def write(slot, checked):
    # A false value leaves an already empty marker byte-for-byte unchanged.
    if checked == (slot.placeholder.casefold() == '[x]'):
        return
    _replace_slot(slot, '[X]' if checked else '[ ]')
