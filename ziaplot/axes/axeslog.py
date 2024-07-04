''' Logscale axes '''

from __future__ import annotations
from typing import Sequence
from functools import lru_cache
import math
from copy import deepcopy

from .axes import XyPlot, Ticks
from ..canvas import Canvas, ViewBox, DataRange
from .. import text


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


class LogYPlot(XyPlot):
    ''' Plot with Y on a log10 scale

        Args:
            title: Title to draw above axes
            xname: Name/label for x axis
            yname: Name/label for y axis
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def _clearcache(self):
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
        yticks, ynames, yminor = logticks(ticks.yticks, divs=self.style.tick.ylogdivisions)
        yrange = yticks[0], yticks[-1]

        ywidth = 0.
        for tick in ynames:
            ywidth = max(ywidth, text.text_size(tick,
                         fontsize=self.style.tick.text.size,
                         font=self.style.tick.text.font).width)

        ticks = Ticks(ticks.xticks, yticks, ticks.xnames,
                      ynames, ywidth, ticks.xrange, yrange,
                      None, yminor)
        return ticks

    def _drawseries(self, canvas: Canvas, axisbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all series lines/markers

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        seriesbackup = self.series
        self.series = [deepcopy(s) for s in seriesbackup]
        for s in self.series:
            s.logy()

        super()._drawseries(canvas, axisbox, databox)
        self.series = seriesbackup


class LogXPlot(XyPlot):
    ''' Plot with Y on a log10 scale

        Args:
            title: Title to draw above axes
            xname: Name/label for x axis
            yname: Name/label for y axis
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def _clearcache(self):
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
        xticks, xnames, xminor = logticks(ticks.xticks, divs=self.style.tick.xlogdivisions)
        xrange = xticks[0], xticks[-1]

        ticks = Ticks(xticks, ticks.yticks, xnames, ticks.ynames,
                      ticks.ywidth, xrange, ticks.yrange, xminor, None)
        return ticks

    def _drawseries(self, canvas: Canvas, axisbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all series lines/markers

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        seriesbackup = self.series
        self.series = [deepcopy(s) for s in seriesbackup]
        for s in self.series:
            s.logx()

        super()._drawseries(canvas, axisbox, databox)
        self.series = seriesbackup


class LogXYPlot(XyPlot):
    ''' Plot with X and Y on a log10 scale

        Args:
            title: Title to draw above axes
            xname: Name/label for x axis
            yname: Name/label for y axis
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def _clearcache(self):
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
        xticks, xnames, xminor = logticks(ticks.xticks, divs=self.style.tick.xlogdivisions)
        xrange = xticks[0], xticks[-1]
        yticks, ynames, yminor = logticks(ticks.yticks, divs=self.style.tick.ylogdivisions)
        yrange = yticks[0], yticks[-1]

        ywidth = 0.
        for tick in ynames:
            ywidth = max(ywidth, text.text_size(tick,
                         fontsize=self.style.tick.text.size,
                         font=self.style.tick.text.font).width)

        ticks = Ticks(xticks, yticks, xnames, ynames, ywidth,
                      xrange, yrange, xminor, yminor)
        return ticks

    def _drawseries(self, canvas: Canvas, axisbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all series lines/markers

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
                databox: ViewBox of data to convert from data to
                    svg coordinates
        '''
        seriesbackup = self.series

        self.series = [deepcopy(s) for s in seriesbackup]
        for s in self.series:
            s.logx()
            s.logy()
        super()._drawseries(canvas, axisbox, databox)
        self.series = seriesbackup
