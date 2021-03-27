''' Methods for drawing text, either as <text> elements or as
    paths via ziamath library
'''

from typing import Literal, Optional

import os
import string
from collections import namedtuple
from xml.etree import ElementTree as ET

try:
    import ziamath
    import ziafont
except ImportError:
    ziamath = None  # type: ignore

DEBUG = False

TextModeType = Literal['text', 'path']
Halign = Literal['left', 'center', 'right']
Valign = Literal['top', 'center', 'baseline', 'bottom']
Size = namedtuple('Size', ['width', 'height'])

textmode: TextModeType = 'path' if ziamath is not None else 'text'


def settextmode(mode: TextModeType) -> None:
    ''' Set the mode for rendering text.

        In 'text' mode, text is drawn as SVG <text> elements
        and will be searchable in the SVG, however it may
        render differently on systems without the same fonts
        installed. In 'path' mode, text converted to SVG
        <path> elements and will render independently of
        any fonts on the system. Path mode enables rendering
        of math expressions, but also requires the
        ziafont/ziamath packages.

        Args:
            mode: Text Mode.
    '''
    if mode == 'path' and ziamath is None:
        raise ValueError('Path mode requires ziamath package')
    global textmode
    textmode = mode


def draw_text(x: float, y: float, s: str, svgelm: ET.Element,
              color: str='black',
              font: str='sans-serif',
              size: float=12,
              halign: Halign='left',
              valign: Valign='bottom',
              rotate: float=None):

    if textmode == 'path':
        draw_text_zia(x, y, s, svgelm=svgelm,
                      color=color, font=font, size=size,
                      halign=halign, valign=valign, rotate=rotate)
    else:
        draw_text_text(x, y, s, svgelm=svgelm,
                       color=color, font=font, size=size,
                       halign=halign, valign=valign, rotate=rotate)


def draw_text_zia(x: float, y: float, s: str, svgelm: ET.Element,
                  color: str='black',
                  font: str='sans',
                  size: float=12,
                  halign: Halign='left',
                  valign: Valign='bottom',
                  rotate: float=None):
    style: Optional[str]
    fontfile: Optional[str]
    if (font.endswith('ttf') or font.endswith('otf')) and os.path.exists(font):
        # font is a font file
        style = None
        ftonfile = font
    else:
        # font is describing the style
        style = font
        fontfile = None
        if style == 'sans-serif':
            style = 'sans'  # Convert to MathML's name

    math = ziamath.Math.fromlatextext(s, size=size, font=fontfile, textstyle=style, mathstyle=style)
    textelm = math.drawon(x, y, svgelm, color=color, halign=halign, valign=valign)
    if rotate:
        textelm.attrib['transform'] = f' rotate({-rotate} {x} {y})'


def draw_text_text(x: float, y: float, s: str, svgelm: ET.Element,
                   color: str='black',
                   font: str='sans-serif',
                   size: float=12,
                   halign: Halign='left',
                   valign: Valign='bottom',
                   rotate: float=None):
        anchor = {'center': 'middle',
                  'left': 'start',
                  'right': 'end'}.get(halign, 'left')
        baseline = {'center': 'middle',
                    'bottom': 'auto',
                    'top': 'hanging'}.get(valign, 'bottom')

        attrib = {'x': str(x),
                  'y': str(y),
                  'fill': color,
                  'font-size': str(size),
                  'font-family': font,
                  'text-anchor': anchor,
                  'dominant-baseline': baseline}

        if rotate:
            attrib['transform'] = f' rotate({-rotate} {x} {y})'

        txt = ET.SubElement(svgelm, 'text', attrib=attrib)
        txt.text = s


def text_size(st: str, fontsize: float=12, font: str='Arial') -> Size:
    ''' Estimate string width based on individual characters

        Args:
            st: string to estimate
            fontsize: font size
            font: font family

        Returns:
            Estimated width of string
    '''
    if textmode == 'path':
        return text_size_zia(st, fontsize, font)
    else:
        return text_size_text(st, fontsize, font)

    
def text_size_zia(st: str, fontsize: float=12, font: str='sans') -> Size:
    text = ziamath.Math.fromlatextext(st, size=fontsize)
    try:
        return Size(*text.getsize())
    except AttributeError:
        return Size(*text.strsize())


def text_size_text(st: str, fontsize: float=12, font: str='Arial') -> Size:
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