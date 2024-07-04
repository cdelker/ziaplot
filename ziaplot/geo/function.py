from __future__ import annotations
from typing import Callable
import math

from .. import util
from ..dataplots import PolyLine


class Function(PolyLine):
    ''' Plot a function

        Args:
            func: Callable function (e.g. lambda x: x**2)
            xmin: Minimum x value
            xmax: Maximum x value
            n: Number of datapoints for discrete representation
    '''
    def __init__(self, func: Callable[[float], float],
                 xmin: float = -5, xmax: float = 5, n: int = 200):
        step = (xmax-xmin) / n
        x = util.zrange(xmin, xmax, step)
        y = [func(x0) for x0 in x]
        self.func = func
        super().__init__(x, y)

    def logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.func = lambda x: math.log10(self.func(x))

    def logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.func = lambda x: self.func(math.log10(x))
