''' Euclidean Lines '''
from __future__ import annotations
from typing import Optional, Sequence, Iterator, TYPE_CHECKING
from dataclasses import dataclass
import math
from xml.etree import ElementTree as ET

from .. import geometry
from ..geometry import PointType
from ..element import Element
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..text import TextPosition, text_align_ofst
from ..style import MarkerTypes
from ..diagrams import Graph

if TYPE_CHECKING:
    from .point import Point


@dataclass
class LineLabel:
    ''' A label along a line

        Args:
            label: The label text
            loc: Location as fraction (0-1) along the line
            align: Alignment with respect to position
            rotate: Rotate text in direction of line
            color: Color of text
            size: Size of text
    '''
    label: str
    loc: float = 0.5
    align: TextPosition = 'N'
    rotate: bool = False
    color: Optional[str] = None
    size: Optional[float] = None


class Line(Element):
    ''' A straight Line extending to infinity

        Args:
            point: One point on the line
            slope: Slope of the line
    '''
    _step_color = True

    def __init__(self, point: PointType|'Point', slope: float = 0):
        super().__init__()
        self.slope = slope
        self.point = point
        self.startmark: Optional[MarkerTypes] = None
        self.endmark: Optional[MarkerTypes] = None
        self.midmark: Optional[MarkerTypes] = None
        self._labels: list[LineLabel] = []
        self.n: int = 200

    def __getitem__(self, idx):
        ''' Index a, b, c of standard form '''
        return self.standard[idx]

    def __iter__(self) -> Iterator[float]:
        return iter(self.standard)

    @property
    def intercept(self) -> float:
        ''' Y-intercept of Line '''
        return -self.slope * self.point[0] + self.point[1]

    @property
    def point2(self) -> PointType:
        ''' Get a second point on the line, 1 unit away '''
        theta = math.atan(self.slope)
        x2 = self.point[0] + math.cos(theta)
        y2 = self.point[1] + math.sin(theta)
        return x2, y2

    @property
    def standard(self) -> tuple[float, float, float]:
        ''' Line coefficients (A, B, C) in standard form Ax + By = C'''
        p1 = self.point
        p2 = self.point2
        a = p1[1] - p2[1]
        b = p2[0] - p1[0]
        c = (p1[0]*p2[1] - p2[0]*p1[1])
        return a, b, -c

    def x(self, y) -> float:
        ''' Calculate x at y '''
        if not math.isfinite(self.intercept) or not math.isfinite(self.slope):
            return self.point[0]
        try:
            return (y - self.intercept) / self.slope
        except ZeroDivisionError:
            return math.nan

    def y(self, x: float) -> float:
        ''' Calculate y at x '''
        y = self.slope * x + self.intercept
        return y

    def xy(self, x: float) -> PointType:
        ''' Calculate y at x, returning point (x, y) '''
        return (x, self.y(x))

    def trim(self, x1: float, x2: float) -> 'Segment':
        ''' Convert the line into a segment '''
        self.__class__ = Segment
        assert isinstance(self, Segment)
        self.p1 = self.xy(x1)
        self.p2 = self.xy(x2)
        return self

    def trimd(self, x: float, d1: float, d2: float) -> 'Segment':
        ''' Covnvert the line into a segment extending a distance
            d1 left and d2 right of point x on the line
        '''
        y = self.y(x)
        theta = math.atan(self.slope)
        costh = math.cos(theta)
        sinth = math.sin(theta)
        x1 = x - d1 * costh
        x2 = x + d2 * costh
        y1 = y - d1 * sinth
        y2 = y + d2 * sinth
        self.p1 = (x1, y1)
        self.p2 = (x2, y2)
        self.__class__ = Segment
        assert isinstance(self, Segment)
        return self

    def normal(self, p: PointType|'Point') -> 'Line':
        ''' Create normal Line passing through p '''
        return Line.from_standard(*geometry.line.normal(self, p))

    def bisect_angle(self, other: 'Line', which: str = '+') -> 'Line':
        ''' Create new line bisecting the two Lines.

            The `which` parameter specifies which of the two bisectors
            to return. It may be `+` to return the bisector with positive or 0 slope,
            or `-` to return the bisector with negative or vertical slope.
        '''
        lines = list(geometry.line.bisect(self, other))
        lines = sorted(lines, key=geometry.line.slope)
        if which == '+':
            return Line.from_standard(*lines[1])
        return Line.from_standard(*lines[0])

    def parallel(self, distance: float) -> 'Line':
        ''' Create a line parallel to another line '''
        slope = self.slope
        if math.isfinite(slope):
            intercept = distance * math.sqrt(1+slope**2) + self.intercept
            return Line.from_slopeintercept(slope, intercept)
        return Line((self.point[0]+distance, self.point[1]), slope)

    def _evaluate(self, x: Sequence[float]) -> tuple[Sequence[float], Sequence[float]]:
        ''' Evaluate and return (x, y) in logscale if needed '''
        y = [self.y(xx) for xx in x]
        return x, y

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'Line':
        ''' Define markers to show at the start and end of the line. Use defaults
            to show arrowheads pointing outward in the direction of the line.
        '''
        self.startmark = start
        self.endmark = end
        return self

    def midmarker(self, midmark: MarkerTypes = '<') -> 'Line':
        ''' Add a marker to the center of the Segment '''
        self.midmark = midmark
        return self

    def label(self, text: str,
              loc: float = 0,
              align: TextPosition = 'N',
              rotate: bool = False,
              color: Optional[str] = None,
              size: Optional[float] = None) -> 'Line':
        ''' Add a label along the Line

            Args:
                text: The text to add
                loc: Position along the line as fraction from 0-1
                align: Text alignment
                rotate: Rotate the text with the line
                color: Text color
                size: Text size
        '''
        self._labels.append(LineLabel(text, loc, align, rotate, color, size))
        return self

    def _tangent_slope(self, x: float) -> float:
        ''' Calculate angle tangent to line at x '''
        return self.slope

    def _endpoints(self, databox: ViewBox) -> tuple[PointType, PointType]:
        ''' Get endpoints of line that will fill the databox '''
        assert databox is not None
        intercept = self.intercept
        if not math.isfinite(intercept):
            # Vertical Line
            x1 = x2 = self.point[0]
            y1 = databox.y
            y2 = databox.y + databox.h
        elif self.slope == 0:
            # Horizontal Line
            x1 = databox.x
            x2 = databox.x + databox.w
            y1 = y2 = intercept
        elif self.slope != 0:
            x1 = (databox.y - intercept) / self.slope
            x2 = (databox.y + databox.h - intercept) / self.slope
            y1 = x1 * self.slope + intercept
            y2 = x2 * self.slope + intercept
        return (x1, x2), (y1, y2)

    @classmethod
    def from_slopeintercept(cls, slope: float, intercept: float = 0) -> 'Line':
        ''' Create a line from slope and intercept '''
        return cls((0, intercept), slope)

    @classmethod
    def from_points(cls, p1: PointType|'Point', p2: PointType|'Point') -> 'Line':
        ''' Create a line from two points '''
        try:
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        except ZeroDivisionError:
            slope = math.inf
        return cls(p1, slope)

    @classmethod
    def from_standard(cls, a: float, b: float, c: float) -> 'Line':
        ''' Create line from standard form ax + by = c '''
        try:
            slope = -a/b
            intercept = c/b
            return cls.from_slopeintercept(slope, intercept)
        except ZeroDivisionError:
            return cls((c/a, 0), math.inf)  # Vertical

    def _place_labels(self, x0: PointType, y0: PointType,
                      canvas: Canvas, databox: ViewBox) -> None:
        ''' Draw labels along line

            Args:
                x0: The x endpoints of the line
                canvas: Canvas to draw on
                databox: Databox within the canvas
        '''
        textstyle = self._build_style('Line.Text')
        for label in self._labels:
            dx, dy, halign, valign = text_align_ofst(
                label.align, textstyle.margin)

            x = x0[0] + (x0[1] - x0[0]) * label.loc
            y = y0[0] + (y0[1] - y0[0]) * label.loc
            angle = None
            if label.rotate:
                angle = math.degrees(math.atan(self.slope))

            color = label.color if label.color else textstyle.get_color()
            size = label.size if label.size else textstyle.font_size
            canvas.text(x, y, label.label,
                        color=color,
                        font=textstyle.font,
                        size=size,
                        halign=halign,
                        valign=valign,
                        rotate=angle,
                        pixelofst=(dx, dy),
                        dataview=databox)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        sty = self._build_style()
        color = sty.get_color()
        x, y = self._endpoints(databox)
        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(
                self.startmark,
                sty.radius,
                sty.get_color(),
                sty.edge_color,
                sty.edge_width,
                orient=True)

        if self.endmark:
            endmark = canvas.definemarker(
                self.endmark,
                sty.radius,
                sty.get_color(),
                sty.edge_color,
                sty.edge_width,
                orient=True)

        canvas.path(x, y,
                    stroke=sty.stroke,
                    color=color,
                    width=sty.stroke_width,
                    startmarker=startmark,
                    endmarker=endmark,
                    dataview=databox,
                    zorder=self._zorder,
                    attrib=self._attrs)

        if self.midmark:
            midmark = canvas.definemarker(self.midmark,
                                          sty.radius,
                                          sty.get_color(),
                                          sty.edge_color,
                                          sty.edge_width,
                                          orient=True)

            midx, midy = (x[0]+x[1])/2, (y[0]+y[1])/2
            slope = self._tangent_slope(0.5)
            dx = midx/1E3
            midx1 = midx + dx
            midy1 = midy + dx*slope
            canvas.path([midx, midx1], [midy, midy1],
                        color='none',
                        startmarker=midmark,
                        dataview=databox,
                        zorder=self._zorder)

        self._place_labels(x, y, canvas, databox)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        graph = Graph()
        graph.add(self)
        return graph.svgxml(border=border)


