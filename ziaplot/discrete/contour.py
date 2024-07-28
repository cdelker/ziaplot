''' Contour plots '''
from __future__ import annotations
from typing import Optional, Sequence, Union, Literal
import xml.etree.ElementTree as ET

from ..util import zrange
from ..style import ColorFade
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..diagrams import Graph
from ..element import Element


ColorBarPos = Literal['top', 'right', 'bottom', 'left']


class Contour(Element):
    ''' Contour Plot

        Args:
            x: 1D array of x values
            y: 1D array of y values
            z: 2D array of z (height) values
            levels: Number of contour lines, or array of
                contour line levels
            colorbar: Position of colorbar, `top`, `bottom`,
                `left`, or `right`.
    '''
    def __init__(self,
                 x: Sequence[float],
                 y: Sequence[float],
                 z: Sequence[Sequence[float]],
                 levels: Union[int, Sequence[float]] = 7,
                 colorbar: Optional[ColorBarPos] = None):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.levels = levels
        self.contours: list[float] = []
        self.colorbar = colorbar

    @property
    def nlevels(self) -> int:
        ''' Number of levels in the contour '''
        if isinstance(self.levels, int):
            return self.levels
        return len(self.levels)

    def get_color_steps(self) -> list[str]:
        ''' Get colors for each level '''
        sty = self._build_style()
        if len(sty.colorcycle) > 2:
            return list(sty.colorcycle)
        return ColorFade(*sty.colorcycle).colors(self.nlevels)
    
    def colors(self, *colors: str, stops: Sequence[float]|None = None) -> 'Contour':
        ''' Set the start and end colors for the contours '''
        self._style.colorcycle = ColorFade(*colors, stops=stops).colors(self.nlevels)
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        try:  # Numpy
            return DataRange(self.x.min(),  # type: ignore
                             self.x.max(),  # type: ignore
                             self.y.min(),  # type: ignore
                             self.y.max())  # type: ignore
        except AttributeError:  # Not numpy
            return DataRange(min(self.x),
                             max(self.x),
                             min(self.y),
                             max(self.y))

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        segments = self._build_contours()
        sty = self._build_style()
        colors = self.get_color_steps()
        for (xsegs, ysegs), color in zip(segments, colors):
            if len(xsegs) > 0:
                for xs, ys in zip(xsegs, ysegs):
                    canvas.path(xs, ys,
                                stroke=sty.stroke,
                                color=color,
                                width=sty.stroke_width,
                                dataview=databox)
        if self.colorbar:
            self._draw_colorbar(canvas)

    def _build_contours(self):
        ''' Marching Squares Algorithm '''
        # This could be optimized a lot

        if isinstance(self.levels, int):
            try:  # Numpy
                mn = self.z.min()
                mx = self.z.max()
            except AttributeError:  # Not Numpy
                mn = (min(min(z) for z in self.z))
                mx = (max(max(z) for z in self.z))

            span = mx - mn
            step = span / (self.levels + 1)
            contours = zrange(mn, mx, step)
        else:
            contours = self.levels
        self.contours = contours

        segments = []
        for contour in contours:
            segmentx = []
            segmenty = []
            try:
                z0 = self.z < contour  # z is Numpy array
            except TypeError:
                # z is list of lists - much slower
                z0 = [[(z < contour) for z in row] for row in self.z]

            blockhalfw = (self.x[1]-self.x[0])/2
            blockhalfh = (self.y[1]-self.y[0])/2
            blockw = blockhalfw*2
            blockh = blockhalfh*2

            for row in range(len(self.z) - 1):
                for col in range(len(self.z[0]) - 1):
                    try:
                        # Numpy
                        block = (z0[row:row+2, col:col+2][::-1])
                        corners = self.z[row:row+2, col:col+2][::-1]
                        blockid = block[1, 0] + 2*block[1, 1] + 4*block[0, 1] + 8*block[0, 0]

                    except TypeError:
                        # Not Numpy
                        block = [zi[col:col+2] for zi in z0[row:row+2]][::-1]
                        corners = [zi[col:col+2] for zi in self.z[row:row+2]][::-1]
                        blockid = block[1][0] + 2*block[1][1] + 4*block[0][1] + 8*block[0][0]

                    blockx = (self.x[col] + self.x[col+1])/2
                    blocky = (self.y[row] + self.y[row+1])/2
                    x1 = x2 = y1 = y2 = None
                    if blockid in [1, 14]:
                        x1 = blockx
                        y1 = blocky + blockh*(contour-corners[1][0])/(corners[0][0] - corners[1][0])
                        y2 = blocky
                        x2 = blockx + blockw*(contour-corners[1][0])/(corners[1][1] - corners[1][0])
                    elif blockid in [2, 13]:
                        x1 = blockx+blockw
                        y1 = blocky + blockh*(contour-corners[1][1])/(corners[0][1] - corners[1][1])
                        y2 = blocky
                        x2 = blockx + blockw*(contour-corners[1][0])/(corners[1][1] - corners[1][0])
                    elif blockid in [3, 12]:
                        x1 = blockx
                        x2 = blockx+blockw
                        y1 = blocky + blockh*(contour-corners[1][0])/(corners[0][0]-corners[1][0])
                        y2 = blocky + blockh*(contour-corners[1][1])/(corners[0][1]-corners[1][1])
                    elif blockid in [4, 11]:
                        x1 = blockx + blockw*(contour-corners[0][0])/(corners[0][1]-corners[0][0])
                        x2 = blockx+blockw
                        y1 = blocky+blockh
                        y2 = blocky + blockh*(contour-corners[1][1])/(corners[0][1]-corners[1][1])
                    elif blockid in [6, 9]:
                        x1 = blockx + blockw*(contour-corners[0][0])/(corners[0][1]-corners[0][0])
                        x2 = blockx + blockw*(contour-corners[1][0])/(corners[1][1]-corners[1][0])
                        y1 = blocky+blockh
                        y2 = blocky
                    elif blockid in [7, 8]:
                        x1 = blockx
                        y1 = blocky + blockh*(contour-corners[1][0])/(corners[0][0]-corners[1][0])
                        x2 = blockx + blockw*(contour-corners[0][0])/(corners[0][1]-corners[0][0])
                        y2 = blocky + blockh
                    if x1 is not None:
                        segmentx.append((x1-blockhalfw, x2-blockhalfw))
                        segmenty.append((y1-blockhalfh, y2-blockhalfw))
            segments.append((segmentx, segmenty))
        return segments

    def _draw_colorbar(self, canvas: Canvas):
        ''' Draw colorbar on Diagram '''
        nlevels = self.nlevels
        colorfade = self.get_color_steps()
        cstyle = self._build_style('Contour.ColorBar')
        width = cstyle.width

        if self.colorbar in ['top', 'bottom']:
            length = canvas.viewbox.w - cstyle.margin*2
            barwidth = length // (nlevels)
            length = nlevels * barwidth  # Adjust for rounding

            x = canvas.viewbox.x + cstyle.margin
            y = canvas.viewbox.y + canvas.viewbox.h - width - cstyle.margin - cstyle.font_size
            y2 = y+width
            if self.colorbar == 'bottom':
                y = canvas.viewbox.y + cstyle.margin
                y2 = y+width
                
            for i, (level, color) in enumerate(zip(self.contours, colorfade)):
                barx = x + barwidth*(i + 0.5)
                canvas.path([barx, barx], [y, y2],
                            width=barwidth, color=color)
                if i in [0, int(nlevels//2), nlevels-1]:
                    canvas.text(barx, y2+3, format(level, cstyle.num_format),
                                color=cstyle.get_color(),
                                size=cstyle.font_size,
                                halign='center', valign='bottom')

            canvas.rect(x, y, length, width,
                        strokewidth=cstyle.stroke_width,
                        strokecolor=cstyle.edge_color,
                        fill=None)
        else:
            length = canvas.viewbox.h - cstyle.margin*2
            barwidth = length // (nlevels)
            length = nlevels * barwidth  # Adjust for rounding

            y = canvas.viewbox.y + cstyle.margin
            x = canvas.viewbox.x + cstyle.margin + cstyle.font_size
            x2 = x+width
            if self.colorbar == 'right':
                x = canvas.viewbox.x + canvas.viewbox.w - width - cstyle.margin
                x2 = x+width

            for i, (level, color) in enumerate(zip(self.contours, colorfade)):
                bary = y + barwidth*(i + 0.5)
                canvas.path([x, x2], [bary, bary],
                            width=barwidth, color=color)
                if i in [0, int(nlevels//2), nlevels-1]:
                    canvas.text(x-3, bary,
                                format(level, cstyle.num_format),
                                color=cstyle.get_color(),
                                size=cstyle.font_size,
                                rotate=90,
                                halign='center', valign='bottom')

            canvas.rect(x, y, width, length,
                        strokewidth=cstyle.stroke_width,
                        strokecolor=cstyle.edge_color,
                        fill=None)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        g = Graph()
        g.add(self)
        return g.svgxml(border=border)
