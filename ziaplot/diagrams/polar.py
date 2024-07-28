''' Polar plotting '''
from __future__ import annotations
from typing import Optional
from functools import lru_cache
import math

from ..text import Halign, Valign
from .diagram import Diagram, Ticks
from .graph import getticks
from ..canvas import Canvas, Borders, ViewBox


class GraphPolar(Diagram):
    ''' Polar Plot. Use with LinePolar to define lines in (radius, angle)
        format.

        Args:
            labeldeg: Draw theta labels in degrees vs. radians
            labeltheta: Angle for drawing R labels
    '''
    def __init__(self, labeldeg: bool = True, labeltheta: float = 0):
        super().__init__()
        self.labeldegrees = labeldeg
        self.labeltheta: float = labeltheta

    def rrange(self, rmax: float) -> None:
        ''' Sets maximum radius to display '''
        self.xrange(0, rmax)

    def yrange(self, ymin: float, ymax: float) -> None:
        ''' Sets range of y data '''
        raise ValueError('Cannot set y (theta) range on polar plot')

    def _clearcache(self):
        ''' Clear the LRU cache when inputs change '''
        super()._clearcache()
        self._maketicks.cache_clear()

    @lru_cache
    def _maketicks(self) -> Ticks:
        ''' Generate tick names and positions. Y/Theta ticks are always
            0 to 360, but can be degrees or radians. X/Radius ticks
            depend on the data, but always start at 0.
        '''
        xsty = self._build_style('Graph.TickX')
        _, xmax, _, _ = self.datarange()
        if self._xtickvalues:
            xticks = self._xtickvalues
            xmax = max(xmax, max(xticks))
        else:
            xticks = getticks(0, xmax, maxticks=6)
            xmax = xticks[-1]

        xnames = self._xticknames
        if xnames is None:
            xnames = [format(xt, xsty.num_format) for xt in xticks]

        yticks = [0, 45, 90, 135, 180, 225, 270, 315]
        if self.labeldegrees:
            ynames = [f'{i}°' for i in yticks]
        else:
            ynames = ['0', 'π/4', 'π/2', '3π/4', 'π', '5π/4', '3π/2', '7π/4']
        ticks = Ticks(xticks, yticks, xnames, ynames, 0, (0, xmax), (0, 360), None, None)
        return ticks

    def _drawframe(self, canvas: Canvas, ticks: Ticks) -> tuple[float, float, float]:
        ''' Draw the graph frame, ticks, and grid

            Args:
                canvas: SVG canvas to draw on
                ticks: Tick names and positions
        '''
        sty = self._build_style()
        gridsty = self._build_style('Graph.GridX')
        ticksty = self._build_style('Graph.TickX')
        radius = min(canvas.viewbox.w, canvas.viewbox.h) / 2 - sty.pad*2 - sty.font_size*2
        cx = canvas.viewbox.x + canvas.viewbox.w/2
        cy = canvas.viewbox.y + canvas.viewbox.h/2

        if self._title:
            tsty = self._build_style('Graph.Title')
            radius -= tsty.font_size/2
            cy -= tsty.font_size/2
            canvas.text(canvas.viewbox.w/2, canvas.viewbox.h,
                        self._title, font=tsty.font,
                        size=tsty.font_size,
                        color=tsty.get_color(),
                        halign='center', valign='top')

        canvas.circle(cx, cy, radius, color=sty.get_color(),
                      strokecolor=sty.edge_color,
                      strokewidth=sty.edge_width)

        for i, rname in enumerate(ticks.xnames):
            if i in [0, len(ticks.xnames)-1]:
                continue
            r = radius / (len(ticks.xticks)-1) * i
            canvas.circle(cx, cy, r, strokecolor=gridsty.get_color(),
                          strokewidth=gridsty.stroke_width,
                          color='none', stroke=gridsty.stroke)

            textx = cx + r * math.cos(math.radians(self.labeltheta))
            texty = cy + r * math.sin(math.radians(self.labeltheta))
            canvas.text(textx, texty, rname, halign='center',
                        color=ticksty.get_color())

        for i, (theta, tname) in enumerate(zip(ticks.yticks, ticks.ynames)):
            thetarad = math.radians(theta)
            x = radius * math.cos(thetarad)
            y = radius * math.sin(thetarad)
            canvas.path([cx, cx+x], [cy, cy+y],
                        color=gridsty.get_color(),
                        width=gridsty.stroke_width,
                        stroke=gridsty.stroke)

            labelx = cx + (radius+sty.margin) * math.cos(-thetarad)
            labely = cy - (radius+sty.margin) * math.sin(-thetarad)
            halign: Halign
            valign: Valign
            if abs(labelx - cx) < .1:
                halign = 'center'
            elif labelx > cx:
                halign = 'left'
            else:
                halign = 'right'
            if abs(labely - cy) < .1:
                valign = 'center'
            elif labely > cy:
                valign = 'bottom'
            else:
                valign = 'top'

            canvas.text(labelx, labely, tname, halign=halign, valign=valign,
                        color=ticksty.get_color())
        return radius, cx, cy

    def _draw_polarcontents(self, canvas: Canvas, radius: float,
                            cx: float, cy: float, ticks: Ticks) -> None:
        ''' Draw all components

            Args:
                canvas: SVG canvas to draw on
                radius: radius of full circle
                cx, cy: canvas center of full circle
                ticks: Tick definitions
        '''
        self._assign_component_colors(self.components)

        dradius = ticks.xticks[-1]
        databox = ViewBox(-dradius, -dradius, dradius*2, dradius*2)
        viewbox = ViewBox(cx-radius, cy-radius, radius*2, radius*2)
        canvas.setviewbox(viewbox)
        for f in self.components:
            f._xml(canvas, databox=databox)
        canvas.resetviewbox()

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        ticks = self._maketicks()
        radius, cx, cy = self._drawframe(canvas, ticks)
        axbox = ViewBox(cx-radius, cy-radius, radius*2, radius*2)
        self._draw_polarcontents(canvas, radius, cx, cy, ticks)
        self._drawlegend(canvas, axbox, ticks)
