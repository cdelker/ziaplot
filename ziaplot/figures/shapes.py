''' Basic shapes '''
from __future__ import annotations
from typing import Optional, Iterator, TYPE_CHECKING
import math

from .. import geometry
from ..geometry import PointType
from ..element import Element
from ..canvas import Canvas, Borders, ViewBox, DataRange
from .line import Line, Segment

if TYPE_CHECKING:
    from .point import Point


class Shape(Element):
    ''' Filled shape '''
    def color(self, color: str) -> 'Shape':
        ''' Sets the fill color '''
        self._style.edge_color = color
        self._style.color = color
        return self

    def fill(self, color: str) -> 'Shape':
        ''' Sets the fill color '''
        self._style.fill_color = color
        return self


class Ellipse(Shape):
    ''' Draw an Ellipse

        Args:
            x: Center x coordinate
            y: Center y coordinate
            r1: Radius 1
            r2: Radius 2
            theta: Angle of rotation (degrees)
    '''
    def __init__(self, center: PointType|'Point',
                 r1: float, r2: float,
                 theta: float = 0):
        super().__init__()
        self.center = tuple(center)
        self.x: float
        self.y: float
        self.x, self.y = center
        self.r1 = r1
        self.r2 = r2
        self.theta = theta

    def __getitem__(self, item: int) -> float:
        return (self.x, self.y, self.r1, self.r2, self.theta)[item]

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y, self.r1, self.r2, self.theta))

    def tangent(self, p: PointType|'Point', which: str = 'top') -> Line:
        ''' Create a tangent line passing through p.

            Args:
                p: Point the tangent passees through, on or outside the circle
                which: Determines which of the two possible tangents to return.
                    may be `top`, `bottom`, `left`, or `right` based on the
                    position ot the tangent point on the circle.
        '''
        tangents = geometry.ellipse.tangent_points(self, p)
        t = geometry.select_which(tangents, which)
        return Line.from_points(t, p)

    def datarange(self) -> DataRange:
        ''' Data limits '''
        r = max(self.r1, self.r2)
        return DataRange(self.x-r, self.x+r, self.y-r, self.y+r)

    def _dxy(self, theta: float) -> PointType:
        ''' Get dx and dy from center to point on ellipse at angle theta (rad) '''
        theta = theta - math.radians(self.theta)
        e = math.sqrt(1 - (self.r2/self.r1)**2)
        phi = math.atan(math.tan(theta) * self.r1 / self.r2)
        r = self.r1 * math.sqrt(1 - e**2 * math.sin(phi)**2)
        dx = r * math.cos(theta)
        dy = r * math.sin(theta)
        return dx, dy

    def xy(self, theta: float) -> PointType:
        ''' Get x, y coordinate on the circle at the angle theta (degrees) '''
        return self._xy(math.radians(theta))

    def _xy(self, theta: float) -> PointType:
        ''' Get x, y coordinate on the circle at the angle theta (rad) '''
        dx, dy = self._dxy(theta)

        if self.theta:
            dx, dy = geometry.rotate((dx, dy), math.radians(self.theta))

        return self.x + dx, self.y + dy

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        canvas.ellipse(self.x, self.y, self.r1, self.r2,
                       theta=self.theta,
                       color=sty.fill_color,
                       strokecolor=sty.get_color(),
                       strokewidth=sty.stroke_width,
                       stroke=sty.stroke,
                       dataview=databox,
                       zorder=self._zorder,
                       attributes=self.svg)


