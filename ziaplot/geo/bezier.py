''' Bezier Curves '''
from __future__ import annotations
from typing import Optional, Sequence
import math
import cmath
import bisect
from itertools import accumulate
from xml.etree import ElementTree as ET

from .. import util
from ..canvas import Canvas, Borders, ViewBox
from ..element import Element
from ..style import MarkerTypes, PointType
from ..diagrams import Graph


class BezierQuad(Element):
    ''' Quadratic Bezier Curve

        Args:
            p1, p2, p3: Control points for curve
    '''
    _step_color = True

    def __init__(self, p1: PointType, p2: PointType, p3: PointType):
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4: Optional[PointType] = None
        self.startmark: Optional[MarkerTypes] = None
        self.endmark: Optional[MarkerTypes] = None
        self.midmark: Optional[MarkerTypes] = None

    def endmarkers(self, start: MarkerTypes = '<', end: MarkerTypes = '>') -> 'BezierQuad':
        ''' Define markers to show at the start and end of the curve. Use defaults
            to show arrowheads pointing outward in the direction of the curve.
        '''
        self.startmark = start
        self.endmark = end
        return self

    def midmarker(self, midmark: MarkerTypes = '<') -> 'BezierQuad':
        ''' Add marker to center of curve '''
        self.midmark = midmark
        return self

    def xy(self, t: float) -> PointType:
        ''' Evaluate (x, y) value of curve at parameter t '''
        x = self.p2[0] + (1-t)**2 * (self.p1[0] - self.p2[0]) + t**2 * (self.p3[0] - self.p2[0])
        y = self.p2[1] + (1-t)**2 * (self.p1[1] - self.p2[1]) + t**2 * (self.p3[1] - self.p2[1])
        return x, y

    def _tangent_slope(self, t: float) -> float:
        ''' Get slope of tangent at parameter t '''
        bprime_x = 2*(1-t) * (self.p2[0] - self.p1[0]) + 2*t*(self.p3[0] - self.p2[0])
        bprime_y = 2*(1-t) * (self.p2[1] - self.p1[1]) + 2*t*(self.p3[1] - self.p2[1])
        return bprime_y / bprime_x

    def _tangent_theta(self, t: float) -> float:
        ''' Get angle of tangent at parameter t '''
        bprime_x = 2*(1-t) * (self.p2[0] - self.p1[0]) + 2*t*(self.p3[0] - self.p2[0])
        bprime_y = 2*(1-t) * (self.p2[1] - self.p1[1]) + 2*t*(self.p3[1] - self.p2[1])
        return math.atan2(bprime_y, bprime_x)

    def length(self, n: int = 50) -> float:
        ''' Approximate length of the curve

            Args:
                n: the number of points in t used to
                    linearly approximate the curve
        '''
        return bezier_length(self, n)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()
        startmark = None
        endmark = None
        if self.startmark:
            startmark = canvas.definemarker(self.startmark,
                                            sty.radius,
                                            color,
                                            sty.edge_color,
                                            sty.edge_width,
                                            orient=True)
        if self.endmark:
            endmark = canvas.definemarker(self.endmark,
                                          sty.radius,
                                          color,
                                          sty.edge_color,
                                          sty.edge_width,
                                          orient=True)

        canvas.bezier(self.p1, self.p2, self.p3, self.p4,
                      stroke=sty.stroke,
                      color=color,
                      width=sty.stroke_width,
                      startmarker=startmark,
                      endmarker=endmark,
                      dataview=databox,
                      zorder=self._zorder)

        if self.midmark:
            midmark = canvas.definemarker(self.midmark,
                                          sty.radius,
                                          color,
                                          sty.edge_color,
                                          sty.edge_width,
                                          orient=True)
            midx, midy = self.xy(0.5)
            slope = self._tangent_slope(0.5)
            dx = midx/1E3
            midx1 = midx + dx
            midy1 = midy + dx*slope
            canvas.path([midx, midx1], [midy, midy1],
                        color='none',
                        startmarker=midmark,
                        dataview=databox,
                        zorder=self._zorder)


    def svgxml(self, border: bool = False) -> ET.Element:
        ''' Generate XML for standalone SVG '''
        graph = Graph()
        graph.add(self)
        return graph.svgxml(border=border)


