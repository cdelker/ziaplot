''' Color cylces '''
from __future__ import annotations
from typing import Sequence

from ..util import interp, linspace


class ColorCycle:
    ''' Color cycle for changing colors of plot lines

        Args:
            cycle: List of string colors, either SVG-compatible names
                or '#FFFFFF' hex values
    '''
    def __init__(self, *colors: str):
        if len(colors) > 0:
            self.cycle = list(colors)
        else:
            self.cycle = ['#ba0c2f', '#ffc600', '#007a86', '#ed8b00',
                          '#8a387c', '#a8aa19', '#63666a', '#c05131',
                          '#d6a461', '#a7a8aa']
        self._steps = 10

    def steps(self, n: int) -> None:
        ''' Set number of steps in cycle '''
        pass  # Nothing to do in regular cycle

    def __getitem__(self, item):
        if isinstance(item, str):
            try:
                item = int(item[1:])  # 'C0', etc.
            except ValueError:
                return item  # named color
        return self.cycle[item % len(self.cycle)]


class ColorFade(ColorCycle):
    ''' Color cycle for changing colors of plot lines by fading
        between two colors

        Args:
            colors: List of string colors, either SVG-compatible names
                or '#FFFFFF' hex values
            stops: List of stop positions for each color in the
                gradient, starting with 0 and ending with 1.
    '''
    def __init__(self, *colors: str, stops: Sequence[float]|None = None):
        if not all(c[0] == '#' for c in colors):
            raise ValueError('ColorFade colors must be #FFFFFF format.')
        self._colors = list(colors)
        self._stops = stops
        if self._stops is not None:
            if len(self._stops) != len(colors):
                raise ValueError('Stops must be same length as colors')
            if self._stops[0] != 0 or self._stops[-1] != 1:
                raise ValueError('First stop must be 0 and last stop must be 1')

        self.steps(len(self._colors))
        super().__init__(*self._colors)

    def colors(self, n: int) -> list[str]:
        ''' Get list of colors for n steps '''
        self.steps(n)
        return self.cycle

    def steps(self, n: int) -> None:
        ''' Set number of steps between start and end color '''
        self._steps = n

        if n < 2:
            self.cycle = self._colors
            return

        if self._stops is None:
            self._stops = linspace(0, 1, len(self._colors))  # Evenly spaced colors...

        norm_steps = linspace(0, 1, self._steps)

        stop_r = [int(c[1:3], 16) for c in self._colors]
        stop_g = [int(c[3:5], 16) for c in self._colors]
        stop_b = [int(c[5:7], 16) for c in self._colors]

        R = interp(norm_steps, self._stops, stop_r)
        G = interp(norm_steps, self._stops, stop_g)
        B = interp(norm_steps, self._stops, stop_b)
        R = [int(x) for x in R]
        G = [int(x) for x in G]
        B = [int(x) for x in B]
        self.cycle = [f'#{rr:02x}{gg:02x}{bb:02x}' for rr, gg, bb in zip(R, G, B)]
