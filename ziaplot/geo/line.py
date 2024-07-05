''' Euclidean Lines '''
from __future__ import annotations
from typing import Optional
import math

from ..canvas import Canvas, Borders, ViewBox
from ..series import Series
from ..dataplots import Point


PointType = tuple[float, float]


class Line(Series):
    ''' A straight line

        Args:
            point: One point on the line
            slope: Slope of the line
        
        See also Line.from_slopeintercept and Line.from_points
        for other means of creating the Line.
    '''
    def __init__(self, point: PointType, slope: float = 0):
        super().__init__()
        self.slope = slope
        self.point = point

    @property
    def intercept(self) -> float:
        return -self.slope * self.point[0] + self.point[1]

    def y(self, x):
        ''' Calculate y at x '''
        return self.slope * x + self.intercept

    def x(self, y):
        ''' Calculate x at y '''
        if not math.isfinite(self.intercept) or not math.isfinite(self.slope):
            return self.point[0]
        try:
            return (y - self.intercept) / self.slope
        except ZeroDivisionError:
            return math.nan

    def _endpoints(self, databox: ViewBox) -> tuple[tuple[float, float], tuple[float, float]]:
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

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        color = self.style.line.color
        x, y = self._endpoints(databox)
        canvas.path(x, y, self.style.line.stroke, color,
                    self.style.line.width, dataview=databox)

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

    @classmethod
    def perp_to(cls, line: 'Line', x: float = 0) -> 'Line':
        ''' Create a Line perpendicular to Line at x '''
        if not math.isfinite(line.slope):
            raise ValueError('Undefined Line')

        try:
            slope = -1 / line.slope
        except ZeroDivisionError as exc:
            slope = math.inf
        return cls(point=(x, line.y(x)), slope=slope)

    @classmethod
    def perp_toy(cls, line: 'Line', y: float = 0) -> 'Line':
        ''' Create a Line perpendicular to Line at y '''
        if line.slope == 0:
            raise ValueError('Undefined Line')

        slope = -1 / line.slope
        x = line.x(y)
        if x and not math.isfinite(x):
            x = line.point[0]
        return cls(point=(x, y), slope=slope)

    def x_point(self, x: float) -> Point:
        ''' Make a Point on the line at x '''
        return Point(x, self.y(x))

    def y_point(self, y):
        ''' Make a Point on the line at y '''
        return Point(self.x(y), y)


class HLine(Line):
    ''' Horizontal Line at y '''
    def __init__(self, y: float):
        super().__init__(point=(0, y), slope=0)


class VLine(Line):
    ''' Vertical Line at x '''
    def __init__(self, x: float):
        super().__init__(point=(x, 0), slope=math.inf)

