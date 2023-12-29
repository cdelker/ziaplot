''' Axes for plotting one or more data series '''

from __future__ import annotations
from typing import Sequence, Optional, Literal
import math
from collections import namedtuple
import xml.etree.ElementTree as ET

from . import styles
from .styletypes import Style
from .series import Series
from . import colors
from .canvas import Canvas, Transform, ViewBox, DataRange
from . import text
from .drawable import Drawable
from .util import zrange, linspace
from . import axis_stack


Ticks = namedtuple('Ticks', ['xticks', 'yticks', 'xnames', 'ynames',
                             'ywidth', 'xrange', 'yrange', 'xminor', 'yminor'])

LegendLoc = Literal['left', 'right', 'none']


def getticks(vmin: float, vmax: float, maxticks: int = 9, fmt: str = 'g') -> list[float]:
    ''' Attempt to find reasonable tick locations given data bounds

        Args:
            vmin: Minimum data value
            vmax: Maximum data value
            maxticks: Maximum number of ticks
    '''
    def round_dn(val, nearest=1):
        return math.floor(val/nearest) * nearest

    def round_up(val, nearest=1):
        return math.ceil(val/nearest) * nearest

    vmax = float(format(vmax, fmt))
    vmin = float(format(vmin, fmt))

    diff = vmax - vmin
    if not math.isfinite(diff) or diff == 0:
        ticks = zrange(-1, 1, 0.5)
        return ticks
    elif diff > 0:
        N = round(math.log10(diff))
    else:
        N = 1

    maxticks = 9
    for inc in [1, 2, 2.5, 5]:
        step = inc * 10**(N-1)
        start = round_dn(vmin, step)
        stop = round_up(vmax, step)
        ticks = zrange(start, stop, step)
        if len(ticks) <= maxticks:
            break
    else:  # nobreak; shouldn't happen
        assert False
    return ticks


