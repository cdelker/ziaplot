''' Point with optiona text and guide lines'''
from __future__ import annotations
from typing import Optional
import math

from ..calcs import line_intersection, func_intersection, local_min, local_max
from ..text import TextPosition, text_align_ofst
from ..style import MarkerTypes, PointType
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..element import Element
from ..shapes import Circle
from .function import Function
from .line import Line
from .bezier import BezierQuad


class Point(Element):
    ''' Point with optional text label

        Args:
            x: X-value
            y: Y-value
    '''
    _step_color = False

    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self._text: Optional[str] = None
        self._text_pos: Optional[TextPosition] = None
        self._guidex: Optional[float] = None
        self._guidey: Optional[float] = None

    @property
    def point(self) -> PointType:
        ''' XY coordinate tuple '''
        return self.x, self.y

    def marker(self, marker: MarkerTypes, radius: Optional[float] = None,
               orient: bool = False) -> 'Point':
        ''' Sets the point marker shape and size '''
        self._style.shape = marker
        if radius:
            self._style.radius = radius
        return self

    def label(self, text: str,
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

    def _logx(self) -> None:
        ''' Convert x coordinates to log(x) '''
        self.x = math.log10(self.x)

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = math.log10(self.y)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        if self._guidex is not None:
            style = self._build_style('Point.GuideX')
            canvas.path([self.x, self.x], [self._guidex, self.y],
                        color=style.get_color(),
                        stroke=style.stroke,
                        width=style.stroke_width,
                        dataview=databox)
        if self._guidey is not None:
            style = self._build_style('Point.GuideY')
            canvas.path([self._guidey, self.x], [self.y, self.y],
                        color=style.get_color(),
                        stroke=style.stroke,
                        width=style.stroke_width,
                        dataview=databox)

        sty = self._build_style()
        markname = canvas.definemarker(sty.shape,
                                       sty.radius,
                                       sty.get_color(),
                                       sty.edge_color,
                                       sty.edge_width)
        canvas.path([self.x], [self.y],
                    color=sty.get_color(),
                    markerid=markname,
                    dataview=databox)

        if self._text:
            style = self._build_style('Point.Text')
            dx, dy, halign, valign = text_align_ofst(
                self._text_pos, style.margin)

            canvas.text(self.x, self.y, self._text,
                        color=style.get_color(),
                        font=style.font,
                        size=style.font_size,
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
        x, y = local_min(f, x1, x2)
        return cls(x, y)

    @classmethod    
    def at_maximum(cls, f: Function, x1: float, x2: float) -> 'Point':
        ''' Draw a Point at local maximum of f between x1 and x2 '''
        x, y = local_max(f, x1, x2)
        return cls(x, y)

    @classmethod
    def on_circle(cls, circle: Circle, theta: float) -> 'Point':
        ''' Draw a Point on the circle at angle theta (degrees) '''
        x, y = circle._xy(math.radians(theta))
        return cls(x, y)

    @classmethod
    def at_intersection(cls, f1: Function, f2: Function,
                        x1: float|None = None,
                        x2: float|None = None) -> 'Point':
        ''' Draw a Point at the intersection of two functions '''
        if isinstance(f1, Line) and isinstance(f2, Line):
            x, y= line_intersection(f1, f2)
        else:
            if x1 is None or x2 is None:
                raise ValueError('x1 and x2 are required for intersection of non-line functions.')
            x, y = func_intersection(f1, f2, x1, x2)
        return cls(x, y)

    @classmethod
    def on_bezier(cls, b: BezierQuad, t: float) -> 'Point':
        x, y = b.xy(t)
        return cls(x, y)
