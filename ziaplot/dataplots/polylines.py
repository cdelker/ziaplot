''' Data Series Lines '''

from __future__ import annotations
from typing import Optional, Sequence
import math
import xml.etree.ElementTree as ET

from ..style import SeriesStyle, MarkerTypes, DashTypes
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..axes import XyPlot
from ..series import Series


class PolyLine(Series):
    ''' A polyline series of x-y data, points connected by line segments

        Args:
            x: X-values to plot
            y: Y-values to plot
    '''
    def __init__(self, x: Sequence[float], y: Sequence[float]):
        super().__init__()
        self.x = x
        self.y = y
        self.startmark: MarkerTypes = None
        self.endmark: MarkerTypes = None

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'PolyLine':
        ''' Define markers to show at the start and end of the line. Use defaults
            to show arrowheads pointing outward in the direction of the line.
        '''
        self.startmark = start
        self.endmark = end
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(min(self.x), max(self.x), min(self.y), max(self.y))

    def logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = [math.log10(y) for y in self.y]

    def logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.x = [math.log10(x) for x in self.x]

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        markname = None
        if self.style.marker.shape:
            markname = canvas.definemarker(self.style.marker.shape,
                                           self.style.marker.radius,
                                           self.style.marker.color,
                                           self.style.marker.strokecolor,
                                           self.style.marker.strokewidth,
                                           orient=self.style.marker.orient)
            self._markername = markname

        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(self.startmark,
                                            self.style.marker.radius,
                                            self.style.marker.color,
                                            self.style.marker.strokecolor,
                                            self.style.marker.strokewidth,
                                            orient=True)
        if self.endmark:
            endmark = canvas.definemarker(self.endmark,
                                          self.style.marker.radius,
                                          self.style.marker.color,
                                          self.style.marker.strokecolor,
                                          self.style.marker.strokewidth,
                                          orient=True)

        color = self.style.line.color
        canvas.path(self.x, self.y,
                    stroke=self.style.line.stroke,
                    color=color,
                    width=self.style.line.width,
                    markerid=markname,
                    startmarker=startmark,
                    endmarker=endmark,
                    dataview=databox)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        ax = XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)


class Scatter(PolyLine):
    ''' An X-Y Scatter series of data

        Args:
            x: X-values to plot
            y: Y-values to plot
    '''
    def __init__(self, x: Sequence[float], y: Sequence[float]):
        super().__init__(x, y)
        self.style.line.color = 'none'
        self.style.line.width = 0
        self.style.marker.shape = 'round'


class ErrorBar(PolyLine):
    ''' An X-Y PolyLine with Error Bars in X and/or Y

        Args:
            x: X-values to plot
            y: Y-values to plot
            yerr: Y errors
            xerr: X errors
    '''
    def __init__(self, x: Sequence[float], y: Sequence[float],
                 yerr: Optional[Sequence[float]] = None, xerr: Optional[Sequence[float]] = None):
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

    def yerrmarker(self, marker: MarkerTypes = '-', length: Optional[float] = None,
                   width: Optional[float] = None, stroke: Optional[DashTypes] = None) -> 'ErrorBar':
        ''' Set marker and linestyle for y-error bars

            Args:
                marker: Shape of the marker
                length: Length of the marker
                width: Linewidth of the marker
                stroke: Stroke/dash style for the errorbar line
        '''
        self.style.yerror.marker = marker
        if length:
            self.style.yerror.length = length
        if width:
            self.style.yerror.width = width
        if stroke:
            self.style.yerror.stroke = stroke
        return self

    def xerrmarker(self, marker: MarkerTypes = '|', length: Optional[float] = None,
                   width: Optional[float] = None, stroke: Optional[DashTypes] = None) -> 'ErrorBar':
        ''' Set marker and linestyle for x-error bars

            Args:
                marker: Shape of the marker
                length: Length of the marker
                width: Linewidth of the marker
                stroke: Stroke/dash style for the errorbar line
        '''
        self.style.xerror.marker = marker
        if length:
            self.style.xerror.length = length
        if width:
            self.style.xerror.width = width
        if stroke:
            self.style.xerror.stroke = stroke
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        color = self.style.line.color
        if self.yerr is not None:
            yerrmark = canvas.definemarker(self.style.yerror.marker,
                                           self.style.yerror.length,
                                           color,
                                           self.style.marker.strokecolor,
                                           self.style.yerror.width)

            for x, y, yerr in zip(self.x, self.y, self.yerr):
                canvas.path([x, x], [y-yerr, y+yerr],
                            stroke=self.style.yerror.stroke,
                            color=color,
                            width=self.style.line.width,
                            startmarker=yerrmark,
                            endmarker=yerrmark,
                            dataview=databox)
        if self.xerr is not None:
            xerrmark = canvas.definemarker(self.style.xerror.marker,
                                           self.style.xerror.length,
                                           color,
                                           self.style.marker.strokecolor,
                                           self.style.xerror.width)

            for x, y, xerr in zip(self.x, self.y, self.xerr):
                canvas.path([x-xerr, x+xerr], [y, y],
                            stroke=self.style.xerror.stroke,
                            color=color,
                            width=self.style.line.width,
                            startmarker=xerrmark,
                            endmarker=xerrmark,
                            dataview=databox)

        super()._xml(canvas, databox, borders)


