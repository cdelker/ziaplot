''' Logscale Graphs '''
from __future__ import annotations
from typing import Sequence
from functools import lru_cache
from copy import deepcopy
import math

from ..canvas import Canvas, ViewBox, DataRange
from .. import text
from ..element import Element
from .graph import Graph, Ticks


def logticks(ticks: Sequence[float], divs=10) -> tuple[list[float], list[str], list[float]]:
    ''' Generate tick minor tick positions on log scale

        Args:
            ticks: Major tick positions generated from original maketicks
            divs: Number of minor divisions between major ticks

        Returns:
            ticks: Tick values on log scale (10**value)
            names: List of tick label names (g format)
            minor: Minor tick positions
    '''
    values: list[float] = list(range(math.floor(ticks[0]), math.ceil(ticks[-1])+1))
    names = [format(10**val, 'g') for val in values]

    minor = None
    if divs:
        if divs == 5:
            t = [2, 4, 6, 8]
        elif divs == 2:
            t = [5]
        else:  # divs == 10:
            t = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        minor = []
        for major in values[1:]:
            minor.extend([math.log10(k*(10**major)/10) for k in t])
    return values, names, minor


class GraphLog(Graph):
    ''' Base Class for log-scale graph '''
    def __init__(self):
        super().__init__()
        self.xlogdivisions = 10
        self.ylogdivisions = 10


class GraphLogY(GraphLog):
    ''' Plot with Y on a log10 scale '''
    def _clearcache(self):
        ''' Clear LRU cache when inputs changes '''
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def datarange(self) -> DataRange:
        ''' Get range of data '''
        drange = super().datarange()
        try:
            ymin = math.log10(drange.ymin)
        except ValueError:
            ymin = 0
        try:
            ymax = math.log10(drange.ymax)
        except ValueError:
            ymax = 1
        
        return DataRange(drange.xmin, drange.xmax, ymin, ymax)

    @lru_cache
    def _maketicks(self) -> Ticks:
        ''' Define ticks and tick labels.

            Returns:
                ticks: Tick names and positions
        '''
        ticks = super()._maketicks()
        yticks, ynames, yminor = logticks(ticks.yticks, divs=self.ylogdivisions)
        yrange = yticks[0], yticks[-1]
        sty = self._build_style()

        ywidth = 0.
        for tick in ynames:
            ywidth = max(ywidth, text.text_size(tick,
                         fontsize=sty.font_size,
                         font=sty.font).width)

        ticks = Ticks(ticks.xticks, yticks, ticks.xnames,
                      ynames, ywidth, ticks.xrange, yrange,
                      None, yminor)
        return ticks

    def _drawcomponents(self, canvas: Canvas, diagbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all components to the graph

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        compbackup = self.components
        self.components = [deepcopy(c) for c in compbackup]
        for c in self.components:
            c._logy()

        super()._drawcomponents(canvas, diagbox, databox)
        self.components = compbackup


class GraphLogX(GraphLog):
    ''' Plot with Y on a log10 scale '''
    def _clearcache(self):
        ''' Clear LRU cache when inputs changes '''
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def datarange(self) -> DataRange:
        ''' Get range of data '''
        drange = super().datarange()
        try:
            xmin = math.log10(drange.xmin)
        except ValueError:
            xmin = 0
        try:
            xmax = math.log10(drange.xmax)
        except ValueError:
            xmax = 1
        return DataRange(xmin, xmax,
                         drange.ymin, drange.ymax)

    @lru_cache
    def _maketicks(self) -> Ticks:
        ''' Define ticks and tick labels.

            Returns:
                ticks: Tick names and positions
        '''
        ticks = super()._maketicks()
        xticks, xnames, xminor = logticks(ticks.xticks, divs=self.xlogdivisions)
        xrange = xticks[0], xticks[-1]

        ticks = Ticks(xticks, ticks.yticks, xnames, ticks.ynames,
                      ticks.ywidth, xrange, ticks.yrange, xminor, None)
        return ticks

    def _drawcomponents(self, canvas: Canvas, diagbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all components to the graph

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        compbackup = self.components
        self.components = [deepcopy(c) for c in compbackup]
        for c in self.components:
            c._logx()

        super()._drawcomponents(canvas, diagbox, databox)
        self.components = compbackup


class GraphLogXY(GraphLog):
    ''' Plot with X and Y on a log10 scale '''
    def _clearcache(self):
        ''' Clear LRU cache when inputs changes '''
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def datarange(self) -> DataRange:
        drange = super().datarange()
        try:
            xmin = math.log10(drange.xmin)
        except ValueError:
            xmin = 0
        try:
            ymin = math.log10(drange.ymin)
        except ValueError:
            ymin = 0
        try:
            xmax = math.log10(drange.xmax)
        except ValueError:
            xmax = 1
        try:
            ymax = math.log10(drange.ymax)
        except ValueError:
            ymax = 1

        return DataRange(xmin, xmax, ymin, ymax)

    @lru_cache
    def _maketicks(self) -> Ticks:
        ''' Define ticks and tick labels.

            Args:
                datarange: Range of x and y data

            Returns:
                ticks: Tick names and positions
        '''
        ticks = super()._maketicks()
        xticks, xnames, xminor = logticks(ticks.xticks, divs=self.xlogdivisions)
        xrange = xticks[0], xticks[-1]
        yticks, ynames, yminor = logticks(ticks.yticks, divs=self.ylogdivisions)
        yrange = yticks[0], yticks[-1]
        sty = self._build_style()

        ywidth = 0.
        for tick in ynames:
            ywidth = max(ywidth, text.text_size(tick,
                         fontsize=sty.font_size,
                         font=sty.font).width)

        ticks = Ticks(xticks, yticks, xnames, ynames, ywidth,
                      xrange, yrange, xminor, yminor)
        return ticks

    def _drawcomponents(self, canvas: Canvas, diagbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all components in the graph

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
                databox: ViewBox of data to convert from data to
                    svg coordinates
        '''
        compbackup = self.components
        self.components = [deepcopy(c) for c in compbackup]
        for c in self.components:
            c._logx()
            c._logy()

        super()._drawcomponents(canvas, diagbox, databox)
        self.components = compbackup
