''' Bar charts (qualitative independent variable) '''
from __future__ import annotations
from typing import Optional, Sequence, Union

from ..drawable import Drawable
from ..series import Series
from ..dataplots import Bars, BarsHoriz
from ..axes import AxesPlot
from ..style import Style
from ..canvas import Canvas, Borders, ViewBox
from .. import axis_stack


class Bar(Series):
    ''' A single bar in a BarChart

        Args:
            value: value assigned to this bar.
    '''
    step_color = True

    def __init__(self, value: float = 1):
        super().__init__()
        self.value = value


class BarChart(AxesPlot):
    ''' A vertical bar chart with a single data series.
        Independent variable is qualitative.

        Note:
            For a bar graph with quantitative x values, use AxesPlot and add Bars instances.
    '''
    def __init__(self):
        super().__init__()
        self.barlist: list[Bar] = []
        self._horiz = False
        self._barwidth = 1.  # Let each bar have data-width = 1
        self._legend = None
        axis_stack.push_series(None)
    
    def add(self, bar: Drawable) -> None:
        ''' Add a single bar '''
        assert isinstance(bar, Bar)
        axis_stack.pause = True
        self.barlist.append(bar)
        newbar: Union[Bars, BarsHoriz]
        if self._horiz:
            newbar = BarsHoriz((0,), (bar.value,), width=self._barwidth, align='center')
            newbar.color(bar._style.color).name(bar._name)
        else:
            newbar = Bars((0,), (bar.value,), width=self._barwidth, align='center')
            newbar.color(bar._style.color).name(bar._name)
        super().add(newbar)
        axis_stack.pause = False

    def build_style(self, name: str | None = None) -> Style:
        ''' Build the Style '''
        if self._horiz:
            if name == 'Axes.TickX':
                name = 'BarChartHoriz.TickY'
            elif name == 'Axes.GridY':
                name = 'BarChartHoriz.GridY'
            elif name == 'Axes.GridY':
                name = 'BarChartHoriz.GridY'
        else:
            if name == 'Axes.TickY':
                name = 'BarChart.TickX'
            elif name == 'Axes.GridX':
                name = 'BarChart.GridX'
            elif name == 'Axes.GridY':
                name = 'BarChart.GridY'
        return super().build_style(name)

    @classmethod
    def fromdict(cls, bars: dict[str, float]) -> 'BarChart':
        ''' Create a barchart from dictionary of name: value pairs '''
        chart = cls()
        for name, value in bars.items():
            axis_stack.pause = True
            chart.add(Bar(value).name(name))
        axis_stack.pause = False
        return chart

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self.build_style()
        names = [bar._name for bar in self.barlist]
        if self._horiz:
            series = self.series[::-1]
            names = names[::-1]
        else:
            series = self.series

        N = len(names)
        tickpos = [i * (self._barwidth + sty.margin) for i in range(N)]

        # Use named ticks
        if self._horiz:
            self.yticks(tickpos, names)
        else:
            self.xticks(tickpos, names)

        # Set bar x positions
        for tick, bar in zip(tickpos, self.series):
            assert isinstance(bar, (Bars, BarsHoriz))
            bar.x = (tick,)
        super()._xml(canvas, databox, borders)


class BarChartHoriz(BarChart):
    ''' A horizontal bar chart with a single data series.
        Independent variable is qualitative.

        Note:
            For a bar graph with quantitative x values, use AxesPlot and add Bars instances.
    '''
    def __init__(self):
        super().__init__()
        self._horiz = True


class BarSeries(Series):
    ''' A series of bars across all groups

        Args:
            values: values assigned to this bar series.
    '''
    step_color = True

    def __init__(self, *values: float):
        self.values = values
        super().__init__()


class BarChartGrouped(AxesPlot):
    ''' A grouped bar chart, where independent variable is qualitative.

        Args:
            groups: list of x value strings

        Note:
            For a bar graph with quantitative x values, use AxesPlot and add Bars instances.
    '''
    def __init__(self, groups: Sequence[str]):
        super().__init__()
        self.barlist: list[BarSeries] = []
        self.groups = groups
        self._horiz = False
        self._barwidth = 1.  # Let each bar have data-width = 1
        axis_stack.push_series(self)

    def add(self, barseries: Drawable) -> None:
        ''' Add a series of bars to the chart '''
        assert isinstance(barseries, BarSeries)
        axis_stack.pause = True
        self.barlist.append(barseries)
        # Use dummy x-values for now since we don't know how many series there will be
        x = list(range(len(barseries.values)))
        bar: Union[Bars, BarsHoriz]
        if self._horiz:
            values = list(reversed(barseries.values))
            bar = BarsHoriz(x, values, width=self._barwidth, align='left')
        else:
            bar = Bars(x, barseries.values, width=self._barwidth, align='left')
        bar.color(barseries._style.color).name(barseries._name)
        super().add(bar)
        axis_stack.pause = False

    def build_style(self, name: str | None = None) -> Style:
        ''' Build the Style '''
        if self._horiz:
            if name == 'Axes.TickX':
                name = 'BarChartHoriz.TickY'
            elif name == 'Axes.GridY':
                name = 'BarChartHoriz.GridY'
            elif name == 'Axes.GridY':
                name = 'BarChartHoriz.GridY'
        else:
            if name == 'Axes.TickY':
                name = 'BarChart.TickX'  # OK
            elif name == 'Axes.GridX':
                name = 'BarChart.GridX'
            elif name == 'Axes.GridY':
                name = 'BarChart.GridY'
        return super().build_style(name)

    @classmethod
    def fromdict(cls, bars: dict[str, Sequence[float]],
                 groups: Sequence[str]) -> 'BarChartGrouped':
        ''' Create Bar Chart from dictionary of name: values list '''
        chart = cls(groups)
        for name, values in bars.items():
            axis_stack.pause = True
            chart.add(BarSeries(*values).name(name))
        axis_stack.pause = False
        return chart

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self.build_style()
        num_series = len(self.barlist)
        num_groups = len(self.groups)
        bargap = sty.margin
        groupwidth = (self._barwidth*num_series) + bargap
        totwidth = groupwidth * num_groups + bargap
        # Use named ticks
        if self._horiz:
            yticks = [bargap + (groupwidth-bargap)/2 + k*groupwidth for k in range(num_groups)]
            self.yticks(yticks, self.groups[::-1])
            self.yrange(0, totwidth)
            # Set bar x positions
            for i, bar in enumerate(self.series[::-1]):
                assert isinstance(bar, (Bars, BarsHoriz))            
                x = [bargap + self._barwidth*i + k*groupwidth for k in range(num_groups)]
                bar.x = x
        else:
            xticks = [bargap + (groupwidth-bargap)/2 + k*groupwidth for k in range(num_groups)]
            self.xticks(xticks, self.groups)
            self.xrange(0, totwidth)

            # Set bar x positions
            for i, bar in enumerate(self.series):
                assert isinstance(bar, (Bars, BarsHoriz))            
                x = [bargap + self._barwidth*i + k*groupwidth for k in range(num_groups)]
                bar.x = x
        super()._xml(canvas, databox, borders=borders)


class BarChartGroupedHoriz(BarChartGrouped):
    ''' Horizontal Grouped Bar Chart '''
    def __init__(self, groups: Sequence[str]):
        super().__init__(groups)
        self._horiz = True