class LineFill(PolyLine):
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

    def fill(self, color: str, alpha: Optional[float] = None) -> 'LineFill':
        ''' Set the region fill color and transparency

            Args:
                color: Fill color
                alpha: Transparency (0-1, with 1 being opaque)
        '''
        self.style.fillcolor = color
        if alpha:
            self.style.fillalpha = alpha
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        # Draw in two parts - filled part doesn't have a stroke
        # because we don't want lines on the left/right edge.
        # Then draw the x,ymax and x,ymin lines as paths

        xy = list(zip(self.x, self.ymax))
        xy = xy + list(reversed(list(zip(self.x, self.ymin))))

        fill = self.style.fillcolor
        alpha = self.style.fillalpha
        if fill is None:
            fill = self.style.line.color

        canvas.poly(xy, color=fill,
                    alpha=alpha,
                    strokecolor='none',
                    dataview=databox)

        markname = None
        if self.style.marker.shape:
            markname = canvas.definemarker(self.style.marker.shape,
                                           self.style.marker.radius,
                                           self.style.marker.color,
                                           self.style.marker.strokecolor,
                                           self.style.marker.strokewidth,
                                           orient=self.style.marker.orient)
            self._markername = markname

        canvas.path(self.x, self.ymax,
                    stroke=self.style.line.stroke,
                    color=self.style.line.color,
                    width=self.style.line.width,
                    markerid=markname,
                    dataview=databox)
        canvas.path(self.x, self.ymin,
                    stroke=self.style.line.stroke,
                    color=self.style.line.color,
                    width=self.style.line.width,
                    markerid=markname,
                    dataview=databox)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        ax = XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)


class Arrow(PolyLine):
    ''' An arrow pointing to an XY location, with optional
        text annotation

        Args:
            xy: XY position to point at
            xytail: XY-position of arrow tail
            s: String to draw at tail of arrow
            strofst: XY offset between text and arrow tail
            marker: Arrowhead marker shape
            tailmarker: Arrowhead tail marker
    '''
    def __init__(self, xy: Sequence[float], xytail: Sequence[float],
                 s: str = '', strofst: Sequence[float] = (0, 0),
                 marker: MarkerTypes = 'arrow', tailmarker: Optional[MarkerTypes] = None):
        self.xy = xy
        self.xytail = xytail
        self.strofst = strofst
        self.string = s

        super().__init__([self.xytail[0], self.xy[0]], [self.xytail[1], self.xy[1]])
        self.style = SeriesStyle()
        self.style.marker.strokewidth = 0
        self.endmarkers(start=tailmarker, end=marker)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        super()._xml(canvas, databox, borders=borders)
        x = self.xytail[0] + self.strofst[0]
        y = self.xytail[1] + self.strofst[1]
        canvas.text(x, y, self.string,
                    color=self.style.text.color,
                    font=self.style.text.font,
                    size=self.style.text.size,
                    dataview=databox)



Plot = PolyLine
Xy = Scatter
