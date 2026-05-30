''' Implicit Function '''
from __future__ import annotations
from typing import Callable

from ..util import linspace
from ..discrete import Contour
from ..geometry import PointType


class Implicit(Contour):
    ''' Plot an implicit function

        Args:
            f: A function of x and y, to plot
                f(x, y) = 0.
            xlim: Range of data for x direction
            ylim: Range of data for y direction
            n: Number of data points along x and y
                used to estimate the plot curves
    '''
    def __init__(self,
                 f: Callable,
                 xlim: PointType = (-1, 1),
                 ylim: PointType = (-1, 1),
                 n: int = 100):
        self.func = f
        self.n = n
        x = linspace(*xlim, n)
        y = linspace(*ylim, n)
        z = [[f(xx, yy) for xx in x] for yy in y]
        super().__init__(x, y, z, levels=(0,))

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        segments = self._build_contours()
        sty = self._build_style()
        color = sty.get_color()
        if color in [None, 'none']:
            color = self.get_color_steps()[0]
        for (xsegs, ysegs) in segments:
            if len(xsegs) > 0:
                for xs, ys in zip(xsegs, ysegs):
                    canvas.path(xs, ys,
                                stroke=sty.stroke,
                                color=color,
                                width=sty.stroke_width,
                                dataview=databox,
                                zorder=self._zorder,
                                attributes=self.svg)