class HLine(Line):
    ''' Horizontal Line at y '''
    def __init__(self, y: float):
        super().__init__(point=(0, y), slope=0)


class VLine(Line):
    ''' Vertical Line at x '''
    def __init__(self, x: float):
        super().__init__(point=(x, 0), slope=math.inf)


class Segment(Line):
    ''' Line segment from p1 to p2 '''
    def __init__(self, p1: PointType|'Point', p2: PointType|'Point'):
        try:
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        except ZeroDivisionError:
            slope = math.inf
        super().__init__(p1, slope)
        self.p1: PointType
        self.p2: PointType
        self.p1 = p1[0], p1[1]
        self.p2 = p2[0], p2[1]

    @property
    def length(self) -> float:
        ''' Length of the segment '''
        return math.sqrt((self.p1[0]- self.p2[0])**2 + (self.p1[1] - self.p2[1])**2)

    @property
    def point2(self) -> PointType:
        ''' Second point on the segment '''
        return self.p2

    def bisect(self) -> Line:
        ''' Perpendicular bisector of the segment '''
        mid = self.midpoint()
        return self.normal(mid)

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        xmin = min(self.p1[0], self.p2[0])
        xmax = max(self.p1[0], self.p2[0])
        ymin = min(self.p1[1], self.p2[1])
        ymax = max(self.p1[1], self.p2[1])
        return DataRange(xmin, xmax, ymin, ymax)

    def trim(self, x1: Optional[float] = None, x2: Optional[float] = None) -> Segment:
        ''' Move endpoints of segment, keeping slope and intercept '''
        y1, y2 = self.p1[1], self.p2[1]
        if x1 is not None:
            y1 = self.slope * x1 + self.intercept
        else:
            x1 = self.p1[0]

        if x2 is not None:
            y2 = self.slope * x2 + self.intercept
        else:
            x2 = self.p2[0]

        self.p1 = (x1, y1)
        self.p2 = (x2, y2)
        return self

    def _endpoints(self, databox: ViewBox) -> tuple[PointType, PointType]:
        ''' Get endpoints of line that will fill the databox '''
        return (self.p1[0], self.p2[0]), (self.p1[1], self.p2[1])

    def midpoint(self) -> PointType:
        ''' Midpoint of the segment '''
        return geometry.midpoint(self.p1, self.p2)

    @classmethod
    def horizontal(cls, p: PointType|'Point', tox: float = 0) -> 'Segment':
        ''' Create a horizontal segment from p to the tox x value '''
        return cls(p, (tox, p[1]))

    @classmethod
    def vertical(cls, p: PointType|'Point', toy: float = 0) -> 'Segment':
        ''' Create a vertical segment from p to the toy y value '''
        return cls(p, (p[0], toy))


class Vector(Segment):
    ''' A Vector arrow from (0, 0) to (x, y) '''
    def __init__(self, x: float, y: float):
        super().__init__((0, 0), (x, y))
        self.endmark = '>'

    @classmethod
    def from_angle(cls, theta: float, d: float = 1):
        ''' Create Vector from angle and length '''
        x = d * math.cos(theta)
        y = d * math.sin(theta)
        return cls(x, y)
