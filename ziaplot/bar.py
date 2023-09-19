''' Bar charts (qualitative independent variable) '''

from typing import Sequence, Union

from .dataseries import Bars, BarsHoriz
from .axes import XyPlot, LegendLoc
from .styletypes import Style
from .canvas import Canvas, ViewBox


class BarChart(XyPlot):
    ''' A bar chart with a single data series. Independent variable is qualitative.

        Args:
            xvalues: list of x value strings
            yvalues: list of bar heights
            horiz: Draw as horizontal bars (x values will be drawn along vertical axis)
            title: Title for chart
            xname: Name/label for x (independent variable) axis
            yname: Name/label for y (dependent variable) axis
            legend: Location for legend
            style: Plotting style

        Note:
            For a bar graph with quantitative x values, use XyPlot and add Bars instances.
    '''
    def __init__(self,
                 xvalues: Sequence[str],
                 yvalues: Sequence[float],
                 horiz: bool = False,
                 title: str = None, xname: str = None, yname: str = None,
                 legend: LegendLoc = 'left', style: Style = None):
        super().__init__(title=title, xname=xname, yname=yname, legend=legend, style=style)
        self.barlist: list[Union[Bars, BarsHoriz]] = []
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.horiz = horiz
        self._barwidth = 1.  # Let each bar have data-width = 1
        self.bargap = 0.1  # With 0.5 between each bar
        if self.horiz:
            self.style.axis.xdatapad = 0
            self.style.axis.ygrid = False
            self.xvalues = list(reversed(self.xvalues))
        else:
            self.style.axis.ydatapad = 0
            self.style.axis.xgrid = False

        bar: Union[Bars, BarsHoriz]
        for value in yvalues:
            # x position of each bar will be set upon drawing to allow
            # user to change self.bargap
            if self.horiz:
                bar = BarsHoriz((0,), (value,), width=self._barwidth, align='center')
            else:
                bar = Bars((0,), (value,), width=self._barwidth, align='center')
            self.add(bar)
            self.barlist.append(bar)
    
    def _xml(self, canvas: Canvas, databox: ViewBox = None) -> None:
        ''' Add XML elements to the canvas '''
        N = len(self.xvalues)
        tickpos = [i * (self._barwidth + self.bargap) for i in range(N)]

        # Use named ticks
        if self.horiz:
            self.yticks(tickpos, self.xvalues)
        else:
            self.xticks(tickpos, self.xvalues)

        # Set bar x positions
        for tick, bar in zip(tickpos, self.barlist):
            bar.x = (tick,)
        super()._xml(canvas)


class BarChartGrouped(XyPlot):
    ''' A grouped bar chart, where independent variable is qualitative.

        Args:
            xvalues: list of x value strings
            horiz: Draw as horizontal bars (x values will be drawn along vertical axis)
            title: Title for chart
            xname: Name/label for x (independent variable) axis
            yname: Name/label for y (dependent variable) axis
            legend: Location for legend
            style: Plotting style

        Note:
            For a bar graph with quantitative x values, use XyPlot and add Bars instances.
    '''
    def __init__(self, xvalues: Sequence[str], horiz: bool = False,
                 title: str = None, xname: str = None, yname: str = None,
                 legend: LegendLoc = 'left', style: Style = None):
        super().__init__(title=title, xname=xname, yname=yname, legend=legend, style=style)
        self.barlist: list[Union[Bars, BarsHoriz]] = []
        self.xvalues = xvalues
        self.horiz = horiz
        self.barwidth = 1.  # Let each bar have data-width = 1
        self.bargap = 0.5  # With 0.5 between each group of bars
        if self.horiz:
            self.style.axis.xdatapad = 0
            self.style.axis.ygrid = False
            self.xvalues = list(reversed(self.xvalues))
        else:
            self.style.axis.ydatapad = 0
            self.style.axis.xgrid = False

    def bar_series(self, values: Sequence[float]) -> Bars:
        ''' Add a series of bars to the chart. Use when each
            x-value has multiple bars.

            Args:
                values: Values for each bar of this series
        '''
        # Use dummy x-values for now since we don't know how many series there will be
        x = list(range(len(values)))
        bar: Union[Bars, BarsHoriz]
        if self.horiz:
            values = list(reversed(values))
            bar = BarsHoriz(x, values, width=self.barwidth, align='left')
        else:
            bar = Bars(x, values, width=self.barwidth, align='left')
        bar.style.line.strokewidth = self.style.series.line.strokewidth
        bar.style.line.strokecolor = self.style.series.line.strokecolor

        # Keep bars in a separate list in addition to series
        if self.horiz:
            self.barlist.insert(0, bar)
        else:
            self.barlist.append(bar)
        self.add(bar)
        return bar
    
    def _xml(self, canvas: Canvas, databox: ViewBox = None) -> None:
        ''' Add XML elements to the canvas '''
        groups = len(self.barlist)
        N = len(self.xvalues)
        groupwidth = (self.barwidth*groups) + self.bargap
        totwidth = groupwidth * N + self.bargap

        # Use named ticks
        if self.horiz:
            yticks = [self.bargap + (groupwidth-self.bargap)/2 + k*groupwidth for k in range(N)]
            self.yticks(yticks, self.xvalues)
            self.yrange(0, totwidth)
        else:
            xticks = [self.bargap + (groupwidth-self.bargap)/2 + k*groupwidth for k in range(N)]
            self.xticks(xticks, self.xvalues)
            self.xrange(0, totwidth)

        # Set bar x positions
        for i, bar in enumerate(self.barlist):
            x = [self.bargap + self.barwidth*i + k*groupwidth for k in range(N)]
            bar.x = x
        super()._xml(canvas)
