''' Drawing containers for holding Diagrams and Components '''
from __future__ import annotations

from .drawable import Drawable
from .style.style import Style, AppliedStyle
from .style.css import CssStyle, parse_css, merge_css
from .style.themes import zptheme
from . import diagram_stack


class Container(Drawable):
    ''' Drawing container base class (either Diagrams or Layouts) '''
    def __init__(self) -> None:
        super().__init__()
        self._containerstyle = CssStyle()
        self._style = Style()
        self._cycleindex = 0
        self.width: float|None = None
        self.height: float|None = None

    def style(self, css: str) -> 'Drawable':
        '''Set the style for this Drawable using CSS elements '''
        self._style = merge_css(self._style, css)
        return self

    def css(self, css: str) -> 'Container':
        ''' Set the CSS style '''
        self._containerstyle = parse_css(css)
        return self

    def _build_style(self, name: str|None = None) -> AppliedStyle:
        ''' Build the Style '''
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


def save(fname: str) -> None:
    ''' Save the current drawing to a file. Must be
        used within a Diagram or Layout context manager.

        Args:
            fname: Filename, with extension.

        Notes:
            SVG format is always supported. EPS, PDF, and PNG formats are
            available when the `cairosvg` package is installed
    '''
    diagram_stack.push_component(None)
    d = diagram_stack.current_diagram()
    if d is None:
        raise ValueError('No diagram to save. ziaplot.save must be run within context manager.')
    diagram_stack.pause = True
    d.save(fname)
    diagram_stack.pause = False
