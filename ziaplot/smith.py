''' Smith chart axis '''

from __future__ import annotations
from typing import Optional

import math
from collections import namedtuple
import xml.etree.ElementTree as ET

from .styletypes import Style
from .axes import getticks, Ticks, LegendLoc
from .series import Series
from .polar import Polar
from .canvas import Canvas, ViewBox, DataRange

ArcType = namedtuple('ArcType', ['x', 'y', 'r', 't1', 't2'])


def circle_intersect(c1: tuple[float, float], c2: tuple[float, float],
                     r1: float, r2: float) -> Optional[tuple[tuple[float, float], tuple[float, float]]]:
    ''' Find intersections of two circles

        Args:
            c1: center (x, y) of first circle
            c2: center (x, y) of second circle
            r1: radius of first circle
            r2: radius of second circle

        Returns:
            c1: First intersection (x, y)
            c2: Second intersection (x, y)
    '''
    x1, y1 = c1
    x2, y2 = c2
    dx, dy = x2-x1, y2-y1
    dist = math.sqrt(dx*dx + dy*dy)

    if dist > r1+r2 or dist < abs(r1-r2):
        return None  # No intersections
    elif dist == 0 and r1 == r2:
        return None  # Identical

    a = (r1*r1 - r2*r2 + dist*dist) / (2*dist)
    h = math.sqrt(r1*r1 - a*a)
    xm = x1 + a*dx/dist
    ym = y1 + a*dy/dist
    xs1 = xm + h*dy/dist
    xs2 = xm - h*dy/dist
    ys1 = ym - h*dx/dist
    ys2 = ym + h*dx/dist
    return (xs1, ys1), (xs2, ys2)


def circle_intersect_theta(c1: tuple[float, float], c2: tuple[float, float],
                           r1: float, r2: float) -> Optional[float]:
    ''' Get end angle of arc for reactance lines '''
    x1, y1 = c1
    try:
        (xs1, ys1), (xs2, ys2) = circle_intersect(c1, c2, r1, r2)  # type: ignore
    except (TypeError, ValueError):
        return None
    theta1 = math.atan2(ys1-y1, xs1-x1)
    theta2 = math.atan2(ys2-y1, xs2-x1)
    # one is always 0 on smith charts - return positive one
    return math.degrees(max(theta1, theta2, key=abs))  # type: ignore


def const_resist_circle(r: float, xmin: float = -math.inf, xmax: float = math.inf) -> ArcType:
    ''' Circle of constant resistance

        Args:
            r: resistance (normalized to 1.0)

        Returns:
            centerx: Center of circle X
            centery: Center of circle Y
            radius: Radius of circle
            theta1: Start angle of arc (if xmin or xmax provided)
            theta2: End angle of arc (if xmin or xmax provided)
    '''
    if r == 0:
        centerx = 0.
        radius = 1.
    elif math.isfinite(r):
        left = 2/(1/r+1) - 1
        centerx = (left+1)/2
        radius = abs(left-1)/2
    else:
        centerx = 1.
        radius = 0.
    centery = 0.

    theta1 = theta2 = None
    if math.isfinite(xmin) or math.isfinite(xmax):
        if xmin == 0:
            theta1 = 180.
        else:
            arc = const_react_arc(abs(xmin), r)
            tx = arc.x + arc.r * math.cos(math.radians(arc.t1))  # Absolute xy
            ty = arc.y + arc.r * math.sin(math.radians(arc.t1))
            theta1 = math.degrees(math.atan2(ty, tx-centerx))  # Angle wrt center of R circle
            if xmin < 0:
                theta1 *= -1

        if xmax == 0:
            theta2 = 180.
        else:
            arc2 = const_react_arc(abs(xmax), rmin=r)
            tx = arc2.x + arc2.r * math.cos(math.radians(arc2.t1))
            ty = arc2.y + arc2.r * math.sin(math.radians(arc2.t1))
            theta2 = math.degrees(math.atan2(ty, tx-centerx))
            if xmax < 0:
                theta2 *= -1
                theta2, theta1 = theta1, theta2

    return ArcType(centerx, centery, radius, theta2, theta1)


