''' Polar plotting axis '''

from __future__ import annotations
from typing import Optional, Sequence
import math
import xml.etree.ElementTree as ET

from .axes import BasePlot, getticks, LegendLoc, Ticks
from .canvas import Canvas, ViewBox, DataRange, Halign, Valign
from .dataseries import Line
from .styletypes import Style


class Polar(BasePlot):
    ''' Polar Plot. Use with LinePolar to define series in (radius, angle)
        format.

        Args:
            labeldeg: Draw theta labels in degrees vs. radians
            title: Title to draw above axes
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def __init__(self, labeldeg: bool = True, title: Optional[str] = None, legend: LegendLoc = 'left',
                 style: Optional[Style] = None):
        super().__init__(title=title, legend=legend, style=style)
        self.labeldegrees = labeldeg

    def rrange(self, rmax: float) -> None:
        ''' Sets maximum radius to display '''
        self.xrange(0, rmax)

    def yrange(self, ymin: float, ymax: float) -> None:
        ''' Sets range of y data '''
        raise ValueError('Cannot set y (theta) range on polar plot')

    def _maketicks(self, datarange: DataRange) -> Ticks:
        ''' Generate tick names and positions. Y/Theta ticks are always
            0 to 360, but can be degrees or radians. X/Radius ticks
            depend on the data, but always start at 0.
        '''
        _, xmax, _, _ = datarange
        if self._xtickvalues:
            xticks = self._xtickvalues
            xmax = max(xmax, max(xticks))
        else:
            xticks = getticks(0, xmax, maxticks=6)
            xmax = xticks[-1]

        xnames = self._xticknames
        if xnames is None:
            xnames = [format(xt, self.style.tick.xstrformat) for xt in xticks]

        yticks = [0, 45, 90, 135, 180, 225, 270, 315]
        if self.labeldegrees:
            ynames = [f'{i}°' for i in yticks]
        else:
            ynames = ['0', 'π/4', 'π/2', '3π/4', 'π', '5π/4', '3π/2', '7π/4']
        ticks = Ticks(xticks, yticks, xnames, ynames, 0, (0, xmax), (0, 360), None, None)
        return ticks

    def _drawframe(self, canvas: Canvas, ticks: Ticks) -> tuple[float, float, float]:
        ''' Draw the axis frame, ticks, and grid

            Args:
                canvas: SVG canvas to draw on
                ticks: Tick names and positions
        '''
        radius = min(canvas.viewbox.w, canvas.viewbox.h) / 2 - self.style.polar.edgepad*2
        cx = canvas.viewbox.x + canvas.viewbox.w/2
        cy = canvas.viewbox.y + canvas.viewbox.h/2

        if self.title:
            radius -= self.style.polar.title.size/2
            cy -= self.style.polar.title.size/2
            canvas.text(canvas.viewbox.w/2, canvas.viewbox.h,
                        self.title, font=self.style.polar.title.font,
                        size=self.style.polar.title.size,
                        color=self.style.polar.title.color,
                        halign='center', valign='top')

        canvas.circle(cx, cy, radius, color=self.style.axis.bgcolor,
                      strokecolor=self.style.axis.color,
                      strokewidth=self.style.axis.framelinewidth)

        for i, rname in enumerate(ticks.xnames):
            if i in [0, len(ticks.xnames)-1]:
                continue
            r = radius / (len(ticks.xticks)-1) * i
            canvas.circle(cx, cy, r, strokecolor=self.style.axis.gridcolor,
                          strokewidth=self.style.axis.gridlinewidth,
                          color='none', stroke=self.style.axis.gridstroke)

            textx = cx + r * math.cos(math.radians(self.style.polar.rlabeltheta))
            texty = cy + r * math.sin(math.radians(self.style.polar.rlabeltheta))
            canvas.text(textx, texty, rname, halign='center',
                        color=self.style.tick.text.color)

        for i, (theta, tname) in enumerate(zip(ticks.yticks, ticks.ynames)):
            thetarad = math.radians(theta)
            x = radius * math.cos(thetarad)
            y = radius * math.sin(thetarad)
            canvas.path([cx, cx+x], [cy, cy+y],
                        color=self.style.axis.gridcolor,
                        width=self.style.axis.gridlinewidth,
                        stroke=self.style.axis.gridstroke)

            labelx = cx + (radius+self.style.polar.labelpad) * math.cos(-thetarad)
            labely = cy - (radius+self.style.polar.labelpad) * math.sin(-thetarad)
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
                        color=self.style.tick.text.color)
        return radius, cx, cy

    def _drawseries(self, canvas: Canvas, radius: float,
                    cx: float, cy: float, ticks: Ticks) -> None:
        ''' Draw all data series

            Args:
                canvas: SVG canvas to draw on
                radius: radius of full circle
                cx, cy: canvas center of full circle
                ticks: Tick definitions
        '''
        colorseries = [s for s in self.series if s.__class__.__name__ != 'Text']
        self.style.colorcycle.steps(len(colorseries))

        for i, s in enumerate(colorseries):
            if s.style.line.color == 'undefined':
                s.style.line.color = self.style.colorcycle[i]
            elif s.style.line.color.startswith('C') and s.style.line.color[1:].isnumeric():
                # Convert things like 'C1'
                s.style.line.color = self.style.colorcycle[s.style.line.color]

            if s.style.marker.color == 'undefined':
                s.style.marker.color = self.style.colorcycle[i]
            elif s.style.marker.color.startswith('C') and s.style.marker.color[1:].isnumeric():
                s.style.marker.color = self.style.colorcycle[s.style.marker.color]

        dradius = ticks.xticks[-1]
        databox = ViewBox(-dradius, -dradius, dradius*2, dradius*2)
        viewbox = ViewBox(cx-radius, cy-radius, radius*2, radius*2)
        canvas.setviewbox(viewbox)
        for s in self.series:
            s._xml(canvas, databox=databox)
        canvas.resetviewbox()

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        datarange = self.datarange()
        ticks = self._maketicks(datarange)
        radius, cx, cy = self._drawframe(canvas, ticks)
        axbox = ViewBox(cx-radius, cy-radius, radius*2, radius*2)
        self._drawseries(canvas, radius, cx, cy, ticks)
        self._drawlegend(canvas, axbox, ticks)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' XML for standalone SVG '''
        canvas = Canvas(self.style.canvasw, self.style.canvash,
                        fill=self.style.bgcolor)
        self._xml(canvas)
        if border:
            attrib = {'x': '0', 'y': '0',
                      'width': '100%', 'height': '100%',
                      'fill': 'none', 'stroke': 'black'}
            ET.SubElement(canvas.group, 'rect', attrib=attrib)
        return canvas.xml()


class LinePolar(Line):
    ''' Define a data Line series using polar coordinates

        Args:
            radius: The radius values to plot
            theta: The theta values to plot, in degres or radians
            deg: Interpret theta as degrees instead of radians
    '''
    def __init__(self, radius: Sequence[float], theta: Sequence[float], deg: bool = False):
        self.radius = radius
        self.theta = theta
        if deg:
            self.theta = [math.radians(t) for t in theta]
        x = [r * math.cos(t) for r, t in zip(self.radius, self.theta)]
        y = [r * math.sin(t) for r, t in zip(self.radius, self.theta)]
        super().__init__(x, y)
