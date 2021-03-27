''' Pie Charts '''

from __future__ import annotations
from typing import Optional, Literal
import math
from dataclasses import dataclass
import xml.etree.ElementTree as ET

from .colors import ColorFade
from .styletypes import Style
from . import styles
from .canvas import Canvas, ViewBox, Halign, Valign
from . import text
from .drawable import Drawable


@dataclass
class Wedge:
    ''' Parameters for a single wedge of a pie '''
    value: float = 1
    name: str = ''
    color: Optional[str] = None
    strokecolor: str = 'black'
    strokewidth: float = 1
    extrude: bool = False


class Pie(Drawable):
    ''' Pie Chart. Total of all wedge values will always be normalized to 100%.

        Args:
            title: Title of the chart
            labels: How to label each wedge
            legend: Location for legend
            style: Plotting style
    '''
    def __init__(self, title: str=None,
                 labels: Literal['name', 'percent', 'value', None]='name',
                 legend: str=None, style: Style=None):
        self.style = style if style is not None else styles.Default()
        self.legend = legend
        self.labels = labels   # 'name', 'value', or 'percent'
        self.title = title
        self.wedgelist: list[Wedge] = []

    def wedges(self, *values: float) -> Pie:
        ''' Add multiple wedges to the pie '''
        for w in values:
            self.wedge(w)
        return self

    def names(self, *names: str) -> Pie:
        ''' Define names of each wedge added by `wedges` method. '''
        for w, n in zip(self.wedgelist, names):
            w.name = n
        return self

    def wedge(self, value: float, name: str='', color: str=None,
              strokecolor: str=None, strokewidth: float=None,
              extrude: bool=False) -> Pie:
        ''' Add a wedge to the pie.

            Args:
                value: The value for this wedge. Total value will be normalized to 100%.
                name: Name for the wedge to include in legend
                color: Color for the wedge
                strokecolor: Color for the wedge border
                strokewidth: Line width of the wedge border
                extrude: Show the wedge pulled out from the pie
        '''
        strokecolor = strokecolor if strokecolor else self.style.pie.strokecolor
        strokewidth = strokewidth if strokewidth else self.style.pie.strokewidth
        self.wedgelist.append(Wedge(value=value,
                                    name=name,
                                    color=color,  # type: ignore
                                    strokecolor=strokecolor,
                                    strokewidth=strokewidth,
                                    extrude=extrude))
        return self

    def colorfade(self, c1: str, c2: str) -> None:
        ''' Define the color cycle evenly fading between two colors.
            `c1` will always be the color of the first series, and `c2`
            the color of the last series, with an even gradient for
            series in between.

            Args:
                c1: Starting color
                c2: Ending color
        '''
        self.style.colorcycle = ColorFade(c1, c2)

    def _legendsize(self) -> tuple[float, float]:
        ''' Calculate size of legend '''
        names = [w.name for w in self.wedgelist if w.name]
        if self.legend is None or len(names) == 0:
            return 0, 0

        boxh = 0.
        boxw = 0.
        square = 16.

        for name in names:
            width = text.text_size(name, fontsize=self.style.legend.text.size,
                                    font=self.style.legend.text.font).width
            boxw = max(boxw, square + width + 5)
            boxh += self.style.legend.text.size + 2
        boxh += 4  # Top and bottom
        return boxw, boxh

    def _drawlegend(self, canvas: Canvas):
        ''' Draw legend on the canvas '''
        wedges = [w for w in self.wedgelist if w.name]
        if len(wedges) == 0: return

        canvas.newgroup()
        boxw, boxh = self._legendsize()
        square = 10

        ytop = canvas.viewbox.y + canvas.viewbox.h
        if self.legend == 'right':
            xleft = canvas.viewbox.x + canvas.viewbox.w - boxw
        else:  # self.legend == 'left':
            xleft = canvas.viewbox.x + 1

        # Draw the box
        if self.style.legend.border not in [None, 'none']:
            legbox = ViewBox(xleft, ytop-boxh, boxw, boxh)
            canvas.rect(legbox.x, legbox.y, legbox.w, legbox.h,
                        strokewidth=1,
                        rcorner=5,
                        strokecolor=self.style.legend.border)

        # Draw each name
        for i, wedge in enumerate(wedges):
            yytext = ytop - 4 - i*(self.style.legend.text.size+2)
            yysquare = yytext - square
            canvas.text(xleft + square + 8, yytext,
                        wedge.name,
                        font=self.style.legend.text.font,
                        size=self.style.legend.text.size,
                        color=self.style.legend.text.color,
                        halign='left', valign='top')
            canvas.rect(xleft+4, yysquare, square, square,
                        fill=wedge.color, strokewidth=1)

    def _xml(self, canvas: Canvas, databox: ViewBox=None) -> None:
        ''' Add XML elements to the canvas '''
        values = [w.value for w in self.wedgelist]
        total = sum(values)
        thetas = [v/total*math.pi*2 for v in values]

        cx = canvas.viewbox.x + canvas.viewbox.w/2
        cy = canvas.viewbox.y + canvas.viewbox.h/2

        radius = (min(canvas.viewbox.w, canvas.viewbox.h) / 2 -
                  self.style.pie.edgepad*2)

        if any([w.extrude for w in self.wedgelist]):
            radius -= self.style.pie.extrude

        if self.title:
            radius -= self.style.pie.title.size/2
            cy -= self.style.pie.title.size/2
            canvas.text(cx, canvas.viewbox.y+canvas.viewbox.h,
                        self.title, font=self.style.pie.title.font,
                        size=self.style.pie.title.size,
                        color=self.style.pie.title.color,
                        halign='center', valign='top')

        if len(self.wedgelist) == 1:
            w = self.wedgelist[0]
            if w.color is None:
                w.color = self.style.colorcycle[0]
            elif w.color.startswith('C'):
                w.color = self.style.colorcycle[w.color]

            canvas.circle(cx, cy, radius,
                          color=w.color,  # type: ignore
                          strokecolor=w.strokecolor,
                          strokewidth=w.strokewidth)

            if self.labels:
                if self.labels is True or self.labels == 'name':
                    labeltext = w.name
                elif self.labels == 'value':
                    labeltext = format(w.value)
                elif self.labels == 'percent':
                    labeltext = f'{w.value/total*100:.1f}%'
                else:
                    labeltext = ''
                
                canvas.text(cx + radius * math.cos(math.pi/4),
                            cy + radius * math.sin(math.pi/4),
                            labeltext,
                            font=self.style.pie.label.font,
                            size=self.style.pie.label.size,
                            color=self.style.pie.label.color)

        else:
            theta = -math.pi/2  # Current wedge angle, start at top
            self.style.colorcycle.steps(len(self.wedgelist))
            for i, w in enumerate(self.wedgelist):
                thetahalf = theta + thetas[i]/2

                if w.color is None:
                    w.color = self.style.colorcycle[i]
                elif w.color.startswith('C'):
                    w.color = self.style.colorcycle[w.color]

                if w.extrude:
                    cxx = cx + self.style.pie.extrude * math.cos(thetahalf)
                    cyy = cy - self.style.pie.extrude * math.sin(thetahalf)
                else:
                    cxx = cx
                    cyy = cy

                canvas.wedge(cxx, cyy, radius, thetas[i], starttheta=theta,
                             color=w.color,  # type: ignore
                             strokecolor=w.strokecolor,
                             strokewidth=w.strokewidth)

                if self.labels:
                    labelx = cxx + (radius+self.style.pie.labelpad) * math.cos(thetahalf)
                    labely = cyy - (radius+self.style.pie.labelpad) * math.sin(thetahalf)
                    halign: Halign = 'left' if labelx > cx else 'right'
                    valign: Valign = 'bottom' if labely > cy else 'top'
                    if self.labels is True or self.labels == 'name':
                        labeltext = w.name
                    elif self.labels == 'value':
                        labeltext = format(w.value)
                    elif self.labels == 'percent':
                        labeltext = f'{w.value/total*100:.1f}%'
                    else:
                        labeltext = ''

                    canvas.text(labelx, labely,
                                labeltext,
                                font=self.style.pie.label.font,
                                size=self.style.pie.label.size,
                                color=self.style.pie.label.color,
                                halign=halign, valign=valign)

                theta += thetas[i]

        if self.legend:
            self._drawlegend(canvas)

    def svgxml(self, border: bool=False) -> ET.Element:
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
