''' Axes parent class for Axes '''
from __future__ import annotations
from typing import Sequence, Optional, Literal
import math
from functools import lru_cache
from collections import namedtuple
import xml.etree.ElementTree as ET

from ..style import ColorFade
from ..canvas import Canvas, ViewBox, DataRange, Borders, PointType
from .. import text
from ..container import Container
from ..figure import Figure, Element
from .. import axis_stack


LegendLoc = Literal['left', 'right', 'topleft', 'topright', 'bottomleft', 'bottomright', 'none']
Ticks = namedtuple('Ticks', ['xticks', 'yticks', 'xnames', 'ynames',
                             'ywidth', 'xrange', 'yrange', 'xminor', 'yminor'])


class Axes(Container):
    ''' Base plotting class

        CSS:
            Axes:
                color: Background color of axis
                edge_color: Color for borders
                edge_width: Width of edges

            Axes.TickX, Axes.TickY:
                color: Color of tick mark
                stroke_width: Width of tick mark
                height: Length of tick mark
                num_format: String formatter for tick mark
                pad: Stretch the x/y range by this fraction of a tick 
                margin: Distance between tick and canvas
                font: Font
                font_size: Point size of font
            Axes.TickXMinor, Axes.TickYMinor:
                color: Color of minor ticks
                height: Length of minor ticks
                stroke_width: Width of minor ticks
            Axes.GridX, Axes.GridY:
                color: Color of grid lines ('none' to remove)
                stroke: Stroke dash type of grid lines
                stroke_width: Width of grid lines
            Axes.XName, Axes.YName, Axes.Title:
                color: Color of axes titles
                font: Font of axes titles
                font_size: Font size of axes titles
                margin: Space around text
            Axes.Legend:
                edge_width: Width of legend border
                font: Font for legend entries
                font_size: Font size for legend entries
                pad: distance between legend border and contents
                radius: Size of bar/pie squares in the legend
    '''
    def __init__(self):
        super().__init__()
        self._title: str|None = None
        self._xname: str|None = None
        self._yname: str|None = None
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
        self.figures: list[Figure] = []   # List of geometric figures in the axis
        self._legend: LegendLoc = 'left'
        self._equal_aspect = False
        self.linespacing = 1.2
        self.fullbox = False
        self.width: float|None = None
        self.height: float|None = None
        self._colorfade: ColorFade|None = None

        axis_stack.push_figure(self)

        self.max_xticks = 9
        self.max_yticks = 9
        self.xminordivisions = 0
        self.yminordivisions = 0

    def __enter__(self):
        axis_stack.push_axis(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        ''' Exit context manager - save to file and display '''
        axis_stack.push_figure(None)
        axis_stack.pop_axis(self)
        if axis_stack.current_axis() is None:
            # Display if not inside another layout
            try:
                display(self)
            except NameError:  # Not in Jupyter/IPython
                pass

    def __contains__(self, figure: Figure):
        return figure in self.figures

    def __iadd__(self, figure: Figure):
        ''' Allow += notation for adding figures '''
        self.add(figure)
        return self

    def _borders(self) -> Borders:
        ''' Calculate borders around axis box to fit the ticks and legend '''
        return Borders(0, 0, 0, 0)

    def size(self, w: float = 600, h: float = 400) -> Axes:
        ''' Set canvas width and height '''
        self.width = w
        self.height = h
        return self

    def xrange(self, xmin: float, xmax: float) -> Axes:
        ''' Set x-range of data display '''
        self._xrange = xmin, xmax
        self._clearcache()
        return self

    def yrange(self, ymin, ymax):
        ''' Set y-range of data display '''
        self._yrange = ymin, ymax
        self._clearcache()
        return self

    def match_y(self, other: Axes):
        ''' Set this axis y range equal to the other axis's y range '''
        r = other.datarange()
        self.yrange(r.ymin, r.ymax)
        return self

    def match_x(self, other: Axes):
        ''' Set this axis x range equal to the other axis's x range '''
        r = other.datarange()
        self.xrange(r.xmin, r.xmax)
        return self

    def equal_aspect(self) -> Axes:
        ''' Set equal aspect ratio on data limits '''
        self._equal_aspect = True
        return self

    def title(self, title: str) -> Axes:
        ''' Set the title '''
        self._title = title
        return self

    def axesnames(self, x: str|None = None, y: str|None = None) -> Axes:
        ''' Set names for the x and y axes '''
        self._xname = x
        self._yname = y
        return self

    def legend(self, loc: LegendLoc = 'left') -> Axes:
        ''' Specify legend location '''
        self._legend = loc
        return self

    def xticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> Axes:
        ''' Set x axis tick values and names '''
        self._xtickvalues = values
        self._xticknames = names
        self._xtickminor = minor
        self._clearcache()
        return self

    def yticks(self, values: Sequence[float], names: Optional[Sequence[str]] = None,
               minor: Optional[Sequence[float]] = None) -> Axes:
        ''' Set y axis tick values and names '''
        self._ytickvalues = values
        self._yticknames = names
        self._ytickminor = minor
        self._clearcache()
        return self

    def noxticks(self) -> Axes:
        ''' Turn off x axis tick marks '''
        self.showxticks = False
        self._clearcache()
        return self

    def noyticks(self) -> Axes:
        ''' Turn off y axis tick marks '''
        self.showyticks = False
        self._clearcache()
        return self
    
    def colorfade(self, *clrs: str, stops: Optional[Sequence[float]] = None) -> Axes:
        ''' Define the color cycle evenly fading between multiple colors.

            Args:
                colors: List of colors in #FFFFFF format
                stops: List of stop positions for each color in the
                    gradient, starting with 0 and ending with 1.
        '''
        self._colorfade = ColorFade(*clrs, stops=stops)
        return self

    def _assign_figure_colors(self, figures: Sequence[Figure]):
        ''' Assign colors to figure that step the colorcycle '''
        for f in figures:
            f._containerstyle = self._containerstyle

        # Filter ones that don't step colors
        figures = [f for f in figures if f._step_color]

        # Apply colorfade if applicable
        if self._colorfade:
            colors = self._colorfade.colors(len(figures))
            for s in figures:
                s._style.colorcycle = colors

        # Set the cycle index for each figure
        i = 0
        for f in figures:
            if f._build_style().color == 'auto':
                f._style._set_cycle_index(i)
                i += 1

    def add(self, figure: Element) -> None:
        ''' Add a figure to the axis '''
        assert isinstance(figure, Element)
        self.figures.append(figure)
        self._clearcache()

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' XML for standalone SVG '''
        sty = self._build_style('Canvas')
        width = self.width if self.width else sty.width
        height = self.height if self.height else sty.height
        canvas = Canvas(width, height, fill=sty.color)
        self._xml(canvas)
        if border:
            attrib = {'x': '0', 'y': '0',
                      'width': '100%', 'height': '100%',
                      'fill': sty.color, 'stroke': sty.edge_color}
            ET.SubElement(canvas.group, 'rect', attrib=attrib)

        return canvas.xml()

    def _clearcache(self):
        ''' Clear LRU cache when inputs changes '''
        self.datarange.cache_clear()
        self._legendsize.cache_clear()

    @lru_cache
    def datarange(self) -> DataRange:
        ''' Get range of data only '''
        xmin = ymin = math.inf
        xmax = ymax = -math.inf
        for f in self.figures:
            drange = f.datarange()
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
        figures = [f for f in self.figures if f._name]
        if self._legend is None or len(figures) == 0:
            return 0, 0

        legstyle = self._build_style('Axes.Legend')
        boxh = 0.
        boxw = 0.
        markw = legstyle.radius
        square = markw / 4

        for f in figures:
            width, _ = text.text_size(
                f._name, fontsize=legstyle.font_size,
                font=legstyle.font)
            if f.legend_square:
                w = square*2
            else:
                w = markw
            boxw = max(boxw, w + width + legstyle.pad*2)
        boxh = legstyle.pad + len(figures)*legstyle.font_size*self.linespacing
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
        legsty = self._build_style('Axes.Legend')
        ytick = self._build_style('Axes.TickX')
        margin = legsty.margin + legsty.stroke_width

        ytop = xright = 0
        if self._legend == 'left':
            ytop = axisbox.y + axisbox.h
            xright = (axisbox.x - ytick.height -
                      ticks.ywidth - ytick.margin*2 + legsty.stroke_width)
        elif self._legend == 'right':
            ytop = axisbox.y + axisbox.h
            xright = axisbox.x + axisbox.w + boxw + margin - legsty.stroke_width*4
        elif self._legend == 'topright':
            ytop = axisbox.y + axisbox.h - margin
            xright = (axisbox.x + axisbox.w - margin)
        elif self._legend == 'bottomleft':
            ytop = axisbox.y + boxh + margin
            xright = (axisbox.x + boxw + margin)
        elif self._legend == 'bottomright':
            ytop = axisbox.y + boxh + legsty.margin
            xright = (axisbox.x + axisbox.w - margin)
        else: # self._legend == 'topleft':
            ytop = axisbox.y + axisbox.h - margin
            xright = (axisbox.x + boxw + margin)

        return ytop, xright

    def _drawlegend(self, canvas: Canvas, axisbox: ViewBox, ticks: Ticks) -> None:
        ''' Draw legend

            Args:
                canvas: SVG canvas to draw on
                axisbox: ViewBox of the axis rectangle. Legend to be
                    placed outside axis.
                ticks: Tick names and positions
        '''
        figures = [f for f in self.figures if f._name]
        if self._legend in [None, 'none'] or len(figures) == 0:
            return

        boxw, boxh = self._legendsize()
        legsty = self._build_style('Axes.Legend')
        legtxt = self._build_style('Axes.LegendText')
        markw = legsty.radius
        square = markw / 4
        pad = legsty.pad

        ytop, xright = self._legendloc(axisbox, ticks, boxw, boxh)

        # Draw the box
        boxl = xright - boxw
        if legsty.stroke not in [None, 'none']:
            legbox = ViewBox(boxl, ytop-boxh, boxw, boxh)
            canvas.rect(legbox.x, legbox.y, legbox.w, legbox.h,
                        strokewidth=legsty.stroke_width,
                        strokecolor=legsty.edge_color,
                        rcorner=5,
                        fill=legsty.get_color())

        # Draw each line
        yytext = ytop - legtxt.font_size
        for i, s in enumerate(figures):
            yyline = yytext + legtxt.font_size/3
            sstyle = s._build_style()
            
            if s.legend_square:
                canvas.text(boxl+square+pad*2, yytext,
                            s._name,
                            font=legtxt.font,
                            size=legtxt.font_size,
                            color=legtxt.get_color(),
                            halign='left', valign='base')
                canvas.rect(boxl+pad, yytext, square, square,
                            fill=sstyle.get_color(),
                            strokecolor=sstyle.edge_color,
                            strokewidth=sstyle.edge_width)

            else:
                canvas.text(xright-boxw+markw, yytext,
                            s._name,
                            color=legtxt.get_color(),
                            font=legtxt.font,
                            size=legsty.font_size,
                            halign='left', valign='base')
                linebox = ViewBox(boxl+pad, ytop-boxh, markw-pad*2, boxh)
                canvas.setviewbox(linebox)  # Clip
                canvas.path([boxl-pad*2, boxl+markw/2, boxl+markw+pad*2],
                            [yyline, yyline, yyline],
                            color=sstyle.get_color(),
                            width=sstyle.stroke_width,
                            markerid=s._markername,
                            stroke=sstyle.stroke)
                canvas.resetviewbox()
            yytext -= legsty.font_size * self.linespacing
