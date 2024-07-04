''' Basic shapes '''

from __future__ import annotations
from typing import Optional

from ..series import Series
from ..canvas import Canvas, Borders, ViewBox


class ShapeBase(Series):
    ''' Filled shape '''
    def color(self, color: str) -> 'Series':
        ''' Sets the fill color '''
        self.style.marker.color = color
        return self

    def strokecolor(self, color: str) -> 'Series':
        ''' Sets the fill color '''
        self.style.marker.strokecolor = color
        return self


class Circle(ShapeBase):
    ''' Draw a circle

        Args:
            x: Center x coordinate
            y: Center y coordinate
            radius: Radius of circle
    '''
    def __init__(self, x: float, y: float, radius: float):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        canvas.circle(self.x, self.y, self.radius,
                      color=self.style.marker.color,
                      strokecolor=self.style.marker.strokecolor,
                      strokewidth=self.style.line.width,
                      dataview=databox)


class Rectangle(ShapeBase):
    ''' A line series of x-y data

        Args:
            x: X-values to plot
            y: Y-values to plot
    '''
    def __init__(self, x: float, y: float,
                 width: float, height: float,
                 cornerradius: float = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cornerradius = cornerradius

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        canvas.rect(self.x, self.y, self.width, self.height,
                    fill=self.style.marker.color,
                    strokecolor=self.style.marker.strokecolor,
                    strokewidth=self.style.line.width,
                    rcorner=self.cornerradius,
                    dataview=databox)
