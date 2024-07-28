''' Layouts for creating multi-diagram drawings '''
from __future__ import annotations
from typing import Set, Optional
import xml.etree.ElementTree as ET

from .diagrams import Graph, Diagram
from .element import Component
from .canvas import Canvas, ViewBox, Borders
from .container import Container
from .drawable import Drawable
from . import diagram_stack


def diag_widths(spec: Optional[str], total: float, gap: float, ndiag: int) -> list[float]:
    ''' Get width of each column (or row) based on the specification string

        Args:
            spec: Column (or row) specification
            total: Total width to fill
            gap: Spacing between columns (or rows)
            ndiag: Number of Diagrams
            
        Notes:
            spec uses a similar style to a CSS grid layout. The string is
            space-delimited with each item either 1) a plain number representing
            the number of pixels 2) a percent of the whole width, 3) a number
            with "fr" suffix representing fractions of the whole. Examples:
                "25% 1fr" --> First column takes 25%, second column the remainder
                "200 1fr" --> First column takes 200 pixels, second column the remainder
                "2fr 1fr" --> First column is twice the width of second
    '''
    dgwidths: list[float]
    if spec is None:
        dgwidths = [(total - gap*(ndiag-1)) / ndiag] * ndiag
    else:
        specitems = spec.split()
        if len(specitems) < ndiag:
            specitems.extend([specitems[-1]]*(ndiag-len(specitems)))
        
        fixedwidths = [(ndiag-1)*gap]
        useablewidth = total - fixedwidths[0]
        fractions = []
        for v in specitems:
            if v.endswith('%'):
                fixedwidths.append(useablewidth * float(v.rstrip('%'))/100)
            elif v.endswith('fr'):
                fractions.append(float(v.rstrip('fr')))
            else:
                fixedwidths.append(float(v))
        dgwidths = []
        fixed = sum(fixedwidths)
        for v in specitems:
            if v.endswith('%'):
                dgwidths.append(useablewidth * float(v.rstrip('%'))/100)
            elif v.endswith('fr'):
                dgwidths.append((useablewidth - fixed) * float(v.rstrip('fr')) / sum(fractions))
            else:
                dgwidths.append(float(v))
        
    return dgwidths


