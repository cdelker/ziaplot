''' Graphs for plotting data with x- and y- axes '''

from __future__ import annotations
from typing import Sequence, Optional
from functools import lru_cache
import math

from .. import text
from ..canvas import Canvas, Transform, ViewBox, DataRange, Borders, PointType
from ..util import zrange, linspace
from .diagram import Diagram, Ticks


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


class Graph(Diagram):
    ''' Plot of x-y data '''
    def __init__(self):
        super().__init__()
        self._equal_aspect = False
        self._pad_datarange = True

    def axesnames(self, x: str|None = None, y: str|None = None) -> Diagram:
        ''' Set names for the x and y axes '''
        self._xname = x
        self._yname = y
        return self

    def xticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> Diagram:
        ''' Set x axis tick values and names '''
        self._xtickvalues = values
        self._xticknames = names
        self._xtickminor = minor
        self._clearcache()
        return self

    def yticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> Diagram:
        ''' Set y axis tick values and names '''
        self._ytickvalues = values
        self._yticknames = names
        self._ytickminor = minor
        self._clearcache()
        return self

    def noxticks(self) -> Diagram:
        ''' Turn off x axis tick marks '''
        self.showxticks = False
        self._clearcache()
        return self

    def noyticks(self) -> Diagram:
        ''' Turn off y axis tick marks '''
        self.showyticks = False
        self._clearcache()
        return self

    def _clearcache(self):
        ''' Clear LRU cache when inputs changes '''
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def _maketicks(self) -> Ticks:
        ''' Define ticks and tick labels.

            Returns:
                ticks: Tick names and positions
        '''
        xsty = self._build_style('Graph.TickX')
        ysty = self._build_style('Graph.TickY')

        xmin, xmax, ymin, ymax = self.datarange()
        if self._xtickvalues:
            xticks = self._xtickvalues
            xmin = min(xmin, min(xticks))
            xmax = max(xmax, max(xticks))
        else:
            xticks = getticks(xmin, xmax, maxticks=self.max_xticks,
                              fmt=xsty.num_format)
            xmin, xmax = xticks[0], xticks[-1]

        if self._ytickvalues:
            yticks = self._ytickvalues
            ymin = min(ymin, min(yticks))
            ymax = max(ymax, max(yticks))
        else:
            yticks = getticks(ymin, ymax, maxticks=self.max_yticks,
                              fmt=ysty.num_format)
            ymin, ymax = yticks[0], yticks[-1]

        # Apply string format if not named manually
        xnames = self._xticknames
        if xnames is None:
            xnames = [format(xt, xsty.num_format) for xt in xticks]
        ynames = self._yticknames
        if ynames is None:
            ynames = [format(yt, ysty.num_format) for yt in yticks]

        # Calculate width of y names for padding left side of diagram
        ywidth = 0.
        for tick in ynames:
            ywidth = max(ywidth, text.text_size(tick,
                         fontsize=ysty.font_size,
                         font=ysty.font).width)

        # Add minor ticks
        xminor: Optional[Sequence[float]]
        yminor: Optional[Sequence[float]]
        if self._xtickminor:
            xminor = self._xtickminor
        elif self.xminordivisions > 0:
            step = (xticks[1] - xticks[0]) / (self.xminordivisions)
            xminor = zrange(xticks[0], xticks[-1], step)
        else:
            xminor = None

        if self._ytickminor:
            yminor = self._ytickminor
        elif self.yminordivisions > 0:
            step = (yticks[1] - yticks[0]) / (self.yminordivisions)
            yminor = zrange(yticks[0], yticks[-1], step)
        else:
            yminor = None

        dx = dy = 0.
        if self._pad_datarange:
            # Add a bit of padding to data range
            dx = xsty.pad * (xmax - xmin)
            dy = ysty.pad * (ymax - ymin)
            if len(xticks) > 1:
                dx = xticks[1]-xticks[0]
            if len(yticks) > 1:
                dy = yticks[1]-yticks[0]
        xrange = (xmin - dx*xsty.pad,
                xmax + dx*xsty.pad)
        yrange = (ymin - dy*ysty.pad,
                ymax + dy*ysty.pad)

        ticks = Ticks(xticks, yticks, xnames, ynames, ywidth,
                      xrange, yrange, xminor, yminor)
        return ticks

    @lru_cache
    def _borders(self) -> Borders:
        ''' Calculate borders around diagram box to fit the ticks and legend '''
        xsty = self._build_style('Graph.TickX')
        ysty = self._build_style('Graph.TickY')
        lsty = self._build_style('Graph.Legend')

        ticks = self._maketicks()
        legw, _ = self._legendsize()
        if self.showyticks:
            leftborder = ticks.ywidth + ysty.height + ysty.margin
        else:
            leftborder = 0
        if self._yname:
            nsty = self._build_style('Graph.YName')
            _, h = text.text_size(self._yname, fontsize=nsty.font_size,
                                  font=nsty.font)
            leftborder += h + ysty.margin
        if self._legend == 'left':
            leftborder += legw + ysty.margin

        if self.showxticks:
            botborder = xsty.height + xsty.font_size + 4
        else:
            botborder = 0
        if self._xname:
            nsty = self._build_style('Graph.XName')
            botborder += text.text_size(
                self._xname, fontsize=nsty.font_size,
                font=nsty.font).height + 2

        topborder = lsty.edge_width + ysty.font_size / 2
        if self._title:
            nsty = self._build_style('Graph.Title')
            topborder += text.text_size(
                self._title, fontsize=nsty.font_size,
                font=nsty.font).height

        rightborder = lsty.edge_width
        if self._legend == 'right':
            rightborder += legw + 5

        borders = Borders(leftborder, rightborder, topborder, botborder)
        return borders

    def _drawframe(self, canvas: Canvas, diagbox: ViewBox) -> None:
        ''' Draw frame

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
        '''
        sty = self._build_style()
        canvas.newgroup()
        bgcolor = sty.get_color()
        if bgcolor:
            canvas.rect(diagbox.x, diagbox.y, diagbox.w, diagbox.h,
                        strokecolor='none', fill=sty.color)

        if self.fullbox:
            canvas.rect(diagbox.x, diagbox.y, diagbox.w, diagbox.h,
                        strokecolor=sty.edge_color,
                        strokewidth=sty.edge_width)
        else:
            canvas.path([diagbox.x, diagbox.x, diagbox.x+diagbox.w],
                        [diagbox.y+diagbox.h, diagbox.y, diagbox.y],
                        color=sty.edge_color,
                        width=sty.edge_width)

    def _drawticks(self, canvas: Canvas, ticks: Ticks, diagbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw tick marks and labels

            Args:
                canvas: SVG canvas to draw on
                ticks: Tick names and locations
                diagbox: ViewBox of diagram within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        sty = self._build_style()
        xsty = self._build_style('Graph.TickX')
        ysty = self._build_style('Graph.TickY')
        gridx_sty = self._build_style('Graph.GridX')
        gridy_sty = self._build_style('Graph.GridY')

        canvas.newgroup()
        xform = Transform(databox, diagbox)
        for xtick, xtickname in zip(ticks.xticks, ticks.xnames):
            x, _ = xform.apply(xtick, 0)
            y1 = diagbox.y
            y2 = y1 - xsty.height
            if (gridx_sty.color not in [None, 'none']
                    and x > diagbox.x+sty.edge_width
                    and x < diagbox.x+diagbox.w-sty.edge_width):
                canvas.path([x, x], [diagbox.y, diagbox.y+diagbox.h],
                            color=gridx_sty.color,
                            stroke=gridx_sty.stroke,
                            width=gridx_sty.stroke_width)

            if self.showxticks:
                canvas.path([x, x], [y1, y2], color=xsty.get_color(),
                            width=xsty.stroke_width)
    
                canvas.text(x, y2-xsty.margin, xtickname,
                            color=xsty.get_color(),
                            font=xsty.font,
                            size=xsty.font_size,
                            halign='center', valign='top')

                if ticks.xminor:
                    xsty_minor = self._build_style('Graph.TickXMinor')
                    for xminor in ticks.xminor:
                        if xminor in ticks.xticks:
                            continue  # Don't double-draw
                        x, _ = xform.apply(xminor, 0)
                        y1 = diagbox.y
                        y2 = y1 - xsty_minor.height
                        canvas.path([x, x], [y1, y2], color=xsty.color,
                                    width=xsty_minor.stroke_width)

        for ytick, ytickname in zip(ticks.yticks, ticks.ynames):
            _, y = xform.apply(0, ytick)
            x1 = diagbox.x
            x2 = diagbox.x - xsty.height

            if (gridy_sty.color not in [None, 'none']
                    and y > diagbox.y+sty.edge_width
                    and y < diagbox.y+diagbox.h-sty.edge_width):
                canvas.path([diagbox.x, diagbox.x+diagbox.w], [y, y],
                            color=gridy_sty.color,
                            stroke=gridy_sty.stroke,
                            width=gridy_sty.stroke_width)

            if self.showyticks:
                canvas.path([x1, x2], [y, y], color=ysty.get_color(),
                            width=ysty.stroke_width)

                canvas.text(x2-ysty.margin, y, ytickname,
                            color=ysty.get_color(),
                            font=ysty.font,
                            size=ysty.font_size,
                            halign='right', valign='center')
    
                if ticks.yminor:
                    ysty_minor = self._build_style('Graph.TickYMinor')
                    for yminor in ticks.yminor:
                        if yminor in ticks.yticks:
                            continue  # Don't double-draw
                        _, y = xform.apply(0, yminor)
                        x1 = diagbox.x
                        x2 = diagbox.x - ysty_minor.height
                        canvas.path([x1, x2], [y, y], color=ysty_minor.get_color(),
                                    width=ysty_minor.stroke_width)

        if self._xname:
            sty = self._build_style('Graph.XName')
            centerx = diagbox.x + diagbox.w/2
            namey = (diagbox.y - xsty.font_size -
                     xsty.height - xsty.margin)
            canvas.text(centerx, namey, self._xname,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='center', valign='top')

        if self._yname:
            sty = self._build_style('Graph.YName')
            centery = diagbox.y + diagbox.h/2
            namex = (diagbox.x - ysty.height -
                     ticks.ywidth - ysty.font_size)
            canvas.text(namex, centery, self._yname,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='center', valign='center',
                        rotate=90)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        ticks = self._maketicks()
        dborders = self._borders()
        if borders is not None:
            dborders = Borders(
                dborders.left if borders.left is None else borders.left,
                dborders.right if borders.right is None else borders.right,
                dborders.top if borders.top is None else borders.top,
                dborders.bottom if borders.bottom is None else borders.bottom)

        diagbox = ViewBox(
            canvas.viewbox.x + dborders.left,
            canvas.viewbox.y + dborders.bottom,
            canvas.viewbox.w - (dborders.left + dborders.right),
            canvas.viewbox.h - (dborders.top + dborders.bottom))

        databox = ViewBox(ticks.xrange[0], ticks.yrange[0],
                          ticks.xrange[1]-ticks.xrange[0],
                          ticks.yrange[1]-ticks.yrange[0])

        if self._equal_aspect:
            daspect = databox.w / databox.h
            diagaspect = diagbox.w / diagbox.h
            ratio = daspect / diagaspect
            diagbox = ViewBox(
                diagbox.x,
                diagbox.y,
                diagbox.w if ratio >= 1 else diagbox.w * ratio,
                diagbox.h if ratio <= 1 else diagbox.h / ratio
            )

        self._drawframe(canvas, diagbox)
        self._drawticks(canvas, ticks, diagbox, databox)
        self._drawtitle(canvas, diagbox)
        self._drawcomponents(canvas, diagbox, databox)
        self._drawlegend(canvas, diagbox, ticks)


class GraphQuad(Graph):
    ''' Graph showing all 4 quadrants of the coordinate plane.
        Axes are drawn as arrows pointing to infinity with
        xname and yname labels at the ends of the arrows.
    '''
    def __init__(self):
        super().__init__()
        self._pad_datarange = False

    def _clearcache(self):
        ''' Clear LRU cache when inputs changes '''
        super()._clearcache()
        self._maketicks.cache_clear()
        self._borders.cache_clear()

    @lru_cache
    def _borders(self) -> Borders:
        ''' Calculate bounding box of where to place diagram within frame,
            shifting left/up to account for labels

            Returns:
                ViewBox of diagram within the full frame
        '''
        databox = self.datarange()
        ticks = self._maketicks()
        legw, _ = self._legendsize()

        xsty = self._build_style('Graph.TickX')
        ysty = self._build_style('Graph.TickY')
        lsty = self._build_style('Graph.Legend')
        sty = self._build_style()
        arrowwidth = sty.edge_width * 3

        if databox.xmin == 0:
            leftborder = ticks.ywidth + ysty.height + ysty.margin        
        else:
            leftborder = 1

        if databox.ymin == 0:
            botborder = xsty.height + xsty.font_size + 4
        else:
            botborder = 1

        rightborder = arrowwidth*2
        topborder = arrowwidth
        
        if self._legend == 'left':
            leftborder += legw + lsty.edge_width
        elif self._legend == 'right':
            rightborder += legw + lsty.edge_width

        drange = self.datarange()
        if drange.xmin == 0:
            leftborder += ticks.ywidth

        if self._yname:
            nsty = self._build_style('Graph.YName')
            topborder += ysty.margin+nsty.font_size + 2

        if self._xname:
            nsty = self._build_style('Graph.XName')
            rightborder += text.text_size(
                self._xname, font=nsty.font,
                fontsize=nsty.font_size).width

        if self._title:
            nsty = self._build_style('Graph.Title')
            topborder += nsty.font_size

        return Borders(leftborder, rightborder, topborder, botborder)

    @lru_cache
    def datarange(self) -> DataRange:
        ''' Get range of x-y data. GraphQuad datarange must include x=0 and y=0 '''
        drange = super().datarange()
        xmin = min(0, drange.xmin)
        xmax = max(0, drange.xmax)
        ymin = min(0, drange.ymin)
        ymax = max(0, drange.ymax)

        if xmin == xmax == ymin == ymax == 0:
            ymin = xmin = -1
            ymax = xmax = 1
        return DataRange(xmin, xmax, ymin, ymax)

    def _drawtitle(self, canvas: Canvas, diagbox: ViewBox) -> None:
        ''' Draw plot title

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
        '''
        # Quad draws the title on the left so the centered y axis
        # doesn't hit it
        if self._title:
            canvas.newgroup()
            sty = self._build_style('Graph.Title')
            canvas.text(diagbox.x, diagbox.y+diagbox.h, self._title,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='left', valign='bottom')

    def _drawframe(self, canvas: Canvas, diagbox: ViewBox) -> None:
        ''' Draw frame

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
        '''
        sty = self._build_style()
        if sty.color:
            canvas.newgroup()
            canvas.rect(diagbox.x, diagbox.y, diagbox.w, diagbox.h,
                        strokecolor='none', fill=sty.color)

    def _legendloc(self, diagbox: ViewBox, ticks: Ticks, boxw: float, boxh: float) -> PointType:
        ''' Calculate legend location

            Args:
                diagbox: ViewBox of the diagram rectangle. Legend to
                    be placed outside data area.
                ticks: Tick names and positions
                boxw: Width of legend box
                boxh: Height of legend box
        '''
        sty = self._build_style('Graph.Legend')
        arrowwidth = sty.edge_width * 3

        if self._legend == 'left':
            ytop = diagbox.y + diagbox.h
            xright = diagbox.x - arrowwidth + sty.edge_width
        elif self._legend == 'right':
            ytop = diagbox.y + diagbox.h
            xright = diagbox.x + diagbox.w + boxw + arrowwidth
        elif self._legend == 'topright':
            ytop = diagbox.y + diagbox.h - sty.pad
            xright = (diagbox.x + diagbox.w - sty.pad)
        elif self._legend == 'bottomleft':
            ytop = diagbox.y + boxh + sty.pad
            xright = (diagbox.x + boxw + sty.pad)
        elif self._legend == 'bottomright':
            ytop = diagbox.y + boxh + sty.pad
            xright = (diagbox.x + diagbox.w - sty.pad)
        else: # self._legend == 'topleft':
            ytop = diagbox.y + diagbox.h - sty.pad
            xright = (diagbox.x + boxw + sty.pad)

        return ytop, xright

    def _drawticks(self, canvas: Canvas, ticks: Ticks, diagbox: ViewBox, databox: ViewBox):
        ''' Draw tick marks and labels

            Args:
                canvas: SVG canvas to draw on
                ticks: Tick names and locations
                diagbox: ViewBox of diagram within the canvas
                databox: ViewBox of data to convert from data to
                    svg coordinates
        '''
        sty = self._build_style()
        xsty = self._build_style('Graph.TickX')
        ysty = self._build_style('Graph.TickY')
        gridx_sty = self._build_style('Graph.GridX')
        gridy_sty = self._build_style('Graph.GridX')

        canvas.newgroup()
        xform = Transform(databox, diagbox)
        xleft = xform.apply(databox.x, 0)
        xrght = xform.apply(databox.x+databox.w, 0)
        ytop = xform.apply(0, databox.y+databox.h)
        ybot = xform.apply(0, databox.y)
        sty = self._build_style()
        arrowwidth = sty.edge_width*3

        startmark = canvas.definemarker('larrow', radius=arrowwidth,
                                        color=sty.edge_color,
                                        strokecolor=sty.edge_color,
                                        orient=True)
        endmark = canvas.definemarker('arrow', radius=arrowwidth,
                                      strokecolor=sty.edge_color,
                                      color=sty.edge_color, orient=True)

        xmarker: Optional[str] = startmark
        ymarker: Optional[str] = endmark
        if databox.x == 0:
            xmarker = None
            xaxis = [xleft[0],
                     xrght[0]-xsty.width]
        else:
            xaxis = [xleft[0]+arrowwidth+xsty.width,
                     xrght[0]-arrowwidth-xsty.width]

        if databox.y == 0:
            ymarker = None
            yaxis = [ytop[1]-ysty.width,
                     ybot[1]]
        else:
            yaxis = [ytop[1]-arrowwidth-ysty.width,
                     ybot[1]+arrowwidth+ysty.width]
        
        canvas.path(xaxis,
                    [xleft[1], xrght[1]],
                    color=sty.edge_color,
                    width=sty.edge_width,
                    startmarker=xmarker,
                    endmarker=endmark)
        canvas.path([ytop[0], ybot[0]],
                    yaxis,
                    color=sty.edge_color,
                    width=sty.edge_width,
                    startmarker=startmark,
                    endmarker=ymarker)

        if self.showxticks:
            for xtick, xtickname in zip(ticks.xticks, ticks.xnames):
                if xtick == 0:
                    continue
                x, _ = xform.apply(xtick, 0)
                y1 = xleft[1] + xsty.height/2
                y2 = xleft[1] - xsty.height/2
                if gridx_sty.color not in [None, 'none']:
                    canvas.path([x, x], [ybot[1], ytop[1]],
                                color=gridx_sty.get_color(),
                                stroke=gridx_sty.stroke,
                                width=gridx_sty.stroke_width)
                    
                if xleft[0] < x < xrght[0]:
                    # Don't draw ticks outside the arrows
                    canvas.path([x, x], [y1, y2], color=xsty.get_color(),
                                width=xsty.stroke_width)

                    canvas.text(x, y2-xsty.margin, xtickname,
                                color=xsty.get_color(),
                                font=xsty.font,
                                size=xsty.font_size,
                                halign='center', valign='top')

            if ticks.xminor:
                xsty_minor = self._build_style('Graph.TickXMinor')
                for xminor in ticks.xminor:
                    if xminor in ticks.xticks:
                        continue  # Don't double-draw
                    x, _ = xform.apply(xminor, 0)
                    y1 = xleft[1] + xsty_minor.height/2
                    y2 = xleft[1] - xsty_minor.height/2
                    canvas.path([x, x], [y1, y2], color=xsty_minor.get_color(),
                                width=xsty_minor.stroke_width)

        if self.showyticks:
            for ytick, ytickname in zip(ticks.yticks, ticks.ynames):
                if ytick == 0:
                    continue
                _, y = xform.apply(0, ytick)
                x1 = ytop[0] + ysty.height/2
                x2 = ytop[0] - ysty.height/2
                if gridy_sty.stroke not in [None, 'none']:
                    canvas.path([xleft[0], xrght[0]], [y, y],
                                color=gridy_sty.get_color(),
                                stroke=gridy_sty.stroke,
                                width=gridy_sty.stroke_width)

                if ybot[1] < y < ytop[1]:
                    # Don't draw ticks outside the arrows
                    canvas.path([x1, x2], [y, y], color=ysty.get_color(),
                                width=xsty.stroke_width)

                    canvas.text(x2-ysty.margin, y, ytickname,
                            color=ysty.get_color(),
                            font=ysty.font,
                            size=ysty.font_size,
                                halign='right', valign='center')
            if ticks.yminor:
                ysty_minor = self._build_style('Graph.TickYMinor')
                for yminor in ticks.yminor:
                    if yminor in ticks.yticks:
                        continue  # Don't double-draw
                    _, y = xform.apply(0, yminor)
                    x1 = ytop[0] + ysty_minor.height/2
                    x2 = ytop[0] - ysty_minor.height/2
                    canvas.path([x1, x2], [y, y], color=ysty_minor.get_color(),
                                width=ysty_minor.stroke_width)

        if self._xname:
            sty = self._build_style('Graph.XName')
            canvas.text(xrght[0]+sty.margin+arrowwidth*1.5,
                        xrght[1],
                        self._xname,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='left', valign='center')

        if self._yname:
            sty = self._build_style('Graph.YName')
            canvas.text(ytop[0],
                        ytop[1]+sty.margin+arrowwidth*1.5,
                        self._yname,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='center', valign='bottom')

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        ticks = self._maketicks()
        dborders = self._borders()
        if borders is not None:
            dborders = Borders(
                dborders.left if borders.left is None else borders.left,
                dborders.right if borders.right is None else borders.right,
                dborders.top if borders.top is None else borders.top,
                dborders.bottom if borders.bottom is None else borders.bottom)

        diagbox = ViewBox(
            canvas.viewbox.x + dborders.left,
            canvas.viewbox.y + dborders.bottom,
            canvas.viewbox.w - (dborders.left + dborders.right),
            canvas.viewbox.h - (dborders.top + dborders.bottom))

        databox = ViewBox(ticks.xrange[0], ticks.yrange[0],
                          ticks.xrange[1]-ticks.xrange[0],
                          ticks.yrange[1]-ticks.yrange[0])

        if self._equal_aspect:
            daspect = databox.w / databox.h
            diagaspect = diagbox.w / diagbox.h
            ratio = daspect / diagaspect
            diagbox = ViewBox(
                diagbox.x,
                diagbox.y,
                diagbox.w if ratio >= 1 else diagbox.w * ratio,
                diagbox.h if ratio <= 1 else diagbox.h / ratio
            )

        self._drawframe(canvas, diagbox)
        self._drawticks(canvas, ticks, diagbox, databox)
        self._drawtitle(canvas, diagbox)
        self._drawcomponents(canvas, diagbox, databox)
        self._drawlegend(canvas, diagbox, ticks)


class GraphQuadCentered(GraphQuad):
    ''' GraphQuad with the origin always centered '''

    @lru_cache
    def datarange(self) -> DataRange:
        ''' Get range of x-y data. GraphQuad datarange must include x=0 and y=0 '''
        drange = super().datarange()
        xmin = min(0, drange.xmin)
        xmax = max(0, drange.xmax)
        ymin = min(0, drange.ymin)
        ymax = max(0, drange.ymax)

        # Keep the origin centered
        x = max(abs(xmax), abs(xmin))
        y = max(abs(ymax), abs(ymin))
        xmin, xmax = -x, x
        ymin, ymax = -y, y

        if xmin == xmax == ymin == ymax == 0:
            ymin = xmin = -1
            ymax = xmax = 1
        return DataRange(xmin, xmax, ymin, ymax)
