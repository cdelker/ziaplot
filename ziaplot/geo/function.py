''' Graph mathematical functions '''
from __future__ import annotations
from typing import Optional, Callable, Sequence
from xml.etree import ElementTree as ET
import math

from .. import util
from ..element import Element
from ..style import MarkerTypes
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..diagrams import Graph


class Function(Element):
    ''' Plot a function

        Args:
            func: Callable function of x, returning y (e.g. lambda x: x**2)
            xmin: Minimum x value
            xmax: Maximum x value
            n: Number of datapoints for discrete representation
    '''
    _step_color = True

    def __init__(self,
                 func: Callable[[float], float],
                 xrange: Optional[tuple[float, float]] = None,
                 n: int = 200):
        super().__init__()
        self._func = func
        self.func = func
        self.xrange = xrange
        self.n = n
        self.startmark: MarkerTypes = None
        self.endmark: MarkerTypes = None
        self.midmark: MarkerTypes = None
        self.__logx = False
        self.__logy = False

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

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.__logy = True

    def _logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.__logx = True

    def y(self, x: float) -> float:
        ''' Evaluate f(x) '''
        y = self.func(x)
        if self.__logy:
            y = math.log10(y) if y > 0 else math.nan
        return y

    def x(self, y: float) -> float:
        ''' Calculate x at given y '''
        x0 = self.xrange[0] if self.xrange else 1
        return util.root_newton(lambda x: self.func(x) - y, x0=x0, tol=y/1E4)

    def _tangent_slope(self, x: float) -> float:
        ''' Calculate angle tangent to function at x '''
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

    def _evaluate(self, x: Sequence[float]) -> tuple[Sequence[float], Sequence[float]]:
        ''' Evaluate and return (x, y) in logscale if needed '''
        y = [self.func(xx) for xx in x]
        if self.__logy:
            y = [math.log10(yy) if yy > 0 else math.nan for yy in y]
        if self.__logx:
            x = [math.log10(xx) if xx > 0 else math.nan for xx in x]
        return x, y

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        sty = self._build_style()
        color = sty.get_color()

        xrange = self.xrange
        if xrange is None:
            xrange = databox.x, databox.x+databox.w
        x, y = self._evaluate(util.linspace(*xrange, self.n))

        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(self.startmark,
                                            sty.radius,
                                            color,
                                            sty.edge_color,
                                            sty.edge_width,
                                            orient=True)
        if self.endmark:
            endmark = canvas.definemarker(self.endmark,
                                          sty.radius,
                                          color,
                                          sty.edge_color,
                                          sty.edge_width,
                                          orient=True)

        canvas.path(x, y,
                    stroke=sty.stroke,
                    color=color,
                    width=sty.stroke_width,
                    startmarker=startmark,
                    endmarker=endmark,
                    dataview=databox)

        if self.midmark:
            midmark = canvas.definemarker(self.midmark,
                                          sty.radius,
                                          color,
                                          sty.edge_color,
                                          sty.stroke_width,
                                          orient=True)
            midx = (xrange[0]+xrange[1])/2
            midy = self.y(midx)
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
        graph = Graph()
        graph.add(self)
        return graph.svgxml(border=border)
