''' Utility Functions. Most are pure-python replacements for numpy functions '''
from __future__ import annotations
from typing import Sequence, Callable, Tuple
import bisect
import math

PointType = Tuple[float, float]


def zrange(start: float, stop: float, step: float) -> list[float]:
    ''' Like builtin range, but works with floats '''
    assert step > 0
    assert step < (stop-start)
    vals = [start]
    while abs(vals[-1] - stop)/step > .1 and vals[-1] < stop:  # Wiggle room for float precision
        vals.append(vals[-1] + step)
    return vals


def linspace(start: float, stop: float, num: int = 50) -> list[float]:
    ''' Generate list of evenly spaced points '''
    if num < 2:
        return [stop]
    diff = (float(stop) - start)/(num - 1)
    return [diff * i + start for i in range(num)]


def interpolate(x1: float, x2: float, y1: float, y2: float, x: float) -> float:
    ''' Perform linear interpolation for x between (x1,y1) and (x2,y2) '''
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)


def interp(newx: Sequence[float], xlist: Sequence[float], ylist: Sequence[float]) -> list[float]:
    ''' Interpolate list of newx values (replacement for np.interp) '''
    newy = []
    for x in newx:
        idx = bisect.bisect_left(xlist, x)
        y = interpolate(xlist[idx-1], xlist[idx], ylist[idx-1], ylist[idx], x)
        newy.append(y)
    return newy


def root(f: Callable, a: float, b: float, tol=1E-4) -> float:
    ''' Find root of f between a and b '''
    def samesign(x, y):
        return x*y > 0

    fa = f(a)
    if samesign(fa, f(b)):
        raise ValueError("Root not bounded by a and b.")

    m = (a + b) / 2
    fm = f(m)
    if abs(fm) < tol:
        return m

    if samesign(fa, fm):
        return root(f, m, b, tol)

    return root(f, a, m, tol)


def root_newton(f: Callable, x0: float, tol=1E-4) -> float:
    ''' Find root using Newton-Raphson method

        Args:
            f: Function
            x0: Initial guess
            tol: Tolerance
    '''
    if abs(f(x0)) < tol:
        return x0
    else:
        df = derivative(f, x0)
        return root_newton(f, x0 - f(x0)/df, tol)


def minimum(f: Callable, a: float, b: float, tolerance: float=1e-5):
    """
    Golden-section search
    to find the minimum of f on [a,b]

    * f: a strictly unimodal function on [a,b]

    Example:
    >>> def f(x): return (x - 2) ** 2
    >>> x = gss(f, 1, 5)
    >>> print(f"{x:.5f}")
    2.00000

    https://en.wikipedia.org/wiki/Golden-section_search
    """
    invphi = (math.sqrt(5) - 1) / 2  # 1 / phi
    tolerance = (b-a)*tolerance

    while abs(b - a) > tolerance:
        c = b - (b - a) * invphi
        d = a + (b - a) * invphi
        if f(c) < f(d):
            b = d
        else:  # f(c) > f(d) to find the maximum
            a = c

    return (b + a) / 2


def maximum(f: Callable, a: float, b: float, tolerance: float=1e-5):
    """
    Golden-section search
    to find the maxumum of f on [a,b]

    * f: a strictly unimodal function on [a,b]

    Example:
    >>> def f(x): return (x - 2) ** 2
    >>> x = gss(f, 1, 5)
    >>> print(f"{x:.5f}")
    2.00000

    https://en.wikipedia.org/wiki/Golden-section_search
    """
    invphi = (math.sqrt(5) - 1) / 2  # 1 / phi
    tolerance = (b-a)*tolerance

    while abs(b - a) > tolerance:
        c = b - (b - a) * invphi
        d = a + (b - a) * invphi
        if f(c) > f(d):
            b = d
        else:  # f(c) > f(d) to find the maximum
            a = c

    return (b + a) / 2


def derivative(f: Callable, a: float):
    ''' Calculate derivative of f at a '''
    h = a/1E6 if a != 0 else 1E-6
    return (f(a+h) - f(a)) / h


def angle_mean(theta1: float, theta2: float) -> float:
    ''' Circular mean over 0 to 2pi '''
    sine = math.sin(theta1) + math.sin(theta2)
    cosine = math.cos(theta1) + math.cos(theta2)
    mean = math.atan2(sine, cosine)
    return (mean + math.tau) % math.tau


def distance(p1: PointType, p2: PointType):
    ''' Distance between two points '''
    return math.sqrt((p1[0]- p2[0])**2 + (p1[1] - p2[1])**2)
