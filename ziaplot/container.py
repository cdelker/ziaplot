''' Drawing containers for holding plots, axes, etc. '''
from .drawable import Drawable
from .style.style import Style
from .style.css import CssStyle, parse_css, merge_css
from .style import theme


class Container(Drawable):
    ''' Drawing container base class (either Axes or Layouts) '''
    style_default = Style()

    def __init__(self):
        super().__init__()
        self._containerstyle = CssStyle()
        self._style = Style()
        self._cycleindex = 0

    def style(self, css: str) -> 'Drawable':
        '''Set the style for this Drawable using CSS elements '''
        self._style = merge_css(self._style, css)
        return self

    def css(self, css: str) -> 'Container':
        ''' Set the CSS style '''
        self._containerstyle = parse_css(css)
        return self

    def build_style(self, name: str|None = None) -> Style:
        ''' Build the Style '''
        if name is None:
            classes = [p.__qualname__ for p in self.__class__.mro()]
        else:
            classes = [name, '*']

        return theme.style(*classes,
                           cssid=self._cssid,
                           cssclass=self._csscls,
                           container=self._containerstyle,
                           instance=self._style)
