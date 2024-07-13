''' Integral Fills '''
from __future__ import annotations
from typing import Optional

from .. import util
from ..canvas import Canvas, Borders, ViewBox
from ..series import Series
from .function import Function


class IntegralFill(Series):
    ''' Fill between two functions or between a function and the x-axis '''
    def __init__(self, f: Function, f2: Optional[Function] = None,
                 x1: Optional[float] = None, x2: Optional[float] = None):
        super().__init__()
        self.func = f
        self.func2 = f2
        self.x1 = x1
        self.x2 = x2

    def alpha(self, alpha: float) -> 'IntegralFill':
        ''' Set the transparency

            Args:
                alpha: Transparency (0-1, with 1 being opaque)
        '''
        self.style.fillalpha = alpha
        return self

    def _xlimits(self, databox: ViewBox) -> tuple[float, float]:
        ''' Get x-limits to draw over '''
        if self.x1 is not None:
            x1 = self.x1
        elif self.func.xrange:
            x1 = self.func.xrange[0]
        else:
            x1 = databox.x
        if self.x2 is not None:
            x2 = self.x2
        elif self.func.xrange:
            x2 = self.func.xrange[1]
        else:
            x2 = databox.x + databox.w
        return x1, x2

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        x1, x2 = self._xlimits(databox)
        xrange = util.linspace(x1, x2, self.func.n)
        x, y = self.func._evaluate(xrange)
        
        if self.func2:
            _, ymin = self.func2._evaluate(xrange)
        else:
            ymin = [0] * len(x)

        xy = list(zip(x, y))
        xy = xy + list(reversed(list(zip(x, ymin))))

        fill = self.style.fillcolor
        alpha = self.style.fillalpha
        if fill is None:
            fill = self.style.line.color

        canvas.poly(xy, color=fill,
                    alpha=alpha,
                    strokecolor='none',
                    dataview=databox)

    @classmethod
    def intersection(cls, f: Function, f2: Function,
                     x1: float, x2: float):
        ''' Integral fill between intersection of f and f2, where
            x1 and x2 are points outside the intersection
        '''
        mid = (x1+x2)/2
        tol = abs(x2-x1) * 1E-4
        try:
            a = util.root(lambda x: f.func(x) - f2.func(x),
                        x1, mid, tol)
        except ValueError:
            a = x1

        try:
            b = util.root(lambda x: f.func(x) - f2.func(x),
                        mid, x2, tol)
        except ValueError:
            b = x2

        return cls(f, f2, a, b)
