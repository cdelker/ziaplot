''' One-dimensional Graph (Number line) '''
from __future__ import annotations
from typing import Sequence, Optional
from functools import lru_cache

from .graph import Graph
from .. import text
from ..canvas import Canvas, Transform, ViewBox, DataRange, Borders, PointType
from ..util import zrange, linspace
from .diagram import Diagram, Ticks


class NumberLine(Graph):
    ''' Number Line
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
            leftborder += lsty.edge_width
        elif self._legend == 'right':
            rightborder += lsty.edge_width

        drange = self.datarange()
        if drange.xmin == 0:
            leftborder += ticks.ywidth

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
        ''' Get range of x-y data. '''
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
        ''' Draw title

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
        '''
        if self._title:
            sty = self._build_style('Graph.Title')
            canvas.text(diagbox.x+diagbox.w/2, diagbox.y+diagbox.h, self._title,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='center', valign='bottom')

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

        xform = Transform(databox, diagbox)
        xleft = xform.apply(databox.x, 0)
        xrght = xform.apply(databox.x+databox.w, 0)
        sty = self._build_style()
        arrowwidth = sty.edge_width*3

        startmark = canvas.definemarker('larrow', radius=arrowwidth,
                                        color=sty.edge_color,
                                        strokecolor=sty.edge_color,
                                        orient=True)
        endmark = canvas.definemarker('arrow', radius=arrowwidth,
                                      strokecolor=sty.edge_color,
                                      color=sty.edge_color, orient=True)

        if databox.x == 0:
            xaxis = [xleft[0],
                     xrght[0]-xsty.width]
        else:
            xaxis = [xleft[0]+arrowwidth+xsty.width,
                     xrght[0]-arrowwidth-xsty.width]

        canvas.path(xaxis,
                    [xleft[1], xrght[1]],
                    color=sty.edge_color,
                    width=sty.edge_width,
                    startmarker=startmark,
                    endmarker=endmark,
                    zorder=self._zorder)

        if self.showxticks:
            for xtick, xtickname in zip(ticks.xticks, ticks.xnames):
                x, _ = xform.apply(xtick, 0)
                y1 = xleft[1] + xsty.height/2
                y2 = xleft[1] - xsty.height/2
                if xleft[0] < x < xrght[0]:
                    # Don't draw ticks outside the arrows
                    canvas.path([x, x], [y1, y2], color=xsty.get_color(),
                                width=xsty.stroke_width,
                                zorder=self._zorder)

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
                                width=xsty_minor.stroke_width,
                                zorder=self._zorder)

        if self._xname:
            sty = self._build_style('Graph.XName')
            canvas.text(xrght[0]+sty.margin+arrowwidth*1.5,
                        xrght[1],
                        self._xname,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='left', valign='center')

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

        self._drawticks(canvas, ticks, diagbox, databox)
        self._drawtitle(canvas, diagbox)
        self._drawcomponents(canvas, diagbox, databox)
        self._drawlegend(canvas, diagbox, ticks)
