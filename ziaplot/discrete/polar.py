from __future__ import annotations
from typing import Sequence
import math

from .polylines import PolyLine


class LinePolar(PolyLine):
    ''' Define a data PolyLine using polar coordinates

        Args:
            radius: The radius values to plot
            theta: The theta values to plot, in degres or radians
            deg: Interpret theta as degrees instead of radians
    '''
    def __init__(self, radius: Sequence[float], theta: Sequence[float], deg: bool = False):
        self.radius = radius
        self.theta = theta
        if deg:
            self.theta = [math.radians(t) for t in theta]
        x = [r * math.cos(t) for r, t in zip(self.radius, self.theta)]
        y = [r * math.sin(t) for r, t in zip(self.radius, self.theta)]
        super().__init__(x, y)
