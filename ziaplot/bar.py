''' Bar charts (qualitative independent variable) '''
from __future__ import annotations
from typing import Optional, Sequence, Union

from .drawable import Drawable
from .series import Series
from .dataseries import Bars, BarsHoriz
from .axes import XyPlot, LegendLoc
from .styletypes import Style
from .canvas import Canvas, ViewBox
from . import axis_stack


class BarSingle(Series):
    ''' A single bar in a BarChart

        Args:
            value: value assigned to this bar.
    '''
    def __init__(self, value: float = 1):
        super().__init__()
        self.value = value


class BarChart(XyPlot):
    ''' A bar chart with a single data series. Independent variable is qualitative.

        Args:
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
                 horiz: bool = False,
                 title: Optional[str] = None,
                 xname: Optional[str] = None,
                 yname: Optional[str] = None,
                 legend: LegendLoc = 'none',
                 style: Optional[Style] = None):
        super().__init__(title=title, xname=xname, yname=yname, legend=legend, style=style)
        self.barlist: list[BarSingle] = []
        self.horiz = horiz
        self._barwidth = 1.  # Let each bar have data-width = 1
        self.bargap = 0.1    # With 0.5 between each bar
        if self.horiz:
            self.style.axis.xdatapad = 0
            self.style.axis.ygrid = False
        else:
            self.style.axis.ydatapad = 0
            self.style.axis.xgrid = False
        axis_stack.push_series(None)
    
    def add(self, bar: Drawable) -> None:
        assert isinstance(bar, BarSingle)
        axis_stack.pause = True
        self.barlist.append(bar)
        newbar: Union[Bars, BarsHoriz]
        if self.horiz:
            newbar = BarsHoriz((0,), (bar.value,), width=self._barwidth, align='center')
            newbar.color(bar.style.line.color).name(bar._name)
        else:
            newbar = Bars((0,), (bar.value,), width=self._barwidth, align='center')
            newbar.color(bar.style.line.color).name(bar._name)
        super().add(newbar)
        axis_stack.pause = False

    @classmethod
    def fromdict(cls, bars: dict[str, float],
                 horiz: bool = False,
                 title: Optional[str] = None,
                 xname: Optional[str] = None,
                 yname: Optional[str] = None,
                 legend: LegendLoc = 'none',
                 style: Optional[Style] = None
                 ) -> 'BarChart':
        chart = cls(horiz=horiz, title=title, xname=xname, yname=yname,
                    legend=legend, style=style)
        for name, value in bars.items():
            axis_stack.pause = True
            chart.add(BarSingle(value).name(name))
        axis_stack.pause = False
        return chart

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''        
        names = [bar._name for bar in self.barlist]
        if self.horiz:
            series = self.series[::-1]
            names = names[::-1]
        else:
            series = self.series
        
        N = len(names)
        tickpos = [i * (self._barwidth + self.bargap) for i in range(N)]

        # Use named ticks
        if self.horiz:
            self.yticks(tickpos, names)
        else:
            self.xticks(tickpos, names)

        # Set bar x positions
        for tick, bar in zip(tickpos, self.series):
            assert isinstance(bar, (Bars, BarsHoriz))
            bar.x = (tick,)
        super()._xml(canvas)


class BarSeries(Series):
    ''' A series of bars across all groups

        Args:
            values: values assigned to this bar series.
    '''
    def __init__(self, *values: float):
        super().__init__()
        self.values = values


class BarChartGrouped(XyPlot):
    ''' A grouped bar chart, where independent variable is qualitative.

        Args:
            groups: list of x value strings
            horiz: Draw as horizontal bars (x values will be drawn along vertical axis)
            title: Title for chart
            xname: Name/label for x (independent variable) axis
            yname: Name/label for y (dependent variable) axis
            legend: Location for legend
            style: Plotting style

        Note:
            For a bar graph with quantitative x values, use XyPlot and add Bars instances.
    '''
    def __init__(self, groups: Sequence[str],
                 horiz: bool = False,
                 title: Optional[str] = None,
                 xname: Optional[str] = None,
                 yname: Optional[str] = None,
                 legend: LegendLoc = 'left',
                 style: Optional[Style] = None):
        super().__init__(title=title, xname=xname, yname=yname, legend=legend, style=style)
        self.barlist: list[BarSeries] = []
        self.groups = groups
        self.horiz = horiz
        self.barwidth = 1.  # Let each bar have data-width = 1
        self.bargap = 0.5  # With 0.5 between each group of bars
        if self.horiz:
            self.style.axis.xdatapad = 0
            self.style.axis.ygrid = False
        else:
            self.style.axis.ydatapad = 0
            self.style.axis.xgrid = False
        axis_stack.push_series(self)

    def add(self, barseries: Drawable) -> None:
        assert isinstance(barseries, BarSeries)
        axis_stack.pause = True
        self.barlist.append(barseries)
        # Use dummy x-values for now since we don't know how many series there will be
        x = list(range(len(barseries.values)))
        bar: Union[Bars, BarsHoriz]
        if self.horiz:
            values = list(reversed(barseries.values))
            bar = BarsHoriz(x, values, width=self.barwidth, align='left')
        else:
            bar = Bars(x, barseries.values, width=self.barwidth, align='left')
        bar.color(barseries.style.line.color).name(barseries._name)
        super().add(bar)
        axis_stack.pause = False

    @classmethod
    def fromdict(cls, bars: dict[str, Sequence[float]],
                 groups: Sequence[str],
                 horiz: bool = False,
                 title: Optional[str] = None,
                 xname: Optional[str] = None,
                 yname: Optional[str] = None,
                 legend: LegendLoc = 'left',
                 style: Optional[Style] = None
                 ) -> 'BarChartGrouped':
        chart = cls(groups=groups, horiz=horiz, title=title, xname=xname, yname=yname,
                    legend=legend, style=style)
        for name, values in bars.items():
            axis_stack.pause = True
            chart.add(BarSeries(*values).name(name))
        axis_stack.pause = False
        return chart

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        num_series = len(self.barlist)
        num_groups = len(self.groups)
        groupwidth = (self.barwidth*num_series) + self.bargap
        totwidth = groupwidth * num_groups + self.bargap
        # Use named ticks
        if self.horiz:
            yticks = [self.bargap + (groupwidth-self.bargap)/2 + k*groupwidth for k in range(num_groups)]
            self.yticks(yticks, self.groups[::-1])
            self.yrange(0, totwidth)
            # Set bar x positions
            for i, bar in enumerate(self.series[::-1]):
                assert isinstance(bar, (Bars, BarsHoriz))            
                x = [self.bargap + self.barwidth*i + k*groupwidth for k in range(num_groups)]
                bar.x = x
        else:
            xticks = [self.bargap + (groupwidth-self.bargap)/2 + k*groupwidth for k in range(num_groups)]
            self.xticks(xticks, self.groups)
            self.xrange(0, totwidth)

            # Set bar x positions
            for i, bar in enumerate(self.series):
                assert isinstance(bar, (Bars, BarsHoriz))            
                x = [self.bargap + self.barwidth*i + k*groupwidth for k in range(num_groups)]
                bar.x = x
        super()._xml(canvas)
