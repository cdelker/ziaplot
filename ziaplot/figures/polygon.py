''' Polygon '''
from __future__ import annotations
from typing import Optional, Sequence
import math

from ..canvas import Canvas, Borders, ViewBox, DataRange
from ..geometry import PointType, poly_clockwise
from .shapes import Shape


class Polygon(Shape):
    ''' A Polygon. If multiple lists of vertices are provided,
        the additional lists will be "holes" in the first polygon.

        Args:
            verts: Lists of polygon Vertices
    '''
    def __init__(self, *verts: Sequence[PointType]):
        super().__init__()
        self.verts = verts

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        xs = [v[0] for side in self.verts for v in side]
        ys = [v[1] for side in self.verts for v in side]
        return DataRange(min(xs),
                         max(xs),
                         min(ys),
                         max(ys))

    def color(self, color: str) -> 'Polygon':
        ''' Sets the edge color '''
        self._style.color = color
        return self

    def fill(self, color: str) -> 'Polygon':
        ''' Set the region fill color and transparency

            Args:
                color: Fill color
        '''
        self._style.fill_color = color
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        clockwise = poly_clockwise(self.verts[0])

        parts = [self.verts[0]]
        for part in self.verts[1:]:
            if poly_clockwise(part) == clockwise:
                # Reverse the hole
                part = list(reversed(part))
            parts.append(part)

        sty = self._build_style()
        canvas.path_multi(*parts,
                          fillcolor=sty.fill_color,
                          strokecolor=sty.get_color(),
                          dataview=databox,
                          zorder=self._zorder,
                          attributes=self.svg)

    @classmethod
    def from_polar(cls, *verts: Sequence[PointType]) -> 'Polygon':
        ''' Create Polygon from vertices in polar coordinates (r, theta) '''
        rect_verts = []
        for vert in verts:
            rect_verts.append(
                [(p[0]*math.cos(p[1]), p[0]*math.sin(p[1])) for p in vert]
                )
        return cls(*rect_verts)
