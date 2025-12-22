''' Bezier Curve calculations '''
from __future__ import annotations
from typing import TYPE_CHECKING
import math
import bisect
from itertools import accumulate

from .. import util
from .geometry import PointType, BezierType, distance

if TYPE_CHECKING:
    from ..figures.bezier import Bezier


def quadratic_xy(b: BezierType|'Bezier', t: float) -> PointType:
    ''' Point on Quadratic Bezier at parameter t '''
    (p1x, p1y), (p2x, p2y), (p3x, p3y), *_ = b
    x = p2x + (1-t)**2 * (p1x - p2x) + t**2 * (p3x - p2x)
    y = p2y + (1-t)**2 * (p1y - p2y) + t**2 * (p3y - p2y)
    return x, y


def quadratic_tangent_slope(b: BezierType|'Bezier', t: float) -> float:
    ''' Slope of tanget at parameter t '''
    (p1x, p1y), (p2x, p2y), (p3x, p3y), *_ = b
    bprime_x = 2*(1-t) * (p2x - p1x) + 2*t*(p3x - p2x)
    bprime_y = 2*(1-t) * (p2y - p1y) + 2*t*(p3y - p2y)
    return bprime_y / bprime_x


def quadtratic_tangent_angle(b: BezierType|'Bezier', t: float) -> float:
    ''' Get angle of tangent at parameter t (radians) '''
    (p1x, p1y), (p2x, p2y), (p3x, p3y), *_ = b
    bprime_x = 2*(1-t) * (p2x - p1x) + 2*t*(p3x - p2x)
    bprime_y = 2*(1-t) * (p2y - p1y) + 2*t*(p3y - p2y)
    return math.atan2(bprime_y, bprime_x)


def cubic_xy(b: BezierType|'Bezier', t: float) -> PointType:
    ''' Point on cubic Bezier at parameter t '''
    (p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y) = b
    x = (p1x*(1-t)**3 + p2x*3*t*(1-t)**2 + p3x*3*(1-t)*t**2 + p4x*t**3)
    y = (p1y*(1-t)**3 + p2y*3*t*(1-t)**2 + p3y*3*(1-t)*t**2 + p4y*t**3)
    return (x, y)


def cubic_tangent_slope(b: BezierType|'Bezier', t: float) -> float:
    ''' Slope of tanget at parameter t '''
    (p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y) = b
    bprime_x = 3*(1-t)**2 * (p2x-p1x) + 6*(1-t)*t*(p3x-p2x) + 3*t**2*(p4x-p3x)
    bprime_y = 3*(1-t)**2 * (p2y-p1y) + 6*(1-t)*t*(p3y-p2y) + 3*t**2*(p4y-p3y)
    return bprime_y / bprime_x


def cubic_tangent_angle(b: BezierType|'Bezier', t: float) -> float:
    ''' Get angle of tangent at parameter t (radians) '''
    (p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y) = b
    bprime_x = 3*(1-t)**2 * (p2x-p1x) + 6*(1-t)*t*(p3x-p2x) + 3*t**2*(p4x-p3x)
    bprime_y = 3*(1-t)**2 * (p2y-p1y) + 6*(1-t)*t*(p3y-p2y) + 3*t**2*(p4y-p3y)
    return math.atan2(bprime_y, bprime_x)


def xy(b: BezierType | 'Bezier', t: float) -> PointType:
    ''' Point on a Bezier curve at parameter t '''
    if len(b) == 3:
        return quadratic_xy(b, t)  # type: ignore
    return cubic_xy(b, t)


def tangent_slope(b: BezierType | 'Bezier', t: float) -> float:
    if len(b) == 3:
        return quadratic_tangent_slope(b, t)  # type: ignore
    return cubic_tangent_slope(b, t)


def tangent_angle(b: BezierType | 'Bezier', t: float) -> float:
    if len(b) == 3:
        return quadtratic_tangent_angle(b, t)
    return cubic_tangent_angle(b, t)


def length(b: BezierType|'Bezier', n: int = 50) -> float:
    ''' Compute approximate length of Bezier curve (Quadtratic or Cubic)

        Args:
            n: Number of points used for piecewise approximation of curve
    '''
    t = util.linspace(0, 1, num=n)

    p = [xy(b, tt) for tt in t]
    dists = [distance(p[i], p[i+1]) for i in range(n-1)]
    return sum(dists)


def equal_spaced_t(
        b: BezierType|'Bezier',
        nsegments: int = 2,
        n: int = 100) -> list[float]:
    ''' Find t values that approximately split the curve into
        equal-length segments.

        Args:
            b: The curve to split
            nsegments: Number of segments to split curve into
            n: Number of points used to approximate curve
    '''
    t = util.linspace(0, 1, num=n)
    p = [xy(b, tt) for tt in t]
    dists = [distance(p[i], p[i+1]) for i in range(n-1)]
    length = sum(dists)
    delta = length / nsegments
    seg_points = [delta*i for i in range(nsegments+1)]
    cumsum = list(accumulate(dists))
    t_points = [bisect.bisect_left(cumsum, seg_points[i]) for i in range(1, nsegments)]
    return [t[0]] + [t[tp] for tp in t_points] + [t[n-1]]


def equal_spaced_points(
        b: BezierType|'Bezier',
        nsegments: int = 2,
        n: int = 100) -> list[PointType]:
    ''' Find (x, y) points spaced equally along a Bezier curve

        Args:
            bezier: The curve to split
            nsegments: Number of segments to split curve into
            n: Number of points used to approximate curve
    '''
    t = equal_spaced_t(b, nsegments, n)
    return [xy(b, tt) for tt in t]
