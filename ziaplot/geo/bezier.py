''' Bezier Curves '''
from __future__ import annotations
from typing import Optional
from xml.etree import ElementTree as ET
import math

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
        self.n = 200
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
                      dataview=databox)

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
                        dataview=databox)


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
        x = (self.p1[0]*(1-t)**3 + self.p2[0]*3*t*(1-t)**2 + self.p3[0]*3*(1-t)*t**2 + self.p4[0]*t**3)
        y = (self.p1[1]*(1-t)**3 + self.p2[1]*3*t*(1-t)**2 + self.p3[1]*3*(1-t)*t**2 + self.p4[1]*t**3)
        return x, y

    def _tangent_slope(self, t: float) -> float:
        ''' Get slope of tangent at parameter t '''
        assert self.p4 is not None
        bprime_x = 3*(1-t)**2 * (self.p2[0]-self.p1[0]) + 6*(1-t)*t*(self.p3[0]-self.p2[0]) + 3*t**2*(self.p4[0]-self.p3[0])
        bprime_y = 3*(1-t)**2 * (self.p2[1]-self.p1[1]) + 6*(1-t)*t*(self.p3[1]-self.p2[1]) + 3*t**2*(self.p4[1]-self.p3[1])
        return bprime_y / bprime_x


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
