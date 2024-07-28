''' Pie Charts '''
from __future__ import annotations
from typing import Optional, Literal
import math

from ..text import Halign, Valign
from ..diagrams import Diagram, Ticks
from ..element import Element
from ..canvas import Canvas, Borders, ViewBox
from .. import diagram_stack


PieLabelMode = Literal['name', 'percent', 'value']


class PieSlice(Element):
    ''' One slice of a pie.

        Args:
            value: value assigned to this slice. Percent
                will be calculated using total value of all
                the slices.
    '''
    _step_color = True
    legend_square = True

    def __init__(self, value: float = 1):
        super().__init__()
        self.value = value
        self._extrude: float = 0

    def extrude(self, extrude: float = 20) -> 'PieSlice':
        ''' Extrude the slice '''
        self._extrude = extrude
        return self

    def edgecolor(self, color: str) -> 'PieSlice':
        ''' Sets the slice stroke/linestyle '''
        self._style.edge_color = color
        return self

    def edgewidth(self, width: float) -> 'PieSlice':
        ''' Set the slice edge width '''
        self._style.stroke_width = width
        return self


class Pie(Diagram):
    ''' Pie Chart. Total of all wedge values will be normalized to 100%.

        Args:
            labelmode: How to label each wedge - by `name`, `percent`,
                or `value`.
    '''
    def __init__(self, labelmode: PieLabelMode = 'name'):
        ''' '''
        super().__init__()
        self.labelmode = labelmode

    @classmethod
    def fromdict(cls,
                 slices: dict[str, float],
                 labelmode: PieLabelMode = 'name') -> 'Pie':
        ''' Create Pie from bars dictionary

            Args:
                slices: dictionary of name:value pairs
                labelmode: How to label each wedge - by `name`, `percent`,
                    or `value`.
        '''
        pie = cls(labelmode=labelmode)
        diagram_stack.pause = True
        for name, value in slices.items():
            pie.add(PieSlice(value).name(name))
        diagram_stack.pause = False
        return pie

    @classmethod
    def fromlist(cls, slices: list[float],
                 labelmode: PieLabelMode = 'name') -> 'Pie':
        ''' Create Pie from list of values

            Args:
                slices: list of values
                labelmode: How to label each wedge - by `name`, `percent`,
                    or `value`.
        '''
        pie = cls(labelmode=labelmode)
        diagram_stack.pause = True
        for value in slices:
            pie.add(PieSlice(value))
        diagram_stack.pause = False
        return pie

    def _legendloc(self, diagbox: ViewBox, ticks: Ticks, boxw: float, boxh: float) -> tuple[float, float]:
        ''' Calculate legend location

            Args:
                diagbox: ViewBox of the diagram
                ticks: Tick names and positions
                boxw: Width of legend box
                boxh: Height of legend box
        '''
        xright = 0
        ytop = diagbox.y + diagbox.h - 1
        if self._legend in ['left', 'topleft']:
            xright = diagbox.x + boxw + 1
        elif self._legend in ['right', 'topright']:
            xright = diagbox.x + diagbox.w - 1
        elif self._legend == 'bottomleft':
            ytop = diagbox.y + boxh + 1
            xright = diagbox.x + boxw + 1
        else: ##if self._legend == 'bottomright':
            ytop = diagbox.y + boxh + 1
            xright = diagbox.x + diagbox.w - 1
        return ytop, xright

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        slices = [c for c in self.components if isinstance(c, PieSlice)]
        self._assign_component_colors(slices)

        values = [w.value for w in slices]
        total = sum(values)
        thetas = [v/total*math.pi*2 for v in values]
        sty = self._build_style()
        cx = canvas.viewbox.x + canvas.viewbox.w/2
        cy = canvas.viewbox.y + canvas.viewbox.h/2
        radius = (min(canvas.viewbox.w, canvas.viewbox.h) / 2 -
                  sty.margin*2)

        if any(w._extrude for w in slices):
            radius -= max(w._extrude for w in slices)

        if self._title:
            tsty = self._build_style('Graph.Title')
            radius -= tsty.font_size/2
            cy -= tsty.font_size/2
            canvas.text(cx, canvas.viewbox.y+canvas.viewbox.h,
                        self._title, font=tsty.font,
                        size=tsty.font_size,
                        color=tsty.get_color(),
                        halign='center', valign='top')

        if len(slices) == 1:
            slice = slices[0]
            slicestyle = slice._build_style()
            canvas.circle(cx, cy, radius,
                          color=slicestyle.get_color(),
                          strokecolor=slicestyle.edge_color,
                          strokewidth=slicestyle.stroke_width)

            if self.labelmode == 'name':
                labeltext = slice._name
            elif self.labelmode == 'value':
                labeltext = format(slice.value)
            elif self.labelmode == 'percent':
                labeltext = f'{slice.value/total*100:.1f}%'
            else:
                labeltext = ''
            if labeltext:
                tsty = self._build_style('PieSlice.Text')
                canvas.text(cx + radius * math.cos(math.pi/4),
                            cy + radius * math.sin(math.pi/4),
                            labeltext,
                            font=tsty.font,
                            size=tsty.font_size,
                            color=tsty.get_color())

        else:
            theta = -math.pi/2  # Current angle, start at top
            for i, slice in enumerate(slices):
                thetahalf = theta + thetas[i]/2
                slicestyle = slice._build_style()

                if slice._extrude:
                    cxx = cx + slice._extrude * math.cos(thetahalf)
                    cyy = cy - slice._extrude * math.sin(thetahalf)
                else:
                    cxx = cx
                    cyy = cy

                canvas.wedge(cxx, cyy, radius, thetas[i], starttheta=theta,
                             color=slicestyle.get_color(),
                             strokecolor=slicestyle.edge_color,
                             strokewidth=slicestyle.stroke_width)

                tstyle = self._build_style('PieSlice.Text')
                labelx = cxx + (radius+tstyle.margin) * math.cos(thetahalf)
                labely = cyy - (radius+tstyle.margin) * math.sin(thetahalf)
                halign: Halign = 'left' if labelx > cx else 'right'
                valign: Valign = 'bottom' if labely > cy else 'top'
                if self.labelmode == 'name':
                    labeltext = slice._name
                elif self.labelmode == 'value':
                    labeltext = format(slice.value)
                elif self.labelmode == 'percent':
                    labeltext = f'{slice.value/total*100:.1f}%'
                else:
                    labeltext = ''

                if labeltext:
                    canvas.text(labelx, labely,
                                labeltext,
                                font=tstyle.font,
                                size=tstyle.font_size,
                                color=tstyle.get_color(),
                                halign=halign, valign=valign)

                theta += thetas[i]

        if self._legend and self._legend != 'none':
            ticks = Ticks(xticks=None, yticks=None, xnames=None, ynames=None,
                          ywidth=0, xrange=None, yrange=None, xminor=None, yminor=None)
            self._drawlegend(canvas, canvas.viewbox, ticks)
