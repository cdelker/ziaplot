''' Utility Functions. Most are pure-python replacements for numpy functions '''
from __future__ import annotations

from typing import Sequence
import bisect


def zrange(start: float, stop: float, step: float) -> list[float]:
    ''' Like builtin range, but works with floats '''
    assert step > 0
    assert step < (stop-start)
    vals = [start]
    while abs(vals[-1] - stop)/step > .1:  # Wiggle room for float precision
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