class Circle(Shape):
    ''' Draw a circle

        Args:
            x: Center x coordinate
            y: Center y coordinate
            radius: Radius of circle
    '''
    # Drawn as ellipse because aspect may not always be square
    def __init__(self, center: PointType, radius: float):
        super().__init__()
        self.radius = radius
        self.center = center

    @property
    def x(self) -> float:
        ''' Center X value '''
        return self.center[0]

    @property
    def y(self) -> float:
        ''' Center Y value '''
        return self.center[1]

    def __getitem__(self, idx):
        return (self.x, self.y, self.radius)[idx]

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y, self.radius))

    def xy(self, theta: float) -> PointType:
        ''' Get x, y coordinate on the circle at the angle theta (degrees) '''
        return self._xy(math.radians(theta))

    def _xy(self, theta: float) -> PointType:
        ''' Get x, y coordinate on the circle at the angle theta (radians) '''
        x = self.x + self.radius * math.cos(theta)
        y = self.y + self.radius * math.sin(theta)
        return x, y

    def datarange(self) -> DataRange:
        ''' Data limits '''
        return DataRange(self.x-self.radius,
                         self.x+self.radius,
                         self.y-self.radius,
                         self.y+self.radius)

    def on_arc_point(self, p: PointType) -> bool:
        ''' Is the angle theta (in degrees) on the circle '''
        return True

    def tangent(self, p: PointType, which: str = 'top') -> Line:
        ''' Create a tangent line passing through p.

            Args:
                p: Point the tangent passees through, on or outside the circle
                which: Determines which of the two possible tangents to return.
                    may be `top`, `bottom`, `left`, or `right` based on the
                    position ot the tangent point on the circle.
        '''
        tangents = geometry.circle.tangent(self, p)  # ((x,y), slope) list
        tandict = dict(tangents)
        tanpoints = [t[0] for t in tangents]
        t = geometry.select_which(tanpoints, which)
        return Line(t, tandict[t])

    def tangent_at(self, theta: float) -> Line:
        ''' Create a tangent line at the angle theta '''
        angle = geometry.circle.tangent_angle(math.radians(theta))
        slope = math.tan(angle)
        xy = self.xy(theta)
        return Line(xy, slope)

    def normal(self, p: PointType) -> Line:
        ''' Create normal line from circle to point '''
        return Line.from_points(p, self.center)

    def normal_at(self, angle: float) -> Line:
        xy = self.xy(angle)
        return Line.from_points(xy, self.center)

    def diameter_segment(self, angle: float = 0) -> Segment:
        ''' Create a new Segment through a diameter at the angle (degrees) '''
        angle = math.radians(angle)
        p1 = self._xy(angle)
        p2 = self._xy(angle + math.pi)
        return Segment(p1, p2)

    def diameter_line(self, angle: float = 0) -> Line:
        ''' Create a new Line through a diameter at the angle (degrees) '''
        angle = math.radians(angle)
        p1 = self._xy(angle)
        p2 = self._xy(angle + math.pi)
        return Line.from_points(p1, p2)

    def radius_segment(self, angle: float = 0) -> Segment:
        ''' Create a new Segment through a radius at the angle (degrees) '''
        angle = math.radians(angle)
        p1 = self._xy(angle)
        return Segment(self.center, p1)

    def secant(self, angle1: float = 0, angle2: float = 180) -> Line:
        ''' Create a secant on the circle through the two angles (degrees) '''
        angle1 = math.radians(angle1)
        angle2 = math.radians(angle2)
        p1 = self._xy(angle1)
        p2 = self._xy(angle2)
        return Line.from_points(p1, p2)

    def chord(self, angle1: float = 0, angle2: float = 180) -> Segment:
        ''' Create a chord on the circle connecting the two angles (degrees) '''
        angle1 = math.radians(angle1)
        angle2 = math.radians(angle2)
        p1 = self._xy(angle1)
        p2 = self._xy(angle2)
        return Segment(p1, p2)

    def sagitta(self, angle1: float = 0, angle2: float = 180) -> Segment:
        ''' Create a sagitta segment (perpendicular to the chord) on a circle
            defined by the chord with endpoints at angle1 and angle2.
        '''
        angle1 = math.radians(angle1)
        angle2 = math.radians(angle2)
        theta = (angle1 + angle2) / 2
        xy = self._xy(theta)  # Point on the circumference

        chord_xy = self._xy(angle1)
        chord_xy2 = self._xy(angle2)
        xy2 = (chord_xy[0] + chord_xy2[0])/2, (chord_xy[1] + chord_xy2[1])/2
        return Segment(xy, xy2)

    @classmethod
    def from_ppp(cls, p1: PointType, p2: PointType, p3: PointType) -> 'Circle':
        ''' Create a circle passing through the three given points '''
        c1 = complex(p1[0], p1[1])
        c2 = complex(p2[0], p2[1])
        c3 = complex(p3[0], p3[1])
        w = (c3-c1)/(c2-c1)
        if abs(w.imag) <= 0:
            raise ValueError('Points are colinear')
        c = (c2-c1)*(w-abs(w)**2)/(2j*w.imag) + c1
        r = abs(c1 - c)
        return cls((c.real, c.imag), r)

    @classmethod
    def from_lll(cls, line1: 'Line', line2: 'Line', line3: 'Line', which: str = 'top') -> 'Circle':
        ''' Create a circle tangent to all three lines.

            The `which` paremeter specifies which of the 4 possible solutions
            to return, based on its center point. Options:

                - top: return the circle with the top-most center
                - bottom: return the circle with the bottom-most center
                - left: return the circle with the left-most center
                - right: return the circle with the right-most center
                - y0, y1, y2, y3: sort the circles by y value and return the Nth
                - x0, x1, x2, x3: sort the circles by x value and return the Nth
        '''
        bisect12a, bisect12b = geometry.line.bisect(line1, line2)
        bisect13a, bisect13b = geometry.line.bisect(line1, line3)
        bisect23a, bisect23b = geometry.line.bisect(line2, line3)

        intersections = geometry.unique_points([
            geometry.intersect.lines(bisect12a, bisect13a),
            geometry.intersect.lines(bisect12a, bisect23a),
            geometry.intersect.lines(bisect13a, bisect23a),
            geometry.intersect.lines(bisect12b, bisect13b),
            geometry.intersect.lines(bisect12b, bisect23b),
            geometry.intersect.lines(bisect13b, bisect23b),
            geometry.intersect.lines(bisect12a, bisect13b),
            geometry.intersect.lines(bisect12a, bisect23b),
            geometry.intersect.lines(bisect13a, bisect23b),
            geometry.intersect.lines(bisect12b, bisect13a),
            geometry.intersect.lines(bisect12b, bisect23a),
            geometry.intersect.lines(bisect13b, bisect23a),
        ])
        center = geometry.select_which(intersections, which)
        radius = geometry.line.normal_distance(line1, center)
        return Circle(center, radius)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        canvas.ellipse(self.x, self.y, self.radius, self.radius,
                       color=sty.fill_color,
                       strokecolor=sty.get_color(),
                       strokewidth=sty.stroke_width,
                       stroke=sty.stroke,
                       dataview=databox,
                       zorder=self._zorder,
                       attributes=self.svg)


