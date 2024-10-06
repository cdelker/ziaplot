''' Polygon '''
from __future__ import annotations
from typing import Optional, Sequence

from ..canvas import Canvas, Borders, ViewBox, DataRange
from .shapes import Shape
from ..style import PointType


class Polygon(Shape):
    ''' A Polygon

        Args:
            v: Vertices
    '''
    def __init__(self, verts: Sequence[PointType]):
        super().__init__()
        self.verts = verts

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        xs = [v[0] for v in self.verts]
        ys = [v[1] for v in self.verts]
        return DataRange(min(xs),
                         max(xs),
                         min(ys),
                         max(ys))

    def color(self, color: str) -> 'Polygon':
        ''' Sets the edge color '''
        self._style.edge_color = color
        return self

    def fill(self, color: str) -> 'Polygon':
        ''' Set the region fill color and transparency

            Args:
                color: Fill color
        '''
        self._style.color = color
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        canvas.poly(self.verts,
                    color=sty.get_color(),
                    strokecolor=sty.edge_color,
                    strokewidth=sty.stroke_width,
                    dataview=databox,
                    zorder=self._zorder)
