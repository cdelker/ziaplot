''' Geometry calculations '''
from __future__ import annotations
from collections import namedtuple
from typing import Sequence, Callable, Tuple
import math


PointType = Tuple[float, float]        # (x, y)
LineType = Tuple[float, float, float]  # (a, b, c), where ax + by + c = 0
CircleType = Tuple[PointType, float]   # (center, radius)
EllipseType = Tuple[PointType, float, float, float]   # (center, radius1, radius2, rotation)
ArcType = Tuple[PointType, float, float, float]   # (center, radius, theta1, theta2)
FunctionType = Callable
BezierQuadType = Tuple[PointType, PointType, PointType]
BezierCubicType = Tuple[PointType, PointType, PointType, PointType]


def distance(p1: PointType, p2: PointType) -> float:
    ''' Distance between two points '''
    return math.sqrt((p1[0]- p2[0])**2 + (p1[1] - p2[1])**2)


def midpoint(p1: PointType, p2: PointType) -> PointType:
    ''' Midpoint between two points '''
    x = (p1[0] + p2[0])/2
    y = (p1[1] + p2[1])/2
    return (x, y)


def point_slope(p1: PointType, p2: PointType) -> float:
    ''' Calculate slope between two points '''
    return (p2[1] - p1[1]) / (p2[0] - p1[0])


def isclose(p1: PointType, p2: PointType) -> bool:
    ''' Determine if the points are identical (x and y within math.isclose) '''
    return math.isclose(p1[0], p2[0]) and math.isclose(p1[1], p2[1])


def unique_points(points: list[PointType]) -> list[PointType]:
    ''' Remove duplicate (isclose) points from the lits '''
    unique = []
    for item in points:
        if not any([isclose(item, x) for x in unique]):
            unique.append(item)
    return unique


def translate(point: PointType, delta: PointType) -> PointType:
    ''' Translate the point by delta '''
    return point[0]+delta[0], point[1]+delta[1]


def rotate(point: PointType, theta: float) -> PointType:
    ''' Rotate the point theta radians about the origin '''
    cth = math.cos(theta)
    sth = math.sin(theta)
    x = point[0] * cth - point[1] * sth
    y = point[0] * sth + point[1] * cth
    return x, y


def reflect(point: PointType, line: LineType) -> PointType:
    ''' Reflect the point over the line '''
    a, b, c = line
    x, y = point
    k = -2*(a*x + b*y - c)/(a**2 + b**2)
    return k*a + x, k*b + y


def image(point: PointType, line: LineType) -> PointType:
    ''' Create a new point imaged onto the line (point on line at
        shortest distance to point)
    '''
    a, b, c = line
    x, y = point
    k = -(a*x + b*y - c)/(a**2 + b**2)
    return k*a + x, k*b + y



def angle_diff(theta1: float, theta2: float):
    ''' Get angular difference between theta2 and theta1 (radians) '''
    delta = math.atan2(math.sin(theta2-theta1), math.cos(theta2-theta1))
    if delta < 0:
        delta = delta + math.tau
    return delta


def angle_isbetween(angle: float, theta1: float, theta2: float) -> bool:
    ''' Is angle between theta1 and theta2 counterclockwise? '''
    delta = angle_diff(theta1, angle)
    length = angle_diff(theta1, theta2)
    return delta <= length


def angle_mean(theta1: float, theta2: float) -> float:
    ''' Circular mean over 0 to 2pi (theta in radians) '''
    sine = math.sin(theta1) + math.sin(theta2)
    cosine = math.cos(theta1) + math.cos(theta2)
    mean = math.atan2(sine, cosine)
    return (mean + math.tau) % math.tau
