''' Bezier Curves '''
from __future__ import annotations
from typing import Optional, Sequence, Iterator, cast
import math
import cmath
import bisect
from itertools import accumulate
import xml.etree.ElementTree as ET

from .. import util
from .. import geometry
from ..geometry import PointType, BezierType, BezierCubicType, BezierQuadType, distance
from ..canvas import Canvas, Borders, ViewBox
from ..attributes import Animatable
from ..element import Element
from ..style import MarkerTypes
from ..diagrams import Graph
from .line import Line, Segment


class Bezier(Element):
    ''' Quadratic or Cubic Bezier Curve

        Args:
            p1, p2, p3, p4: Control points for curve. p4 Optional.
    '''
    _step_color = True

    def __init__(self, p1: PointType, p2: PointType, p3: PointType, p4: Optional[PointType] = None):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        if p4:
            self.p4 = p4
        else:
            self.p4 = (math.nan, math.nan)
        self.startmark: Optional[MarkerTypes] = None
        self.endmark: Optional[MarkerTypes] = None
        self.midmark: Optional[MarkerTypes] = None
        self.svg.startmark = Animatable()
        self.svg.endmark = Animatable()
        self.svg.midmark = Animatable()

    def __getitem__(self, idx):
        return [self.p1, self.p2, self.p3][idx]

    def __len__(self):
        return 3 if not math.isfinite(self.p4[0]) else 4

    def __iter__(self) -> Iterator[PointType]:
        return iter((self.p1, self.p2, self.p3, self.p4))

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'Bezier':
        ''' Define markers to show at the start and end of the curve. Use defaults
            to show arrowheads pointing outward in the direction of the curve.
        '''
        self.startmark = start
        self.endmark = end
        return self

    def midmarker(self, midmark: MarkerTypes = '<') -> 'Bezier':
        ''' Add marker to center of curve '''
        self.midmark = midmark
        return self

    def xy(self, t: float) -> PointType:
        ''' Evaluate (x, y) value of curve at parameter t '''
        return geometry.bezier.xy(self, t)

    def tangent(self, t: float) -> Line:
        ''' Create tangent line at parameter t '''
        assert 0 <= t <= 1
        slope = geometry.bezier.tangent_slope(self, t)
        p = self.xy(t)
        return Line(p, slope)

    def normal(self, t: float) -> Line:
        ''' Create a normal line at parameter t '''
        assert 0 <= t <= 1
        slope = geometry.bezier.tangent_slope(self, t)
        p = self.xy(t)
        try:
            m = -1/slope
        except ZeroDivisionError:
            m = math.inf
        return Line(p, m)

    def secant(self, t1: float, t2: float) -> Line:
        ''' Create a secant line between parameters t1 and t2 '''
        p1 = self.xy(t1)
        p2 = self.xy(t2)
        return Line.from_points(p1, p2)

    def chord(self, t1: float, t2: float) -> Segment:
        ''' Create a Chord segment between parameters t1 and t2 '''
        p1 = self.xy(t1)
        p2 = self.xy(t2)
        return Segment(p1, p2)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()
        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(
                self.startmark,
                sty.radius,
                color,
                sty.edge_color,
                sty.edge_width,
                orient=True,
                attributes=self.svg.startmark)

        if self.endmark:
            endmark = canvas.definemarker(
                self.endmark,
                sty.radius,
                color,
                sty.edge_color,
                sty.edge_width,
                orient=True,
                attributes=self.svg.endmark)

        p4 = self.p4 if len(self) == 4 else None
        canvas.bezier(self.p1, self.p2, self.p3, p4,
                      stroke=sty.stroke,
                      color=color,
                      width=sty.stroke_width,
                      startmarker=startmark,
                      endmarker=endmark,
                      dataview=databox,
                      zorder=self._zorder,
                      attributes=self.svg)

        if self.midmark:
            midmark = canvas.definemarker(
                self.midmark,
                sty.radius,
                color,
                sty.edge_color,
                sty.edge_width,
                orient=True,
                attributes=self.svg.midmark)

            midx, midy = self.xy(0.5)
            slope = geometry.bezier.tangent_slope(self, 0.5)
            dx = midx/1E3
            midx1 = midx + dx
            midy1 = midy + dx*slope
            canvas.path([midx, midx1], [midy, midy1],
                        color='none',
                        startmarker=midmark,
                        dataview=databox,
                        zorder=self._zorder,
                        attributes=self.svg.midmark)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        graph = Graph()
        graph.add(self)
        return graph.svgxml(border=border)


