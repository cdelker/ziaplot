''' Discrete Data Elements '''
from __future__ import annotations
from typing import Optional, Sequence
import xml.etree.ElementTree as ET
import math

from ..style import MarkerTypes
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..diagrams import Graph
from ..element import Element


class Discrete(Element):
    ''' Base class for elements defined by X, Y coordinate pairs '''
    _step_color = True

    def __init__(self, x: Sequence[float], y: Sequence[float]):
        super().__init__()
        self.x = x
        self.y = y
        self._marker_orient = False

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(min(self.x), max(self.x), min(self.y), max(self.y))

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = [math.log10(y) for y in self.y]

    def _logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.x = [math.log10(x) for x in self.x]

    def marker(self, marker: MarkerTypes, radius: Optional[float] = None, orient: bool = False) -> Discrete:
        ''' Sets the element marker '''
        self._style.shape = marker
        self._style.radius = radius
        self._marker_orient = orient
        return self

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        g = Graph()
        g.add(self)
        return g.svgxml(border=border)


class PolyLine(Discrete):
    ''' A polyline of x-y data, points connected by line segments

        Args:
            x: X-values to plot
            y: Y-values to plot
    '''
    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        markname = None
        if sty.shape not in [None, 'none']:
            markname = canvas.definemarker(sty.shape,
                                           sty.radius,
                                           sty.get_color(),
                                           sty.edge_color,
                                           sty.edge_width,
                                           orient=self._marker_orient)
            self._markername = markname  # For legend

        canvas.path(self.x, self.y,
                    stroke=sty.stroke,
                    color=sty.get_color(),
                    width=sty.stroke_width,
                    markerid=markname,
                    dataview=databox)


class Scatter(Discrete):
    ''' An X-Y Scatter data

        Args:
            x: X-values to plot
            y: Y-values to plot
    '''
    _step_color = True
    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        markname = canvas.definemarker(sty.shape,
                                       sty.radius,
                                       sty.get_color(),
                                       sty.edge_color,
                                       sty.edge_width,
                                       orient=self._marker_orient)
        self._markername = markname  # For legend

        canvas.path(self.x, self.y,
                    color='none',
                    markerid=markname,
                    dataview=databox)


class ErrorBar(PolyLine):
    ''' An X-Y PolyLine with Error Bars in X and/or Y

        Args:
            x: X-values to plot
            y: Y-values to plot
            yerr: Y errors
            xerr: X errors
    '''
    def __init__(self, x: Sequence[float],
                 y: Sequence[float],
                 yerr: Optional[Sequence[float]] = None,
                 xerr: Optional[Sequence[float]] = None):
        super().__init__(x, y)
        self.yerr = yerr
        self.xerr = xerr

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        if self.xerr is not None:
            xmin = min([x-xe for x, xe in zip(self.x, self.xerr)])
            xmax = max([x+xe for x, xe in zip(self.x, self.xerr)])
        else:
            xmin = min(self.x)
            xmax = max(self.x)

        if self.yerr is not None:
            ymin = min([y-ye for y, ye in zip(self.y, self.yerr)])
            ymax = max([y+ye for y, ye in zip(self.y, self.yerr)])
        else:
            ymin = min(self.y)
            ymax = max(self.y)

        return DataRange(xmin, xmax, ymin, ymax)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()
        if self.yerr is not None:
            ymarkstyle = self._build_style('ErrorBar.MarkerYError')
            ycolor = color if ymarkstyle.color == 'auto' else ymarkstyle.get_color()
            yerrmark = canvas.definemarker(ymarkstyle.shape,
                                           ymarkstyle.radius,
                                           ycolor,
                                           ycolor,
                                           ymarkstyle.edge_width)

            for x, y, yerr in zip(self.x, self.y, self.yerr):
                canvas.path([x, x], [y-yerr, y+yerr],
                            stroke=ymarkstyle.stroke,
                            color=ycolor,
                            width=ymarkstyle.stroke_width,
                            startmarker=yerrmark,
                            endmarker=yerrmark,
                            dataview=databox)
        if self.xerr is not None:
            xmarkstyle = self._build_style('ErrorBar.MarkerXError')
            xcolor = color if xmarkstyle.color == 'auto' else xmarkstyle.get_color()
            xerrmark = canvas.definemarker(xmarkstyle.shape,
                                           xmarkstyle.radius,
                                           xcolor,
                                           xcolor,
                                           xmarkstyle.edge_width)

            for x, y, xerr in zip(self.x, self.y, self.xerr):
                canvas.path([x-xerr, x+xerr], [y, y],
                            stroke=xmarkstyle.stroke,
                            color=xcolor,
                            width=xmarkstyle.stroke_width,
                            startmarker=xerrmark,
                            endmarker=xerrmark,
                            dataview=databox)

        super()._xml(canvas, databox, borders)


class LineFill(Discrete):
    ''' A filled line/region

        Args:
            x: X-values
            ymax: Y-values defining upper limit of region
            ymin: Y-values defining lower limit of region. Defaults to 0.
    '''
    def __init__(self, x: Sequence[float], ymax: Sequence[float], ymin: Optional[Sequence[float]] = None):
        super().__init__(x, ymax)
        self.x = x
        self.ymax = ymax
        if ymin is None:
            ymin = [0] * len(self.ymax)
        self.ymin = ymin

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(min(self.x),
                         max(self.x),
                         min(min(self.ymax), min(self.ymin)),
                         max(max(self.ymax), max(self.ymin)))

    def color(self, color: str) -> 'LineFill':
        ''' Sets the edge color '''
        self._style.edge_color = color
        return self

    def fill(self, color: str) -> 'LineFill':
        ''' Set the region fill color and transparency

            Args:
                color: Fill color
        '''
        self._style.color = color
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        # Draw in two parts - filled part doesn't have a stroke
        # because we don't want lines on the left/right edge.
        # Then draw the x,ymax and x,ymin lines as paths

        xy = list(zip(self.x, self.ymax))
        xy = xy + list(reversed(list(zip(self.x, self.ymin))))

        sty = self._build_style()
        canvas.poly(xy, color=sty.get_color(),
                    strokecolor='none',
                    dataview=databox)

        canvas.path(self.x, self.ymax,
                    stroke=sty.stroke,
                    color=sty.edge_color,
                    width=sty.stroke_width,
                    dataview=databox)
        canvas.path(self.x, self.ymin,
                    stroke=sty.stroke,
                    color=sty.edge_color,
                    width=sty.stroke_width,
                    dataview=databox)


Plot = PolyLine
Xy = Scatter
