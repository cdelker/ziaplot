''' Point with optional text and guide lines'''
from __future__ import annotations
from typing import Optional, Iterator
import math

from .. import geometry
from ..geometry import PointType, LineType
from ..text import TextPosition, text_align_ofst
from ..style import MarkerTypes
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..element import Element
from .shapes import Circle, Arc
from .function import Function
from .line import Line
from .bezier import Bezier


class Point(Element):
    ''' Point with optional text label

        Args:
            p: x, y tuple
    '''
    _step_color = False

    def __init__(self, p: PointType):
        super().__init__()
        self.x, self.y = p
        self._text: Optional[str] = None
        self._text_pos: Optional[TextPosition] = None
        self._guidex: Optional[float] = None
        self._guidey: Optional[float] = None
        self._zorder: int = 6  # Points should usually be above other things

    def __getitem__(self, idx):
        return [self.x, self.y][idx]

    def __iter__(self) -> Iterator[float]:
        return iter(self.point)

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
                        dataview=databox,
                        zorder=self._zorder)
        if self._guidey is not None:
            style = self._build_style('Point.GuideY')
            canvas.path([self._guidey, self.x], [self.y, self.y],
                        color=style.get_color(),
                        stroke=style.stroke,
                        width=style.stroke_width,
                        dataview=databox,
                        zorder=self._zorder)

        sty = self._build_style()
        markname = canvas.definemarker(sty.shape,
                                       sty.radius,
                                       sty.get_color(),
                                       sty.edge_color,
                                       sty.edge_width)
        canvas.path([self.x], [self.y],
                    color=sty.get_color(),
                    markerid=markname,
                    dataview=databox,
                    zorder=self._zorder)

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

    def reflect(self, line: LineType) -> 'Point':
        ''' Create a new point reflected over line '''
        x, y = geometry.reflect(self, line)
        return Point((x, y))

    def image(self, line: LineType) -> 'Point':
        ''' Create a new point imaged onto the line (point on line at
            shortest distance to point)
        '''
        x, y = geometry.image(self, line)
        return Point((x, y))

    def bisect(self, point: PointType) -> 'Line':
        ''' Create a new line bisecting the two points '''
        return Line.from_standard(*geometry.line.bisect_points(self, point))

    @classmethod
    def at(cls, f: Function, x: float) -> 'Point':
        ''' Draw a Point at y = f(x) '''
        y = f.y(x)
        return cls((x, y))

    @classmethod
    def at_y(cls, f: Function, y: float) -> 'Point':
        ''' Draw a Point at y = f(x) '''
        x = f.x(y)
        return cls((x, y))

    @classmethod
    def at_minimum(cls, f: Function, x1: float, x2: float) -> 'Point':
        ''' Draw a Point at local minimum of f between x1 and x2 '''
        x, y = geometry.function.local_min(f.y, x1, x2)
        return cls((x, y))

    @classmethod
    def at_maximum(cls, f: Function, x1: float, x2: float) -> 'Point':
        ''' Draw a Point at local maximum of f between x1 and x2 '''
        x, y = geometry.function.local_max(f.y, x1, x2)
        return cls((x, y))

    @classmethod
    def at_midpoint(cls, a: PointType, b: PointType) -> 'Point':
        ''' Draw a point at the midpoint between the two given points '''
        x, y = geometry.midpoint(a, b)
        return cls((x, y))

    @classmethod
    def on_circle(cls, circle: Circle, theta: float) -> 'Point':
        ''' Draw a Point on the circle at angle theta (degrees) '''
        x, y = geometry.circle.point(circle, math.radians(theta))
        return cls((x, y))

    @classmethod
    def at_intersection(cls, f1: Function|Line|Circle|Arc, f2: Function|Line|Circle|Arc,
                        bounds: Optional[tuple[float, float]] = None,
                        which: str = 'top',
                        offarc: bool = False
                        ) -> 'Point':
        ''' Draw a Point at the intersection of two functions, lines, circles, or arcs.

            Args:
                f1: First function
                f2: Second function
                bounds: tuple of x values to bound the search. Only used for intersection
                    of two Functions
                which: in cases where more than one intersection occurs, return the
                    `top`, `bottom`, `left` or `right`-most point.
        '''
        if isinstance(f1, Line) and isinstance(f2, Line):
            x, y = geometry.intersect.lines(f1, f2)

        elif isinstance(f1, (Arc, Circle)) and isinstance(f2, (Arc, Circle)):
            points = geometry.intersect.circles(f1, f2)
            x, y = geometry.select_which(points, which)

        elif isinstance(f1, Line) and isinstance(f2, Arc) and not offarc:
            points = geometry.intersect.line_arc(f1, f2)
            x, y = geometry.select_which(points, which)
        elif isinstance(f1, Arc) and isinstance(f2, Line) and not offarc:
            points = geometry.intersect.line_arc(f2, f1)
            x, y = geometry.select_which(points, which)
        elif isinstance(f1, Line) and isinstance(f2, Circle):
            points = geometry.intersect.line_circle(f1, f2)
            x, y = geometry.select_which(points, which)
        elif isinstance(f1, Circle) and isinstance(f2, Line):
            points = geometry.intersect.line_circle(f2, f1)
            x, y = geometry.select_which(points, which)

        else:
            if bounds is None:
                raise ValueError('bounds are required for intersection of non-line functions.')
            assert callable(f1.y)
            assert callable(f2.y)
            x, y = geometry.intersect.functions(f1.y, f2.y, *bounds)

        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError('No intersection found')

        return cls((x, y))

    @classmethod
    def on_bezier(cls, b: Bezier, t: float) -> 'Point':
        ''' Create a Point on the Bezier curve '''
        x, y = b.xy(t)
        return cls((x, y))