class BasePlot(Drawable):
    ''' Base plotting class

        Args:
            title: Title to draw above axes
            xname: Name/label for x axis
            yname: Name/label for y axis
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def __init__(self, title: Optional[str] = None, xname: Optional[str] = None, yname: Optional[str] = None,
                 legend: LegendLoc = 'left', style: Optional[Style] = None):
        self.title = title
        self.xname = xname
        self.yname = yname
        self.style = style if style is not None else styles.Default()
        self._xrange: Optional[tuple[float, float]] = None
        self._yrange: Optional[tuple[float, float]] = None
        self._xticknames: Optional[Sequence[str]] = None
        self._yticknames: Optional[Sequence[str]] = None
        self._xtickvalues: Optional[Sequence[float]] = None
        self._ytickvalues: Optional[Sequence[float]] = None
        self._xtickminor: Optional[Sequence[float]] = None
        self._ytickminor: Optional[Sequence[float]] = None
        self.series: list[Series] = []   # List of XY lines/series
        self.legend = legend
        axis_stack.push_series(self)

    def __enter__(self):
        axis_stack.push_axis(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        ''' Exit context manager - save to file and display '''
        axis_stack.push_series(None)
        axis_stack.pop_axis(self)
        if axis_stack.current_axis() is None:
            # Display if not inside another layout
            try:
                display(self)
            except NameError:  # Not in Jupyter/IPython
                pass

    def __contains__(self, series: Drawable):
        return series in self.series

    def __iadd__(self, series: Series):
        ''' Allow += notation for adding series '''
        self.add(series)
        return self

    def xrange(self, xmin: float, xmax: float) -> BasePlot:
        ''' Set x-range of data display '''
        self._xrange = xmin, xmax
        return self

    def yrange(self, ymin, ymax):
        ''' Set y-range of data display '''
        self._yrange = ymin, ymax
        return self

    def xticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> BasePlot:
        ''' Set x axis tick values and names '''
        self._xtickvalues = values
        self._xticknames = names
        self._xtickminor = minor
        return self

    def yticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> BasePlot:
        ''' Set y axis tick values and names '''
        self._ytickvalues = values
        self._yticknames = names
        self._ytickminor = minor
        return self

    def colorfade(self, *clrs: str, stops: Optional[Sequence[float]] = None) -> None:
        ''' Define the color cycle evenly fading between multiple colors.

            Args:
                colors: List of colors in #FFFFFF format
                stops: List of stop positions for each color in the
                    gradient, starting with 0 and ending with 1.
        '''
        self.style.colorcycle = colors.ColorFade(*clrs, stops=stops)

    def add(self, series: Drawable) -> None:
        ''' Add a data series to the axis '''
        assert isinstance(series, Series)
        self.series.append(series)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' XML for standalone SVG '''
        canvas = Canvas(self.style.canvasw, self.style.canvash)
        self._xml(canvas)
        if border:
            attrib = {'x': '0', 'y': '0',
                      'width': '100%', 'height': '100%',
                      'fill': 'none', 'stroke': 'black'}
            ET.SubElement(canvas.group, 'rect', attrib=attrib)
        return canvas.xml()

    def datarange(self) -> DataRange:
        ''' Get range of data only '''
        xmin = ymin = math.inf
        xmax = ymax = -math.inf
        for s in self.series:
            drange = s.datarange()
            if drange.xmin is not None and drange.xmax is not None:
                xmin = min(drange.xmin, xmin)
                xmax = max(drange.xmax, xmax)
            if drange.ymin is not None and drange.ymax is not None:
                ymin = min(drange.ymin, ymin)
                ymax = max(drange.ymax, ymax)

        if xmin == xmax:
            xmin -= 1
            xmax += 1
        if ymin == ymax:
            ymin -= 1
            ymax += 1

        if self._xrange:
            xmin, xmax = self._xrange
        if self._yrange:
            ymin, ymax = self._yrange

        return DataRange(xmin, xmax, ymin, ymax)

    def _legendsize(self) -> tuple[float, float]:
        ''' Calculate pixel size of legend '''
        series = [s for s in self.series if s._name]
        if self.legend is None or len(series) == 0:
            return 0, 0
        boxh = 0.
        boxw = 0.
        markw = 40
        square = 10
        spacing = self.style.legend.text.size/3
            
        for s in series:
            width, height = text.text_size(
                s._name, fontsize=self.style.legend.text.size,
                font=self.style.legend.text.font)
            if s.__class__.__name__ in ['Histogram', 'Bars', 'BarsHoriz', 'PieSlice']:
                w = square*2
            else:
                w = markw
            boxw = max(boxw, w + width + 5)
            boxh += self.style.legend.text.size+spacing
        boxh += 8  # Top and bottom pad
        return boxw, boxh

    def _legendloc(self, axisbox: ViewBox, ticks: Ticks, boxw: float) -> tuple[float, float]:
        ''' Calculate legend location

            Args:
                axisbox: ViewBox of the axis rectangle. Legend to be
                    placed outside axis.
                ticks: Tick names and positions
                boxw: Width of legend box
        '''
        ytop = xright = 0
        if self.legend == 'left':
            ytop = axisbox.y + axisbox.h
            xright = (axisbox.x - self.style.tick.length -
                      ticks.ywidth - self.style.tick.textofst*2)
        elif self.legend == 'right':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x + axisbox.w + boxw + self.style.tick.textofst
        return ytop, xright

    def _drawlegend(self, canvas: Canvas, axisbox: ViewBox, ticks: Ticks) -> None:
        ''' Draw legend

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of the axis rectangle. Legend to be
                    placed outside axis.
                ticks: Tick names and positions
        '''
        series = [s for s in self.series if s._name]
        if self.legend is None or len(series) == 0:
            return

        boxw, boxh = self._legendsize()
        markw = 40
        square = 10
        spacing = self.style.legend.text.size/3

        ytop, xright = self._legendloc(axisbox, ticks, boxw)

        # Draw the box
        boxl = xright - boxw
        if self.style.legend.border not in [None, 'none']:
            legbox = ViewBox(boxl, ytop-boxh, boxw, boxh)
            canvas.rect(legbox.x, legbox.y, legbox.w, legbox.h,
                        strokewidth=1,
                        strokecolor=self.style.legend.border,
                        rcorner=5,
                        fill=self.style.legend.fill)

        # Draw each line
        yytext = ytop
        for i, s in enumerate(series):
            textw, texth = text.text_size(s._name, self.style.legend.text.size)
            yyline = yytext - self.style.legend.text.size * 2/3
            yytext -= max(self.style.legend.text.size, spacing)
            if s.__class__.__name__ in ['Histogram', 'Bars', 'BarsHoriz', 'PieSlice']:
                yysquare = yytext - square/2
                canvas.text(boxl + square + 8, yytext - self.style.legend.text.size/3,
                            s._name,
                            font=self.style.legend.text.font,
                            size=self.style.legend.text.size,
                            color=self.style.legend.text.color,
                            halign='left', valign='base')
                canvas.rect(boxl+4, yysquare, square, square,
                            fill=s.style.line.color, strokewidth=1)

            else:
                canvas.text(xright-boxw+markw, yytext,
                            s._name,
                            color=self.style.axis.color,
                            font=self.style.legend.text.font,
                            size=self.style.legend.text.size,
                            halign='left', valign='base')
                linebox = ViewBox(boxl+5, ytop-boxh, markw-10, boxh)
                canvas.setviewbox(linebox)  # Clip
                canvas.path([boxl-10, boxl+markw/2, boxl+markw+10],
                            [yyline, yyline, yyline],
                            color=s.style.line.color,
                            width=s.style.line.width,
                            markerid=s._markername,
                            stroke=s.style.line.stroke)
                canvas.resetviewbox()
            yytext -= spacing


