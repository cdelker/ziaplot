''' Point with optiona text and guide lines'''
from __future__ import annotations
from typing import Optional
import math

from ..text import TextPosition
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..series import Series
from ..shapes import Circle
from . import Function


class Point(Series):
    ''' Point with optional text label

        Args:
            x: X-value
            y: Y-value
    '''
    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self._text = None
        self._text_pos = None
        self._guidex = None
        self._guidey = None
        self.style.line.width = 0
        self.style.marker.shape = 'round'
        self.style.marker.radius = 4
        self.style.marker.color = 'C2'

    def label(self, text: str = None,
              pos: TextPosition = 'NE') -> 'Point':
        ''' Add a text label to the point

            Args:
                text: Label
                text_pos: Position for label with repsect
                    to the point (N, E, S, W, NE, NW, SE, SW)
        '''
        self._text = text
        self._text_pos = pos
        return self

    def guidex(self, toy: float = 0) -> 'Point':
        ''' Draw a vertical guide line between point and toy '''
        self._guidex = toy
        return self

    def guidey(self, tox: float = 0) -> 'Point':
        ''' Draw a horizontal guide line between point and tox '''
        self._guidey = tox
        return self

    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        delta = .05
        dx = abs(self.x) * delta
        dy = abs(self.y) * delta
        return DataRange(self.x - dx, self.x + dx,
                         self.y - dy, self.y + dy)

    def logx(self) -> None:
        ''' Convert x coordinates to log(x) '''
        self.x = math.log10(self.x)

    def logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = math.log10(self.y)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        if self._guidex is not None:
            canvas.path([self.x, self.x], [self._guidex, self.y],
                        color=self.style.point.guidex.color,
                        stroke=self.style.point.guidex.stroke,
                        width=self.style.point.guidex.width,
                        dataview=databox)
        if self._guidey is not None:
            canvas.path([self._guidey, self.x], [self.y, self.y],
                        color=self.style.point.guidex.color,
                        stroke=self.style.point.guidex.stroke,
                        width=self.style.point.guidex.width,
                        dataview=databox)

        markname = canvas.definemarker(self.style.point.marker.shape,
                                        self.style.point.marker.radius,
                                        self.style.point.marker.color,
                                        self.style.point.marker.strokecolor,
                                        self.style.point.marker.strokewidth)
        color = self.style.line.color
        canvas.path([self.x], [self.y],
                    color=color,
                    markerid=markname,
                    dataview=databox)

        if self._text:
            x, y = self.x, self.y
            dx = dy = 0
            halign, valign = 'center', 'center'
            if 'N' in self._text_pos:
                valign = 'bottom'
                dy = self.style.point.text_ofst
            elif 'S' in self._text_pos:
                valign = 'top'
                dy = -self.style.point.text_ofst
            if 'E' in self._text_pos:
                halign = 'left'
                dx = self.style.point.text_ofst
            elif 'W' in self._text_pos:
                halign = 'right'
                dx = -self.style.point.text_ofst

            if dx and dy:
                dx /= math.sqrt(2)
                dy /= math.sqrt(2)

            canvas.text(x, y, self._text,
                        color=self.style.point.text.color,
                        font=self.style.point.text.font,
                        size=self.style.point.text.size,
                        halign=halign,
                        valign=valign,
                        pixelofst=(dx, dy),
                        dataview=databox)

    @classmethod
    def at(cls, f: Function, x: float) -> 'Point':
        ''' Draw a Point at y = f(x) '''
        y = f.y(x)
        return cls(x, y)

    @classmethod
    def at_minimum(cls, f: Function, x1: float, x2: float) -> 'Point':
        ''' Draw a Point at local minimum of f between x1 and x2 '''
        x = f._local_min(x1, x2)
        y = f.y(x)
        return cls(x, y)

    @classmethod    
    def at_maximum(cls, f: Function, x1: float, x2: float) -> 'Point':
        ''' Draw a Point at local maximum of f between x1 and x2 '''
        x = f._local_max(x1, x2)
        y = f.y(x)
        return cls(x, y)

    @classmethod
    def on_circle(cls, circle: Circle, theta: float) -> 'Point':
        ''' Draw a Point on the circle at angle theta (degrees) '''
        x, y = circle._xy(math.radians(theta))
        return cls(x, y)
