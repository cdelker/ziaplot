''' Color cylces '''

from typing import Sequence

class ColorCycle:
    ''' Color cycle for changing colors of plot lines

        Args:
            cycle: List of string colors, either SVG-compatible names
                or '#FFFFFF' hex values
    '''
    def __init__(self, *colors: str):
        if len(colors) > 0:
            self.cycle = colors
        else:
            self.cycle = ('#ba0c2f', '#ffc600', '#007a86', '#ed8b00',
                          '#8a387c', '#a8aa19', '#63666a', '#c05131',
                          '#d6a461', '#a7a8aa')
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
    '''
    def __init__(self, *colors: str):
        if not all([c[0] == '#' for c in colors]):
            raise ValueError('ColorFade colors must be #FFFFFF format.')
        self.colors = colors
        self.steps(len(self.colors))
        super().__init__(*self.colors)

    def steps(self, n: int) -> None:
        ''' Set number of steps between start and end color '''
        self._steps = n

        if n < 2:
            self.cycle = self.colors
            return

        c1 = self.colors[0]
        c2 = self.colors[1]

        r1, r2 = int(c1[1:3], 16), int(c2[1:3], 16)
        g1, g2 = int(c1[3:5], 16), int(c2[3:5], 16)
        b1, b2 = int(c1[5:7], 16), int(c2[5:7], 16)

        r = []
        g = []
        b = []
        rstep = (r2 - r1) / (self._steps-1)
        gstep = (g2 - g1) / (self._steps-1)
        bstep = (b2 - b1) / (self._steps-1)

        for i in range(self._steps):
            r.append(int(r1 + rstep * i))
            g.append(int(g1 + gstep * i))
            b.append(int(b1 + bstep * i))

        self.cycle = tuple([f'#{rr:02x}{gg:02x}{bb:02x}' for rr, gg, bb in zip(r, g, b)])
