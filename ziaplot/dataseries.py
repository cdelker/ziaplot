''' Data Series Lines '''

from __future__ import annotations
from typing import Optional, Sequence, Callable
import math
from collections import Counter
import xml.etree.ElementTree as ET

from .styletypes import SeriesStyle, MarkerTypes, DashTypes
from .series import Series
from . import axes
from .canvas import Canvas, ViewBox, DataRange, Halign, Valign
from . import util


class Line(Series):
    ''' A line series of x-y data

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

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'Line':
        ''' Define markers to show at the start and end of the line. Use defaults
            to show arrowheads pointing outward in the direction of the line.
        '''
        self.startmark = start
        self.endmark = end
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(min(self.x), max(self.x), min(self.y), max(self.y))

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None):
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
        ax = axes.XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)


class Function(Line):
    ''' Plot a function

        Args:
            func: Callable function (e.g. lambda x: x**2)
            xmin: Minimum x value
            xmax: Maximum x value
            n: Number of datapoints for discrete representation
    '''
    def __init__(self, func: Callable[[float], float],
                 xmin: float = -5, xmax: float = 5, n: int = 200):
        step = (xmax-xmin) / n
        x = util.zrange(xmin, xmax, step)
        y = [func(x0) for x0 in x]
        super().__init__(x, y)


class Xy(Line):
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


class ErrorBar(Line):
    ''' An X-Y Line with Error Bars in X and/or Y

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

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
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

        super()._xml(canvas, databox)


class LineFill(Line):
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

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None):
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
        ax = axes.XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)


class Text(Series):
    ''' A text element to draw at a specific x-y location

        Args:
            x: X-position for text
            y: Y-position for text
            s: String to draw
            halign: Horizontal alignment
            valign: Vertical alignment
            rotate: Rotation angle, in degrees
    '''
    def __init__(self, x: float, y: float, s: str, halign: Halign = 'left',
                 valign: Valign = 'bottom', rotate: Optional[float] = None):
        super().__init__()
        self.style = SeriesStyle()
        self.x = x
        self.y = y
        self.s = s
        self.halign = halign
        self.valign = valign
        self.rotate = rotate

    def color(self, color: str) -> 'Text':
        ''' Sets the text color '''
        self.style.text.color = color
        return self

    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        return DataRange(None, None, None, None)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        canvas.text(self.x, self.y, self.s,
                    color=self.style.text.color,
                    font=self.style.text.font,
                    size=self.style.text.size,
                    halign=self.halign,
                    valign=self.valign,
                    rotate=self.rotate,
                    dataview=databox)


class Arrow(Line):
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

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        super()._xml(canvas, databox)
        x = self.xytail[0] + self.strofst[0]
        y = self.xytail[1] + self.strofst[1]
        canvas.text(x, y, self.string,
                    color=self.style.text.color,
                    font=self.style.text.font,
                    size=self.style.text.size,
                    dataview=databox)


class HLine(Series):
    ''' Horizontal line spanning the plot

        Args:
            y: Y-value of the line
    '''
    def __init__(self, y: float):
        super().__init__()
        self.y = y

    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        return DataRange(None, None, self.y, self.y)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        color = self.style.line.color
        xpath = ViewBox(databox.x, databox.x + databox.w, databox.w, databox.h)
        ypath = (self.y, self.y)
        canvas.path(xpath, ypath, self.style.line.stroke, color,
                    self.style.line.width, dataview=databox)


class VLine(Series):
    ''' Vertical line spanning the plot

        Args:
            x: X-value of the line
    '''
    def __init__(self, x: float):
        super().__init__()
        self.x = x

    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        return DataRange(self.x, self.x, None, None)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        assert databox is not None
        color = self.style.line.color
        xpath = (self.x, self.x)
        ypath = (databox.y, databox.y + databox.h)
        canvas.path(xpath, ypath, self.style.line.stroke, color,
                    self.style.line.width, dataview=databox)