class Rectangle(Shape):
    ''' Draw a rectangle

        Args:
            x: lower left x value
            y: lower left y value
            width: width of rectangle
            height: height of rectangle
            cornerradius: radius of corners
    '''
    def __init__(self, x: float, y: float,
                 width: float, height: float,
                 cornerradius: float = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cornerradius = cornerradius

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        canvas.rect(self.x, self.y, self.width, self.height,
                    fill=sty.fill_color,
                    strokecolor=sty.get_color(),
                    strokewidth=sty.stroke_width,
                    stroke=sty.stroke,
                    rcorner=self.cornerradius,
                    dataview=databox,
                    zorder=self._zorder,
                    attributes=self.svg)


class Arc(Circle):
    ''' Draw a circular arc

        Args:
            x: Center x coordinate
            y: Center y coordinate
            radius: Radius of arc
            theta1: Start angle (degrees)
            theta2: End angle (degrees)
    '''
    def __init__(self, center: PointType,
                 radius: float, theta1: float, theta2: float = 0):
        super().__init__(center, radius)
        self.theta1 = theta1
        self.theta2 = theta2
        self.theta1_rad = math.radians(self.theta1)
        self.theta2_rad = math.radians(self.theta2)
        self.arc_length_rad = geometry.angle_diff(self.theta1_rad, self.theta2_rad)

    def __getitem__(self, idx):
        return (self.x, self.y, self.radius, self.theta1_rad, self.theta2_rad)[idx]

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y, self.radius, self.theta1_rad, self.theta2_rad))

    def on_arc(self, theta: float) -> bool:
        ''' Determine whether angle theta (degrees) falls within the arc '''
        theta = math.radians(theta)
        delta = geometry.angle_diff(self.theta1_rad, theta)
        return delta <= self.arc_length_rad

    def on_arc_point(self, p: PointType) -> bool:
        ''' Determine whether angle of point falls on the arc '''
        theta = math.degrees(math.atan2(p[1]-self.y, p[0]-self.x))
        return self.on_arc(theta)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        canvas.arc(self.x, self.y, self.radius,
                   theta1=self.theta1, theta2=self.theta2,
                   strokecolor=sty.get_color(),
                   strokewidth=sty.stroke_width,
                   stroke=sty.stroke,
                   dataview=databox,
                   zorder=self._zorder,
                   attributes=self.svg)


class CompassArc(Arc):
    def __init__(self, center: PointType,
                 radius: float, theta: float,
                 thetawidth: float):
        super().__init__(
            center,
            radius,
            theta,
            theta+thetawidth)
