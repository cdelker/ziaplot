''' Geometric Figure base class '''
from __future__ import annotations

from . import axis_stack
from .drawable import Drawable
from .canvas import DataRange
from .style.style import Style, DashTypes
from .style.css import merge_css, CssStyle
from .style.themes import zptheme


class Element(Drawable):
    ''' Base class for things added to an axes '''
    _step_color = False

    def __init__(self):
        super().__init__()
        self._style = Style()
        self._containerstyle: CssStyle | None = None
        self._name = None
        axis_stack.push_figure(self)

    def style(self, style: str) -> 'Figure':
        ''' Add CSS key-name pairs to the style '''
        self._style = merge_css(self._style, style)
        return self

    def _build_style(self, name: str|None = None) -> Style:
        ''' Build the style '''
        if name is None:
            classes = [p.__qualname__ for p in self.__class__.mro()]
        else:
            classes = [name, '*']

        return zptheme.style(
            *classes,
            cssid=self._cssid,
            cssclass=self._csscls,
            container=self._containerstyle,
            instance=self._style)

    def color(self, color: str) -> 'Figure':
        ''' Sets the figure color '''
        self._style.color = color
        return self

    def stroke(self, stroke: DashTypes) -> 'Figure':
        ''' Sets the figure stroke/linestyle '''
        self._style.stroke = stroke
        return self

    def strokewidth(self, width: float) -> 'Figure':
        ''' Sets the figure strokewidth '''
        self._style.stroke_width = width
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(None, None, None, None)


class Figure(Element):
    ''' Base class for figures, defining a single object in a plot '''
    _step_color = False  # Whether to increment the color cycle
    legend_square = False  # Draw legend item as a square

    def __init__(self):
        super().__init__()
        self._style = Style()
        self._name = ''
        self._containerstyle: CssStyle | None = None
        self._markername = None  # SVG ID of marker for legend

    def _set_cycle_index(self, index: int = 0):
        ''' Set the index of this figure within the colorcycle '''
        self._style._set_cycle_index(index)

    def name(self, name: str) -> 'Figure':
        ''' Sets the figure name to include in the legend '''
        self._name = name
        return self

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''

    def _logx(self) -> None:
        ''' Convert x values to log(x) '''

    def _tangent_slope(self, x: float) -> float:
        ''' Calculate angle tangent to Figure at x '''
        raise NotImplementedError
