''' Methods for drawing text, either as <text> elements or as
    paths via ziamath library
'''
from __future__ import annotations
from typing import Optional, Literal, cast
import math

import string
from collections import namedtuple
from xml.etree import ElementTree as ET
import warnings

try:
    import ziamath
    import ziafont
except ImportError:
    ziamath = None  # type: ignore
else:
    ziamath.config.math.variant = 'sans'


from .config import config

TextPosition = Literal['N', 'E', 'S', 'W',
                       'NE', 'NW', 'SE', 'SW']
Halign = Literal['left', 'center', 'right']
Valign = Literal['top', 'center', 'baseline', 'base', 'bottom']
Size = namedtuple('Size', ['width', 'height'])


def fmt(f: float) -> str:
    ''' String format, stripping trailing zeros '''
    p = f'.{config.precision}f'
    s = format(float(f), p)
    return s.rstrip('0').rstrip('.')  # Strip trailing zeros


def text_align_ofst(pos: Optional[TextPosition], ofst: float) -> tuple[float, float, Halign, Valign]:
    ''' Get text pixel offset and alignment
    
        Args:
            pos: Text Position relative to anchor
            ofst: Pixel offset, directionless
        
        Returns:
            dx: x-offset
            dy: y-offset
            halign: Horizontal alignment
            valign: Vertical alignment
    '''
    dx = dy = 0.
    halign, valign = 'center', 'center'
    if pos is None or 'N' in pos:
        valign = 'bottom'
        dy = ofst
    elif 'S' in pos:
        valign = 'top'
        dy = -ofst
    if pos is None or 'E' in pos:
        halign = 'left'
        dx = ofst
    elif 'W' in pos:
        halign = 'right'
        dx = -ofst

    if dx and dy:
        dx /= math.sqrt(2)
        dy /= math.sqrt(2)

    return dx, dy, cast(Halign, halign), cast(Valign, valign)


def draw_text(x: float, y: float, s: str, svgelm: ET.Element,
              color: str = 'black',
              font: str = 'sans-serif',
              size: float = 14,
              halign: Halign = 'left',
              valign: Valign = 'bottom',
              rotate: Optional[float] = None):

    if config.text == 'path':
        draw_text_zia(x, y, s, svgelm=svgelm,
                      color=color, font=font, size=size,
                      halign=halign, valign=valign, rotate=rotate)
    else:
        draw_text_text(x, y, s, svgelm=svgelm,
                       color=color, font=font, size=size,
                       halign=halign, valign=valign, rotate=rotate)


def draw_text_zia(x: float, y: float, s: str, svgelm: ET.Element,
                  color: str = 'black',
                  font: str = 'sans',
                  size: float = 14,
                  halign: Halign = 'left',
                  valign: Valign = 'base',
                  rotate: Optional[float] = None):
    math = ziamath.Text(s, size=size, textfont=font, color=color,
                        halign=halign, valign=valign)
    textelm = math.drawon(svgelm, x, y)

    if rotate:
        textelm.attrib['transform'] = f' rotate({-rotate} {fmt(x)} {fmt(y)})'


def draw_text_text(x: float, y: float, s: str, svgelm: ET.Element,
                   color: str = 'black',
                   font: str = 'sans-serif',
                   size: float = 14,
                   halign: Halign = 'left',
                   valign: Valign = 'bottom',
                   rotate: Optional[float] = None):
    anchor = {'center': 'middle',
              'left': 'start',
              'right': 'end'}.get(halign, 'left')
    baseline = {'center': 'middle',
                'bottom': 'auto',
                'top': 'hanging'}.get(valign, 'bottom')

    attrib = {'x': fmt(x),
              'y': fmt(y),
              'fill': color,
              'font-size': str(size),
              'font-family': font,
              'text-anchor': anchor,
              'dominant-baseline': baseline}

    if rotate:
        attrib['transform'] = f' rotate({-rotate} {fmt(x)} {fmt(y)})'

    txt = ET.SubElement(svgelm, 'text', attrib=attrib)
    txt.text = s


def text_size(st: str, fontsize: float = 14, font: str = 'Arial') -> Size:
    ''' Estimate string width based on individual characters

        Args:
            st: string to estimate
            fontsize: font size
            font: font family

        Returns:
            Estimated width of string
    '''
    if config.text == 'path':
        return text_size_zia(st, fontsize, font)
    else:
        return text_size_text(st, fontsize, font)

    
def text_size_zia(st: str, fontsize: float = 14, font: str = 'sans') -> Size:
    text = ziamath.Text(st, size=fontsize)
    return Size(*text.getsize())


def text_size_text(st: str, fontsize: float = 14, font: str = 'Arial') -> Size:
    ''' Estimate string width based on individual characters

        Args:
            st: string to estimate
            fontsize: font size
            font: font family

        Returns:
            Estimated width of string
    '''
    # adapted from https://stackoverflow.com/a/16008023/13826284
    # The only alternative is to draw the string to an actual canvas

    size = 0  # in milinches
    if 'times' in font.lower() or ('serif' in font.lower() and 'sans' not in font.lower()):
        # Estimates based on Times Roman
        for s in st:
            if s in 'lij:.,;t': size += 47
            elif s in '|': size += 37
            elif s in '![]fI/\\': size += 55
            elif s in '`-(){}r': size += 60
            elif s in 'sJ°': size += 68
            elif s in '"zcae?1': size += 74
            elif s in '*^kvxyμbdhnopqug#$_α' + string.digits: size += 85
            elif s in '#$+<>=~FSP': size += 95
            elif s in 'ELZT': size += 105
            elif s in 'BRC': size += 112
            elif s in 'DAwHUKVXYNQGO': size += 122
            elif s in '&mΩ': size += 130
            elif s in '%': size += 140
            elif s in 'MW@∠': size += 155
            else: size += 60

    else:  # Arial, or other sans fonts
        for s in st:
            if s in 'lij|\' ': size += 37
            elif s in '![]fI.,:;/\\t': size += 50
            elif s in '`-(){}r"': size += 60
            elif s in '*^zcsJkvxyμ°': size += 85
            elif s in 'aebdhnopqug#$L+<>=?_~FZTα' + string.digits: size += 95
            elif s in 'BSPEAKVXY&UwNRCHD': size += 112
            elif s in 'QGOMm%@Ω': size += 140
            elif s in 'W∠': size += 155
            else: size += 75
    return Size(size * 72 / 1000.0 * (fontsize/12), fontsize)  # to points