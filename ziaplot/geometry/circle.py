''' Calculations on circles '''
from typing import Optional
import math

from .geometry import PointType, LineType, CircleType, isclose
from . import line as _line


def point(circle: CircleType, theta: float) -> PointType:
    ''' Coordinates of point on circle at angle theta (rad) '''
    (centerx, centery), radius, *_ = circle
    x = centerx + radius * math.cos(theta)
    y = centery + radius * math.sin(theta)
    return (x, y)


def tangent_angle(theta: float) -> float:
    ''' Angle of tangent to circle at given theta around circle '''
    return (theta + math.pi/2 + math.tau) % math.tau


def tangent_at(circle: CircleType, theta: float) -> LineType:
    ''' Find tanget to circle at given theta '''
    x, y = point(circle, theta)
    phi = tangent_angle(theta)
    slope = math.tan(phi)
    intercept = -slope*x+y
    return _line.new(slope, intercept)


def tangent_points(circle: CircleType, p: PointType) -> tuple[PointType, PointType]:
    ''' Find the two points on the circle that form a tangent line through
        the given point
    '''
    (centerx, centery), radius = circle
    px, py = p

    px = px - centerx
    py = py - centery
    rsq = radius**2
    dsq = px**2 + py**2

    try:
        x1 = centerx + rsq/dsq*px + radius/dsq*math.sqrt(dsq - rsq) * (-py)
        y1 = centery + rsq/dsq*py + radius/dsq*math.sqrt(dsq - rsq) * px
        x2 = centerx + rsq/dsq*px - radius/dsq*math.sqrt(dsq - rsq) * (-py)
        y2 = centery + rsq/dsq*py - radius/dsq*math.sqrt(dsq - rsq) * px
    except ZeroDivisionError as exc:
        raise ValueError('Point is in circle. No tangent.') from exc
    return (x1, y1), (x2, y2)


def tangent(circle: CircleType, p: PointType) -> tuple[tuple[PointType, float], tuple[PointType, float]]:
    ''' Find tangent points and slope of the two tangents to the circle through the point p '''
    (centerx, centery), radius = circle
    p1, p2 = tangent_points(circle, p)

    if isclose(p1, p):
        theta = math.atan2(p[1]-centery, p[0]-centerx)
        m1 = math.tan(tangent_angle(theta))
        return (p, m1), (p, m1)

    try:
        m1 = (p1[1] - p[1]) / (p1[0] - p[0])
    except ZeroDivisionError:
        m1 = math.inf

    try:
        m2 = (p2[1] - p[1]) / (p2[0] - p[0])
    except ZeroDivisionError:
        m2 = math.inf

    return (p1, m1), (p2, m2)
