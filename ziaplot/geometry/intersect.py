''' Methods for finding intersections between lines, circles, functions, etc. '''
from __future__ import annotations
from typing import TYPE_CHECKING
import math

from ..util import root
from .geometry import (
    PointType,
    LineType,
    CircleType,
    ArcType,
    FunctionType,
    distance,
    angle_isbetween
    )
from . import line as _line

if TYPE_CHECKING:
    from ..figures.line import Line
    from ..figures.shapes import Circle, Arc


def lines(line1: LineType|'Line', line2: LineType|'Line') -> PointType:
    ''' Find point of intersection of two lines '''
    a1, b1, c1 = line1
    a2, b2, c2 = line2
    d = a1*b2 - b1*a2
    dx = c1*b2 - b1*c2
    dy = a1*c2 - c1*a2
    if d == 0:
        raise ValueError('No intersection')
    return (dx/d, dy/d)


def line_angle(line1: LineType|'Line', line2: LineType|'Line') -> float:
    ''' Find angle (rad) of intersection between the two lines '''
    m1 = _line.slope(line1)
    m2 = _line.slope(line2)
    theta = abs(math.atan(m1) - math.atan(m2)) % math.tau
    return theta


def line_circle(line: LineType|'Line', circle: CircleType|'Circle') -> tuple[PointType, PointType]:
    ''' Find intersections between line and circle '''
    slope = _line.slope(line)
    centerx, centery, radius, *_ = circle

    if not math.isfinite(slope):
        xint = _line.xvalue(line, 0)
        A = 1.0
        B = -2*centery
        C = centerx**2 + centery**2 - radius**2 - 2*xint*centerx + xint**2
        try:
            d = math.sqrt(B**2 - 4*A*C)
        except ValueError as exc:
            if B**2 - 4*A*C < 1E-14:
                d = 0  # Close enough - point is tangent
            else:
                raise ValueError('No intersection') from exc
        y1 = (-B+d) / (2*A)
        y2 = (-B-d) / (2*A)
        x1 = _line.xvalue(line, y1)
        x2 = _line.xvalue(line, y2)

    else:
        intercept = _line.intercept(line)  # Any point on the line
        A = slope**2 + 1
        B = 2*(slope*intercept - slope*centery - centerx)
        C = (centery**2 - radius**2 + centerx**2 - 2*intercept*centery + intercept**2)
        try:
            d = math.sqrt(B**2 - 4*A*C)
        except ValueError as exc:
            if B**2 - 4*A*C < 1E-14:
                d = 0  # Close enough - point is tangent
            else:
                raise ValueError('No intersection') from exc

        x1 = (-B + d) / (2*A)
        x2 = (-B - d) / (2*A)
        y1 = _line.yvalue(line, x1)
        y2 = _line.yvalue(line, x2)

    return (x1, y1), (x2, y2)


def circles(circle1: CircleType|ArcType|'Circle',
            circle2: CircleType|ArcType|'Circle') -> tuple[PointType, PointType]:
    ''' Get points of intersection between two circles '''
    x1, y1, r1, *_ = circle1
    x2, y2, r2, *_ = circle2
    dx, dy = x2 - x1, y2 - y1
    dist = distance((x1, y1), (x2, y2))

    if dist > r1 + r2 or dist < abs(r1 - r2):
        # No intersections
        return (math.nan, math.nan), (math.nan, math.nan)
    elif dist == 0 and r1 == r2:
        # Identical circles (infinite intersections)
        return (math.nan, math.nan), (math.nan, math.nan)

    a = (r1*r1 - r2*r2 + dist*dist) / (2*dist)
    h = math.sqrt(r1*r1 - a*a)
    xm = x1 + a*dx/dist
    ym = y1 + a*dy/dist
    xs1 = xm + h*dy/dist
    xs2 = xm - h*dy/dist
    ys1 = ym - h*dx/dist
    ys2 = ym + h*dx/dist

    if len(tuple(circle1)) > 4:
        # circle1 is arc, ensure points fall on the arc
        atheta1, atheta2 = circle1[3], circle1[4]  # type: ignore
        thetap1 = math.atan2(ys1-y1, xs1-x1)
        thetap2 = math.atan2(ys2-y1, xs2-x1)
        if not angle_isbetween(thetap1, atheta1, atheta2):
            xs1, ys1 = math.nan, math.nan
        if not angle_isbetween(thetap2, atheta1, atheta2):
            xs2, ys2 = math.nan, math.nan

    if len(tuple(circle2)) > 4:
        # circle2 is arc, ensure points fall on the arc
        atheta1, atheta2 = circle2[3], circle2[4]  # type: ignore
        thetap1 = math.atan2(ys1-y2, xs1-x2)
        thetap2 = math.atan2(ys2-y2, xs2-x2)
        if not angle_isbetween(thetap1, atheta1, atheta2):
            xs1, ys1 = math.nan, math.nan
        if not angle_isbetween(thetap2, atheta1, atheta2):
            xs2, ys2 = math.nan, math.nan

    if not math.isfinite(xs1) and math.isfinite(xs2):
        (xs1, ys1), (xs2, ys2) = (xs2, ys2), (xs1, ys1)

    return (xs1, ys1), (xs2, ys2)


def line_arc(line: LineType|'Line', arc: ArcType|'Arc'):
    ''' Find intersection of line and arc. Same as circle, but ensures point falls on the arc '''
    centerx, centery, radius, atheta1, atheta2 = arc
    p1, p2 = line_circle(line, (centerx, centery, radius))

    theta1 = math.atan2(p1[1]-centery, p1[0]-centerx)
    theta2 = math.atan2(p2[1]-centery, p2[0]-centerx)

    if not angle_isbetween(theta1, atheta1, atheta2):
        p1 = (math.nan, math.nan)
    if not angle_isbetween(theta2, atheta1, atheta2):
        p2 = (math.nan, math.nan)

    if not math.isfinite(p1[0]) and math.isfinite(p2[0]):
        p1, p2 = p2, p1

    return p1, p2


def functions(f1: FunctionType, f2: FunctionType,
              x1: float, x2: float) -> PointType:
    ''' Find intersection between two Functions in the
        interval x1 to x2.
        Raises ValueError if the curves do not intersect.
    '''
    tol = abs(x2-x1) * 1E-4
    try:
        x = root(lambda x: f1(x) - f2(x),
                 a=x1, b=x2, tol=tol)
    except (ValueError, RecursionError) as exc:
        raise ValueError('No intersection found') from exc

    y = f1(x)
    return x, y
