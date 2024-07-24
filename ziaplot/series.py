''' Series of X-Y Data, base class '''
from __future__ import annotations

from .style import DashTypes
from .drawable import Drawable
from .canvas import DataRange
from . import axis_stack
from .style.style import Style
from .style.css import merge_css, CssStyle
from .style import theme


class Element(Drawable):
    ''' Base class for things added to an axes '''
    step_color = False

    def __init__(self):
        super().__init__()
        self._style = Style()
        self._containerstyle: CssStyle | None = None
        self._name = None
        axis_stack.push_series(self)

    def style(self, style: str) -> 'Series':
        ''' Add CSS key-name pairs to the style '''
        self._style = merge_css(self._style, style)
        return self

    def build_style(self, name: str|None = None) -> Style:
        ''' Build the style '''
        if name is None:
            classes = [p.__qualname__ for p in self.__class__.mro()]
        else:
            classes = [name, '*']

        return theme.style(*classes,
                           cssid=self._cssid,
                           cssclass=self._csscls,
                           container=self._containerstyle,
                           instance=self._style)

    def color(self, color: str) -> 'Series':
        ''' Sets the series color '''
        self._style.color = color
        return self

    def stroke(self, stroke: DashTypes) -> 'Series':
        ''' Sets the series stroke/linestyle '''
        self._style.stroke = stroke
        return self

    def strokewidth(self, width: float) -> 'Series':
        ''' Sets the series strokewidth '''
        self._style.stroke_width = width
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(None, None, None, None)



class Series(Element):
    ''' Base class for data series, defining a single object in a plot '''
    step_color = False  # Whether to increment the color cycle
    legend_square = False  # Draw legend item as a square

    def __init__(self):
        super().__init__()
        self._style = Style()
        self._name = ''
        self._containerstyle: CssStyle | None = None
        self._markername = None  # SVG ID of marker for legend
        axis_stack.push_series(self)

    def set_cycle_index(self, index: int = 0):
        ''' Set the index of this series within the colorcycle '''
        self._style.set_cycle_index(index)

    def name(self, name: str) -> 'Series':
        ''' Sets the series name to include in the legend '''
        self._name = name
        return self

    def logy(self) -> None:
        ''' Convert y coordinates to log(y) '''

    def logx(self) -> None:
        ''' Convert x values to log(x) '''

    def _tangent_slope(self, x: float) -> float:
        ''' Calculate angle tangent to Series at x '''
        raise NotImplementedError
