'''' Text annotations '''
from __future__ import annotations
from typing import Optional
import math

from ..style import SeriesStyle, MarkerTypes, DashTypes
from ..canvas import Canvas, Borders, ViewBox, DataRange, Halign, Valign
from ..series import Series


class Text(Series):
    ''' A text element to draw at a specific x-y location

        Args:
            x: X-position for text
            y: Y-position for text
            s: String to draw
            halign: Horizontal alignment
            valign: Vertical alignment
            rotate: Rotation angle, in degrees
    '''
    def __init__(self, x: float, y: float, s: str, halign: Halign = 'left',
                 valign: Valign = 'bottom', rotate: Optional[float] = None):
        super().__init__()
        self.style = SeriesStyle()
        self.x = x
        self.y = y
        self.s = s
        self.halign = halign
        self.valign = valign
        self.rotate = rotate

    def color(self, color: str) -> 'Text':
        ''' Sets the text color '''
        self.style.text.color = color
        return self

    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        return DataRange(None, None, None, None)

    def logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = math.log10(self.y)

    def logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.x = math.log10(self.x)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        canvas.text(self.x, self.y, self.s,
                    color=self.style.text.color,
                    font=self.style.text.font,
                    size=self.style.text.size,
                    halign=self.halign,
                    valign=self.valign,
                    rotate=self.rotate,
                    dataview=databox)
