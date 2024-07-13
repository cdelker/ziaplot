''' Basic shapes '''

from __future__ import annotations
from typing import Optional
import math

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


class Ellipse(ShapeBase):
    ''' Draw an Ellipse

        Args:
            x: Center x coordinate
            y: Center y coordinate
            r1: Radius 1
            r2: Radius 2
            theta: Angle of rotation (degrees)
    '''
    def __init__(self, x: float, y: float,
                 r1: float, r2: float,
                 theta: float = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.r1 = r1
        self.r2 = r2
        self.theta = theta

    def _dxy(self, theta: float) -> tuple[float, float]:
        ''' Get dx and dy from center to point on ellipse at angle theta (rad) '''
        theta = theta - math.radians(self.theta)
        e = math.sqrt(1 - (self.r2/self.r1)**2)
        phi = math.atan(math.tan(theta) * self.r1 / self.r2)
        r = self.r1 * math.sqrt(1 - e**2 * math.sin(phi)**2)
        dx = r * math.cos(theta)
        dy = r * math.sin(theta)
        return dx, dy

    def _tangent(self, theta: float) -> float:
        ''' Angle (radians) tangent to the Ellipse at theta (radians) '''
        dx, dy = self._dxy(theta)
        phi = math.atan2(dy * self.r1**2, dx * self.r2**2)
        tan = phi + math.pi/2 + math.radians(self.theta)
        return (tan + math.tau) % math.tau
        return (tan + math.pi) % math.tau - math.pi

    def _xy(self, theta: float) -> tuple[float, float]:
        ''' Get x, y coordinate on the circle at the angle theta (rad) '''
        dx, dy = self._dxy(theta)

        if self.theta:
            costh = math.cos(math.radians(self.theta))
            sinth = math.sin(math.radians(self.theta))
            dx, dy = (dx * costh - dy * sinth,
                      dx * sinth + dy * costh)

        return self.x + dx, self.y + dy

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        canvas.ellipse(self.x, self.y, self.r1, self.r2,
                       theta=self.theta,
                       color=self.style.marker.color,
                       strokecolor=self.style.marker.strokecolor,
                       strokewidth=self.style.line.width,
                       dataview=databox)


class Circle(Ellipse):
    ''' Draw a circle

        Args:
            x: Center x coordinate
            y: Center y coordinate
            radius: Radius of circle
    '''
    def __init__(self, x: float, y: float, radius: float):
        super().__init__(x, y, radius, radius)

    def _xy(self, theta: float) -> tuple[float, float]:
        ''' Get x, y coordinate on the circle at the angle theta (degrees) '''
        theta = math.radians(theta)
        x = self.x + self.r1 * math.cos(theta)
        y = self.y + self.r1 * math.sin(theta)
        return x, y


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
