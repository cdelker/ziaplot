''' Tangent and Normal lines '''
import math

from ..shapes import Circle, Ellipse
from .line import Segment, Line
from .function import Function
from .bezier import BezierQuad


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

    @classmethod
    def to_bezier(cls, b: BezierQuad, t: float) -> Line:
        ''' Create a linle tangent to Bezier at parameter t '''
        assert 0 <= t <= 1
        slope = b._tangent_slope(t)
        xy = b.xy(t)
        return Line(xy, slope)


class TangentSegment:
    ''' Create Segment tangent to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float,
           d1: float = 1, d2: float = 1) -> Segment:
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
                  d1: float = 1, d2: float = 1) -> Segment:
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

    @classmethod
    def to_bezier(cls, b: BezierQuad, t: float,
                  d1: float = 1, d2: float = 1) -> Segment:
        ''' Create a linle tangent to Bezier at parameter t
            extending d1 to the left and d2 to the right.
        '''
        assert 0 <= t <= 1
        slope = b._tangent_slope(t)
        theta = math.atan(slope)
        x, y = b.xy(t)
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

    @classmethod
    def to_bezier(cls, b: BezierQuad, t: float) -> Line:
        ''' Create a linle normal to Bezier at parameter t '''
        assert 0 <= t <= 1
        slope = -1 / b._tangent_slope(t)
        xy = b.xy(t)
        return Line(xy, slope)



class NormalSegment:
    ''' Create Segment normal to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float,
           d1: float = 1, d2: float = 1) -> Segment:
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
                  d1: float = 1, d2: float = 1) -> Segment:
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

    @classmethod
    def to_bezier(cls, b: BezierQuad, t: float,
                  d1: float = 1, d2: float = 1) -> Segment:
        ''' Create a linle tangent to Bezier at parameter t
            extending d1 to the left and d2 to the right.
        '''
        assert 0 <= t <= 1
        slope = -1 / b._tangent_slope(t)
        theta = math.atan(slope)
        x, y = b.xy(t)
        x1 = x - d1 * math.cos(theta)
        x2 = x + d2 * math.cos(theta)
        y1 = y - d1 * math.sin(theta)
        y2 = y + d2 * math.sin(theta)
        return Segment((x1, y1), (x2, y2))


class Diameter(Segment):
    ''' Create Diameter Segment on a Circle or Ellipse
        at an angle of theta (degrees).
    '''
    def __init__(self, circle: Ellipse, theta: float = 0):
        theta = math.radians(theta)
        xy = circle._xy(theta)
        xy2 = circle._xy(theta + math.pi)
        super().__init__(xy, xy2)


class Radius(Segment):
    ''' Create Radius Segment on a Circle or Ellipse
        at an angle of theta (degrees).
    '''
    def __init__(self, circle: Ellipse, theta: float = 0):
        theta = math.radians(theta)
        xy = circle._xy(theta)
        super().__init__((circle.x, circle.y), xy)


class Secant(Line):
    ''' Create Secant Line on a Circle or Ellipse.
        between points on the circle with angles
        of theta1 and theta2 (degrees).

        See also: Chord 
    '''
    def __init__(self, circle: Ellipse, theta1: float = 0, theta2: float = 180):
        theta1 = math.radians(theta1)
        theta2 = math.radians(theta2)
        xy = circle._xy(theta1)
        xy2 = circle._xy(theta2)
        slope = (xy2[1] - xy[1]) / (xy2[0] - xy[0])
        super().__init__(xy, slope)

    @classmethod
    def to_function(cls, f: Function, x1: float, x2: float) -> 'Line':
        ''' Create a secant line on the function f '''
        xy = x1, f.y(x1)
        xy2 = x2, f.y(x2)
        slope = (xy2[1] - xy[1]) / (xy2[0] - xy[0])
        return Line(xy, slope)

    @classmethod
    def to_bezier(cls, b: BezierQuad, t1: float, t2: float) -> 'Line':
        ''' Create a secant line on the function f '''
        xy = b.xy(t1)
        xy2 = b.xy(t2)
        slope = (xy2[1] - xy[1]) / (xy2[0] - xy[0])
        return Line(xy, slope)



class Chord(Segment):
    ''' Create Chord Segment on a Circle or Ellipse.
        between points on the circle with angles
        of theta1 and theta2 (degrees).

        See also: Secant 
    '''
    def __init__(self, circle: Ellipse, theta1: float = 0, theta2: float = 180):
        theta1 = math.radians(theta1)
        theta2 = math.radians(theta2)
        xy = circle._xy(theta1)
        xy2 = circle._xy(theta2)
        super().__init__(xy, xy2)

    @classmethod
    def to_function(cls, f: Function, x1: float, x2: float) -> Segment:
        ''' Create a Chord Segment on the function f '''
        xy = x1, f.y(x1)
        xy2 = x2, f.y(x2)
        return Segment(xy, xy2)

    @classmethod
    def to_bezier(cls, b: BezierQuad, t1: float, t2: float) -> Segment:
        ''' Create a secant line on the function f '''
        xy = b.xy(t1)
        xy2 = b.xy(t2)
        return Segment(xy, xy2)


class Sagitta(Segment):
    ''' Create Sagitta Segment (perpendicular to a chord) on a Circle or Ellipse,
        defined by a chord between points on the circle with angles
        of theta1 and theta2 (degrees).
    '''
    def __init__(self, circle: Ellipse, theta1: float = 0, theta2: float = 180):
        theta1 = math.radians(theta1)
        theta2 = math.radians(theta2)
        theta = (theta1 + theta2) / 2
        xy = circle._xy(theta)  # Point on the circumference

        chord_xy = circle._xy(theta1)
        chord_xy2 = circle._xy(theta2)
        xy2 = (chord_xy[0] + chord_xy2[0])/2, (chord_xy[1] + chord_xy2[1])/2
        super().__init__(xy, xy2)

