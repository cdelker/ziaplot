''' Tangent and Normal lines '''
import math

from ..shapes import Circle
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
        ''' Create a Line tangent to the circle at theta '''
        x, y = circle._xy(theta)
        try:
            slope = -1/math.tan(theta)
        except ZeroDivisionError:
            slope = math.inf
        return Line((x, y), slope)


class TangentSegment:
    ''' Create Segment tangent to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float,
           d1: float = 0, d2: float = 0,
           d_is_length: bool = True) -> Line:
        ''' Create a Segment tangent to f at x,
            extending d1 to the left and d2 to the right.
            If d_is_length, d1 and d2 are the length of segment on each side.
            Otherwise, they are the x-component of length on each side.
        '''
        slope = f._tangent_slope(x)
        y = f.y(x)
        if d_is_length:
            theta = math.tan(slope)
            x1 = x - d1 * math.cos(theta)
            x2 = x + d2 * math.cos(theta)
            y1 = y - d1 * math.sin(theta)
            y2 = y + d2 * math.sin(theta)
        else:
            x1 = x - d1
            x2 = x + d2
            y1 = y - slope * d1
            y2 = y + slope * d2
        return Segment((x1, y1), (x2, y2))

    @classmethod
    def to_circle(cls, circle: Circle, theta: float,
                  d1: float = 0, d2: float = 0,
                  d_is_length: bool = True) -> Line:
        ''' Create a Segment tangent to the circle at theta
            extending d1 to the left and d2 to the right.
            If d_is_length, d1 and d2 are the length of segment on each side.
            Otherwise, they are the x-component of length on each side.
        '''
        x, y = circle._xy(theta)
        if d_is_length:
            theta = theta + math.pi/2
            x1 = x - d1 * math.cos(theta)
            x2 = x + d2 * math.cos(theta)
            y1 = y - d1 * math.sin(theta)
            y2 = y + d2 * math.sin(theta)
        else:
            try:
                slope = -1/math.tan(theta)
            except ZeroDivisionError:
                slope = math.inf
            
            x1 = x - d1
            x2 = x + d2
            y1 = y - slope * d1
            y2 = y + slope * d2
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
    def to_circle(cls, circle: Circle, theta: float) -> Line:
        ''' Create a Line tangent to the circle at theta '''
        x, y = circle._xy(theta)
        try:
            slope = math.tan(theta)
        except ZeroDivisionError:
            slope = math.inf
        return Line((x, y), slope)


class NormalSegment:
    ''' Create Segment normal to other geometric instances '''
    @classmethod
    def to(cls, f: Function, x: float,
           d1: float = 0, d2: float = 0,
           d_is_length: bool = True) -> Line:
        ''' Create a Line tangent to f at x,
            extending d1 to the left and d2 to the right.
            If d_is_length, d1 and d2 are the length of segment on each side.
            Otherwise, they are the x-component of length on each side.
        '''
        y = f.y(x)
        try:
            slope = -1 / f._tangent_slope(x)
        except ZeroDivisionError:
            slope = math.inf
        if d_is_length:
            theta = math.tan(slope)
            x1 = x - d1 * math.cos(theta)
            x2 = x + d2 * math.cos(theta)
            y1 = y - d1 * math.sin(theta)
            y2 = y + d2 * math.sin(theta)
        else:
            y = 0 if not math.isfinite(y) else y
            x1 = x - d1
            x2 = x + d2
            y1 = y - slope * d1
            y2 = y + slope * d2
        return Segment((x1, y1), (x2, y2))

    @classmethod
    def to_circle(cls, circle: Circle, theta: float,
                  d1: float = 0, d2: float = 0,
                  d_is_length: bool = True) -> Line:
        ''' Create a Line tangent to the circle at theta
            extending d1 to the left and d2 to the right.
            If d_is_length, d1 and d2 are the length of segment on each side.
            Otherwise, they are the x-component of length on each side.
        '''
        x, y = circle._xy(theta)
        if d_is_length:
            x1 = x - d1 * math.cos(theta)
            x2 = x + d2 * math.cos(theta)
            y1 = y - d1 * math.sin(theta)
            y2 = y + d2 * math.sin(theta)
        else:
            try:
                slope = math.tan(theta)
            except ZeroDivisionError:
                slope = math.inf
            x1 = x - d1
            x2 = x + d2
            y1 = y - slope * d1
            y2 = y + slope * d2
        return Segment((x1, y1), (x2, y2))
