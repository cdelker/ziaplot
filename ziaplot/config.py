''' Global configuration options '''
from typing import Literal

try:
    import ziamath  # type: ignore
    from ziafont import config as zfconfig
except ImportError:
    zfconfig = None  # type: ignore

TextMode = Literal['text', 'path']


class Config:
    ''' Global configuration options for Ziaplot

        Attributes
        ----------
        text: How to represent text elements in SVG. Either 'text'
            or 'path'.
        svg2: Use SVG2.0. Disable for better browser compatibility,
            at the expense of SVG size
        precision: SVG decimal precision for coordinates
    '''
    _text: TextMode = 'path' if zfconfig is not None else 'text'
    _svg2: bool = True
    _precision: float = 4

    def __repr__(self):
        return f'ZPconfig(text={self.text}; svg2={self.svg2}; precision={self.precision})'

    @property
    def svg2(self) -> bool:
        if zfconfig is not None:
            return zfconfig.svg2
        else:
            return self._svg2

    @svg2.setter
    def svg2(self, value: bool) -> None:
        if zfconfig is not None:
            zfconfig.svg2 = value
        else:
            self._svg2 = value

    @property
    def precision(self) -> float:
        if zfconfig is not None:
            return zfconfig.precision
        else:
            return self._precision

    @precision.setter
    def precision(self, value: float) -> None:
        if zfconfig is not None:
            zfconfig.precision = value
        else:
            self._precision = value

    @property
    def text(self) -> TextMode:
        ''' One of 'path' or 'text'. In 'text' mode, text is drawn
            as SVG <text> elements and will be searchable in the
            SVG, however it may render differently on systems without
            the same fonts installed. In 'path' mode, text is
            converted to SVG <path> elements and will render
            independently of any fonts on the system. Path mode
            enables full rendering of math expressions, but also
            requires the ziafont/ziamath packages.
        '''
        return self._text

    @text.setter
    def text(self, value: TextMode) -> None:
        if value == 'path' and zfconfig is None:
            raise ValueError('Path mode requires ziamath package')
        if value not in ['path', 'text']:
            raise ValueError('text mode must be "path" or "text".')
        self._text = value


config = Config()
