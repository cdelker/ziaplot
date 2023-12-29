''' Contour plots '''
from __future__ import annotations
from typing import Optional, Sequence, Union, Literal
import xml.etree.ElementTree as ET

from .series import Series
from .axes import zrange, XyPlot
from .canvas import Canvas, ViewBox, DataRange
from .colors import ColorFade

ColorBarPos = Literal['top', 'right', 'bottom', 'left']


class Contour(Series):
    ''' Contour Plot

        Args:
            x: 2D array of x values
            y: 2D array of y values
            z: 2D array of z (height) values
            levels: Number of contour lines, or array of
                contour line levels
            colorbar: Position of colorbar, `top`, `bottom`,
                `left`, or `right`.
    '''
    def __init__(self,
                 x: Sequence[Sequence[float]],
                 y: Sequence[Sequence[float]],
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

    def colors(self, *colors: str, stops: Optional[Sequence[float]] = None) -> 'Contour':
        ''' Set the start and end colors for the contours '''
        self.style.colorbar.colors = ColorFade(*colors, stops=stops)
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        try:  # Numpy
            return DataRange(self.x.min(),  # type: ignore
                             self.x.max(),  # type: ignore
                             self.y.min(),  # type: ignore
                             self.y.max())  # type: ignore
        except AttributeError:  # Not numpy
            return DataRange(min(min(x) for x in self.x),
                             max(max(x) for x in self.x),
                             min(min(y) for y in self.y),
                             max(max(y) for y in self.y))

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None):
        ''' Add XML elements to the canvas '''
        segments = self._build_contours()
        colors = self.style.colorbar.colors
        colors.steps(len(segments))
        for (xsegs, ysegs), color in zip(segments, colors):
            if len(xsegs) > 0:
                for xs, ys in zip(xsegs, ysegs):
                    canvas.path(xs, ys,
                                stroke=self.style.line.stroke,
                                color=color,
                                width=self.style.line.width,
                                dataview=databox)
        if self.colorbar:
            self._draw_colorbar(canvas, databox)

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
                Y = self.y[:, 0]
            except TypeError:
                # z is list of lists - much slower
                z0 = [[(z < contour) for z in row] for row in self.z]
                Y = [y[0] for y in self.y]

            X = self.x[0]
            z = self.z

            blockhalfw = (X[1]-X[0])/2
            blockhalfh = (Y[1]-Y[0])/2
            blockw = blockhalfw*2
            blockh = blockhalfh*2

            for row in range(len(z) - 1):
                for col in range(len(z[0]) - 1):
                    try:
                        # Numpy
                        block = (z0[row:row+2, col:col+2][::-1])
                        corners = self.z[row:row+2, col:col+2][::-1]
                    except TypeError:
                        # Not Numpy
                        block = [zi[col:col+2] for zi in z0[row:row+2]][::-1]
                        corners = [zi[col:col+2] for zi in z[row:row+2]][::-1]

                    blockid = block[1][0] + 2*block[1][1] + 4*block[0][1] + 8*block[0][0]
                    blockx = (X[col] + X[col+1])/2
                    blocky = (Y[row] + Y[row+1])/2
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

    def _draw_colorbar(self, canvas: Canvas, databox: Optional[ViewBox] = None):
        ''' Draw colorbar on axis '''
        nlevels = len(self.contours)
        xpad = self.style.colorbar.xpad
        ypad = self.style.colorbar.ypad
        width = self.style.colorbar.width
        colorfade = self.style.colorbar.colors
        colorfade.steps(nlevels)

        if self.colorbar in ['top', 'bottom']:
            length = canvas.viewbox.w - xpad*2
            barwidth = length // (nlevels)
            length = nlevels * barwidth  # Adjust for rounding

            x = canvas.viewbox.x + xpad
            y = canvas.viewbox.y + canvas.viewbox.h - width - ypad*2.5
            y2 = y+width
            if self.colorbar == 'bottom':
                y = canvas.viewbox.y + ypad
                y2 = y+width
                
            for i, (level, color) in enumerate(zip(self.contours, colorfade)):
                barx = x + barwidth*(i + 0.5)
                canvas.path([barx, barx], [y, y2],
                            width=barwidth, color=color)
                if i in [0, int(nlevels//2), nlevels-1]:
                    canvas.text(barx, y2+3, format(level, self.style.colorbar.formatter),
                                color=self.style.colorbar.text.color,
                                size=self.style.colorbar.text.size,
                                halign='center', valign='bottom')

            canvas.rect(x, y, length, width,
                        strokewidth=self.style.colorbar.borderwidth,
                        strokecolor=self.style.colorbar.bordercolor,
                        fill=None)
        else:
            xpad, ypad = ypad, xpad
            length = canvas.viewbox.h - xpad*2
            barwidth = length // (nlevels)
            length = nlevels * barwidth  # Adjust for rounding

            y = canvas.viewbox.y + xpad
            x = canvas.viewbox.x + ypad
            x2 = x+width
            if self.colorbar == 'right':
                x = canvas.viewbox.x + canvas.viewbox.w - width - xpad
                x2 = x+width

            for i, (level, color) in enumerate(zip(self.contours, colorfade)):
                bary = y + barwidth*(i + 0.5)
                canvas.path([x, x2], [bary, bary],
                            width=barwidth, color=color)
                if i in [0, int(nlevels//2), nlevels-1]:
                    canvas.text(x-3, bary,
                                format(level, self.style.colorbar.formatter),
                                color=self.style.colorbar.text.color,
                                size=self.style.colorbar.text.size,
                                rotate=90,
                                halign='center', valign='bottom')

            canvas.rect(x, y, width, length,
                        strokewidth=self.style.colorbar.borderwidth,
                        strokecolor=self.style.colorbar.bordercolor,
                        fill=None)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        ax = XyPlot(style=self._axisstyle)
        ax.add(self)
        return ax.svgxml(border=border)
