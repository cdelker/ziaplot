'''' Text annotations '''
from __future__ import annotations
from typing import Optional
import math

from ..text import Halign, Valign
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..element import Component


class Text(Component):
    ''' A text element to draw at a specific x-y location

        Args:
            x: X-position for text
            y: Y-position for text
            s: String to draw
            halign: Horizontal alignment
            valign: Vertical alignment
            rotate: Rotation angle, in degrees
    '''
    def __init__(self, x: float, y: float, s: str,
                 halign: Halign = 'left',
                 valign: Valign = 'bottom',
                 rotate: Optional[float] = None):
        super().__init__()
        self.x = x
        self.y = y
        self.s = s
        self.halign = halign
        self.valign = valign
        self.rotate = rotate

    def color(self, color: str) -> 'Text':
        ''' Sets the text color '''
        self._style.color = color
        return self

    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        return DataRange(None, None, None, None)

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = math.log10(self.y)

    def _logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.x = math.log10(self.x)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        canvas.text(self.x, self.y, self.s,
                    color=sty.get_color(),
                    font=sty.font,
                    size=sty.font_size,
                    halign=self.halign,
                    valign=self.valign,
                    rotate=self.rotate,
                    dataview=databox)
