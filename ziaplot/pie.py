from __future__ import annotations
from typing import Optional, Literal, Sequence
from dataclasses import dataclass
import math

from .axes import BasePlot, Ticks, LegendLoc
from .series import Series
from .styletypes import Style
from . import colors
from .canvas import Canvas, ViewBox, Halign, Valign
from . import axis_stack


class PieSlice(Series):
    ''' One slice of a pie.

        Args:
            value: value assigned to this slice. Percent
                will be calculated using total value of all
                the slices.
    '''
    def __init__(self, value: float = 1):
        super().__init__()
        self.value = value
        self._extrude = False

    def extrude(self, extrude: bool) -> 'PieSlice':
        ''' Extrude the slice '''
        self._extrude = extrude
        return self

    def edgecolor(self, color: str) -> 'Series':
        ''' Sets the series stroke/linestyle '''
        self.style.border.color = color
        return self

    def edgewidth(self, width: float) -> 'Series':
        self.style.border.width = width
        return self


class Pie(BasePlot):
    ''' Pie Chart. Total of all wedge values will be normalized to 100%.

        Args:
            title: Title of the chart
            legend: Location for legend
            labelmode: How to label each wedge - by `name`, `percent`,
                or `value`.
            style: Plotting style
    '''
    def __init__(self,
                 title: Optional[str] = None,
                 legend: LegendLoc = 'left',
                 labelmode: str = 'name',
                 style: Optional[Style] = None):
        ''' '''
        super().__init__(title=title, style=style, legend=legend)
        self.labelmode = labelmode  # TODO put Literals in enum?

    @classmethod
    def fromdict(cls,
                 slices: dict[str, float],
                 title: Optional[str] = None,
                 legend: LegendLoc = 'left',
                 labelmode: str = 'name',
                 ) -> 'Pie':
        ''' Create Pie from bars dictionary

            Args:
                slices: dictionary of name:value pairs
                title: Title of the chart
                legend: Location for legend
                labelmode: How to label each wedge - by `name`, `percent`,
                    or `value`.
                style: Plotting style
        '''
        pie = cls(title=title, legend=legend, labelmode=labelmode)
        for name, value in slices.items():
            axis_stack.pause = True
            pie.add(PieSlice(value).name(name))
        axis_stack.pause = False
        return pie

    @classmethod
    def fromlist(cls, slices: list[float],
                 title: Optional[str] = None,
                 legend: LegendLoc = 'none',
                 labelmode: str = 'name',
                 ) -> 'Pie':
        ''' Create Pie from list of values

            Args:
                slices: list of values
                title: Title of the chart
                legend: Location for legend
                labelmode: How to label each wedge - by `name`, `percent`,
                    or `value`.
                style: Plotting style
        '''
        pie = cls(title=title, legend=legend, labelmode=labelmode)
        for value in slices:
            axis_stack.pause = True
            pie.add(PieSlice(value))
        axis_stack.pause = False
        return pie

    def colorfade(self, *clrs: str, stops: Optional[Sequence[float]] = None) -> None:
        ''' Define the color cycle evenly fading between two colors.
            `c1` will always be the color of the first series, and `c2`
            the color of the last series, with an even gradient for
            series in between.

            Args:
                colors: List of colors to fade through
                stops: Stop positions, starting with 0 and ending with 1
        '''
        self.style.colorcycle = colors.ColorFade(*clrs, stops=stops)    

    def _legendloc(self, axisbox: ViewBox, ticks: Ticks, boxw: float) -> tuple[float, float]:
        ''' Calculate legend location

            Args:
                axisbox: ViewBox of the axis
                ticks: Tick names and positions
                boxw: Width of legend box
        '''
        xright = 0
        ytop = axisbox.y + axisbox.h - 1
        if self.legend == 'left':
            xright = axisbox.x + boxw + 1
        elif self.legend == 'right':
            xright = axisbox.x + axisbox.w - 1
        return ytop, xright

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        slices = [s for s in self.series if isinstance(s, PieSlice)]
        values = [w.value for w in slices]
        total = sum(values)
        thetas = [v/total*math.pi*2 for v in values]
        self.style.colorcycle.steps(len(slices))

        cx = canvas.viewbox.x + canvas.viewbox.w/2
        cy = canvas.viewbox.y + canvas.viewbox.h/2

        radius = (min(canvas.viewbox.w, canvas.viewbox.h) / 2 -
                  self.style.pie.edgepad*2)

        if any(w._extrude for w in slices):
            radius -= self.style.pie.extrude

        if self.title:
            radius -= self.style.pie.title.size/2
            cy -= self.style.pie.title.size/2
            canvas.text(cx, canvas.viewbox.y+canvas.viewbox.h,
                        self.title, font=self.style.pie.title.font,
                        size=self.style.pie.title.size,
                        color=self.style.pie.title.color,
                        halign='center', valign='top')

        if len(slices) == 1:
            w = slices[0]
            if w.style.line.color == 'undefined':
                w.style.line.color = self.style.colorcycle[0]
            elif w.style.line.color.startswith('C'):
                w.style.line.color = self.style.colorcycle[w.color]

            canvas.circle(cx, cy, radius,
                          color=w.style.line.color,  # type: ignore
                          strokecolor=w.style.border.color,
                          strokewidth=w.style.border.width)

            if self.labelmode == 'name':
                labeltext = w._name
            elif self.labelmode == 'value':
                labeltext = format(w.value)
            elif self.labelmode == 'percent':
                labeltext = f'{w.value/total*100:.1f}%'
            else:
                labeltext = ''
            if labeltext:
                canvas.text(cx + radius * math.cos(math.pi/4),
                            cy + radius * math.sin(math.pi/4),
                            labeltext,
                            font=self.style.pie.label.font,
                            size=self.style.pie.label.size,
                            color=self.style.pie.label.color)

        else:
            theta = -math.pi/2  # Current angle, start at top
            for i, w in enumerate(slices):
                thetahalf = theta + thetas[i]/2

                if w.style.line.color == 'undefined':
                    w.style.line.color = self.style.colorcycle[i]
                elif w.style.line.color.startswith('C') and w.style.line.color[1:].isnumeric():
                    # Convert things like 'C1'
                    w.style.line.color = self.style.colorcycle[w.style.line.color]

                if w._extrude:
                    cxx = cx + self.style.pie.extrude * math.cos(thetahalf)
                    cyy = cy - self.style.pie.extrude * math.sin(thetahalf)
                else:
                    cxx = cx
                    cyy = cy

                canvas.wedge(cxx, cyy, radius, thetas[i], starttheta=theta,
                             color=w.style.line.color,  # type: ignore
                             strokecolor=w.style.border.color,
                             strokewidth=w.style.border.width)

                labelx = cxx + (radius+self.style.pie.labelpad) * math.cos(thetahalf)
                labely = cyy - (radius+self.style.pie.labelpad) * math.sin(thetahalf)
                halign: Halign = 'left' if labelx > cx else 'right'
                valign: Valign = 'bottom' if labely > cy else 'top'
                if self.labelmode == 'name':
                    labeltext = w._name
                elif self.labelmode == 'value':
                    labeltext = format(w.value)
                elif self.labelmode == 'percent':
                    labeltext = f'{w.value/total*100:.1f}%'
                else:
                    labeltext = ''

                if labeltext:
                    canvas.text(labelx, labely,
                                labeltext,
                                font=self.style.pie.label.font,
                                size=self.style.pie.label.size,
                                color=self.style.pie.label.color,
                                halign=halign, valign=valign)

                theta += thetas[i]

        if self.legend and self.legend != 'none':
            ticks = Ticks(xticks=None, yticks=None, xnames=None, ynames=None,
                          ywidth=0, xrange=None, yrange=None, xminor=None, yminor=None)
            self._drawlegend(canvas, canvas.viewbox, ticks)