class Bars(Series):
    ''' A series of bars to add to an XyPlot (quantitative x values)
        For qualitative bar chart, use a BarChart instance.

        Args:
            x: X-values of each bar
            y: Y-values of each bar
            y2: Minimum y-values of each bar
            width: Width of all bars
            align: Bar position in relation to x value
    '''
    def __init__(self, x: Sequence[float], y: Sequence[float], y2: Optional[Sequence[float]] = None,
                 width: Optional[float] = None, align: Halign = 'center'):
        super().__init__()
        self.x = x
        self.y = y
        self.align = align
        self.width = width if width is not None else self.x[1]-self.x[0]
        self.y2 = y2 if y2 is not None else [0] * len(self.x)

    def datarange(self):
        ''' Get x-y datarange '''
        ymin, ymax = min(self.y2), max(self.y)+max(self.y)/25
        if self.align == 'left':
            xmin, xmax = min(self.x), max(self.x)+self.width
        elif self.align == 'center':
            xmin, xmax = min(self.x)-self.width/2, max(self.x)+self.width/2
        else:  # self.align == 'right':
            xmin, xmax = min(self.x)-self.width, max(self.x)
        return DataRange(xmin, xmax, ymin, ymax)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        color = self.style.line.color
        for x, y, y2 in zip(self.x, self.y, self.y2):
            if self.align == 'center':
                x -= self.width/2
            elif self.align == 'right':
                x -= self.width

            canvas.rect(x, y2, self.width, y-y2,
                        fill=color,
                        strokecolor=self.style.border.color,
                        strokewidth=self.style.border.width,
                        dataview=databox)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        ax = axes.XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)


class BarsHoriz(Bars):
    ''' Horizontal bars '''
    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        rng = super().datarange()  # Transpose it
        return DataRange(rng.ymin, rng.ymax, rng.xmin, rng.xmax)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        color = self.style.line.color
        for x, y, y2 in zip(self.x, self.y, self.y2):
            if self.align == 'center':
                x -= self.width/2
            elif self.align in ['right', 'top']:
                x -= self.width

            canvas.rect(y2, x, y-y2,
                        self.width,
                        fill=color,
                        strokecolor=self.style.border.color,
                        strokewidth=self.style.border.width,
                        dataview=databox)


class Histogram(Bars):
    ''' Histogram data series

        Args:
            x: Data to show as histogram
            bins: Number of bins for histogram
            binrange: Tuple of (start, stop, step) defining bins
            density: Normalize the histogram
            weights: Weights to apply to each x value
    '''
    def __init__(self, x: Sequence[float], bins: Optional[int] = None,
                 binrange: Optional[tuple[float, float, float]] = None,
                 density: bool = False, weights: Optional[Sequence[float]] = None):
        xmin = min(x)
        if binrange is not None:
            binleft = binrange[0]
            binright = binrange[1]
            binwidth = binrange[2]
            bins = math.ceil((binright - binleft) / binwidth)
            binlefts = [binleft + binwidth*i for i in range(bins)]
        elif bins is None:
            bins = math.ceil(math.sqrt(len(x)))
            binwidth = (max(x) - xmin) / bins
            binlefts = [xmin + binwidth*i for i in range(bins)]
            binright = binlefts[-1] + binwidth
        else:
            binwidth = (max(x) - xmin) / bins
            binlefts = [xmin + binwidth*i for i in range(bins)]
            binright = binlefts[-1] + binwidth

        binr = binright-binlefts[0]
        xnorm = [(xx-binlefts[0])/binr * bins for xx in x]
        xint = [math.floor(v) for v in xnorm]

        if weights is None:
            counter = Counter(xint)
            counts: list[float] = [counter[xx] for xx in range(bins)]
            if binrange is None:
                # If auto-binning, need to include rightmost endpoint
                counts[-1] += counter[bins]
        else:  # weighed
            counts = [0] * bins
            for w, b in zip(weights, xint):
                try:
                    counts[b] += w
                except IndexError:
                    if b == len(counts) and binrange is None:
                        # If auto-binning, need to include rightmost endpoint
                        counts[-1] += w

        if density:
            cmax = sum(counts) * binwidth
            counts = [c/cmax for c in counts]

        super().__init__(binlefts, counts, align='left')
