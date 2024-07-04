''' Style for Smith charts '''

from __future__ import annotations
import math
from dataclasses import dataclass, field


@dataclass
class SmithGrid:
    ''' Grid specification for Smith Charts

        Attributes:
            circles: list of (R, xmax, xmin, major)
            arcs: list of (X, rmax, rmin, major)
    '''
    circles: list[tuple[float, float, float, bool]] = field(default_factory=list)
    arcs: list[tuple[float, float, float, bool]] = field(default_factory=list)


def defaultgrid():
    ''' Get default Smith grid dictionary '''
    grid = {}
    grid['coarse'] = SmithGrid(
        circles=[(.2, 2, 0, True), (.5, 5, 0, True), (1, 5, 0, True),
                 (2, math.inf, 0, True), (5, math.inf, 0, True)],
        arcs=[(.2, 2, 0, True), (.5, 2, 0, True), (1, 5, 0, True),
              (2, 5, 0, True), (5, math.inf, 0, True)])

    grid['medium'] = SmithGrid(
        circles=[(.1, 2, 0, True), (.3, 2, 0, True), (.5, 3, 0, True),
                 (1, 3, 0, True), (1.5, 5, 0, True), (2, 5, 0, True),
                 (3, 10, 0, True), (4, 10, 0, True), (5, 10, 0, True),
                 (10, 20, 0, True), (20, math.inf, 0, True)],
        arcs=[(.2, 2, 0, True), (.4, 3, 0, True), (.6, 3, 0, True),
              (.8, 3, 0, True), (1, 5, 0, True), (1.5, 5, 0, True),
              (2, 5, 0, True), (3, 10, 0, True), (4, 10, 0, True),
              (5, 10, 0, True), (10, 20, 0, True), (20, math.inf, 0, True)])

    grid['fine'] = SmithGrid(
        circles=[(.1, 1, 0, False), (.2, 2, 0, True), (.3, 1, 0, False),
                 (.4, 5, 0, True), (.5, 1, 0, False), (.6, 2, 0, True),
                 (.7, 1, 0, False), (.8, 2, 0, True), (.9, 1, 0, False),
                 (1, 10, 0, True), (1.2, 2, 0, True), (1.4, 5, 0, True),
                 (1.6, 2, 0, True), (1.8, 2, 0, False), (2.0, 10, 0, True),
                 (2.5, 5, 0, False), (3, 5, 0, True), (4, 10, 0, True),
                 (5, 10, 0, True), (6, 10, 0, False), (7, 10, 0, False),
                 (8, 10, 0, False), (9, 10, 0, False), (10, 20, 0, True),
                 (20, math.inf, 0, True)],
        arcs=[(.1, 1, 0, False), (.2, 2, 0, True), (.3, 1, 0, False),
              (.4, 5, 0, True), (.5, 1, 0, False), (.6, 2, 0, True),
              (.7, 1, 0, False), (.8, 2, 0, True), (.9, 1, 0, False),
              (1, 10, 0, True), (1.2, 2, 0, True), (1.4, 4, 0, True),
              (1.6, 2, 0, True), (1.8, 2, 0, False), (2, 10, 0, True),
              (2.5, 5, 0, False), (3, 10, 0, True), (3.5, 5, 0, False),
              (4, 10, 0, True), (5, 20, 0, True), (6, 10, 0, False),
              (7, 10, 0, False), (8, 10, 0, False), (9, 10, 0, False),
              (10, 20, 0, True), (15, 20, 0, False), (20, math.inf, 0, True)])

    grid['extrafine'] = SmithGrid(
        circles=[  # Finest wedge by 0.01
                 (.01, .2, 0, False), (.02, .5, 0, False), (.03, .2, 0, False),
                 (.04, .5, 0, False), (.05, .2, 0, False), (.06, .5, 0, False),
                 (.07, .2, 0, False), (.08, .5, 0, False), (.09, .2, 0, False),
                 (.1,  2, 0, True), (.11, .2, 0, False), (.12, .5, 0, False),
                 (.13, .2, 0, False), (.14, .5, 0, False), (.15, .2, 0, False),
                 (.16, .5, 0, False), (.17, .2, 0, False), (.18, .5, 0, False),
                 (.19, .2, 0, False), (.2, 5, 0, True), (.22, .5, 0, False),
                 # Next wedge by 0.02
                 (.24, .5, 0, False), (.26, .5, 0, False), (.28, .5, 0, False),
                 (.3, 2, 0, True), (.32, .5, 0, False), (.34, .5, 0, False),
                 (.36, .5, 0, False), (.38, .5, 0, False), (.4, 5, 0, True),
                 (.42, .5, 0, False), (.44, .5, 0, False), (.46, .5, 0, False),
                 (.48, .5, 0, False), (.5, 2, 0, True),
                 # Wedge by 0.05
                 (.55, 1, 0, False), (.6, 5, 0, True), (.65, 1, 0, False),
                 (.7, 2, 0, True), (.75, 1, 0, False), (.8, 5, 0, True),
                 (.85, 1, 0, False), (.9, 2, 0, True), (.95, 1, 0, False),
                 (1, 10, 0, True),
                 # "Sub-wedge" by 0.05x
                 (.05, 1, .5, False), (.15, 1, .5, False), (.25, 1, .5, False),
                 (.35, 1, .5, False), (.45, 1, .5, False), (1.1, 2, 0, False),
                 # Wedge x.1 from 1-2
                 (1.2, 5, 0, True), (1.3, 2, 0, False), (1.4, 5, 0, True),
                 (1.5, 2, 0, False), (1.6, 5, 0, True), (1.7, 2, 0, False),
                 (1.8, 5, 0, True), (1.9, 2, 0, False), (2.0, 20, 0, True),
                 # Wedge from 3-10
                 (2.2, 5, 0, False), (2.4, 5, 0, False), (2.6, 5, 0, False),
                 (2.8, 5, 0, False), (3.0, 10, 0, True), (3.2, 5, 0, False),
                 (3.4, 5, 0, False), (3.6, 5, 0, False), (3.8, 5, 0, False),
                 (4.0, 20, 0, True), (4.2, 5, 0, False), (4.4, 5, 0, False),
                 (4.6, 5, 0, False), (4.8, 5, 0, False), (5.0, 10, 0, True),
                 # Wedge 5+
                 (6, 20, 0, False), (7, 10, 0, False), (8, 20, 0, False),
                 (9, 10, 0, False), (10, math.inf, 0, True), (12, 20, 0, False),
                 (14, 20, 0, False), (16, 20, 0, False), (18, 20, 0, False),
                 (20, 50, 0, True), (30, 50, 0, False), (40, 50, 0, False),
                 (50, math.inf, 0, True)],
        arcs=[  # Finest wedge 0.01x
              (.01, .2, 0, False), (.02, .5, 0, False), (.03, .2, 0, False),
              (.04, .5, 0, False), (.05, .2, 0, False), (.06, .5, 0, False),
              (.07, .2, 0, False), (.08, .5, 0, False), (.09, .2, 0, False),
              (.1, 2, 0, True), (.11, .2, 0, False), (.12, .5, 0, False),
              (.13, .2, 0, False), (.14, .5, 0, False), (.15, .2, 0, False),
              (.16, .5, 0, False), (.17, .2, 0, False), (.18, .5, 0, False),
              (.19, .2, 0, False), (.2, 5, 0, True),
              # Wedge 0.02x
              (.22, .5, 0, False), (.24, .5, 0, False), (.26, .5, 0, False),
              (.28, .5, 0, False), (.3, 2, 0, True), (.32, .5, 0, False),
              (.34, .5, 0, False), (.36, .5, 0, False), (.38, .5, 0, False),
              (.4, 5, 0, True), (.42, .5, 0, False), (.44, .5, 0, False),
              (.46, .5, 0, False), (.48, .5, 0, False), (.5, 2, 0, True),
              # Wedge by 0.05x
              (.55, 1, 0, False), (.6, 5, 0, True), (.65, 1, 0, False),
              (.7, 2, 0, True), (.75, 1, 0, False), (.8, 5, 0, True),
              (.85, 1, 0, False), (.9, 2, 0, True), (.95, 1, 0, False),
              (1, 10, 0, True),
              # Subwedge x0.05 bw 0.5 and 1
              (.05, 1, .5, False), (.15, 1, .5, False), (.25, 1, .5, False),
              (.35, 1, .5, False), (.45, 1, .5, False), (.55, 1, .5, False),
              # Wedge x.1  (1-2)
              (1.1, 2, 0, False), (1.2, 5, 0, True), (1.3, 2, 0, False),
              (1.4, 5, 0, True), (1.5, 2, 0, False), (1.6, 5, 0, True),
              (1.7, 2, 0, False), (1.8, 5, 0, True), (1.9, 2, 0, False),
              (2, 20, 0, True),
              # Wedge x.2 (2-5)
              (2.2, 5, 0, False), (2.4, 5, 0, False), (2.6, 5, 0, False),
              (2.8, 5, 0, False), (3, 10, 0, True), (3.2, 5, 0, False),
              (3.4, 5, 0, False), (3.6, 5, 0, False), (3.8, 5, 0, False),
              (4, 20, 0, True), (4.2, 5, 0, False), (4.4, 5, 0, False),
              (4.6, 5, 0, False), (4.8, 5, 0, False), (5, 10, 0, True),
              # Wedge > 5
              (6, 20, 0, False), (7, 10, 0, False), (8, 20, 0, False),
              (9, 10, 0, False), (10, 20, 0, True), (12, math.inf, 0, False),
              (14, 20, 0, False), (16, 20, 0, False), (18, 20, 0, False),
              (20, 50, 0, True), (30, 50, 0, False), (40, 50, 0, False),
              (50, math.inf, 0, True)
              ])
    return grid


@dataclass
class SmithStyle:
    ''' Style for Smith Charts

        Attributes:
            grid: Dictionary of grid specifications. [coarse, medium, fine, extrafine]
            majorcolor: Color for major grid lines
            majorwidth: Stroke width for major grid lines
            minorcolor: Color for minor grid lines
            minorwidth: Stroke width for minor grid lines
    '''
    grid: dict[str, SmithGrid] = field(default_factory=defaultgrid)
    majorcolor: str = '#DDDDDD'
    majorwidth: float = 1.2
    minorcolor: str = '#E8E8E8'
    minorwidth: float = 1.0
