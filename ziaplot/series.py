''' Series of X-Y Data, base class '''

from copy import deepcopy

from .styletypes import MarkerTypes, DashTypes
from .styles import Default
from .drawable import Drawable
from .canvas import DataRange
from . import axis_stack
from typing import Optional


class Series(Drawable):
    ''' Base class for data series, defining a single line in a plot '''
    def __init__(self):
        self._name = ''
        axis = axis_stack.current_axis()
        if axis and hasattr(axis, 'style'):
            self.style = deepcopy(axis.style.series)
            self._axisstyle = axis.style
        else:
            self._axisstyle = Default()
            self.style = self._axisstyle.series

        self._markername = None  # SVG ID of marker
        axis_stack.push_series(self)

    def datarange(self) -> DataRange:
        return DataRange(None, None, None, None)

    def color(self, color: str) -> 'Series':
        ''' Sets the series color '''
        self.style.line.color = color
        self.style.marker.color = color
        return self

    def stroke(self, stroke: DashTypes) -> 'Series':
        ''' Sets the series stroke/linestyle '''
        self.style.line.stroke = stroke
        return self

    def strokewidth(self, width: float) -> 'Series':
        ''' Sets the series strokewidth '''
        self.style.line.width = width
        return self

    def marker(self, marker: MarkerTypes, radius: Optional[float] = None, orient: bool = False) -> 'Series':
        ''' Sets the series marker '''
        self.style.marker.shape = marker
        self.style.marker.orient = orient
        if radius:
            self.style.marker.radius = radius
        return self

    def name(self, name: str) -> 'Series':
        ''' Sets the series name to include in the legend '''
        self._name = name
        return self