class Curve(Bezier):
    ''' Symmetric curve connecting the two points with deflection k
        as fraction of distance between endpoints
    '''
    def __init__(self, p1: PointType, p2: PointType, k: float = .15):
        thetanorm = math.atan2((p2[1] - p1[1]), (p2[0] - p1[0])) + math.pi/2
        mid = (p1[0] + p2[0])/2, (p1[1] + p2[1]) / 2
        length = geometry.distance(p1, p2) * k
        pc = (mid[0] + length * math.cos(thetanorm),
              mid[1] + length * math.sin(thetanorm))
        super().__init__(p1, pc, p2)


class CurveThreePoint(Bezier):
    ''' Bezier Curve passing through three points and parameter t '''
    def __init__(self, start: PointType, end: PointType, mid: PointType,
                 t: float = 0.5):
        p2x = mid[0] / (2*t*(1-t)) - start[0] * t / (2*(1-t)) - end[0] * (1-t)/(2*t)
        p2y = mid[1] / (2*t*(1-t)) - start[1] * t / (2*(1-t)) - end[1] * (1-t)/(2*t)
        super().__init__(start, (p2x, p2y), end)


class BezierSpline(Element):
    ''' A curve made of connected Cubic Bezier curves

        Note the endpoint of curve N is shared with the
        start point of curve N+1. i.e. to define a 2-curve
        spline, 7 points are needed.
    '''
    _step_color = True

    def __init__(self, *points: PointType):
        super().__init__()
        self.points = points

    def xy(self, t: float) -> PointType:
        ''' Evaluate (x, y) on curve at parameter t, where
            t goes from 0 to 1 along the entire spline
        '''
        if t == 1:
            return self.points[-1]
        if t == 0:
            return self.points[0]

        curves: list[BezierType] = [cast(BezierType, self.points[i:i+4])
                                    for i in range(0, len(self.points)-1, 3)]
        n = len(curves)
        curve_num = int(t * n)
        curve_t = t*n - curve_num
        return geometry.bezier.cubic_xy(cast(BezierCubicType, curves[curve_num]), curve_t)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()

        canvas.bezier_spline(
            self.points,
            stroke=sty.stroke,
            color=color,
            width=sty.stroke_width,
            dataview=databox,
            zorder=self._zorder,
            attributes=self.svg)

    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        graph = Graph()
        graph.add(self)
        return graph.svgxml(border=border)


