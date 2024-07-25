from __future__ import annotations
from typing import Sequence, Literal, Tuple
from dataclasses import dataclass, asdict


MarkerTypes = Literal['round', 'o', 'square', 's', 'triangle', '^',
                      'triangled', 'v', 'larrow', '<', 'arrow', '>',
                      '+', 'x', '-', '|', '||', '|||', 'undefined', None]
DashTypes = Literal['-', ':', 'dotted', '--', 'dashed', '-.', '.-', 'dashdot']
ColorType = str
TextPosition = Literal['N', 'E', 'S', 'W',
                       'NE', 'NW', 'SE', 'SW']
Halign = Literal['left', 'center', 'right']
Valign = Literal['top', 'center', 'baseline', 'base', 'bottom']

OffsetType = Tuple[float, float]
PointType = Tuple[float, float]
SpanType = Tuple[int, int]


@dataclass
class Style:
    ''' Style parameters, common to all Drawables

        All initiated to None, which means get from parent
    '''
    color: ColorType | None = None
    edge_color: ColorType | None = None
    stroke: DashTypes | None = None
    stroke_width: float | None = None
    opacity: float | None = None

    shape: MarkerTypes | None = None
    radius: float | None = None
    edge_width: float | None = None
    
    font: str | None = None
    font_size: float | None = None
    num_format: str | None = None

    height: float | None = None
    width: float | None = None
    margin: OffsetType | None = None
    pad: OffsetType | None = None
    span: SpanType | None = None

    colorcycle: Sequence[ColorType] | None = None
    _cycleindex: int = 0

    def __post_init__(self):
        if isinstance(self.colorcycle, str):
            self.colorcycle = [self.colorcycle]

    def _set_cycle_index(self, i: int) -> None:
        self._cycleindex = i

    def values(self):
        ''' Get dict of values that are not None '''
        return {k:v for k, v in asdict(self).items() if v is not None}

    def get_color(self) -> str:
        ''' Get color, pulling from colorcycle if necessary '''

        if self.color in ['auto', None]:
            i = self._cycleindex
            return self.colorcycle[i%len(self.colorcycle)]
        
        elif self.color.startswith('C') and self.color[1:].isnumeric():
            i = int(self.color[1:])
            return self.colorcycle[i%len(self.colorcycle)]

        return self.color

