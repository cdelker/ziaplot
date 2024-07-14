''' Point with optiona text and guide lines'''
from __future__ import annotations
from typing import Optional
import math

from ..text import TextPosition, text_align_ofst
from ..style import MarkerTypes
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..series import Series
from ..shapes import Circle
from .function import Function
from .bezier import BezierQuad
from ..util import root



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
        self.style.point.marker.shape = 'round'
        self.style.point.marker.radius = 4

    def color(self, color: str) -> 'Series':
        ''' Sets the series color '''
        self.style.point.marker.color = color
        return self

    def marker(self, marker: MarkerTypes, radius: Optional[float] = None) -> 'Point':
        ''' Sets the series marker '''
        self.style.point.marker.shape = marker
        if radius:
            self.style.point.marker.radius = radius
        return self

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
        canvas.path([self.x], [self.y],
                    color=self.style.point.marker.color,
                    markerid=markname,
                    dataview=databox)

        if self._text:
            dx, dy, halign, valign = text_align_ofst(
                self._text_pos, self.style.point.text_ofst)

            canvas.text(self.x, self.y, self._text,
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
    def at_y(cls, f: Function, y: float) -> 'Point':
        ''' Draw a Point at y = f(x) '''
        x = f.x(y)
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

    @classmethod
    def at_intersection(cls, f1: Function, f2: Function,
                        x1: float, x2: float) -> 'Point':
        ''' Draw a Point at the intersection of two functions '''
        tol = (x2-x1) * 1E-4
        x = root(lambda x: f1.func(x) - f2.func(x),
                 a=x1, b=x2, tol=tol)
        y = f1.y(x)
        return cls(x, y)

    @classmethod
    def on_bezier(cls, b: BezierQuad, t: float) -> 'Point':
        x, y = b.xy(t)
        return cls(x, y)
