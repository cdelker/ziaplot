''' Layouts for creating multi-axis plots '''
from __future__ import annotations
from typing import Set, Optional
import xml.etree.ElementTree as ET

from .axes import AxesPlot
from .series import Series
from .canvas import Canvas, ViewBox, Borders
from .drawable import Drawable
from . import axis_stack


def axis_widths(spec: Optional[str], total: float, gap: float, naxes: int) -> list[float]:
    ''' Get width of each column (or row) based on the specification string

        Args:
            spec: Column (or row) specification
            total: Total width to fill
            gap: Spacing between columns (or rows)
            naxes: Number of axes
            
        Notes:
            spec uses a similar style to a CSS grid layout. The string is
            space-delimited with each item either 1) a plain number representing
            the number of pixels 2) a percent of the whole width, 3) a number
            with "fr" suffix representing fractions of the whole. Examples:
                "25% 1fr" --> First column takes 25%, second column the remainder
                "200 1fr" --> First column takes 200 pixels, second column the remainder
                "2fr 1fr" --> First column is twice the width of second
    '''
    axwidths: list[float]
    if spec is None:
        axwidths = [(total - gap*(naxes-1)) / naxes] * naxes
    else:
        specitems = spec.split()
        if len(specitems) < naxes:
            specitems.extend([specitems[-1]]*(naxes-len(specitems)))
        
        fixedwidths = [(naxes-1)*gap]
        useablewidth = total - fixedwidths[0]
        fractions = []
        for v in specitems:
            if v.endswith('%'):
                fixedwidths.append(useablewidth * float(v.rstrip('%'))/100)
            elif v.endswith('fr'):
                fractions.append(float(v.rstrip('fr')))
            else:
                fixedwidths.append(float(v))
        axwidths = []
        fixed = sum(fixedwidths)
        for v in specitems:
            if v.endswith('%'):
                axwidths.append(useablewidth * float(v.rstrip('%'))/100)
            elif v.endswith('fr'):
                axwidths.append((useablewidth - fixed) * float(v.rstrip('fr')) / sum(fractions))
            else:
                axwidths.append(float(v))
        
    return axwidths


class LayoutGrid(Drawable):
    ''' Lay out axes in a grid. Axes added to the layout
        fill the grid from left to right, adding rows as needed.

        Args:
            axes: The axes to add
            columns: Number of columns
            column_widths: String specifying widths of each column (see Note)
            row_heights: String specifying widths of each column (see Note)
            column_gap: Spacing between columns
            row_gap: Spacing between rows

        Notes:
            column_widths and row_heights specification is a similar style to a CSS
            grid layout. The string is space-delimited with each item either 1)
            a plain number representing the number of pixels 2) a percent of the
            whole width, 3) a number with "fr" suffix representing fractions of
            the whole. Examples:
            "25% 1fr" --> First column takes 25%, second column the remainder
            "200 1fr" --> First column takes 200 pixels, second column the remainder
            "2fr 1fr" --> First column is twice the width of second
    '''
    def __init__(self,
                 *axes: Drawable,
                 columns: int = 1,
                 column_widths: Optional[str] = None,
                 row_heights: Optional[str] = None,
                 column_gap: float = 10,
                 row_gap: float = 10,
                 **kwargs):
        self.axes = list(axes)
        self.width = 600
        self.height = 400
        self.columns = columns
        self.column_widths = column_widths
        self.row_heights = row_heights
        self.column_gap = column_gap
        self.row_gap = row_gap

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

    def add(self, axis: Drawable):
        ''' Add an axis to the grid '''
        self.axes.append(axis)

    def size(self, w: float = 600, h: float = 400) -> 'LayoutGrid':
        ''' Set canvas width and height '''
        self.width = w
        self.height = h
        return self

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
        drawaxes: list[Drawable] = []
        for ax in self.axes:
            if isinstance(ax, Series):
                a = AxesPlot()
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
        
        cellmap: dict[tuple[int, int], Drawable] = {}  # All cells covered
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
            if hasattr(ax, '_borders'):
                b = ax._borders()
                topborders[row1] = max(topborders[row1], b.top)
                botborders[row2-1] = max(botborders[row2-1], b.bottom)
                lftborders[col1] = max(lftborders[col1], b.left)
                rgtborders[col2-1] = max(rgtborders[col2-1], b.right)

        # Size of viewboxes, not including borders
        axwidths = axis_widths(self.column_widths, self.width, self.column_gap, ncols)
        axheights = axis_widths(self.row_heights, self.height, self.row_gap, nrows)

        vboxes = []
        for i, ax in enumerate(drawaxes):
            row1, col1, row2, col2 = cellloc[ax]
            width = sum(axwidths[col1:col2]) + (col2-col1-1)*self.column_gap
            height = sum(axheights[row1:row2]) + (row2-row1-1)*self.row_gap
            x = sum(axwidths[:col1]) + col1*self.column_gap
            y = self.height - (sum(axheights[:row2]) + (row2-1)*self.row_gap)
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


class LayoutEmpty(Drawable):
    ''' Empty placeholder for layout '''
    def __init__(self):
        axis_stack.push_series(self)
        super().__init__()

    def _borders(self, **kwargs):
        return Borders(0,0,0,0)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''


class LayoutV(LayoutGrid):
    ''' Lay out axes in vertical stack

        Args:
            axes: The axes to add
            row_gap: Spacing between rows
    '''
    def __init__(self,
                 *axes: Drawable,
                 row_gap: float = 10, **kwargs):
        super().__init__(*axes,
                         row_gap=row_gap,
                         columns=1, **kwargs)


class LayoutH(LayoutGrid):
    ''' Lay out axis in horizontal row
    
        Args:
            axes: The axes to add
            column_gap: Spacing between columns
    '''
    def __init__(self,
                 *axes: Drawable,
                 column_gap: float = 10, **kwargs):
        super().__init__(*axes,
                         column_gap=column_gap,
                         columns=-1, **kwargs)
