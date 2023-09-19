''' Logscale axes '''

from __future__ import annotations
from typing import Sequence
import math
from copy import deepcopy

from .axes import XyPlot, Ticks
from .canvas import Canvas, ViewBox, DataRange
from .dataseries import Line, Text, Bars, HLine, VLine
from . import text


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
    def datarange(self) -> DataRange:
        ''' Get range of data '''
        drange = super().datarange()
        try:
            ymin = math.log10(drange.ymin)
        except ValueError:
            ymin = 0
        return DataRange(drange.xmin, drange.xmax, ymin, math.log10(drange.ymax))

    def _maketicks(self, datarange: DataRange) -> Ticks:
        ''' Define ticks and tick labels.

            Args:
                datarange: Range of x and y data

            Returns:
                ticks: Tick names and positions
        '''
        ticks = super()._maketicks(datarange)
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
            if isinstance(s, (Line, Bars)):
                s.y = [math.log10(y) for y in s.y]
            elif isinstance(s, (Text, HLine)):
                s.y = math.log10(s.y)

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
    def datarange(self) -> DataRange:
        ''' Get range of data '''
        drange = super().datarange()
        try:
            xmin = math.log10(drange.xmin)
        except ValueError:
            xmin = 0
        return DataRange(xmin, math.log10(drange.xmax),
                         drange.ymin, drange.ymax)

    def _maketicks(self, datarange: DataRange) -> Ticks:
        ''' Define ticks and tick labels.

            Args:
                datarange: Range of x and y data

            Returns:
                ticks: Tick names and positions
        '''
        ticks = super()._maketicks(datarange)
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
            if isinstance(s, (Line, Bars)):
                s.x = [math.log10(x) for x in s.x]
                if isinstance(s, Bars):
                    s.width = math.log10(s.x[1]) - math.log10(s.x[0])
            elif isinstance(s, (Text, VLine)):
                s.x = math.log10(s.x)

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

        return DataRange(xmin, math.log10(drange.xmax),
                         ymin, math.log10(drange.ymax))

    def _maketicks(self, datarange: DataRange) -> Ticks:
        ''' Define ticks and tick labels.

            Args:
                datarange: Range of x and y data

            Returns:
                ticks: Tick names and positions
        '''
        ticks = super()._maketicks(datarange)
        xticks, xnames, xminor = logticks(ticks.xticks, divs=self.style.tick.xlogdivisions)
        xrange = xticks[0], xticks[-1]
        ticks = super()._maketicks(datarange)
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
            if isinstance(s, (Line, Bars)):
                s.x = [math.log10(x) for x in s.x]
                s.y = [math.log10(y) for y in s.y]
                if isinstance(s, Bars):
                    s.width = math.log10(s.x[1]) - math.log10(s.x[0])
            elif isinstance(s, (Text)):
                s.x = math.log10(s.x)
                s.y = math.log10(s.y)
            elif isinstance(s, HLine):
                s.y = math.log10(s.y)
            elif isinstance(s, VLine):
                s.x = math.log10(s.x)
        super()._drawseries(canvas, axisbox, databox)
        self.series = seriesbackup
