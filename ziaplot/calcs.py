''' Calculations for finding intersections, maxima, minima, etc. '''
from typing import Optional, TYPE_CHECKING
import math

from .util import root, maximum, minimum

if TYPE_CHECKING:
    from .geo.line import Line
    from .geo.function import Function
    from .shapes import Circle, Arc
    from .style import PointType


def line_intersection(line1: 'Line', line2: 'Line') -> 'PointType':
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


def angle_of_intersection(line1: 'Line', line2: 'Line') -> float:
    ''' Find angle between the two lines in degrees '''
    m1, m2 = line1.slope, line2.slope
    theta = abs(math.atan(m1) - math.atan(m2)) % math.tau
    return math.degrees(theta)


def y_intercept(line: 'Line') -> 'PointType':
    ''' Get XY point of line's y-intercept '''
    return (0, line.intercept)


def x_intercept(line: 'Line') -> 'PointType':
    ''' Get XY point of line's x-intercept '''
    return (-line.intercept/line.slope, 0)


def func_intersection(f1: 'Function', f2: 'Function',
                      x1: float, x2: float) -> 'PointType':
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


def _circle_intersection(c1: tuple[float, float],
                         c2: tuple[float, float],
                         r1: float,
                         r2: float) -> tuple['PointType', 'PointType']:
    x1, y1 = c1
    x2, y2 = c2
    dx, dy = x2-x1, y2-y1
    dist = math.sqrt(dx*dx + dy*dy)

    if dist > r1+r2 or dist < abs(r1-r2):
        # No intersections
        return (math.nan, math.nan), (math.nan, math.nan)
    elif dist == 0 and r1 == r2:
        # Identical circles (infinite intersections)
        return (math.nan, math.nan), (math.nan, math.nan)

    a = (r1*r1 - r2*r2 + dist*dist) / (2*dist)
    h = math.sqrt(r1*r1 - a*a)
    xm = c1[0] + a*dx/dist
    ym = c1[1] + a*dy/dist
    xs1 = xm + h*dy/dist
    xs2 = xm - h*dy/dist
    ys1 = ym - h*dx/dist
    ys2 = ym + h*dx/dist
    return (xs1, ys1), (xs2, ys2)


def circle_intersection(c1: 'Circle', c2: 'Circle') -> tuple['PointType', 'PointType']:
    ''' Find intersections of two circles

        Args:
            c1: first circle
            c2: second circle

        Returns:
            p1: First intersection (x, y)
            p2: Second intersection (x, y)
    '''
    p1 = c1.x, c1.y
    p2 = c2.x, c2.y
    r1, r2 = c1.radius, c2.radius

    # Ensure point is within Arc angle if c1 or c2 is an Arc
    p1, p2 = _circle_intersection(p1, p2, r1, r2)
    if hasattr(c1, 'on_arc'):
        if not c1.on_arc_point(p1):
            p1 = (math.nan, math.nan)
        if not c1.on_arc_point(p2):
            p2 = (math.nan, math.nan)
    if hasattr(c2, 'on_arc'):
        if not c2.on_arc_point(p1):
            p1 = (math.nan, math.nan)
        if not c2.on_arc_point(p2):
            p2 = (math.nan, math.nan)

    if not math.isfinite(p1[0]) and math.isfinite(p2[0]):
        p1, p2 = p2, p1

    return p1, p2


def line_circle_intersection(line: 'Line', circle: 'Circle|Arc') -> tuple['PointType', 'PointType']:
    ''' Find intersections between line and circle '''
    if not math.isfinite(line.slope):
        A = 1.0
        B = 2*circle.y
        C = circle.x**2 + circle.y**2 - circle.radius**2 + line.point[0]**2
        try:
            d = math.sqrt(B**2 - 4*A*C)
        except ValueError as exc:
            raise ValueError('No intersection') from exc
        y1 = (-B+d) / (2*A)
        y2 = (-B-d) / (2*A)
        x1 = line.x(y1)
        x2 = line.x(y2)

    else:
        A = line.slope**2 + 1
        B = 2*(line.slope*line.intercept - line.slope*circle.y - circle.x)
        C = (circle.y**2 - circle.radius**2 + circle.x**2 - 2*line.intercept*circle.y + line.intercept**2)
        try:
            d = math.sqrt(B**2 - 4*A*C)
        except ValueError as exc:
            raise ValueError('No intersection') from exc

        x1 = (-B + d) / (2*A)
        x2 = (-B - d) / (2*A)
        y1 = line.y(x1)
        y2 = line.y(x2)

    return (x1, y1), (x2, y2)


def line_arc_intersection(line: 'Line', arc: 'Arc') -> tuple['PointType', 'PointType']:
    ''' Find intersections between line and arc '''
    p1, p2 = line_circle_intersection(line, arc)

    theta1 = math.degrees(math.atan2(p1[1]-arc.y, p1[0]-arc.x))
    theta2 = math.degrees(math.atan2(p2[1]-arc.y, p2[0]-arc.x))

    if not arc.on_arc(theta1):
        p1 = (math.nan, math.nan)
    if not arc.on_arc(theta2):
        p2 = (math.nan, math.nan)

    if not math.isfinite(p1[0]) and math.isfinite(p2[0]):
        p1, p2 = p2, p1

    return p1, p2



def local_max(f: 'Function', x1: float, x2: float) -> 'PointType':
    ''' Find local maximum of function f between x1 and x2 '''
    x = maximum(f.func, x1, x2)
    y = f.y(x)
    return x, y


def local_min(f: 'Function', x1: float, x2: float) -> 'PointType':
    ''' Find local minimum of function f between x1 and x2 '''
    x = minimum(f.func, x1, x2)
    y = f.y(x)
    return x, y