def hobby_curve(points: Sequence[PointType], omega: float = 0.5) -> list[PointType]:
    ''' Calculate cubic Bezier control points using Hobby's algorithm '''
    # Translated from Jake Low's Javascript algorithm:
    # https://www.jakelow.com/blog/hobby-curves
    n = len(points) - 1

    p = [complex(*p) for p in points]
    chords = [p[i]-p[i-1] for i in range(1, len(p))]
    d = [abs(c) for c in chords]

    def angle_between(w: complex, v: complex):
        ''' Calcluate angle between w and v '''
        return math.atan2(w.imag * v.real - w.real*v.imag, v.real*w.real + v.imag*w.imag)

    gamma = [0] + [angle_between(chords[i], chords[i-1]) for i in range(1, len(chords))] + [0]

    A = [0.] * (n+1)
    B = [0.] * (n+1)
    C = [0.] * (n+1)
    D = [0.] * (n+1)
    B[0] = 2 + omega
    C[0] = 2 * omega + 1
    D[0] = -C[0] * gamma[1]

    for i in range(1, n):
        A[i] = 1/d[i-1]
        B[i] = (2*d[i-1] + 2*d[i]) / (d[i-1] * d[i])
        C[i] = 1/d[i]
        D[i] = (-1 * (2 * gamma[i] * d[i] + gamma[i+1] * d[i-1])) / (d[i-1] * d[i])
    A[n] = 2*omega + 1
    B[n] = 2 + omega
    D[n] = 0

    def thomas(a, b, c, d):
        ''' Thomas algorithm for solving a system of linear equations
            in a tridiagonal matrix
        '''
        n = len(b) - 1
        Cp = [0] * (n+1)
        Dp = [0] * (n+1)
        Cp[0] = c[0] / b[0]
        Dp[0] = d[0] / b[0]
        for i in range(1, n+1):
            denom = b[i] - Cp[i-1] * a[i]
            Cp[i] = C[i] / denom
            Dp[i] = (d[i] - Dp[i-1] * a[i]) / denom
        x = [0] * (n+1)
        x[n] = Dp[n]
        for i in range(n-1, -1, -1):
            x[i] = Dp[i] - Cp[i] * x[i+1]
        return x

    alpha = thomas(A, B, C, D)
    beta = [-gamma[i] - alpha[i] for i in range(1, n+1)]
    beta[n-1] = -alpha[n]
    alpha = alpha[:-1]

    c0 = [0+0j] * n
    c1 = [0+0j] * n

    def rho(alpha, beta):
        ''' Velociy function '''
        c = 2/3
        return 2 / (1 + c * math.cos(beta) + (1-c) * math.cos(alpha))

    def rotate(v: complex, theta: float):
        ''' Rotate a complex number by theta '''
        v = v * cmath.exp(1j*theta)
        return v / abs(v)

    for i in range(n):
        a = rho(alpha[i], beta[i]) * d[i] / 3
        b = rho(beta[i], alpha[i]) * d[i] / 3
        c0[i] = p[i] + rotate(chords[i], alpha[i]) * a
        c1[i] = p[i+1] - rotate(chords[i], -beta[i]) * b

    ctrlpoints: list[PointType] = []
    for i in range(n):
        ctrlpoints.extend(
            (points[i],
            (c0[i].real, c0[i].imag),
            (c1[i].real, c1[i].imag)))
    ctrlpoints.append(points[-1])
    return ctrlpoints


class BezierHobby(BezierSpline):
    def __init__(self, *points: PointType, omega: float = 0.5):
        self.onpoints = points  # Points ON the curve
        self.omega = omega
        ctrlpoints = hobby_curve(points, omega)
        super().__init__(*ctrlpoints)


def spline_equal_spaced_t(
        spline: BezierSpline,
        nsegments: int = 2,
        n: int = 100) -> list[float]:
    ''' Find equally spaced t values along a BezierSpline

        Args:
            spline: The curve to split
            nsegments: Number of segments to split curve into
            n: Number of points used to approximate curve
    '''
    curves: list[BezierType] = [cast(BezierCubicType, spline.points[i:i+4])
                                for i in range(0, len(spline.points)-1, 3)]
    t = util.linspace(0, 1, n)
    dists = []
    for curve in curves:
        xy = [geometry.bezier.cubic_xy(cast(BezierCubicType, curve), tt) for tt in t]
        dists.extend([distance(xy[i], xy[i+1]) for i in range(n-1)])
    length = sum(dists)
    delta = length / nsegments
    seg_points = [delta*i for i in range(nsegments+1)]
    cumsum = list(accumulate(dists))
    t_points = [bisect.bisect_left(cumsum, seg_points[i]) for i in range(1, nsegments)]
    fullt = util.linspace(0, 1, n*len(curves))
    return [0.] + [fullt[tp] for tp in t_points] + [1.]


def spline_equal_spaced_points(
        spline: BezierSpline,
        nsegments: int = 2,
        n: int = 100) -> list[PointType]:
    ''' Find (x, y) points spaced equally along the spline.

        Args:
            spline: The curve to split
            nsegments: Number of segments to split curve into
            n: Number of points used to approximate curve
    '''
    t = spline_equal_spaced_t(spline, nsegments, n)
    return [spline.xy(tt) for tt in t]
