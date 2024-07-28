''' Histogram and bar chart Bars '''
from __future__ import annotations
from typing import Optional, Sequence
import math
import xml.etree.ElementTree as ET
from collections import Counter

from ..text import Halign
from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..diagrams import Graph
from ..element import Element


class Bars(Element):
    ''' A series of bars to add to an Graph (quantitative x values)
        For qualitative bar chart, use a BarChart instance.

        Args:
            x: X-values of each bar
            y: Y-values of each bar
            y2: Minimum y-values of each bar
            width: Width of all bars
            align: Bar position in relation to x value
    '''
    _step_color = True
    legend_square = True

    def __init__(self, x: Sequence[float], y: Sequence[float], y2: Optional[Sequence[float]] = None,
                 width: Optional[float] = None, align: Halign = 'center'):
        super().__init__()
        self.x = x
        self.y = y
        self.align = align
        self.width = width if width is not None else self.x[1]-self.x[0]
        self.y2 = y2 if y2 is not None else [0] * len(self.x)

    def datarange(self):
        ''' Get x-y datarange '''
        ymin, ymax = min(self.y2), max(self.y)+max(self.y)/25
        if self.align == 'left':
            xmin, xmax = min(self.x), max(self.x)+self.width
        elif self.align == 'center':
            xmin, xmax = min(self.x)-self.width/2, max(self.x)+self.width/2
        else:  # self.align == 'right':
            xmin, xmax = min(self.x)-self.width, max(self.x)
        return DataRange(xmin, xmax, ymin, ymax)

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''
        self.y = [math.log10(y) for y in self.y]

    def _logx(self) -> None:
        ''' Convert x values to log(x) '''
        self.x = [math.log10(x) for x in self.x]
        self.width = math.log10(self.x[1] - math.log10(self.x[0]))

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()
        for x, y, y2 in zip(self.x, self.y, self.y2):
            if self.align == 'center':
                x -= self.width/2
            elif self.align == 'right':
                x -= self.width

            canvas.rect(x, y2, self.width, y-y2,
                        fill=color,
                        strokecolor=sty.edge_color,
                        strokewidth=sty.edge_width,
                        dataview=databox)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        graph = Graph()
        graph.add(self)
        return graph.svgxml(border=border)


class BarsHoriz(Bars):
    ''' Horizontal bars '''
    def datarange(self) -> DataRange:
        ''' Get x-y datarange '''
        rng = super().datarange()  # Transpose it
        return DataRange(rng.ymin, rng.ymax, rng.xmin, rng.xmax)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()
        for x, y, y2 in zip(self.x, self.y, self.y2):
            if self.align == 'center':
                x -= self.width/2
            elif self.align in ['right', 'top']:
                x -= self.width

            canvas.rect(y2, x, y-y2,
                        self.width,
                        fill=color,
                        strokecolor=sty.edge_color,
                        strokewidth=sty.edge_width,
                        dataview=databox)


class Histogram(Bars):
    ''' Histogram data

        Args:
            x: Data to show as histogram
            bins: Number of bins for histogram
            binrange: Tuple of (start, stop, step) defining bins
            density: Normalize the histogram
            weights: Weights to apply to each x value
    '''
    def __init__(self, x: Sequence[float], bins: Optional[int] = None,
                 binrange: Optional[tuple[float, float, float]] = None,
                 density: bool = False, weights: Optional[Sequence[float]] = None):
        xmin = min(x)
        if binrange is not None:
            binleft = binrange[0]
            binright = binrange[1]
            binwidth = binrange[2]
            bins = math.ceil((binright - binleft) / binwidth)
            binlefts = [binleft + binwidth*i for i in range(bins)]
        elif bins is None:
            bins = math.ceil(math.sqrt(len(x)))
            binwidth = (max(x) - xmin) / bins
            binlefts = [xmin + binwidth*i for i in range(bins)]
            binright = binlefts[-1] + binwidth
        else:
            binwidth = (max(x) - xmin) / bins
            binlefts = [xmin + binwidth*i for i in range(bins)]
            binright = binlefts[-1] + binwidth

        binr = binright-binlefts[0]
        xnorm = [(xx-binlefts[0])/binr * bins for xx in x]
        xint = [math.floor(v) for v in xnorm]

        if weights is None:
            counter = Counter(xint)
            counts: list[float] = [counter[xx] for xx in range(bins)]
            if binrange is None:
                # If auto-binning, need to include rightmost endpoint
                counts[-1] += counter[bins]
        else:  # weighed
            counts = [0] * bins
            for w, b in zip(weights, xint):
                try:
                    counts[b] += w
                except IndexError:
                    if b == len(counts) and binrange is None:
                        # If auto-binning, need to include rightmost endpoint
                        counts[-1] += w

        if density:
            cmax = sum(counts) * binwidth
            counts = [c/cmax for c in counts]

        super().__init__(binlefts, counts, align='left')


class HistogramHoriz(Histogram, BarsHoriz):
    pass
