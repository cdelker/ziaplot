''' Calculations on functions '''
import math

from ..util import maximum, minimum, derivative
from .geometry import PointType, LineType, FunctionType
from . import line as _line


def local_max(f: FunctionType, x1: float, x2: float) -> PointType:
    ''' Find local maximum of function f between x1 and x2 '''
    x = maximum(f, x1, x2)
    y = f(x)
    return x, y


def local_min(f: FunctionType, x1: float, x2: float) -> PointType:
    ''' Find local minimum of function f between x1 and x2 '''
    x = minimum(f, x1, x2)
    y = f(x)
    return x, y


def tangent(f: FunctionType, x: float) -> LineType:
    ''' Find tangent to function at x '''
    slope = derivative(f, x)
    y = f(x)
    y = 0 if not math.isfinite(y) else y
    return _line.new_pointslope((x, y), slope)


def normal(f: FunctionType, x: float) -> LineType:
    ''' Find normal to function at x '''
    try:
        slope = -1 / derivative(f, x)
    except ZeroDivisionError:
        slope = math.inf
    y = f(x)
    y = 0 if not math.isfinite(y) else y
    return _line.new_pointslope((x, y), slope)
