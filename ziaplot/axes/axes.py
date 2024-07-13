''' Axes for plotting one or more data series '''

from __future__ import annotations
from typing import Sequence, Optional
from functools import lru_cache
import math

from ..style.styletypes import Style
from ..canvas import Canvas, Transform, ViewBox, DataRange, Borders
from .. import text
from ..util import zrange, linspace
from .baseplot import BasePlot, LegendLoc, Ticks



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

    for inc in [1, 2, 2.5, 5]:
        step = inc * 10**(N-1)
        start = round_dn(vmin, step)
        stop = round_up(vmax, step)
        ticks = zrange(start, stop, step)
        if len(ticks) <= maxticks:
            break
    else:
        ticks = linspace(vmin, vmax, maxticks)
    return ticks


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
    def _clearcache(self):
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def _maketicks(self) -> Ticks:
        ''' Define ticks and tick labels.

            Returns:
                ticks: Tick names and positions
        '''
        xmin, xmax, ymin, ymax = self.datarange()
        if self._xtickvalues:
            xticks = self._xtickvalues
            xmin = min(xmin, min(xticks))
            xmax = max(xmax, max(xticks))
        else:
            xticks = getticks(xmin, xmax, maxticks=self.style.tick.maxticksx,
                              fmt=self.style.tick.xstrformat)
            xmin, xmax = xticks[0], xticks[-1]

        if self._ytickvalues:
            yticks = self._ytickvalues
            ymin = min(ymin, min(yticks))
            ymax = max(ymax, max(yticks))
        else:
            yticks = getticks(ymin, ymax, maxticks=self.style.tick.maxticksy,
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

        # Add a bit of padding to data range
        dx = xticks[1]-xticks[0]
        dy = yticks[1]-yticks[0]
        xrange = (xmin - dx*self.style.axis.xtickpad,
                  xmax + dx*self.style.axis.xtickpad)
        yrange = (ymin - dy*self.style.axis.ytickpad,
                  ymax + dy*self.style.axis.ytickpad)

        ticks = Ticks(xticks, yticks, xnames, ynames, ywidth,
                      xrange, yrange, xminor, yminor)
        return ticks

    @lru_cache
    def _borders(self) -> Borders:
        ''' Calculate bounding box of where to place axis within frame,
            shifting left/up to account for labels

            Args:
                fullframe: ViewBox full size of svg
                ticks: Tick definitions

            Returns:
                ViewBox of axis within the full frame
        '''
        ticks = self._maketicks()
        legw, _ = self._legendsize()
        if self.showyticks:
            leftborder = ticks.ywidth + self.style.tick.length + self.style.tick.textofst
        else:
            leftborder = 0
        if self.yname:
            _, h = text.text_size(self.yname, fontsize=self.style.axis.yname.size,
                                  font=self.style.axis.yname.font)
            leftborder += h + self.style.tick.textofst
        if self.legend == 'left':
            leftborder += legw + self.style.tick.textofst

        if self.showxticks:
            botborder = self.style.tick.length + self.style.tick.text.size + 4
        else:
            botborder = 0
        if self.xname:
            botborder += text.text_size(
                self.xname, fontsize=self.style.axis.xname.size,
                font=self.style.axis.xname.font).height + 2

        topborder = self.style.axis.framelinewidth
        if self.title:
            topborder += text.text_size(
                self.title, fontsize=self.style.axis.title.size,
                font=self.style.axis.title.font).height

        rightborder = self.style.axis.framelinewidth
        if self.legend == 'right':
            rightborder += legw + 5

        borders = Borders(leftborder, rightborder, topborder, botborder)
        return borders

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

            if self.showxticks:
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

            if self.showyticks:
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

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        if self.style.bgcolor not in [None, 'none']:
            canvas.rect(*canvas.viewbox, fill=self.style.bgcolor,
                        strokecolor=self.style.bgcolor)

        ticks = self._maketicks()
        dborders = self._borders()
        if borders is not None:
            dborders = Borders(
                dborders.left if borders.left is None else borders.left,
                dborders.right if borders.right is None else borders.right,
                dborders.top if borders.top is None else borders.top,
                dborders.bottom if borders.bottom is None else borders.bottom)

        axisbox = ViewBox(
            canvas.viewbox.x + dborders.left,
            canvas.viewbox.y + dborders.bottom,
            canvas.viewbox.w - (dborders.left + dborders.right),
            canvas.viewbox.h - (dborders.top + dborders.bottom))

        databox = ViewBox(ticks.xrange[0], ticks.yrange[0],
                          ticks.xrange[1]-ticks.xrange[0],
                          ticks.yrange[1]-ticks.yrange[0])

        if self._equal_aspect:
            daspect = databox.w / databox.h
            axisaspect = axisbox.w / axisbox.h
            ratio = daspect / axisaspect
            axisbox = ViewBox(
                axisbox.x,
                axisbox.y,
                axisbox.w if ratio >= 1 else axisbox.w * ratio,
                axisbox.h if ratio <= 1 else axisbox.h / ratio
            )

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
    def __init__(self, centerorigin: bool = False, title: Optional[str] = None,
                 xname: str = 'x', yname: str = 'y',
                 legend: LegendLoc = 'left', style: Optional[Style] = None):
        super().__init__(title=title, xname=xname, yname=yname,
                         legend=legend, style=style)
        self.centerorigin = centerorigin
        self.arrowwidth = self.style.axis.framelinewidth * 3
        self.style.axis.xtickpad = 0
        self.style.axis.ytickpad = 0

    def _clearcache(self):
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def _borders(self) -> Borders:
        ''' Calculate bounding box of where to place axis within frame,
            shifting left/up to account for labels

            Returns:
                ViewBox of axis within the full frame
        '''
        databox = self.datarange()
        ticks = self._maketicks()
        legw, _ = self._legendsize()

        if databox.xmin == 0:
            leftborder = ticks.ywidth + self.style.tick.length + self.style.tick.textofst        
        else:
            leftborder = 1

        if databox.ymin == 0:
            botborder = self.style.tick.length + self.style.tick.text.size + 4
        else:
            botborder = 1

        rightborder = self.arrowwidth*2
        topborder = self.arrowwidth
        
        if self.legend == 'left':
            leftborder += legw + self.style.axis.framelinewidth
        elif self.legend == 'right':
            rightborder += legw + self.style.axis.framelinewidth

        drange = self.datarange()
        if drange.xmin == 0:
            leftborder += ticks.ywidth

        if self.yname:
            topborder += self.style.tick.textofst+self.style.axis.yname.size + 2

        if self.xname:
            rightborder += text.text_size(
                self.xname, font=self.style.axis.xname.font,
                fontsize=self.style.axis.xname.size).width

        if self.title:
            topborder += self.style.axis.title.size

        return Borders(leftborder, rightborder, topborder, botborder)

    @lru_cache
    def datarange(self) -> DataRange:
        ''' Get range of x-y data. XyGraph datarange must include x=0 and y=0 '''
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

        if xmin == xmax == ymin == ymax == 0:
            ymin = xmin = -1
            ymax = xmax = 1
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

    def _legendloc(self, axisbox: ViewBox, ticks: Ticks, boxw: float, boxh: float) -> tuple[float, float]:
        ''' Calculate legend location

            Args:
                axisbox: ViewBox of the axis rectangle. Legend to
                    be placed outside axis.
                ticks: Tick names and positions
                boxw: Width of legend box
                boxh: Height of legend box
        '''
        if self.legend == 'left':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x - self.arrowwidth
        elif self.legend == 'right':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x + axisbox.w + boxw + self.arrowwidth
        elif self.legend == 'topright':
            ytop = axisbox.y + axisbox.h - self.style.legend.pad
            xright = (axisbox.x + axisbox.w - self.style.legend.pad)
        elif self.legend == 'bottomleft':
            ytop = axisbox.y + boxh + self.style.legend.pad
            xright = (axisbox.x + boxw + self.style.legend.pad)
        elif self.legend == 'bottomright':
            ytop = axisbox.y + boxh + self.style.legend.pad
            xright = (axisbox.x + axisbox.w - self.style.legend.pad)
        else: # self.legend == 'topleft':
            ytop = axisbox.y + axisbox.h - self.style.legend.pad
            xright = (axisbox.x + boxw + self.style.legend.pad)

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

        xmarker = startmark
        ymarker = endmark
        if databox.x == 0:
            xmarker = None
            xaxis = [xleft[0],
                     xrght[0]-self.style.tick.width]
        else:
            xaxis = [xleft[0]+self.arrowwidth+self.style.tick.width,
                     xrght[0]-self.arrowwidth-self.style.tick.width]

        if databox.y == 0:
            ymarker = None
            yaxis = [ytop[1]-self.style.tick.width,
                     ybot[1]]
        else:
            yaxis = [ytop[1]-self.arrowwidth-self.style.tick.width,
                     ybot[1]+self.arrowwidth+self.style.tick.width]
        
        canvas.path(xaxis,
                    [xleft[1], xrght[1]],
                    color=self.style.axis.color,
                    width=self.style.axis.framelinewidth,
                    startmarker=xmarker,
                    endmarker=endmark)
        canvas.path([ytop[0], ybot[0]],
                    yaxis,
                    color=self.style.axis.color,
                    width=self.style.axis.framelinewidth,
                    startmarker=startmark,
                    endmarker=ymarker)

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
                
            if xleft[0] < x < xrght[0]:
                # Don't draw ticks outside the arrows
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

            if ybot[1] < y < ytop[1]:
                # Don't draw ticks outside the arrows
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
                        ytop[1]+self.style.tick.textofst+self.arrowwidth,
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

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        if self.style.bgcolor not in [None, 'none']:
            canvas.rect(*canvas.viewbox, fill=self.style.bgcolor,
                        strokecolor=self.style.bgcolor)

        ticks = self._maketicks()
        dborders = self._borders()
        if borders is not None:
            dborders = Borders(
                dborders.left if borders.left is None else borders.left,
                dborders.right if borders.right is None else borders.right,
                dborders.top if borders.top is None else borders.top,
                dborders.bottom if borders.bottom is None else borders.bottom)

        axisbox = ViewBox(
            canvas.viewbox.x + dborders.left,
            canvas.viewbox.y + dborders.bottom,
            canvas.viewbox.w - (dborders.left + dborders.right),
            canvas.viewbox.h - (dborders.top + dborders.bottom))

        databox = ViewBox(ticks.xrange[0], ticks.yrange[0],
                          ticks.xrange[1]-ticks.xrange[0],
                          ticks.yrange[1]-ticks.yrange[0])

        if self._equal_aspect:
            daspect = databox.w / databox.h
            axisaspect = axisbox.w / axisbox.h
            ratio = daspect / axisaspect
            axisbox = ViewBox(
                axisbox.x,
                axisbox.y,
                axisbox.w if ratio >= 1 else axisbox.w * ratio,
                axisbox.h if ratio <= 1 else axisbox.h / ratio
            )

        self._drawframe(canvas, axisbox)
        self._drawticks(canvas, ticks, axisbox, databox)
        self._drawtitle(canvas, axisbox)
        self._drawseries(canvas, axisbox, databox)
        self._drawlegend(canvas, axisbox, ticks)
