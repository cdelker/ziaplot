''' SVG Drawable base class '''

from typing import Optional, Literal, Tuple
import os
import xml.etree.ElementTree as ET

from .canvas import Canvas, Borders, ViewBox


SpanType = Tuple[int, int]



class Drawable:
    ''' Drawable SVG/XML object. Implements common XML and SVG functions,
        plus _repr_ for Jupyter
    '''
    def __init__(self) -> None:
        self._cssid: str | None = None
        self._csscls: str | None = None
        self._span: SpanType = 1, 1
        self._zorder: int = 1

    def __contains__(self, other: 'Drawable'):
        return None

    def cssid(self, idn: str) -> 'Drawable':
        ''' Set the CSS id for the item. Matches items in CSS with #name selector '''
        self._cssid = idn
        return self

    def cssclass(self, cls: str) -> 'Drawable':
        ''' Set the CSS class name for the item. Matches items in CSS with .name selector '''
        self._csscls = cls
        return self

    def span(self, columns: int = 1, rows: int = 1) -> 'Drawable':
        ''' Set the row and column span for the item when placed in a
            grid layout.
        '''
        self._span = columns, rows
        return self

    def zorder(self, zorder: int = 1) -> 'Drawable':
        ''' Set zorder for the drawable '''
        self._zorder = zorder
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Draw elements to canvas '''

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for a standalone SVG '''
        canvas = Canvas(600, 400)
        if border:
            canvas.rect(0, 0, 600, 400)
        return canvas.xml()

    def svg(self) -> str:
        ''' Get SVG string representation '''
        return ET.tostring(self.svgxml(), encoding='unicode')

    def _repr_svg_(self):
        ''' Representer function for Jupyter '''
        return self.svg()

    def imagebytes(self, fmt: Literal['svg', 'eps', 'pdf', 'png'] = 'svg') -> bytes:
        ''' Get byte data for image

            Args:
                ext: File format extension. Will be extracted from
                    fname if not provided.
        '''
        img = self.svg().encode()
        if fmt != 'svg':
            import cairosvg  # type: ignore

            if fmt == 'eps':
                img = cairosvg.svg2eps(img)
            elif fmt == 'pdf':
                img = cairosvg.svg2pdf(img)
            elif fmt == 'png':
                img = cairosvg.svg2png(img)
            else:
                raise ValueError(
                    f'Cannot convert to {fmt} format. Supported formats: svg, eps, pdf, png')
        return img

    def save(self, fname: str):
        ''' Save image to a file

            Args:
                fname: Filename, with extension.

            Notes:
                SVG format is always supported. EPS, PDF, and PNG formats are
                available when the `cairosvg` package is installed
        '''
        _, ext = os.path.splitext(fname)
        ext = ext.lower()[1:]

        img = self.imagebytes(ext)  # type: ignore

        with open(fname, 'wb') as f:
            f.write(img)
