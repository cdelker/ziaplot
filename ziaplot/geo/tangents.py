''' Tangent and Normal lines '''
import math

from ..shapes import Circle, Ellipse
from .line import Segment, Line
from .function import Function


class Tangent:
    ''' Create Line tangent to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float) -> Line:
        ''' Create a Line tangent to f at x '''
        slope = f._tangent_slope(x)
        y = f.y(x)
        y = 0 if not math.isfinite(y) else y
        return Line((x, y), slope)

    @classmethod
    def to_circle(cls, circle: Circle, theta: float) -> Line:
        ''' Create a Line tangent to the circle at theta (degrees) '''
        theta = math.radians(theta)
        x, y = circle._xy(theta)
        phi = circle._tangent(theta)
        slope = math.tan(phi)
        return Line((x, y), slope)


class TangentSegment:
    ''' Create Segment tangent to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float,
           d1: float = 0, d2: float = 0) -> Line:
        ''' Create a Segment tangent to f at x,
            extending d1 to the left and d2 to the right.
        '''
        slope = f._tangent_slope(x)
        y = f.y(x)
        theta = math.atan(slope)
        x1 = x - d1 * math.cos(theta)
        x2 = x + d2 * math.cos(theta)
        y1 = y - d1 * math.sin(theta)
        y2 = y + d2 * math.sin(theta)
        return Segment((x1, y1), (x2, y2))

    @classmethod
    def to_circle(cls, circle: Ellipse, theta: float,
                  d1: float = 0, d2: float = 0) -> Line:
        ''' Create a Segment tangent to the circle/ellipse at theta (degrees)
            extending d1 to the left and d2 to the right.
        '''
        x, y = circle._xy(math.radians(theta))
        theta = circle._tangent(math.radians(theta))
        x1 = x - d1 * math.cos(theta)
        x2 = x + d2 * math.cos(theta)
        y1 = y - d1 * math.sin(theta)
        y2 = y + d2 * math.sin(theta)
        return Segment((x1, y1), (x2, y2))


class Normal:
    ''' Create Lines normal to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float) -> Line:
        ''' Create a Line tangent to f at x '''
        try:
            slope = -1 / f._tangent_slope(x)
        except ZeroDivisionError:
            slope = math.inf
        y = f.y(x)
        y = 0 if not math.isfinite(y) else y
        return Line((x, y), slope)

    @classmethod
    def to_circle(cls, circle: Ellipse, theta: float) -> Line:
        ''' Create a Line tangent to the circle/ellipse at theta '''
        theta = math.radians(theta)
        x, y = circle._xy(theta)
        phi = circle._tangent(math.radians(theta))
        slope = math.tan(phi)
        return Line((x, y), slope)


class NormalSegment:
    ''' Create Segment normal to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float,
           d1: float = 0, d2: float = 0) -> Line:
        ''' Create a Segment normal to f at x,
            extending d1 to the left and d2 to the right.
        '''
        y = f.y(x)
        try:
            slope = -1 / f._tangent_slope(x)
        except ZeroDivisionError:
            slope = math.inf
        theta = math.atan(slope)
        x1 = x - d1 * math.cos(theta)
        x2 = x + d2 * math.cos(theta)
        y1 = y - d1 * math.sin(theta)
        y2 = y + d2 * math.sin(theta)
        return Segment((x1, y1), (x2, y2))

    @classmethod
    def to_circle(cls, circle: Ellipse, theta: float,
                  d1: float = 0, d2: float = 0) -> Line:
        ''' Create a Segment normal to the circle/ellipse at theta
            extending d1 to the left and d2 to the right.
        '''
        x, y = circle._xy(math.radians(theta))
        theta = circle._tangent(math.radians(theta))# + math.pi/2
        theta -= math.pi/2
        x1 = x + d1 * math.cos(theta)
        x2 = x - d2 * math.cos(theta)
        y1 = y + d1 * math.sin(theta)
        y2 = y - d2 * math.sin(theta)
        return Segment((x1, y1), (x2, y2))