def const_react_arc(x: float, rmin: float = 0,
                    rmax: float = math.inf) -> ArcType:
    ''' Arc of constant reactance

        Args:
            x: reactance (normalized to 1.0)
            a1: minimum resistance circle
            a2: maximum resistance circle

        Returns:
            centerx: Center X of arc
            centery: Center Y of arc
            radius: Radius of arc
            theta1: Angle (degrees) of arc end point
            theta2: Angle (degrees) of acr start point (270 if a2 not defined)
    '''
    radius = 1/x

    # At what angle does the const-x arc intersect the unit circle
    if rmin == 0:
        circ1 = ArcType(0., 0., 1., 0., 0.)
    else:
        circ1 = const_resist_circle(rmin)  # type: ignore

    theta1 = circle_intersect_theta((1, radius), (circ1.x, circ1.y), radius, circ1.r)
    if math.isfinite(rmax):
        circ2 = const_resist_circle(rmax)
        theta2 = circle_intersect_theta((1, radius), (circ2.x, circ2.y), radius, circ2.r)
    else:
        theta2 = 270
    centery = radius
    centerx = 1
    return ArcType(centerx, centery, radius, theta1, theta2)


class Smith(Polar):
    ''' Smith Chart Axis

        Args:
            grid: Smith grid spacing
            title: Title to draw above axes
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def __init__(self, grid: str = 'coarse', title: Optional[str] = None,
                 legend: LegendLoc = 'left', style: Optional[Style] = None):
        super().__init__(title=title, legend=legend, style=style)
        if grid not in self.style.smith.grid:
            raise ValueError(f'Undefined grid type {grid}. Avaliable grids are '
                             + ', '.join(self.style.smith.grid.keys()))
        self.grid = grid

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
            canvas.text(canvas.viewbox.x + canvas.viewbox.w/2,
                        canvas.viewbox.y + canvas.viewbox.h,
                        self.title, font=self.style.polar.title.font,
                        size=self.style.polar.title.size,
                        color=self.style.polar.title.color,
                        halign='center', valign='top')

        # Fill/background circle
        canvas.circle(cx, cy, radius, color=self.style.axis.bgcolor,
                      strokecolor='none',
                      strokewidth=self.style.axis.framelinewidth)

        dest = ViewBox(cx-radius, cy-radius, radius*2, radius*2)
        src = ViewBox(-1, -1, 2, 2)
        canvas.setviewbox(dest, clippad=5)

        # Arcs of constant reactance
        for b, rmax, rmin, major in self.style.smith.grid.get(self.grid).arcs:    # type: ignore
            arc = const_react_arc(b, rmin, rmax)
            color = self.style.smith.majorcolor if major else self.style.smith.minorcolor
            width = self.style.smith.majorwidth if major else self.style.smith.minorwidth

            canvas.arc(arc.x, arc.y, arc.r,
                       theta1=arc.t1,
                       theta2=arc.t2,
                       strokecolor=color,
                       strokewidth=width,
                       dataview=src)
            canvas.arc(arc.x, -arc.y, arc.r, theta1=-arc.t2, theta2=-arc.t1,
                       strokecolor=color,
                       strokewidth=width,
                       dataview=src)

            tx = arc.x + arc.r * math.cos(math.radians(arc.t1))
            ty = arc.y + arc.r * math.sin(math.radians(arc.t1))
            ttheta = math.atan2(ty, tx)
            tx += .01 * math.cos(ttheta)
            ty += .01 * math.sin(ttheta)
            if major:
                canvas.text(tx, ty, format(b, '.1f' if b < 10 else '.0f'),
                            color='black',
                            size=10, rotate=arc.t1-180, halign='center', valign='bottom',
                            dataview=src)
                canvas.text(tx, -ty, format(-b, '.1f' if b < 10 else '.0f'),
                            color='black',
                            size=10, rotate=180-arc.t1, halign='center', valign='top',
                            dataview=src)

        # Circles of constant resistance
        for a, xmax, xmin, major in self.style.smith.grid.get(self.grid).circles:  # type: ignore
            if xmin == 0:
                xmin = -xmax
            arc = const_resist_circle(a, xmin, xmax)
            color = self.style.smith.majorcolor if major else self.style.smith.minorcolor
            width = self.style.smith.majorwidth if major else self.style.smith.minorwidth

            if arc.t1 == arc.t2:
                canvas.circle(arc.x, arc.y, arc.r,
                              strokecolor=color,
                              strokewidth=width, color='none',
                              dataview=src)
            elif xmin == -xmax:
                canvas.arc(arc.x, arc.y, arc.r, theta1=arc.t1, theta2=arc.t2,
                           strokecolor=color,
                           strokewidth=width,
                           dataview=src)
            else:
                canvas.arc(arc.x, arc.y, arc.r, theta1=arc.t1, theta2=arc.t2,
                           strokecolor=color,
                           strokewidth=width,
                           dataview=src)
                canvas.arc(arc.x, arc.y, arc.r, theta1=-arc.t2, theta2=-arc.t1,
                           strokecolor=color,
                           strokewidth=width,
                           dataview=src)

            if major:
                canvas.text(arc.x-arc.r-.01, arc.y+.01,
                            format(a, '.1f' if a < 10 else '.0f'),
                            color='black',
                            size=10, rotate=90,
                            dataview=src)

        # Horizontal
        canvas.path([-1, 1], [0, 0],
                    color=self.style.smith.majorcolor,
                    width=self.style.smith.majorwidth,
                    dataview=src)

        canvas.text(-1.01, 0, '0',
                    color='black',
                    size=10, rotate=90, halign='center', valign='bottom',
                    dataview=src)

        # Dark border circle
        canvas.circle(cx, cy, radius, color='none',
                      strokecolor=self.style.axis.color,
                      strokewidth=self.style.axis.framelinewidth)
        canvas.resetviewbox()
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

        databox = ViewBox(-1, -1, 2, 2)
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


class SmithConstResistance(Series):
    ''' Smith chart circle of constant Resistance (normalized)

        Args:
            resistance: Resistance value (0 to inf)
            xmin: Minimum reactance intersection value
            xmax: Maximum reactance intersection value

        Notes:
            Leave xmin and xmax at inf to draw full circle
    '''
    def __init__(self, resistance: float, xmin: float = -math.inf, xmax: float = math.inf):
        super().__init__()
        self.resistance = resistance
        self.xmin = xmin
        self.xmax = xmax

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None):
        ''' Add XML elements to the canvas '''
        color = self.style.line.color
        arc = const_resist_circle(self.resistance, self.xmin, self.xmax)
        if arc.t1 is not None and arc.t2 is not None:
            canvas.arc(arc.x, arc.y, arc.r, arc.t1, arc.t2,
                       strokecolor=color,
                       strokewidth=self.style.line.width,
                       dataview=databox)
        else:
            canvas.circle(arc.x, arc.y, arc.r,
                          color='none', strokecolor=color,
                          strokewidth=self.style.line.width,
                          dataview=databox)


class SmithConstReactance(Series):
    ''' Smith chart arcs of constant Reactance (normalized). Draws
        both positive and negative (capacitive and inductive) arcs.

        Args:
            reactance: Reactance value
            rmax: maximum resistance intersection value
            rmin: minimum resistance intersection value
    '''
    def __init__(self, reactance: float, rmax: float = math.inf, rmin: float = 0):
        super().__init__()
        self.reactance = abs(reactance)
        self.rmax = rmax
        self.rmin = rmin

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None):
        ''' Add XML elements to the canvas '''
        color = self.style.line.color
        arc = const_react_arc(self.reactance, rmax=self.rmax, rmin=self.rmin)
        canvas.arc(arc.x, arc.y, arc.r, theta1=arc.t1, theta2=arc.t2,
                   strokecolor=color,
                   strokewidth=self.style.line.width,
                   dataview=databox)
        canvas.arc(arc.x, -arc.y, arc.r, theta1=-arc.t2, theta2=-arc.t1,
                   strokecolor=color,
                   strokewidth=self.style.line.width,
                   dataview=databox)
