''' Parse CSS-like style configuration '''
from __future__ import annotations
from typing import Any, Sequence
import re
from dataclasses import dataclass, field, replace

from .style import Style


def merge(style: Style, style2: Style) -> Style:
    ''' Merge style2 on top of style1, replacing any non-none items '''
    return replace(style, **style2.values())


def merge_css(style: Style, css: str) -> Style:
    ''' Merge the css items (no selectors) with the style '''
    values = parse_style(css)
    return replace(style, **values)


@dataclass
class CssStyle:
    ''' Style objects loaded from a CSS

        Args:
            cssids: Styles from CSS selectors starting with #
            cssclasses: Styles from CSS selectors starting with .
            drawables: Styles from Ziaplot class names
    '''
    cssids: dict[str, Style] = field(default_factory=dict)
    cssclasses: dict[str, Style] = field(default_factory=dict)
    drawables: dict[str, Style] = field(default_factory=dict)

    def extract(self, classnames: Sequence[str],
                cssclass: str|None = '', cssid: str|None = '') -> Style:
        ''' Get styles that match - from most general (classname) to most specific (id) '''
        style = Style()
        for cls in classnames:
            style = merge(style, self.drawables.get(cls, Style()))

        if cssclass:
            style = merge(style, self.cssclasses.get(cssclass, Style()))
        
        if cssid:
            style = merge(style, self.cssids.get(cssid, Style()))
        return style


def splitcolors(cssvalue: str) -> Any:
    ''' Split the comma-separated color values '''
    # Split on comma but not if comma is within ()
    # eg. red, blue is split at comma
    # rgb(1,2,3) is not
    return re.split(r',\s*(?![^()]*\))', cssvalue)


def caster(cssvalue: str) -> int | float | str:
    ''' Attempt to cast the value to int or float '''
    try:
        val = float(cssvalue)
    except ValueError:
        return cssvalue
    if val.is_integer():
        return int(val)
    return val


def parse_style(style: str | None) -> dict[str, Any]:
    ''' Parse items in one style group {...} '''
    if style is None:
        return {}

    # Remove CSS comments inside /* ... */
    style = re.sub(r'(\/\*[^*]*\*+([^/*][^*]*\*+)*\/)', '', style)

    items = {}
    for item in style.split(';'):
        item = item.strip()
        if item:
            key,val = item.split(':', maxsplit=1)
            if key.strip() == 'colorcycle':
                items[key.strip()] = splitcolors(val.strip())
            else:
                items[key.strip()] = caster(val.strip())
    return items


def parse_css(css: str) -> CssStyle:
    ''' Parse full CSS '''
    # Split groups of 'XXX { YYY }'
    matches = re.findall(r'(.*?)\{(.+?)\}', css, flags=re.MULTILINE|re.DOTALL)
    cssitems = [(idn.strip(), val.strip()) for idn, val in matches]

    def update(dict, selector, style):
        if selector not in dict:
            dict[selector] = style
        else:
            dict[selector] = merge(dict[selector], style)

    cssstyle = CssStyle()
    for selector, value in cssitems:
        style = Style(**parse_style(value))
        if selector.startswith('#'):
            update(cssstyle.cssids, selector[1:], style)
        elif selector.startswith('.'):
            update(cssstyle.cssclasses, selector[1:], style)
        else:
            update(cssstyle.drawables, selector, style)
    return cssstyle
