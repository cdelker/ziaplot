from __future__ import annotations
from typing import Optional, Callable, Sequence
from xml.etree import ElementTree as ET
import math

from .. import util
from ..series import Series
from ..style import MarkerTypes
from ..canvas import Canvas, Borders, ViewBox
from ..axes import AxesPlot


class Function(Series):
    ''' Plot a function

        Args:
            func: Callable function (e.g. lambda x: x**2)
            xmin: Minimum x value
            xmax: Maximum x value
            n: Number of datapoints for discrete representation
    '''
    def __init__(self, func: Callable[[float], float],
                 xrange: Optional[tuple[float, float]] = None, n: int = 200):
        super().__init__()
        self._func = func
        self.func = func
        self.xrange = xrange
        self.n = n
        self.startmark: MarkerTypes = None
        self.endmark: MarkerTypes = None
        self.midmark: MarkerTypes = None
        self._logx = False
        self._logy = False

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'Function':
        ''' Define markers to show at the start and end of the line. Use defaults
            to show arrowheads pointing outward in the direction of the line.
        '''
        self.startmark = start
        self.endmark = end
        return self

    def midmarker(self, midmark: MarkerTypes = '<') -> 'Function':
        ''' Define marker for midpoint (x/2) of Function curve '''
        self.midmark = midmark
        return self

    def logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self._logy = True

    def logx(self) -> None:
        ''' Convert x values to log(x) '''
        self._logx = True

    def y(self, x: float):
        y = self.func(x)
        if self._logy:
            y = math.log10(y) if y > 0 else math.nan
        return y

    def _tangent_slope(self, x: float) -> float:
        ''' Calculate angle tangent to Series at x '''
        return util.derivative(self.func, x)

    def _local_max(self, x1: float, x2: float) -> float:
        ''' Return x value where maximum point occurs
            between x1 and x2
        '''
        return util.maximum(self.func, x1, x2)

    def _local_min(self, x1: float, x2: float) -> float:
        ''' Return x value where minimum point occurs
            between x1 and x2
        '''
        return util.minimum(self.func, x1, x2)

    def _evaluate(self, x: Sequence[float]) -> tuple[list[float], list[float]]:
        y = [self.func(xx) for xx in x]
        if self._logy:
            y = [math.log10(yy) if yy > 0 else math.nan for yy in y]
        if self._logx:
            x = [math.log10(xx) if xx > 0 else math.nan for xx in x]
        return x, y

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        xrange = self.xrange
        if xrange is None:
            xrange = databox.x, databox.x+databox.w
        x = util.linspace(*xrange, self.n)
        x, y = self._evaluate(x)
        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(self.startmark,
                                            self.style.marker.radius,
                                            self.style.marker.color,
                                            self.style.marker.strokecolor,
                                            self.style.marker.strokewidth,
                                            orient=True)
        if self.endmark:
            endmark = canvas.definemarker(self.endmark,
                                          self.style.marker.radius,
                                          self.style.marker.color,
                                          self.style.marker.strokecolor,
                                          self.style.marker.strokewidth,
                                          orient=True)

        color = self.style.line.color
        canvas.path(x, y,
                    stroke=self.style.line.stroke,
                    color=color,
                    width=self.style.line.width,
                    startmarker=startmark,
                    endmarker=endmark,
                    dataview=databox)

        if self.midmark:
            midmark = canvas.definemarker(self.midmark,
                                          self.style.marker.radius,
                                          self.style.marker.color,
                                          self.style.marker.strokecolor,
                                          self.style.marker.strokewidth,
                                          orient=True)
            midx, midy = self.xy(0.5)
            slope = self._tangent_slope(0.5)
            dx = midx/1E3
            midx1 = midx + dx
            midy1 = midy + dx*slope
            canvas.path([midx, midx1], [midy, midy1],
                        color='none',
                        startmarker=midmark,
                        dataview=databox)


    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        ax = AxesPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)
