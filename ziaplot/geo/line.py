''' Euclidean Lines '''
from __future__ import annotations
from typing import Optional
from xml.etree import ElementTree as ET
import math

from ..canvas import Canvas, Borders, ViewBox
from ..text import TextPosition, text_align_ofst
from ..series import PointType, Series
from ..style import MarkerTypes
from ..axes import AxesPlot
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
        ax = AxesPlot(style=self._axisstyle)
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
        self._label_start: Optional[tuple[str, TextPosition]] = None
        self._label_end: Optional[tuple[str, TextPosition]] = None

    @property
    def length(self) -> float:
        ''' Length of the segment '''
        return math.sqrt((self.p1[0]- self.p2[0])**2 + (self.p1[1] - self.p2[1])**2)

    def label_start(self, text: str = None,
                    pos: TextPosition = 'NE') -> 'Segment':
        ''' Add a text label to the start of the segment

            Args:
                text: Label
                text_pos: Position for label with repsect
                    to the point (N, E, S, W, NE, NW, SE, SW)
        '''
        self._label_start = text, pos
        return self

    def label_end(self, text: str = None,
                  pos: TextPosition = 'NE') -> 'Segment':
        ''' Add a text label to the end of the segment

            Args:
                text: Label
                text_pos: Position for label with repsect
                    to the point (N, E, S, W, NE, NW, SE, SW)
        '''
        self._label_end = text, pos
        return self

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

        if self._label_start is not None:
            self._draw_label(
                x[0], y[0], self._label_start[0], self._label_start[1],
                canvas, databox)

        if self._label_end is not None:
            self._draw_label(
                x[1], y[1], self._label_end[0], self._label_end[1],
                canvas, databox)

    def _draw_label(self, x, y, text, pos, canvas, databox):
        ''' Draw the label

            Args:
                x: X anchor position
                y: Y anchor position
                text: Text to draw
                pos: Position/alignment of text about the anchor
                canvas: Canvas to draw on
                databox: Databox within the canvas
        '''
        dx, dy, halign, valign = text_align_ofst(
            pos, self.style.point.text_ofst)

        canvas.text(x, y, text,
                    color=self.style.point.text.color,
                    font=self.style.point.text.font,
                    size=self.style.point.text.size,
                    halign=halign,
                    valign=valign,
                    pixelofst=(dx, dy),
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


class Angle(Series):
    ''' Draw angle between two Lines/Segments '''
    def __init__(self, line1: Line, line2: Line, quad: int = 1):
        super().__init__()
        self.line1 = line1
        self.line2 = line2
        self.quad = quad
        self._label: str = None
        self.square_right = True

    def label(self, label: str) -> 'Angle':
        self._label = label
        return self

    def color(self, color: str) -> 'Angle':
        ''' Sets the color of the angle arc '''
        self.style.angle.color = color
        return self

    def strokewidth(self, width: float) -> 'Angle':
        ''' Sets the strokewidth of the angle arc '''
        self.style.angle.strokewidth = width
        return self

    def radius(self, radius: float, text_radius: Optional[float] = None) -> 'Angle':
        ''' Sets the radius of the angle arc '''
        self.style.angle.radius = radius
        if text_radius:
            self.style.angle.text_radius = text_radius
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        m1, m2 = self.line1.slope, self.line2.slope
        b1, b2 = self.line1.intercept, self.line2.intercept

        # Point of intersection
        x = (b2 - b1) / (m1 - m2)
        y = self.line1.y(x)
        if not math.isfinite(x):
            x = self.line1.point[0]
            y = self.line1.y(x)
        if not math.isfinite(y):
            y = self.line2.y(x)

        theta1 = math.atan(m1)
        theta2 = math.atan(m2)

        if m1 < m2:
            theta1, theta2 = theta2, theta1

        if self.quad == 2:
            theta2 += math.pi
            theta1 += math.pi
            theta2, theta1 = theta1, theta2

        elif self.quad == 3:
            theta1 += math.pi
        elif self.quad == 4:
            theta2, theta1 = theta1, theta2
        else:
            theta2 += math.pi

        theta1 = (theta1 + math.tau) % math.tau
        theta2 = (theta2 + math.tau) % math.tau

        # Calculate radius of angle arc in data coordinates
        r = self.style.angle.radius * databox.w / canvas.viewbox.w
        dtheta = abs(theta1 - theta2) % math.pi
        if self.square_right and math.isclose(dtheta, math.pi/2):
            # Right Angle
            r2 = r / math.sqrt(2)
            xpath = [x + r2 * math.cos(theta1),
                     x + r * math.cos(theta1+math.pi/4),
                     x + r2 * math.cos(theta2)]
            ypath = [y + r2 * math.sin(theta1),
                     y + r * math.sin(theta1+math.pi/4),
                     y + r2 * math.sin(theta2)]
            canvas.path(xpath, ypath,
                        color=self.style.angle.color,
                        width=self.style.angle.strokewidth,
                        dataview=databox
                        )
        else:
            canvas.arc(x, y, r,
                    math.degrees(theta1),
                    math.degrees(theta2),
                    strokecolor=self.style.angle.color,
                    strokewidth=self.style.angle.strokewidth,
                    dataview=databox
                    )

        if self._label:
            r = self.style.angle.text_radius
            labelangle = angle_mean(theta1, theta2)
            dx = r * math.cos(labelangle)
            dy = r * math.sin(labelangle)

            if labelangle < math.tau/8 or labelangle > 7*math.tau/8:
                halign = 'left'
            elif 3 * math.tau / 8 < labelangle < 5 * math.tau / 8:
                halign = 'right'
            else:
                halign = 'center'

            if math.tau/8 < labelangle < 3 * math.tau / 8:
                valign = 'bottom'
            elif 5 * math.tau / 8 < labelangle < 7 * math.tau / 8:
                valign = 'top'
            else:
                valign = 'center'

            canvas.text(x, y, self._label,
                        color=self.style.angle.text.color,
                        font=self.style.angle.text.font,
                        size=self.style.angle.text.size,
                        halign=halign, valign=valign,
                        pixelofst=(dx, dy),
                        dataview=databox)


def angle_mean(theta1: float, theta2: float) -> float:
    ''' Circular mean over 0 to 2pi '''
    sine = math.sin(theta1) + math.sin(theta2)
    cosine = math.cos(theta1) + math.cos(theta2)
    mean = math.atan2(sine, cosine)
    return (mean + math.tau) % math.tau
