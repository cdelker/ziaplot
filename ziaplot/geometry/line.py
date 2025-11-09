''' Calculations on lines '''
from __future__ import annotations
import math
from typing import TYPE_CHECKING

from .geometry import LineType, PointType

if TYPE_CHECKING:
    from ..figures.line import Line
    from ..figures.point import Point


def new(slope: float, intercept: float) -> LineType:
    ''' Create a line from slope and intercept '''
    b = 1
    c = intercept
    a = -slope
    return a, b, c


def new_pointslope(point: PointType|'Point', slope: float) -> LineType:
    ''' Create a line from point and slope '''
    if math.isfinite(slope):
        intercept = -slope*point[0] + point[1]
        return new(slope, intercept)
    return (1, 0, point[0])  # Vertical line


def slope(line: LineType|'Line') -> float:
    ''' Get slope of the line '''
    a, b, c = line
    try:
        return -a / b
    except ZeroDivisionError:
        return math.inf


def intercept(line: LineType|'Line') -> float:
    ''' Get y-intercept of the line '''
    a, b, c = line
    try:
        return c / b
    except ZeroDivisionError:
        return math.inf


def xintercept(line: LineType|'Line') -> float:
    ''' Get x-intercept of the line '''
    a, b, c = line
    try:
        return c / a
    except ZeroDivisionError:
        return math.inf


def yvalue(line: LineType|'Line', x: float) -> float:
    ''' Get y value of the line at x '''
    a, b, c = line
    try:
        return (c - a*x) / b
    except ZeroDivisionError:
        return math.nan  # Vertical Line


def xvalue(line: LineType|'Line', y: float) -> float:
    ''' Get x value of the line at y '''
    a, b, c = line
    try:
        return (c - b*y) / a
    except ZeroDivisionError:
        return math.nan  # Horizontal Line


def normal_distance(line: LineType|'Line', point: PointType|'Point') -> float:
    ''' Normal distance from point to line '''
    a, b, c = line
    x, y = point
    return abs(a*x + b*y - c) / math.sqrt(a**2 + b**2)


def normal(line: LineType|'Line', point: PointType|'Point') -> LineType:
    ''' Find the line normal to given line through point '''

    m = slope(line)
    try:
        normslope = -1 / m
    except ZeroDivisionError:
        normslope = math.inf
    return new_pointslope(point, normslope)


def bisect(line1: LineType|'Line', line2: LineType|'Line') -> tuple[LineType, LineType]:
    ''' Find the two lines bisecting the given two lines '''
    a1, b1, c1 = line1
    a2, b2, c2 = line2

    def bisect(sign=1):
        A = a1 / math.sqrt(a1**2+b1**2) + sign * a2 / math.sqrt(a2**2 + b2**2)
        B = b1 / math.sqrt(a1**2+b1**2) + sign * b2 / math.sqrt(a2**2 + b2**2)
        C = c1 / math.sqrt(a1**2+b1**2) + sign * c2 / math.sqrt(a2**2 + b2**2)
        return A, B, C

    return bisect(sign=1), bisect(sign=-1)


def bisect_points(p1: PointType|'Point', p2: PointType|'Point') -> LineType:
    ''' Find the line bisecting the two points '''
    mid = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
    slope = (p2[1]-p1[1]) / (p2[0]-p1[0])
    try:
        m = -1/slope
    except ZeroDivisionError:
        m = math.inf
    return new_pointslope(mid, m)