class XyPlot(BasePlot):
    ''' Plot of x-y data

        Args:
            title: Title to draw above axes
            xname: Name/label for x axis
            yname: Name/label for y axis
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def _maketicks(self, datarange: DataRange) -> Ticks:
        ''' Define ticks and tick labels.

            Args:
                datarange: Range of x and y data

            Returns:
                ticks: Tick names and positions
        '''
        xmin, xmax, ymin, ymax = datarange
        if self._xtickvalues:
            xticks = self._xtickvalues
            xmin = min(xmin, min(xticks))
            xmax = max(xmax, max(xticks))
        else:
            xticks = getticks(xmin, xmax, maxticks=9,
                              fmt=self.style.tick.xstrformat)
            xmin, xmax = xticks[0], xticks[-1]

        if self._ytickvalues:
            yticks = self._ytickvalues
            ymin = min(ymin, min(yticks))
            ymax = max(ymax, max(yticks))
        else:
            yticks = getticks(ymin, ymax, maxticks=9,
                              fmt=self.style.tick.ystrformat)
            ymin, ymax = yticks[0], yticks[-1]

        # Apply string format if not named manually
        xnames = self._xticknames
        if xnames is None:
            xnames = [format(xt, self.style.tick.xstrformat) for xt in xticks]
        ynames = self._yticknames
        if ynames is None:
            ynames = [format(yt, self.style.tick.ystrformat) for yt in yticks]

        # Calculate width of y names for padding left side of figure
        ywidth = 0.
        for tick in ynames:
            ywidth = max(ywidth, text.text_size(tick,
                         fontsize=self.style.tick.text.size,
                         font=self.style.tick.text.font).width)

        # Add minor ticks
        xminor: Optional[Sequence[float]]
        yminor: Optional[Sequence[float]]
        if self._xtickminor:
            xminor = self._xtickminor
        elif self.style.tick.xminordivisions > 0:
            step = (xticks[1] - xticks[0]) / (self.style.tick.xminordivisions)
            xminor = zrange(xticks[0], xticks[-1], step)
        else:
            xminor = None

        if self._ytickminor:
            yminor = self._ytickminor
        elif self.style.tick.yminordivisions > 0:
            step = (yticks[1] - yticks[0]) / (self.style.tick.yminordivisions)
            yminor = zrange(yticks[0], yticks[-1], step)
        else:
            yminor = None

        # Add a bit of padding to range if not set manually
        dx = 0 if self._xrange else xticks[1]-xticks[0]
        dy = 0 if self._yrange else yticks[1]-yticks[0]
        xrange = (xmin - dx*self.style.axis.xdatapad,
                  xmax + dx*self.style.axis.xdatapad)
        yrange = (ymin - dy*self.style.axis.ydatapad,
                  ymax + dy*self.style.axis.ydatapad)

        ticks = Ticks(xticks, yticks, xnames, ynames, ywidth,
                      xrange, yrange, xminor, yminor)
        return ticks

    def _axisvbox(self, fullframe: ViewBox, ticks: Ticks) -> ViewBox:
        ''' Calculate bounding box of where to place axis within frame,
            shifting left/up to account for labels

            Args:
                fullframe: ViewBox full size of svg
                ticks: Tick definitions

            Returns:
                ViewBox of axis within the full frame
        '''
        legw, _ = self._legendsize()
        leftborder = ticks.ywidth + self.style.tick.length + self.style.tick.textofst
        if self.yname:
            _, h = text.text_size(self.yname, fontsize=self.style.axis.yname.size,
                                  font=self.style.axis.yname.font)
            leftborder += h + self.style.tick.textofst
        if self.legend == 'left':
            leftborder += legw + self.style.tick.textofst

        botborder = self.style.tick.length + self.style.tick.text.size + 4
        if self.xname:
            botborder += text.text_size(
                self.xname, fontsize=self.style.axis.xname.size,
                font=self.style.axis.xname.font).height + 2

        topborder = self.style.axis.framelinewidth + 5
        if self.title:
            topborder += text.text_size(
                self.title, fontsize=self.style.axis.title.size,
                font=self.style.axis.title.font).height

        rightborder = self.style.axis.framelinewidth + 5
        if self.legend == 'right':
            rightborder += legw + 5
        elif ticks.xnames[-1]:
            rightborder += text.text_size(
                ticks.xnames[-1], fontsize=self.style.tick.text.size,
                font=self.style.tick.text.font).width

        return ViewBox(fullframe.x + leftborder,
                       fullframe.y + botborder,
                       fullframe.w - (leftborder+rightborder),
                       fullframe.h - (topborder+botborder))

    def _drawframe(self, canvas: Canvas, axisbox: ViewBox) -> None:
        ''' Draw axis frame

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
        '''
        canvas.newgroup()
        if self.style.axis.bgcolor:
            canvas.rect(axisbox.x, axisbox.y, axisbox.w, axisbox.h,
                        strokecolor='none', fill=self.style.axis.bgcolor)

        if self.style.axis.fullbox:
            canvas.rect(axisbox.x, axisbox.y, axisbox.w, axisbox.h,
                        strokecolor=self.style.axis.color,
                        strokewidth=self.style.axis.framelinewidth)
        else:
            canvas.path([axisbox.x, axisbox.x, axisbox.x+axisbox.w],
                        [axisbox.y+axisbox.h, axisbox.y, axisbox.y],
                        color=self.style.axis.color,
                        width=self.style.axis.framelinewidth)

    def _drawticks(self, canvas: Canvas, ticks: Ticks, axisbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw tick marks and labels

            Args:
                canvas: SVG canvas to draw on
                ticks: Tick names and locations
                axisbox: ViewBox of axis within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        canvas.newgroup()
        xform = Transform(databox, axisbox)
        for xtick, xtickname in zip(ticks.xticks, ticks.xnames):
            x, _ = xform.apply(xtick, 0)
            y1 = axisbox.y
            y2 = y1 - self.style.tick.length
            if (self.style.axis.xgrid
                    and x > axisbox.x+self.style.axis.framelinewidth
                    and x < axisbox.x+axisbox.w-self.style.axis.framelinewidth):
                canvas.path([x, x], [axisbox.y, axisbox.y+axisbox.h],
                            color=self.style.axis.gridcolor,
                            stroke=self.style.axis.gridstroke,
                            width=self.style.axis.gridlinewidth)

            canvas.path([x, x], [y1, y2], color=self.style.axis.color,
                        width=self.style.tick.width)

            canvas.text(x, y2-self.style.tick.textofst, xtickname,
                        color=self.style.tick.text.color,
                        font=self.style.tick.text.font,
                        size=self.style.tick.text.size,
                        halign='center', valign='top')
        if ticks.xminor:
            for xminor in ticks.xminor:
                if xminor in ticks.xticks:
                    continue  # Don't double-draw
                x, _ = xform.apply(xminor, 0)
                y1 = axisbox.y
                y2 = y1 - self.style.tick.minorlength
                canvas.path([x, x], [y1, y2], color=self.style.axis.color,
                            width=self.style.tick.minorwidth)

        for ytick, ytickname in zip(ticks.yticks, ticks.ynames):
            _, y = xform.apply(0, ytick)
            x1 = axisbox.x
            x2 = axisbox.x - self.style.tick.length

            if (self.style.axis.ygrid
                    and y > axisbox.y+self.style.axis.framelinewidth
                    and y < axisbox.y+axisbox.h-self.style.axis.framelinewidth):
                canvas.path([axisbox.x, axisbox.x+axisbox.w], [y, y],
                            color=self.style.axis.gridcolor,
                            stroke=self.style.axis.gridstroke,
                            width=self.style.axis.gridlinewidth)

            canvas.path([x1, x2], [y, y], color=self.style.axis.color,
                        width=self.style.tick.width)

            canvas.text(x2-self.style.tick.textofst, y, ytickname,
                        color=self.style.tick.text.color,
                        font=self.style.tick.text.font,
                        size=self.style.tick.text.size,
                        halign='right', valign='center')

        if ticks.yminor:
            for yminor in ticks.yminor:
                if yminor in ticks.yticks:
                    continue  # Don't double-draw
                _, y = xform.apply(0, yminor)
                x1 = axisbox.x
                x2 = axisbox.x - self.style.tick.minorlength
                canvas.path([x1, x2], [y, y], color=self.style.axis.color,
                            width=self.style.tick.minorwidth)

        if self.xname:
            centerx = axisbox.x + axisbox.w/2
            namey = (axisbox.y - self.style.tick.text.size -
                     self.style.tick.length - self.style.tick.textofst)
            canvas.text(centerx, namey, self.xname,
                        color=self.style.axis.xname.color,
                        font=self.style.axis.xname.font,
                        size=self.style.axis.xname.size,
                        halign='center', valign='top')

        if self.yname:
            centery = axisbox.y + axisbox.h/2
            namex = (axisbox.x - self.style.tick.length -
                     ticks.ywidth - self.style.tick.text.size)
            canvas.text(namex, centery, self.yname,
                        color=self.style.axis.yname.color,
                        font=self.style.axis.yname.font,
                        size=self.style.axis.yname.size,
                        halign='center', valign='center',
                        rotate=90)

    def _drawtitle(self, canvas: Canvas, axisbox: ViewBox) -> None:
        ''' Draw plot title

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
        '''
        canvas.newgroup()
        if self.title:
            centerx = axisbox.x + axisbox.w/2
            canvas.text(centerx, axisbox.y+axisbox.h, self.title,
                        color=self.style.axis.color,
                        font=self.style.axis.title.font,
                        size=self.style.axis.title.size,
                        halign='center', valign='bottom')

    def _drawseries(self, canvas: Canvas, axisbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all series lines/markers

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        canvas.setviewbox(axisbox)

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

        for s in self.series:
            s._xml(canvas, databox=databox)
        canvas.resetviewbox()

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        if self.style.bgcolor not in [None, 'none']:
            canvas.rect(*canvas.viewbox, fill=self.style.bgcolor,
                        strokecolor=self.style.bgcolor)

        datarange = self.datarange()
        ticks = self._maketicks(datarange)
        axisbox = self._axisvbox(canvas.viewbox, ticks)
        databox = ViewBox(ticks.xrange[0], ticks.yrange[0],
                          ticks.xrange[1]-ticks.xrange[0],
                          ticks.yrange[1]-ticks.yrange[0])

        self._drawframe(canvas, axisbox)
        self._drawticks(canvas, ticks, axisbox, databox)
        self._drawtitle(canvas, axisbox)
        self._drawseries(canvas, axisbox, databox)
        self._drawlegend(canvas, axisbox, ticks)


class XyGraph(XyPlot):
    ''' X-Y Graph. Axes are drawn as arrows pointing to infinity with
        xname and yname labels at the ends of the arrows. Often used
        to visualize functions (e.g. y = x**2) rather than empirical data.

        Args:
            centerorigin: Place the (0, 0) origin in the center of the axis
            title: Title to draw above axes
            xname: Name/label for x axis
            yname: Name/label for y axis
            legend: Location of legend
            style: Drawing style

        Attributes:
            style: Drawing style
    '''
    def __init__(self, centerorigin: bool = True, title: Optional[str] = None,
                 xname: str = 'x', yname: str = 'y',
                 legend: LegendLoc = 'left', style: Optional[Style] = None):
        super().__init__(title=title, xname=xname, yname=yname,
                         legend=legend, style=style)
        self.centerorigin = centerorigin
        self.arrowwidth = self.style.axis.framelinewidth * 3

    def _axisvbox(self, fullframe: ViewBox, ticks: Ticks) -> ViewBox:
        ''' Calculate bounding box of where to place axis within frame,
            shifting left/up to account for labels

            Args:
                fullframe: ViewBox full size of svg
                ticks: Tick definitions

            Notes:
                XyGraph doesn't need to account for tick text, unlike XyPlot

            Returns:
                ViewBox of axis within the full frame
        '''
        legw, _ = self._legendsize()
        leftborder = self.arrowwidth*2
        rightborder = self.arrowwidth*2
        topborder = self.arrowwidth
        botborder = self.arrowwidth*2

        if self.legend == 'left':
            leftborder += legw + self.style.axis.framelinewidth
        elif self.legend == 'right':
            rightborder += legw + self.style.axis.framelinewidth

        drange = self.datarange()
        if drange.xmin == 0:
            leftborder += ticks.ywidth

        if self.yname:
            topborder += self.style.axis.yname.size + 2

        if self.xname:
            rightborder += text.text_size(
                self.xname, font=self.style.axis.xname.font,
                fontsize=self.style.axis.xname.size).width

        if self.title:
            topborder += self.style.axis.title.size

        return ViewBox(fullframe.x + leftborder,
                       fullframe.y + botborder,
                       fullframe.w - (leftborder+rightborder),
                       fullframe.h - (topborder+botborder))

    def datarange(self) -> DataRange:
        ''' Get range of x-y data. XyGraph datarange must include 0 '''
        drange = super().datarange()
        xmin = min(0, drange.xmin)
        xmax = max(0, drange.xmax)
        ymin = min(0, drange.ymin)
        ymax = max(0, drange.ymax)
        if self.centerorigin:
            x = max(abs(xmax), abs(xmin))
            y = max(abs(ymax), abs(ymin))
            xmin, xmax = -x, x
            ymin, ymax = -y, y
        return DataRange(xmin, xmax, ymin, ymax)

    def _drawframe(self, canvas: Canvas, axisbox: ViewBox) -> None:
        ''' Draw axis frame

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
        '''
        if self.style.axis.bgcolor:
            canvas.newgroup()
            canvas.rect(axisbox.x, axisbox.y, axisbox.w, axisbox.h,
                        strokecolor='none', fill=self.style.axis.bgcolor)

    def _legendloc(self, axisbox: ViewBox, ticks: Ticks, boxw: float) -> tuple[float, float]:
        ''' Calculate legend location

            Args:
                axisbox: ViewBox of the axis rectangle. Legend to
                    be placed outside axis.
                ticks: Tick names and positions
                boxw: Width of legend box
        '''
        if self.legend == 'left':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x - self.arrowwidth
        elif self.legend == 'right':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x + axisbox.w + boxw + self.arrowwidth
        return ytop, xright

    def _drawticks(self, canvas: Canvas, ticks: Ticks, axisbox: ViewBox, databox: ViewBox):
        ''' Draw tick marks and labels

            Args:
                canvas: SVG canvas to draw on
                ticks: Tick names and locations
                axisbox: ViewBox of axis within the canvas
                databox: ViewBox of data to convert from data to
                    svg coordinates
        '''
        canvas.newgroup()
        xform = Transform(databox, axisbox)
        xleft = xform.apply(databox.x, 0)
        xrght = xform.apply(databox.x+databox.w, 0)
        ytop = xform.apply(0, databox.y+databox.h)
        ybot = xform.apply(0, databox.y)

        startmark = canvas.definemarker('larrow', radius=self.arrowwidth,
                                        color=self.style.axis.color,
                                        strokecolor=self.style.axis.color,
                                        orient=True)
        endmark = canvas.definemarker('arrow', radius=self.arrowwidth,
                                      strokecolor=self.style.axis.color,
                                      color=self.style.axis.color, orient=True)

        canvas.path([xleft[0]-self.arrowwidth+self.style.tick.width,
                     xrght[0]+self.arrowwidth-self.style.tick.width],
                    [xleft[1], xrght[1]],
                    color=self.style.axis.color,
                    width=self.style.axis.framelinewidth,
                    startmarker=startmark, endmarker=endmark)
        canvas.path([ytop[0], ybot[0]],
                    [ytop[1]+self.arrowwidth-self.style.tick.width,
                     ybot[1]-self.arrowwidth+self.style.tick.width],
                    color=self.style.axis.color,
                    width=self.style.axis.framelinewidth,
                    startmarker=startmark, endmarker=endmark)

        for xtick, xtickname in zip(ticks.xticks, ticks.xnames):
            if xtick == 0:
                continue
            x, _ = xform.apply(xtick, 0)
            y1 = xleft[1] + self.style.tick.length/2
            y2 = xleft[1] - self.style.tick.length/2
            if self.style.axis.xgrid:
                canvas.path([x, x], [ybot[1], ytop[1]],
                            color=self.style.axis.gridcolor,
                            stroke=self.style.axis.gridstroke,
                            width=self.style.axis.gridlinewidth)
            canvas.path([x, x], [y1, y2], color=self.style.axis.color,
                        width=self.style.tick.width)

            canvas.text(x, y2-self.style.tick.textofst, xtickname,
                        color=self.style.tick.text.color,
                        font=self.style.tick.text.font,
                        size=self.style.tick.text.size,
                        halign='center', valign='top')
        if ticks.xminor:
            for xminor in ticks.xminor:
                if xminor in ticks.xticks:
                    continue  # Don't double-draw
                x, _ = xform.apply(xminor, 0)
                y1 = xleft[1] + self.style.tick.minorlength/2
                y2 = xleft[1] - self.style.tick.minorlength/2
                canvas.path([x, x], [y1, y2], color=self.style.axis.color,
                            width=self.style.tick.minorwidth)

        for ytick, ytickname in zip(ticks.yticks, ticks.ynames):
            if ytick == 0:
                continue
            _, y = xform.apply(0, ytick)
            x1 = ytop[0] + self.style.tick.length/2
            x2 = ytop[0] - self.style.tick.length/2
            if self.style.axis.ygrid:
                canvas.path([xleft[0], xrght[0]], [y, y],
                            color=self.style.axis.gridcolor,
                            stroke=self.style.axis.gridstroke,
                            width=self.style.axis.gridlinewidth)
            canvas.path([x1, x2], [y, y], color=self.style.axis.color,
                        width=self.style.tick.width)

            canvas.text(x2-self.style.tick.textofst, y, ytickname,
                        color=self.style.tick.text.color,
                        font=self.style.tick.text.font,
                        size=self.style.tick.text.size,
                        halign='right', valign='center')
        if ticks.yminor:
            for yminor in ticks.yminor:
                if yminor in ticks.yticks:
                    continue  # Don't double-draw
                _, y = xform.apply(0, yminor)
                x1 = ytop[0] + self.style.tick.minorlength/2
                x2 = ytop[0] - self.style.tick.minorlength/2
                canvas.path([x1, x2], [y, y], color=self.style.axis.color,
                            width=self.style.tick.minorwidth)

        if self.xname:
            canvas.text(xrght[0]+self.style.tick.textofst+self.arrowwidth,
                        xrght[1],
                        self.xname,
                        color=self.style.axis.color,
                        font=self.style.axis.xname.font,
                        size=self.style.axis.xname.size,
                        halign='left', valign='center')

        if self.yname:
            canvas.text(ytop[0],
                        ytop[1]+self.style.tick.textofst*2+self.arrowwidth,
                        self.yname,
                        color=self.style.axis.color,
                        font=self.style.axis.yname.font,
                        size=self.style.axis.yname.size,
                        halign='center', valign='bottom')

    def _drawtitle(self, canvas: Canvas, axisbox: ViewBox) -> None:
        ''' Draw plot title

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of axis within the canvas
        '''
        canvas.newgroup()
        if self.title:
            canvas.text(axisbox.x, axisbox.y+axisbox.h, self.title,
                        color=self.style.axis.color,
                        font=self.style.axis.title.font,
                        size=self.style.axis.title.size,
                        halign='left', valign='bottom')

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> None:
        ''' Add XML elements to the canvas '''
        if self.style.bgcolor not in [None, 'none']:
            canvas.rect(*canvas.viewbox, fill=self.style.bgcolor,
                        strokecolor=self.style.bgcolor)

        datarange = self.datarange()
        ticks = self._maketicks(datarange)
        axisbox = self._axisvbox(canvas.viewbox, ticks)
        databox = ViewBox(ticks.xrange[0], ticks.yrange[0],
                          ticks.xrange[1]-ticks.xrange[0],
                          ticks.yrange[1]-ticks.yrange[0])

        self._drawframe(canvas, axisbox)
        self._drawticks(canvas, ticks, axisbox, databox)
        self._drawtitle(canvas, axisbox)
        self._drawseries(canvas, axisbox, databox)
        self._drawlegend(canvas, axisbox, ticks)
