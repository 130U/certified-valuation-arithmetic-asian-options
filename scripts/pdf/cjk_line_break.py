"""CJK paragraph wrapping with indivisible native numeric text.

Adapted from ReportLab 4.4.9's ``cjkFragSplit`` and ``breakLinesCJK``.
Copyright ReportLab Europe Ltd. 2000-2017.
Copyright (c) 2000-2024, ReportLab Inc. All rights reserved.
Redistribution is under the BSD terms retained in LICENSE-ReportLab.txt.

Local changes: group decimal/integer/scientific numeric tokens before width
measurement, use the first character safely in the Latin backtracking test,
and use the fragment splitter even for a paragraph containing one fragment.
Numbers remain ordinary PDF text; no formula/image callback is introduced.
"""
import re
from unicodedata import category
from reportlab.platypus import paragraph as _p


NUMERIC_TOKEN = re.compile(
    r'[+\-\u2212]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)'
    r'(?:[eE][+\-\u2212]?\d+)?'
)


def _text_units(text):
    """Keep every numeric token whole, splitting the surrounding text normally."""
    position = 0
    for match in NUMERIC_TOKEN.finditer(text):
        yield from text[position:match.start()]
        yield match.group()
        position = match.end()
    yield from text[position:]


def cjk_frag_split(frags, max_widths, calc_bounds, encoding='utf8'):
    units = []
    for frag in frags:
        text = frag.text
        if _p.isBytes(text):
            text = text.decode(encoding)
        if hasattr(frag, 'cbDefn'):
            # Existing callback width/drawing is authoritative. An empty
            # anchor/image gets a marker, never an extra numeric callback.
            units.append(_p.cjkU(text or '\ufffc', frag, encoding))
        elif text:
            units.extend(_p.cjkU(token, frag, encoding) for token in _text_units(text))
        else:
            units.append(_p.cjkU(text, frag, encoding))
    lines = []
    index = width_used = line_start = 0
    max_width = max_widths[0]
    while index < len(units):
        unit = units[index]
        index += 1
        width = unit.width
        if hasattr(width, 'normalizedValue'):
            width._normalizer = max_width
            width = width.normalizedValue(max_width)
        width_used += width
        line_break = hasattr(unit.frag, 'lineBreak')
        end_line = (width_used > max_width + _p._FUZZ and width_used > 0) or line_break
        if end_line:
            extra_space = max_width - width_used
            if not line_break:
                if unit and ord(unit[0]) < 0x3000:
                    limit = (line_start + index) >> 1
                    for j in range(index - 1, limit, -1):
                        previous = units[j]
                        if previous and (category(previous[0]) == 'Zs' or ord(previous[0]) >= 0x3000):
                            following = j + 1
                            if following < index:
                                after_following = following + 1
                                extra_space += sum(units[k].width for k in range(after_following, index))
                                width = units[following].width
                                unit = units[following]
                                index = after_following
                                break
                if unit not in _p.ALL_CANNOT_START and index > line_start + 1:
                    index -= 1
                    extra_space += width
            lines.append(_p.makeCJKParaLine(units[line_start:index], max_width, width_used,
                                          extra_space, line_break, calc_bounds))
            max_width = max_widths[min(len(lines), len(max_widths) - 1)]
            line_start = index
            width_used = 0
    if width_used > 0:
        lines.append(_p.makeCJKParaLine(units[line_start:], max_width, width_used,
                                      max_width - width_used, False, calc_bounds))
    return _p.ParaLines(kind=1, lines=lines)


def break_lines_cjk(paragraph, max_widths):
    """ReportLab CJK entry point with the safe splitter for every fragment count."""
    if not isinstance(max_widths, (list, tuple)):
        max_widths = [max_widths]
    paragraph.height = 0
    style = paragraph.style
    _p._handleBulletWidth(paragraph.bulletText, style, max_widths)
    if not paragraph.frags:
        return _p.ParaLines(kind=0, fontSize=style.fontSize, fontName=style.fontName,
                            textColor=style.textColor, lines=[], ascent=style.fontSize,
                            descent=-0.2 * style.fontSize)
    if hasattr(paragraph, 'blPara') and getattr(paragraph, '_splitpara', 0):
        return paragraph.blPara
    auto_leading = getattr(paragraph, 'autoLeading', getattr(style, 'autoLeading', ''))
    return cjk_frag_split(paragraph.frags, max_widths, auto_leading not in ('', 'off'))
