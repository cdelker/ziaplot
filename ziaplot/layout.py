''' Layouts for creating multi-axis plots '''
from __future__ import annotations
from typing import Union, Set
import xml.etree.ElementTree as ET

from .axes import BasePlot, XyPlot
from .series import Series
from .canvas import Canvas, ViewBox, Borders
from .drawable import Drawable
from . import axis_stack
from typing import Optional


class GridLayout(Drawable):
    ''' Lay out axes in a grid. Axes added to the layout
        fill the grid from left to right, adding rows as needed.

        Args:
            axes: The axes to add
            width: Width of the grid
            height: Height of the grid
            columns: Number of columns
            gutter: Spacing between columns and rows
    '''
    def __init__(self,
                 *axes: BasePlot,
                 width: float = 600,
                 height: float = 400,
                 columns: int = 1,
                 gutter: float = 10,
                 **kwargs):
        self.axes = list(axes)
        self.width = width
        self.height = height
        self.columns = columns
        self.gutter = gutter

    def __contains__(self, axis: Drawable):
        return axis in self.axes

    def __enter__(self):
        ''' Context Manager - put grid on drawing stack '''
        axis_stack.push_series(self)
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

    def add(self, axis: BasePlot):
        ''' Add an axis to the grid '''
        self.axes.append(axis)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' XML for standalone SVG '''
        canvas = Canvas(self.width, self.height)
        self._xml(canvas)
        if border:
            attrib = {'x': '0', 'y': '0',
                      'width': '100%', 'height': '100%',
                      'fill': 'none', 'stroke': 'black'}
            ET.SubElement(canvas.group, 'rect', attrib=attrib)
        return canvas.xml()

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        naxes = len(self.axes)
        ncols = self.columns if self.columns > 0 else naxes

        # Convert Series, etc. to Axes
        drawaxes = []
        for ax in self.axes:
            if isinstance(ax, Series):
                a = XyPlot()
                a.add(ax)
                a.colspan, a.rowspan = ax.colspan, ax.rowspan
                drawaxes.append(a)
            else:
                drawaxes.append(ax)

        def nextcell(row: int, col: int) -> tuple[int, int]:
            ''' Advance to next cell '''
            col += 1
            if col >= ncols:
                row, col = row+1, 0
            return row, col

        def usedcells(row_start: int, col_start: int, rowspan: int, colspan: int) -> Set[tuple[int, int]]:
            ''' Get all cells covered by the axis '''
            return {
                (row, column)
                for row in range(row_start, row_start + rowspan)
                for column in range(col_start, col_start + colspan)}
        
        cellmap: dict[tuple(int, int), Drawable] = {}  # All cells covered
        cellloc: dict[Drawable, tuple[int, int, int, int]] = {}  # Cell to x, y, x+sp, y+sp
        row, col = (0, 0)
        for ax in drawaxes:
            while True:
                axcells = usedcells(row, col, ax.rowspan, ax.colspan)
                if cellmap.keys().isdisjoint(axcells):
                    for cell in axcells:
                        cellmap[cell] = ax
                    cellloc[ax] = row, col, row+ax.rowspan, col+ax.colspan
                    break
                else:
                    row, col = nextcell(row, col)
            row, col = nextcell(row, col)

        nrows = row
        nrows = max(c[0] for c in cellmap.keys()) + 1

        topborders = [0] * nrows
        botborders = [0] * nrows
        lftborders = [0] * ncols
        rgtborders = [0] * ncols

        for i, ax in enumerate(drawaxes):
            row1, col1, row2, col2 = cellloc[ax] 
            b = ax._borders()
            topborders[row1] = max(topborders[row1], b.top)
            botborders[row2-1] = max(botborders[row2-1], b.bottom)
            lftborders[col1] = max(lftborders[col1], b.left)
            rgtborders[col2-1] = max(rgtborders[col2-1], b.right)

        # Calculate viewbox for each axis
        # Without considering borders
        axheight = (self.height - self.gutter*(nrows-1)) / nrows
        axwidth = (self.width - self.gutter*(ncols-1)) / ncols

        vboxes = []
        for i, ax in enumerate(drawaxes):
            row1, col1, row2, col2 = cellloc[ax]
            width = (col2-col1)*(axwidth) + (col2-col1-1)*self.gutter
            height = (row2-row1)*(axheight) + (row2-row1-1)*self.gutter
            y = (nrows-row2) * (axheight+self.gutter) 
            x = col1 * (axwidth+self.gutter)
            vboxes.append(ViewBox(x, y, width, height))

        # Draw a background rectangle over whole grid
        # TODO: get style from layout, not last axis that was placed
        if hasattr(ax, 'style') and hasattr(ax.style, 'bgcolor'):  # type: ignore
            canvas.resetviewbox()
            canvas.rect(canvas.viewbox.x,
                        canvas.viewbox.y,
                        canvas.viewbox.w,
                        canvas.viewbox.h,
                        fill=ax.style.bgcolor,  # type: ignore
                        strokecolor=ax.style.bgcolor)  # type: ignore

        # Now draw the axes
        for i, ax in enumerate(drawaxes):
            row1, col1, row2, col2 = cellloc[ax]
            borders = Borders(
                lftborders[col1],
                rgtborders[col2-1],
                topborders[row1],
                botborders[row2-1])

            canvas.setviewbox(vboxes[i])
            ax._xml(canvas, borders=borders)
            canvas.resetviewbox()


class GridEmpty(Drawable):
    ''' Empty placeholder for layout '''
    def __init__(self):
        axis_stack.push_series(self)
        super().__init__()

    def _borders(self, **kwargs):
        return Borders(0,0,0,0)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''


class Vlayout(GridLayout):
    ''' Lay out axes in vertical stack

        Args:
            axes: The axes to add
            width: Width of the grid
            height: Height of the grid
            gutter: Spacing between rows
    '''
    def __init__(self,
                 *axes: Drawable,
                 width: float = 600,
                 height: float = 400,
                 gutter: float = 10, **kwargs):
        super().__init__(*axes, width=width, height=height,
                         gutter=gutter,
                         columns=1, **kwargs)


class Hlayout(GridLayout):
    ''' Lay out axis in horizontal row
    
        Args:
            axes: The axes to add
            width: Width of the grid
            height: Height of the grid
            gutter: Spacing between columns
    '''
    def __init__(self,
                 *axes: Drawable,
                 width: float = 600,
                 height: float = 400,
                 gutter: float = 10, **kwargs):
        super().__init__(*axes, width=width, height=height,
                         gutter=gutter,
                         columns=-1, **kwargs)