class LayoutGrid(Container):
    ''' Lay out Diagrams in a grid. Diagrams added to the layout
        fill the grid from left to right, adding rows as needed.

        Args:
            diagrams: The diagrams to add
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
                 *diagrams: Drawable,
                 columns: int = 1,
                 column_widths: Optional[str] = None,
                 row_heights: Optional[str] = None,
                 column_gap: float = 10,
                 row_gap: float = 10,
                 **kwargs):
        super().__init__()
        self.diagrams = list(diagrams)
        self.columns = columns
        self.column_widths = column_widths
        self.row_heights = row_heights
        self.column_gap = column_gap
        self.row_gap = row_gap

    def __contains__(self, diagram: Drawable):
        return diagram in self.diagrams

    def __enter__(self):
        ''' Context Manager - put grid on drawing stack '''
        diagram_stack.push_component(self)
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

    def __iadd__(self, comp: Drawable):
        ''' Allow += notation for adding components '''
        self.add(comp)
        return self

    def add(self, diagram: Drawable):
        ''' Add a Diagram to the grid '''
        self.diagrams.append(diagram)

    def size(self, w: float = 600, h: float = 400) -> 'LayoutGrid':
        ''' Set canvas width and height '''
        self.width = w
        self.height = h
        return self

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
                      'fill': 'none', 'stroke': 'black'}
            ET.SubElement(canvas.group, 'rect', attrib=attrib)
        return canvas.xml()

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        ndiagrams = len(self.diagrams)
        ncols = self.columns if self.columns > 0 else ndiagrams

        # Convert Component, etc. to Diagrams
        drawdiags: list[Drawable] = []
        for diag in self.diagrams:
            if isinstance(diag, Component):
                sty = diag._build_style()
                a = Graph()
                a.add(diag)
                a._span = diag._span
                drawdiags.append(a)
            else:
                drawdiags.append(diag)

        def nextcell(row: int, col: int) -> tuple[int, int]:
            ''' Advance to next cell '''
            col += 1
            if col >= ncols:
                row, col = row+1, 0
            return row, col

        def usedcells(row_start: int, col_start: int, rowspan: int, colspan: int) -> Set[tuple[int, int]]:
            ''' Get all cells covered by the Diagram '''
            return {
                (row, column)
                for row in range(row_start, row_start + rowspan)
                for column in range(col_start, col_start + colspan)}
        
        cellmap: dict[tuple[int, int], Drawable] = {}  # All cells covered
        cellloc: dict[Drawable, tuple[int, int, int, int]] = {}  # Cell to x, y, x+sp, y+sp
        row, col = (0, 0)
        for diag in drawdiags:
            assert isinstance(diag, Container)
            sty = diag._build_style()
            while True:
                diagcells = usedcells(row, col, *diag._span)
                if cellmap.keys().isdisjoint(diagcells):
                    for cell in diagcells:
                        cellmap[cell] = diag
                    cellloc[diag] = row, col, row+diag._span[0], col+diag._span[1]
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
        for i, diag in enumerate(drawdiags):
            row1, col1, row2, col2 = cellloc[diag]
            if hasattr(diag, '_borders'):
                b = diag._borders()
                topborders[row1] = max(topborders[row1], b.top)
                botborders[row2-1] = max(botborders[row2-1], b.bottom)
                lftborders[col1] = max(lftborders[col1], b.left)
                rgtborders[col2-1] = max(rgtborders[col2-1], b.right)

        # Size of viewboxes, not including borders
        sty = self._build_style('Canvas')
        fullwidth = self.width if self.width else sty.width
        fullheight = self.height if self.height else sty.height

        dgwidths = diag_widths(self.column_widths, fullwidth, self.column_gap, ncols)
        dgheights = diag_widths(self.row_heights, fullheight, self.row_gap, nrows)

        vboxes = []
        for i, diag in enumerate(drawdiags):
            row1, col1, row2, col2 = cellloc[diag]
            width = sum(dgwidths[col1:col2]) + (col2-col1-1)*self.column_gap
            height = sum(dgheights[row1:row2]) + (row2-row1-1)*self.row_gap
            x = sum(dgwidths[:col1]) + col1*self.column_gap
            y = fullheight - (sum(dgheights[:row2]) + (row2-1)*self.row_gap)
            vboxes.append(ViewBox(x, y, width, height))

        # Draw a background rectangle over whole grid
        cstyle = self._build_style('Canvas')
        if cstyle.get_color() not in [None, 'none']:
            canvas.resetviewbox()
            canvas.rect(canvas.viewbox.x,
                        canvas.viewbox.y,
                        canvas.viewbox.w,
                        canvas.viewbox.h,
                        fill=cstyle.color,
                        strokecolor=cstyle.edge_color)

        # Now draw each diagram
        for i, diag in enumerate(drawdiags):
            row1, col1, row2, col2 = cellloc[diag]
            borders = Borders(
                lftborders[col1],
                rgtborders[col2-1],
                topborders[row1],
                botborders[row2-1])

            canvas.setviewbox(vboxes[i])
            diag._xml(canvas, borders=borders)
            canvas.resetviewbox()


class LayoutEmpty(Container):
    ''' Empty placeholder for layout '''
    def __init__(self):
        super().__init__()
        diagram_stack.push_component(self)

    def _borders(self, **kwargs) -> Borders:
        ''' Calculate borders around the layout box to fit the ticks and legend '''
        return Borders(0,0,0,0)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''


class LayoutV(LayoutGrid):
    ''' Lay out Diagrams in vertical stack

        Args:
            diagrams: The Diagrams/Graphs to add
            row_gap: Spacing between rows
    '''
    def __init__(self,
                 *diagrams: Drawable,
                 row_gap: float = 10, **kwargs):
        super().__init__(*diagrams,
                         row_gap=row_gap,
                         columns=1, **kwargs)


class LayoutH(LayoutGrid):
    ''' Lay out Diagrams in horizontal row
    
        Args:
            diagrams: The Diagrams/Graphs to add
            column_gap: Spacing between columns
    '''
    def __init__(self,
                 *diagrams: Drawable,
                 column_gap: float = 10, **kwargs):
        super().__init__(*diagrams,
                         column_gap=column_gap,
                         columns=-1, **kwargs)
