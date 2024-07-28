''' Diagram - a blank drawing surface and base class for Graphs
    which add axes.
 '''
from __future__ import annotations
from typing import Sequence, Optional, Literal
import math
from functools import lru_cache
from collections import namedtuple
import xml.etree.ElementTree as ET

from ..style import ColorFade
from ..drawable import Drawable
from ..canvas import Canvas, ViewBox, DataRange, Borders, PointType
from .. import text
from ..container import Container
from ..element import Element, Component
from .. import diagram_stack


LegendLoc = Literal['left', 'right', 'topleft', 'topright', 'bottomleft', 'bottomright', 'none']
Ticks = namedtuple('Ticks', ['xticks', 'yticks', 'xnames', 'ynames',
                             'ywidth', 'xrange', 'yrange', 'xminor', 'yminor'])


class Diagram(Container):
    ''' Base plotting class '''
    def __init__(self) -> None:
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
        self.components: list[Component] = []   # List of Components in the Diagram
        self._legend: LegendLoc = 'left'
        self._equal_aspect = True
        self.linespacing = 1.2
        self.fullbox = False
        self._colorfade: ColorFade|None = None
        self.max_xticks = 9
        self.max_yticks = 9
        self.xminordivisions = 0
        self.yminordivisions = 0
        self._pad_datarange = False
        diagram_stack.push_component(self)

    def __enter__(self):
        diagram_stack.push_diagram(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        ''' Exit context manager - save to file and display '''
        diagram_stack.push_component(None)
        diagram_stack.pop_diagram(self)
        if diagram_stack.current_diagram() is None:
            # Display if not inside another layout
            try:
                display(self)
            except NameError:  # Not in Jupyter/IPython
                pass

    def __contains__(self, comp: Drawable):
        return comp in self.components

    def __iadd__(self, comp: Component):
        ''' Allow += notation for adding components '''
        self.add(comp)
        return self

    def _borders(self) -> Borders:
        ''' Calculate borders around data area to fit the ticks and legend '''
        if self._title:
            sty = self._build_style('Graph.Title')
            title_size = sty.font_size
            return Borders(0, 0, title_size+4, 0)

        return Borders(0, 0, 0, 0)

    def size(self, w: float = 600, h: float = 400) -> Diagram:
        ''' Set canvas width and height '''
        self.width = w
        self.height = h
        return self

    def xrange(self, xmin: float, xmax: float) -> Diagram:
        ''' Set x-range of data display '''
        self._xrange = xmin, xmax
        self._clearcache()
        return self

    def yrange(self, ymin, ymax):
        ''' Set y-range of data display '''
        self._yrange = ymin, ymax
        self._clearcache()
        return self

    def match_y(self, other: Diagram):
        ''' Set this diagram's y range equal to the other diagram's y range '''
        r = other.datarange()
        self.yrange(r.ymin, r.ymax)
        return self

    def match_x(self, other: Diagram):
        ''' Set this diagram's x range equal to the other diagram's x range '''
        r = other.datarange()
        self.xrange(r.xmin, r.xmax)
        return self

    def equal_aspect(self) -> Diagram:
        ''' Set equal aspect ratio on data limits '''
        self._equal_aspect = True
        return self

    def title(self, title: str) -> Diagram:
        ''' Set the title '''
        self._title = title
        return self

    def legend(self, loc: LegendLoc = 'left') -> Diagram:
        ''' Specify legend location '''
        self._legend = loc
        return self
    
    def colorfade(self, *clrs: str, stops: Optional[Sequence[float]] = None) -> Diagram:
        ''' Define the color cycle evenly fading between multiple colors.

            Args:
                colors: List of colors in #FFFFFF format
                stops: List of stop positions for each color in the
                    gradient, starting with 0 and ending with 1.
        '''
        self._colorfade = ColorFade(*clrs, stops=stops)
        return self

    def _assign_component_colors(self, components: Sequence[Component]):
        ''' Assign colors to component that step the colorcycle '''
        for comp in components:
            comp._containerstyle = self._containerstyle

        # Filter ones that don't step colors
        components = [f for f in components if f._step_color]

        # Apply colorfade if applicable
        if self._colorfade:
            colors = self._colorfade.colors(len(components))
            for comp in components:
                comp._style.colorcycle = colors

        # Set the cycle index for each component
        i = 0
        for comp in components:
            if comp._build_style().color == 'auto':
                comp._style._set_cycle_index(i)
                i += 1

    def add(self, comp: Component) -> None:
        ''' Add a component to the diagram '''
        assert isinstance(comp, Component)
        self.components.append(comp)
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
        for f in self.components:
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
        components = [elm for elm in self.components if elm._name]
        if self._legend is None or len(components) == 0:
            return 0, 0

        legstyle = self._build_style('Graph.Legend')
        boxh = 0.
        boxw = 0.
        markw = legstyle.radius
        square = markw / 4

        for f in components:
            assert isinstance(f, Element)
            if not f._name:
                continue
            width, _ = text.text_size(
                f._name, fontsize=legstyle.font_size,
                font=legstyle.font)
            if f.legend_square:
                w = square*2
            else:
                w = markw
            boxw = max(boxw, w + width + legstyle.pad*2)
        boxh = legstyle.pad + len(components)*legstyle.font_size*self.linespacing
        return boxw, boxh

    def _legendloc(self, diagbox: ViewBox, ticks: Ticks, boxw: float, boxh: float) -> PointType:
        ''' Calculate legend location

            Args:
                diagbox: ViewBox of the data area. Legend to be
                    placed outside.
                ticks: Tick names and positions
                boxw: Width of legend box
                boxh: Height of legend box
        '''
        legsty = self._build_style('Graph.Legend')
        ytick = self._build_style('Graph.TickX')
        margin = legsty.margin + legsty.stroke_width

        ytop = xright = 0
        if self._legend == 'left':
            ytop = diagbox.y + diagbox.h
            xright = (diagbox.x - ytick.height -
                      ticks.ywidth - ytick.margin*2 + legsty.stroke_width)
        elif self._legend == 'right':
            ytop = diagbox.y + diagbox.h
            xright = diagbox.x + diagbox.w + boxw + margin - legsty.stroke_width*4
        elif self._legend == 'topright':
            ytop = diagbox.y + diagbox.h - margin
            xright = (diagbox.x + diagbox.w - margin)
        elif self._legend == 'bottomleft':
            ytop = diagbox.y + boxh + margin
            xright = (diagbox.x + boxw + margin)
        elif self._legend == 'bottomright':
            ytop = diagbox.y + boxh + legsty.margin
            xright = (diagbox.x + diagbox.w - margin)
        else: # self._legend == 'topleft':
            ytop = diagbox.y + diagbox.h - margin
            xright = (diagbox.x + boxw + margin)

        return ytop, xright

    def _drawlegend(self, canvas: Canvas, diagbox: ViewBox, ticks: Ticks) -> None:
        ''' Draw legend

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of the data area. Legend to be
                    placed outside.
                ticks: Tick names and positions
        '''
        components = [comp for comp in self.components if comp._name]
        if self._legend in [None, 'none'] or len(components) == 0:
            return

        boxw, boxh = self._legendsize()
        legsty = self._build_style('Graph.Legend')
        legtxt = self._build_style('Graph.LegendText')
        markw = legsty.radius
        square = markw / 4
        pad = legsty.pad

        ytop, xright = self._legendloc(diagbox, ticks, boxw, boxh)

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
        for comp in components:
            assert isinstance(comp, Element)
            if not comp._name:
                continue

            yyline = yytext + legtxt.font_size/3
            sstyle = comp._build_style()
            
            if comp.legend_square:
                canvas.text(boxl+square+pad*2, yytext,
                            comp._name,
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
                            comp._name,
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
                            markerid=comp._markername,
                            stroke=sstyle.stroke)
                canvas.resetviewbox()
            yytext -= legsty.font_size * self.linespacing

    def _drawtitle(self, canvas: Canvas, diagbox: ViewBox) -> None:
        ''' Draw plot title

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
        '''
        if self._title:
            canvas.newgroup()
            sty = self._build_style('Graph.Title')
            centerx = diagbox.x + diagbox.w/2
            canvas.text(centerx, diagbox.y+diagbox.h, self._title,
                        color=sty.get_color(),
                        font=sty.font,
                        size=sty.font_size,
                        halign='center', valign='bottom')

    def _drawcomponents(self, canvas: Canvas, diagbox: ViewBox, databox: ViewBox) -> None:
        ''' Draw all components to the diagram

            Args:
                canvas: SVG canvas to draw on
                diagbox: ViewBox of diagram within the canvas
                databox: ViewBox of data to convert from data to svg coordinates
        '''
        canvas.setviewbox(diagbox)
        self._assign_component_colors(self.components)

        for comp in self.components:
            comp._xml(canvas, databox=databox)
        canvas.resetviewbox()

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
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

        rng = self.datarange()

        # Expand data range slightly so strokes aren't cut off
        padx = (rng.xmax-rng.xmin)*.05
        pady = (rng.ymax-rng.ymin)*.05
        databox = ViewBox(rng.xmin- padx,
                          rng.ymin - pady,
                          rng.xmax-rng.xmin + padx*2,
                          rng.ymax-rng.ymin + pady*2)

        # Adjust aspect ratio
        if self._equal_aspect:
            daspect = databox.w / databox.h
            aspect = diagbox.w / diagbox.h
            ratio = daspect / aspect
            diagbox = ViewBox(
                diagbox.x,
                diagbox.y,
                diagbox.w if ratio >= 1 else diagbox.w * ratio,
                diagbox.h if ratio <= 1 else diagbox.h / ratio
            )

        self._drawtitle(canvas, diagbox)
        self._drawcomponents(canvas, diagbox, databox)
