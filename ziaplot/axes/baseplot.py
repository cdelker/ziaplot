''' BasePlot parent class for Axes '''
from __future__ import annotations
from typing import Sequence, Optional, Literal
import math
from functools import lru_cache
from collections import namedtuple
import xml.etree.ElementTree as ET

from ..style import styles
from ..style.styletypes import Style
from ..series import Series
from ..style import colors
from ..canvas import Canvas, ViewBox, DataRange, Borders, PointType
from .. import text
from ..drawable import Drawable
from .. import axis_stack


LegendLoc = Literal['left', 'right', 'topleft', 'topright', 'bottomleft', 'bottomright', 'none']
Ticks = namedtuple('Ticks', ['xticks', 'yticks', 'xnames', 'ynames',
                             'ywidth', 'xrange', 'yrange', 'xminor', 'yminor'])



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
        super().__init__()
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
        self.showxticks = True
        self.showyticks = True
        self.series: list[Series] = []   # List of XY lines/series
        self.legend = legend
        self._equal_aspect = False
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

    def _borders(self) -> Borders:
        return Borders(0, 0, 0, 0)

    def xrange(self, xmin: float, xmax: float) -> BasePlot:
        ''' Set x-range of data display '''
        self._xrange = xmin, xmax
        self._clearcache()
        return self

    def yrange(self, ymin, ymax):
        ''' Set y-range of data display '''
        self._yrange = ymin, ymax
        self._clearcache()
        return self

    def match_y(self, other: BasePlot):
        ''' Set this axis y range equal to the other axis's y range '''
        r = other.datarange()
        self.yrange(r.ymin, r.ymax)
        return self

    def match_x(self, other: BasePlot):
        ''' Set this axis x range equal to the other axis's x range '''
        r = other.datarange()
        self.xrange(r.xmin, r.xmax)
        return self

    def equal_aspect(self) -> BasePlot:
        ''' Set equal aspect ratio on data limits '''
        self._equal_aspect = True
        return self

    def xticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> BasePlot:
        ''' Set x axis tick values and names '''
        self._xtickvalues = values
        self._xticknames = names
        self._xtickminor = minor
        self._clearcache()
        return self

    def yticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> BasePlot:
        ''' Set y axis tick values and names '''
        self._ytickvalues = values
        self._yticknames = names
        self._ytickminor = minor
        self._clearcache()
        return self

    def noxticks(self) -> BasePlot:
        ''' Turn off x axis tick marks '''
        self.showxticks = False
        self._clearcache()
        return self

    def noyticks(self) -> BasePlot:
        ''' Turn off y axis tick marks '''
        self.showyticks = False
        self._clearcache()
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
        self._clearcache()

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

    def _clearcache(self):
        self.datarange.cache_clear()
        self._legendsize.cache_clear()

    @lru_cache
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

    @lru_cache
    def _legendsize(self) -> tuple[float, float]:
        ''' Calculate pixel size of legend '''
        series = [s for s in self.series if s._name]
        if self.legend is None or len(series) == 0:
            return 0, 0
        boxh = 0.
        boxw = 0.
        markw = 40
        square = 10
            
        for s in series:
            width, height = text.text_size(
                s._name, fontsize=self.style.legend.text.size,
                font=self.style.legend.text.font)
            if s.__class__.__name__ in ['Histogram', 'Bars', 'BarsHoriz', 'PieSlice']:
                w = square*2
            else:
                w = markw
            boxw = max(boxw, w + width + self.style.legend.margin*2)
        boxh = self.style.legend.margin + len(series)*self.style.legend.text.size*self.style.legend.linespacing
        return boxw, boxh

    def _legendloc(self, axisbox: ViewBox, ticks: Ticks, boxw: float, boxh: float) -> PointType:
        ''' Calculate legend location

            Args:
                axisbox: ViewBox of the axis rectangle. Legend to be
                    placed outside axis.
                ticks: Tick names and positions
                boxw: Width of legend box
                boxh: Height of legend box
        '''
        ytop = xright = 0
        if self.legend == 'left':
            ytop = axisbox.y + axisbox.h
            xright = (axisbox.x - self.style.tick.length -
                      ticks.ywidth - self.style.tick.textofst*2)
        elif self.legend == 'right':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x + axisbox.w + boxw + self.style.tick.textofst
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
        margin = self.style.legend.margin

        ytop, xright = self._legendloc(axisbox, ticks, boxw, boxh)

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
        yytext = ytop - self.style.legend.text.size
        for i, s in enumerate(series):
            textw, texth = text.text_size(s._name, self.style.legend.text.size)
            yyline = yytext + self.style.legend.text.size/3
            if s.__class__.__name__ in ['Histogram', 'Bars', 'BarsHoriz', 'PieSlice']:
                canvas.text(boxl+square+margin*2, yytext,
                            s._name,
                            font=self.style.legend.text.font,
                            size=self.style.legend.text.size,
                            color=self.style.legend.text.color,
                            halign='left', valign='base')
                canvas.rect(boxl+margin, yytext, square, square,
                            fill=s.style.line.color, strokewidth=1)

            else:
                canvas.text(xright-boxw+markw, yytext,
                            s._name,
                            color=self.style.axis.color,
                            font=self.style.legend.text.font,
                            size=self.style.legend.text.size,
                            halign='left', valign='base')
                linebox = ViewBox(boxl+margin, ytop-boxh, markw-margin*2, boxh)
                canvas.setviewbox(linebox)  # Clip
                canvas.path([boxl-margin*2, boxl+markw/2, boxl+markw+margin*2],
                            [yyline, yyline, yyline],
                            color=s.style.line.color,
                            width=s.style.line.width,
                            markerid=s._markername,
                            stroke=s.style.line.stroke)
                canvas.resetviewbox()
            yytext -= self.style.legend.text.size * self.style.legend.linespacing
