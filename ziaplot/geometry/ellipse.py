''' Calculations on ellipses '''
import math

from .geometry import PointType, LineType, CircleType, EllipseType, distance, rotate, translate
from . import line as _line


def _dxy(ellipse: EllipseType, theta: float) -> PointType:
    ''' Get distance from center to point on ellipse at angle theta (rad) '''
    (centerx, centery), r1, r2, angle = ellipse
    e = math.sqrt(1 - (r2 / r1)**2)
    phi = math.atan(math.tan(angle) * r1 / r2)
    r = r1 * math.sqrt(1 - e**2 * math.sin(phi)**2)
    dx = r * math.cos(theta)
    dy = r * math.sin(theta)
    return (dx, dy)


def point(ellipse: EllipseType, theta: float) -> PointType:
    ''' Get point on ellipse at angle theta '''
    dx, dy = _dxy(ellipse, theta)
    (centerx, centery), r1, r2, etheta = ellipse
    if etheta:
        costh = math.cos(math.radians(etheta))
        sinth = math.sin(math.radians(etheta))
        dx, dy = dx * costh - dy * sinth, dx * sinth + dy * costh
    return (centerx + dx, centery + dy)


def tangent_points(ellipse: EllipseType, p: PointType) -> tuple[PointType, PointType]:
    ''' Find the two points on the Ellipse that form a tangent line through
        the given point
    '''
    (cx, cy), rx, ry, theta = ellipse
    px, py = p
    theta = math.radians(theta)

    # Shift to origin and rotate -theta
    px = px - cx
    py = py - cy
    if theta != 0:
        px, py = rotate((px, py), -theta)

    # Algebraic solution gives div/0 if px==rx
    if math.isclose(px, rx):
        m1 = math.inf
        m2 = (py-ry)*(py+ry)/(2*py*rx)
    else:
        m1 = (px*py - math.sqrt(px**2*ry**2 + py**2*rx**2 - rx**2*ry**2))/(px**2-rx**2)
        m2 = (px*py + math.sqrt(px**2*ry**2 + py**2*rx**2 - rx**2*ry**2))/(px**2-rx**2)

    # Tangent lines, untranslated
    tline1 = _line.new_pointslope((px, py), m1)
    tline2 = _line.new_pointslope((px, py), m2)

    # Points of tangency on the ellipse
    if math.isclose(px, rx):
        t1 = rx, 0
        t2x = rx*(ry**2-py**2)/(py**2+ry**2)
        t2 = t2x, _line.yvalue(tline2, t2x)
    else:
        t1x = (2*m1**2*px/ry**2 - 2*m1*py/ry**2) / (2*m1**2/ry**2 + 2/rx**2)
        t2x = (2*m2**2*px/ry**2 - 2*m2*py/ry**2) / (2*m2**2/ry**2 + 2/rx**2)
        t1 = t1x, _line.yvalue(tline1, t1x)
        t2 = t2x, _line.yvalue(tline2, t2x)

    # Now translate and rotate back
    if theta != 0:
        m1 = math.tan(math.atan(m1) + theta)
        m2 = math.tan(math.atan(m2) + theta)
        t1 = rotate(t1, theta)
        t2 = rotate(t2, theta)
    t1 = translate(t1, (cx, cy))
    t2 = translate(t2, (cx, cy))
    return t1, t2


def tangent_angle(ellipse: EllipseType, theta: float) -> float:
    ''' Angle (radians) tangent to the Ellipse at theta (radians) '''
    dx, dy = _dxy(ellipse, theta)
    (centerx, centery), r1, r2, etheta = ellipse
    phi = math.atan2(dy * r1**2, dx * r2**2)
    tan = phi + math.pi/2 + math.radians(etheta)
    return (tan + math.tau) % math.tau
