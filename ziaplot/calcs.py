''' Calculations for finding intersections, maxima, minima, etc. '''
import math

from .geo.line import Line
from .geo.function import Function
from .style import PointType
from .util import root, maximum, minimum


def line_intersection(line1: Line, line2: Line) -> PointType:
    ''' Find intersection between two lines. Raises
        ValueError if the lines do not intersect.
    '''
    a1, b1, c1 = line1.homogeneous
    a2, b2, c2 = line2.homogeneous
    d = a1*b2 - b1*a2
    dx = c1*b2 - b1*c2
    dy = a1*c2 - c1*a2
    if d == 0:
        raise ValueError('No intersection')
    return dx/d, dy/d


def angle_of_intersection(line1: Line, line2: Line) -> float:
    ''' Find angle between the two lines in degrees '''
    m1, m2 = line1.slope, line2.slope
    theta = abs(math.atan(m1) - math.atan(m2)) % math.tau
    return math.degrees(theta)


def y_intercept(line: Line) -> PointType:
    ''' Get XY point of line's y-intercept '''
    return (0, line.intercept)


def x_intercept(line: Line) -> PointType:
    ''' Get XY point of line's x-intercept '''
    return (-line.intercept/line.slope, 0)


def func_intersection(f1: Function, f2: Function,
                      x1: float, x2: float) -> PointType:
    ''' Find intersection between two Functions (either of
        which may be a Line) in the interval x1 to x2.
        Raises ValueError if the curves do not intersect.
    '''
    tol = abs(x2-x1) * 1E-4
    try:
        x = root(lambda x: f1.func(x) - f2.func(x),
                 a=x1, b=x2, tol=tol)
    except (ValueError, RecursionError) as exc:
        raise ValueError('No intersection found')

    y = f1.y(x)
    return x, y


def local_max(f: Function, x1: float, x2: float) -> PointType:
    ''' Find local maximum of function f between x1 and x2 '''
    x = maximum(f.func, x1, x2)
    y = f.y(x)
    return x, y


def local_min(f: Function, x1: float, x2: float) -> PointType:
    ''' Find local minimum of function f between x1 and x2 '''
    x = minimum(f.func, x1, x2)
    y = f.y(x)
    return x, y
