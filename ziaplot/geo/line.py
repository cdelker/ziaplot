''' Euclidean Lines '''
from __future__ import annotations
from typing import Optional
from xml.etree import ElementTree as ET
import math

from ..canvas import Canvas, Borders, ViewBox
from ..series import PointType
from ..style import MarkerTypes
from ..axes import XyPlot
from .function import Function


class Line(Function):
    ''' A straight Line extending to infinity

        Args:
            point: One point on the line
            slope: Slope of the line
    '''
    def __init__(self, point: PointType, slope: float = 0):
        self.slope = slope
        self.point = point
        intercept = -slope * point[0] + point[1]
        super().__init__(lambda x: intercept + slope * x)
        self.startmark: Optional[MarkerTypes] = None
        self.endmark: Optional[MarkerTypes] = None

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'Line':
        ''' Define markers to show at the start and end of the line. Use defaults
            to show arrowheads pointing outward in the direction of the line.
        '''
        self.startmark = start
        self.endmark = end
        return self

    @property
    def intercept(self) -> float:
        ''' Y-intercept of Line '''
        return -self.slope * self.point[0] + self.point[1]

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

    def _tangent_slope(self, x: float) -> float:
        ''' Calculate angle tangent to Series at x '''
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
    def from_points(cls, p1: PointType, p2: PointType) -> 'Line':
        ''' Create a line from two points '''
        try:
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        except ZeroDivisionError:
            slope = math.inf
        return cls(p1, slope)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        color = self.style.line.color
        x, y = self._endpoints(databox)
        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(self.startmark,
                                            self.style.marker.radius,
                                            self.style.marker.color,
                                            self.style.marker.strokecolor,
                                            self.style.marker.strokewidth,
                                            orient=True)
        if self.endmark:
            endmark = canvas.definemarker(self.endmark,
                                          self.style.marker.radius,
                                          self.style.marker.color,
                                          self.style.marker.strokecolor,
                                          self.style.marker.strokewidth,
                                          orient=True)
        canvas.path(x, y,
                    stroke=self.style.line.stroke,
                    color=color,
                    width=self.style.line.width,
                    startmarker=startmark,
                    endmarker=endmark,
                    dataview=databox)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        ax = XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)


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
    def __init__(self, p1: PointType, p2: PointType):
        try:
            slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        except ZeroDivisionError:
            slope = math.inf
        super().__init__(p1, slope)
        self.p1 = p1
        self.p2 = p2
        self.midmark: MarkerTypes = None

    @property
    def length(self) -> float:
        ''' Length of the segment '''
        return math.sqrt((self.p1[0]- self.p2[0])**2 + (self.p1[1] - self.p2[1])**2)

    def midmarker(self, marker: MarkerTypes) -> Segment:
        ''' Add a marker to the center of the Segment '''
        self.midmark = marker
        return self

    def trim(self, x1: Optional[float] = None, x2: Optional[float] = None) -> None:
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

    def _endpoints(self, databox: ViewBox) -> tuple[PointType, PointType]:
        ''' Get endpoints of line that will fill the databox '''
        return (self.p1[0], self.p2[0]), (self.p1[1], self.p2[1])

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        color = self.style.line.color
        x, y = self._endpoints(databox)
        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(self.startmark,
                                            self.style.marker.radius,
                                            self.style.marker.color,
                                            self.style.marker.strokecolor,
                                            self.style.marker.strokewidth,
                                            orient=True)
        if self.endmark:
            endmark = canvas.definemarker(self.endmark,
                                          self.style.marker.radius,
                                          self.style.marker.color,
                                          self.style.marker.strokecolor,
                                          self.style.marker.strokewidth,
                                          orient=True)

        color = self.style.line.color
        canvas.path(x, y,
                    stroke=self.style.line.stroke,
                    color=color,
                    width=self.style.line.width,
                    startmarker=startmark,
                    endmarker=endmark,
                    dataview=databox)

        if self.midmark:
            midmark = canvas.definemarker(self.midmark,
                                          self.style.marker.radius,
                                          self.style.marker.color,
                                          self.style.marker.strokecolor,
                                          self.style.marker.strokewidth,
                                          orient=True)
            midx = [(x[1] + x[0]) / 2]
            midy = [(y[1] + y[0]) / 2]
            canvas.path(midx, midy,
                        startmarker=midmark,
                        dataview=databox)


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
