''' Bar charts (qualitative independent variable) '''

from typing import Sequence, Union
import xml.etree.ElementTree as ET

from .dataseries import Bars, BarsHoriz
from .axes import XyPlot, LegendLoc
from .styletypes import Style
from .canvas import Canvas, ViewBox


class BarChart(XyPlot):
    ''' A bar chart, where independent variable is qualitative.

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
    def __init__(self, xvalues: Sequence[str], horiz: bool=False,
                 title: str=None, xname: str=None, yname: str=None,
                 legend: LegendLoc='left', style: Style=None):
        super().__init__(title=title, xname=xname, yname=yname, legend=legend, style=style)
        self.barlist: list[Union[Bars, BarsHoriz]] = []
        self.xvalues = xvalues
        self.horiz = horiz
        self.barwidth = 1.  # Let each bar have data-width = 1
        self.bargap = 0.5  # With 0.5 between each group of bars
        if self.horiz:
            self.style.axis.xdatapad = 0
            self.style.axis.ygrid = False
        else:
            self.style.axis.ydatapad = 0
            self.style.axis.xgrid = False
        
    def bar(self, values: Sequence[float]) -> Bars:
        ''' Add a set of bars to the chart

            Args:
                values: Values for each bar of this series
        '''
        # Use dummy x-values for now since we don't know how many series there will be
        x = list(range(len(values)))
        bar: Union[Bars, BarsHoriz]
        if self.horiz:
            bar = BarsHoriz(x, values, width=self.barwidth, align='left')
        else:
            bar = Bars(x, values, width=self.barwidth, align='left')
        bar.style.line.strokewidth = self.style.series.line.strokewidth
        bar.style.line.strokecolor = self.style.series.line.strokecolor
        self.barlist.append(bar)  # Keep bars in a separate list in addition to series
        self.add(bar)
        return bar

    def _xml(self, canvas: Canvas, databox: ViewBox=None) -> None:
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