class BezierCubic(BezierQuad):
    ''' Cubic Bezier Curve

        Args:
            p1, p2, p3, p4: Control points for curve
    '''
    def __init__(self, p1: PointType, p2: PointType,
                 p3: PointType, p4: PointType):
        super().__init__(p1, p2, p3)
        self.p4 = p4

    def xy(self, t: float) -> PointType:
        ''' Evaluate (x, y) on curve at parameter t '''
        assert self.p4 is not None
        return cubic_xy(t, self.p1, self.p2, self.p3, self.p4)

    def _tangent_slope(self, t: float) -> float:
        ''' Get slope of tangent at parameter t '''
        assert self.p4 is not None
        bprime_x = 3*(1-t)**2 * (self.p2[0]-self.p1[0]) + 6*(1-t)*t*(self.p3[0]-self.p2[0]) + 3*t**2*(self.p4[0]-self.p3[0])
        bprime_y = 3*(1-t)**2 * (self.p2[1]-self.p1[1]) + 6*(1-t)*t*(self.p3[1]-self.p2[1]) + 3*t**2*(self.p4[1]-self.p3[1])
        return bprime_y / bprime_x

    def _tangent_theta(self, t: float) -> float:
        assert self.p4 is not None
        bprime_x = 3*(1-t)**2 * (self.p2[0]-self.p1[0]) + 6*(1-t)*t*(self.p3[0]-self.p2[0]) + 3*t**2*(self.p4[0]-self.p3[0])
        bprime_y = 3*(1-t)**2 * (self.p2[1]-self.p1[1]) + 6*(1-t)*t*(self.p3[1]-self.p2[1]) + 3*t**2*(self.p4[1]-self.p3[1])
        return math.atan2(bprime_y, bprime_x)


class Curve(BezierQuad):
    ''' Symmetric curve connecting the two points with deflection k
        as fraction of distance between endpoints
    '''
    def __init__(self, p1: PointType, p2: PointType, k: float = .15):
        thetanorm = math.atan2((p2[1] - p1[1]), (p2[0] - p1[0])) + math.pi/2
        mid = (p1[0] + p2[0])/2, (p1[1] + p2[1]) / 2
        length = util.distance(p1, p2) * k
        pc = (mid[0] + length * math.cos(thetanorm),
              mid[1] + length * math.sin(thetanorm))
        super().__init__(p1, pc, p2)        


class CurveThreePoint(BezierQuad):
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

        curves = [self.points[i:i+4] for i in range(0, len(self.points)-1, 3)]
        n = len(curves)
        curve_num = int(t * n)
        curve_t = t*n - curve_num
        return cubic_xy(curve_t, *curves[curve_num])

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
                      zorder=self._zorder)

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
        for i in range(1,n+1):
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
            (c1[i].real, c1[i].imag),
            ))
    ctrlpoints.append(points[-1])
    return ctrlpoints


class BezierHobby(BezierSpline):
    def __init__(self, *points: PointType, omega: float = 0.5):
        self.onpoints = points  # Points ON the curve
        self.omega = omega
        ctrlpoints = hobby_curve(points, omega)
        super().__init__(*ctrlpoints)



def cubic_xy(t: float, *p: PointType) -> PointType:
    ''' Calculate (x, y) point at parameter t on a cubic bezier with
        control points p
    '''
    p1, p2, p3, p4 = p
    x = (p1[0]*(1-t)**3 + p2[0]*3*t*(1-t)**2 + p3[0]*3*(1-t)*t**2 + p4[0]*t**3)
    y = (p1[1]*(1-t)**3 + p2[1]*3*t*(1-t)**2 + p3[1]*3*(1-t)*t**2 + p4[1]*t**3)
    return (x, y)


def bezier_length(bezier: BezierQuad | BezierCubic, n: int = 50) -> float:
    ''' Compute approximate length of Bezier curve

        Args:
            n: Number of points used to approximate curve
    '''
    t = util.linspace(0, 1, num=50)
    xy = [bezier.xy(tt) for tt in t]
    dists = [util.distance(xy[i], xy[i+1]) for i in range(n-1)]
    return sum(dists)


def bezier_equal_spaced_t(
        bezier: BezierQuad | BezierCubic,
        nsegments: int = 2,
        n: int = 100) -> list[float]:
    ''' Find t values that approximately split the curve into
        equal-length segments.

        Args:
            bezier: The curve to split
            nsegments: Number of segments to split curve into
            n: Number of points used to approximate curve
    '''
    t = util.linspace(0, 1, num=n)
    xy = [bezier.xy(tt) for tt in t]
    dists = [util.distance(xy[i], xy[i+1]) for i in range(n-1)]
    length = sum(dists)
    delta = length / nsegments
    seg_points = [delta*i for i in range(nsegments+1)]
    cumsum = list(accumulate(dists))
    t_points = [bisect.bisect_left(cumsum, seg_points[i]) for i in range(1, nsegments)]
    return [t[0]] + [t[tp] for tp in t_points] + [t[n-1]]


def bezier_equal_spaced_points(
        bezier: BezierQuad | BezierCubic,
        nsegments: int = 2,
        n: int = 100) -> list[PointType]:
    ''' Find (x, y) points spaced equally along a Bezier curve

        Args:
            bezier: The curve to split
            nsegments: Number of segments to split curve into
            n: Number of points used to approximate curve
    '''
    t = bezier_equal_spaced_t(bezier, nsegments, n)
    return [bezier.xy(tt) for tt in t]


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
    curves = [spline.points[i:i+4] for i in range(0, len(spline.points)-1, 3)]
    t = util.linspace(0, 1, n)
    length = 0
    dists = []
    for curve in curves:
        xy = [cubic_xy(tt, *curve) for tt in t]
        dists.extend([util.distance(xy[i], xy[i+1]) for i in range(n-1)])
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
