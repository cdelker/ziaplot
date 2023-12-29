''' SVG-drawing functions '''

from __future__ import annotations
from typing import Sequence, Literal, Optional
import math
from collections import namedtuple
import xml.etree.ElementTree as ET

from . import text
from .config import config
from .styletypes import MarkerTypes, DashTypes


ViewBox = namedtuple('ViewBox', ['x', 'y', 'w', 'h'])
DataRange = namedtuple('DataRange', ['xmin', 'xmax', 'ymin', 'ymax'])
Halign = Literal['left', 'center', 'right']
Valign = Literal['top', 'center', 'baseline', 'base', 'bottom']


def fmt(f: float) -> str:
    ''' String format, stripping trailing zeros '''
    p = f'.{config.precision}f'
    s = format(float(f), p)
    return s.rstrip('0').rstrip('.')  # Strip trailing zeros


def getdash(dash: DashTypes = ':', linewidth: float = 2) -> str:
    ''' Convert dash style into a stroke-dasharray tag for SVG path '''
    if dash in [':', 'dotted']:
        dash = f'{linewidth} {linewidth}'
    elif dash in ['--', 'dashed']:
        dash = f'{linewidth*3} {linewidth*4}'
    elif dash in ['-.', '.-', 'dashdot']:
        dash = f'{linewidth*3} {linewidth} {linewidth/2} {linewidth}'
    return dash


class Transform:
    ''' Transformation from source to destination viewbox

        Args:
            src: Source view
            dest: Destination view
    '''
    def __init__(self, src: ViewBox, dest: ViewBox):
        self.src = src
        self.dest = dest
        self.xscale = self.dest.w / self.src.w
        self.yscale = self.dest.h / self.src.h
        self.xshift = self.dest.x - self.src.x*self.xscale
        self.yshift = self.dest.y - self.src.y*self.yscale

    def __repr__(self):
        return (f'Transform(scale=({fmt(self.xscale)},{fmt(self.yscale)}); '
                f'shift=({fmt(self.xshift)},{fmt(self.yshift)}))')

    def apply(self, x: float, y: float) -> tuple[float, float]:
        ''' Apply the transformation to the x, y point '''
        return (x*self.xscale + self.xshift,
                y*self.yscale + self.yshift)

    def apply_list(self, x: Sequence[float], y: Sequence[float]) -> tuple[list[float], list[float]]:
        ''' Apply the transofrmation to a list of x, y points '''
        xy = [self.apply(xx, yy) for xx, yy in zip(x, y)]
        x = [z[0] for z in xy]
        y = [z[1] for z in xy]
        return x, y


class Canvas:
    ''' SVG Drawing canvas

        Args:
            width: Pixel width of the canvas
            height: Pixel height of the canvas
            fill: Fill color for canvas background
    '''
    def __init__(self, width: float, height: float, fill: Optional[str] = None):
        self.canvaswidth = width
        self.canvasheight = height
        self.viewbox = ViewBox(0, 0, width, height)
        attrib = {'xmlns': 'http://www.w3.org/2000/svg',
                  'height': str(height),
                  'width': str(width),
                  'viewBox': f'0 0 {fmt(width)} {fmt(height)}'}
        self.root = ET.Element('svg', attrib=attrib)
        if fill:
            attrib = {'width': '100%', 'height': '100%', 'fill': fill}
            ET.SubElement(self.root, 'rect', attrib=attrib)
        self.defs: Optional[ET.Element] = None
        self.clip: Optional[str] = None
        self._clipnames: list[str] = []
        self._marknames: list[str] = []
        self.newgroup()

    def xml(self) -> ET.Element:
        ''' Get XML Element for SVG '''
        return self.root

    def svg(self) -> str:
        ''' Get SVG text '''
        return ET.tostring(self.root, encoding='unicode')

    def resetviewbox(self) -> None:
        ''' Reset the current canvas viewbox to the full canvas '''
        self.viewbox = ViewBox(0, 0, self.canvaswidth, self.canvasheight)
        self.clip = None

    def setviewbox(self, viewbox: ViewBox, clippad: float = 0) -> None:
        ''' Set the viewbox for canvas drawing. '''
        self.viewbox = viewbox
        if self.defs is None:
            self.defs = ET.Element('defs')
            self.root.insert(0, self.defs)

        name = 'axesclip{}'.format(len(self._clipnames)+1)
        self._clipnames.append(name)
        clip = ET.SubElement(self.defs, 'clipPath', attrib={'id': name})
        y = self.flipy(self.viewbox.y) - self.viewbox.h

        attrib = {'x': fmt(self.viewbox.x-clippad), 'y': str(y-clippad),
                  'width': fmt(self.viewbox.w+2*clippad),
                  'height': fmt(self.viewbox.h+2*clippad)}
        ET.SubElement(clip, 'rect', attrib=attrib)
        self.clip = name

    def newgroup(self) -> ET.Element:
        ''' Start a new SVG group <g> tag. '''
        self.group = ET.SubElement(self.root, 'g')
        return self.group

    def definemarker(self, shape: MarkerTypes = 'round', radius: float = 4, color: str = 'red',
                     strokecolor: str = 'black', strokewidth: float = 1,
                     orient: bool = False) -> str:
        ''' Define a new marker in SVG <defs>.

            Args:
                shape: Marker shape
                radius: Marker radius (or half-width)
                color: Marker color
                strokecolor: Marker border color
                strokewidth: Marker border width
                orient: Rotate the marker to the same angle as its line
        '''
        name = f'dot{len(self._marknames)+1}'
        self._marknames.append(name)

        if self.defs is None:
            self.defs = ET.Element('defs')
            self.root.insert(0, self.defs)
        mark = ET.SubElement(self.defs, 'marker')
        diam = radius*2
        rstroke = radius + strokewidth
        mark.attrib['id'] = name
        mark.attrib['viewBox'] = f'{-strokewidth} {-strokewidth} {rstroke*2} {rstroke*2}'
        mark.attrib['refX'] = f'{radius}'
        mark.attrib['refY'] = f'{radius}'
        mark.attrib['markerWidth'] = f'{diam}'
        mark.attrib['markerHeight'] = f'{diam}'
        mark.attrib['markerUnits'] = 'userSpaceOnUse'

        if shape in ['round', 'o']:
            sh = ET.SubElement(mark, 'circle')
            sh.attrib['cx'] = f'{radius}'
            sh.attrib['cy'] = f'{radius}'
            sh.attrib['r'] = f'{radius}'
        elif shape in ['square', 's']:
            sh = ET.SubElement(mark, 'polygon')
            sh.attrib['points'] = f'0,0 0,{diam}, {diam},{diam}, {diam},0'
        elif shape in ['triangle', '^']:
            sh = ET.SubElement(mark, 'polygon')
            sh.attrib['points'] = f'0,{diam} {diam},{diam} {radius},0'
        elif shape in ['triangled', 'v']:
            sh = ET.SubElement(mark, 'polygon')
            sh.attrib['points'] = f'{diam},0 0,0 {radius},{diam}'
        elif shape in ['larrow', '<']:
            sh = ET.SubElement(mark, 'polygon')
            sh.attrib['points'] = f'0,{radius} {diam},0 {diam},{diam}'
        elif shape in ['arrow', '>']:
            sh = ET.SubElement(mark, 'polygon')
            sh.attrib['points'] = f'0,0 0,{diam} {diam},{radius}'
        elif shape == '-':
            sh = ET.SubElement(mark, 'path')
            sh.attrib['d'] = f'M 0,{radius} L {diam},{radius}'
            sh.attrib['stroke'] = color
        elif shape == '|':
            sh = ET.SubElement(mark, 'path')
            sh.attrib['d'] = f'M {radius},{diam} L {radius},0'
            sh.attrib['stroke'] = color
        elif shape in ['+', 'x']:
            sh = ET.SubElement(mark, 'polygon')
            k = diam/3
            ks = fmt(k)
            ks2 = fmt(k*2)
            sh.attrib['points'] = (f'{ks},0 {ks2},0 {ks2},{ks}, {diam},{ks} '
                                   f'{diam},{ks2} {ks2},{ks2} {ks2},{diam} {ks},{diam} '
                                   f'{ks},{ks2} 0,{ks2} 0,{ks} {ks},{ks}')
            if shape == 'x':
                sh.attrib['transform'] = f'rotate(45 {radius} {radius})'
        else:
            raise ValueError(f'Unknown marker type {shape}')

        if orient:
            mark.attrib['orient'] = 'auto'

        if shape not in ['-', '|']:
            sh.attrib['fill'] = color
            sh.attrib['stroke'] = strokecolor
        sh.attrib['stroke-width'] = str(strokewidth)

        return name

    def flipy(self, y: float) -> float:
        ''' Flip the y coordinate because SVG defines y=0 at the top '''
        return self.canvasheight - y

    def path(self, x: Sequence[float], y: Sequence[float], stroke: DashTypes = '-',
             color: str = 'black', width: float = 2, markerid: Optional[str] = None,
             startmarker: Optional[str] = None, endmarker: Optional[str] = None,
             dataview: Optional[ViewBox] = None):
        ''' Add a path to the SVG

            Args:
                x: X-values of the path
                y: Y-values of the path
                stroke: Stroke/linestyle of hte path
                color: Path color
                width: Width of path line
                markerid: ID name of marker (defined using `definemarker`)
                    for midpoints of path
                startmarker: ID name of marker for start point of path
                endmarker: ID name of marker for end point of path
                dataview: Viewbox for transforming x, y data into SVG coordinates
        '''
        if dataview:  # apply transform from dataview -> self.viewbox
            xform = Transform(dataview, self.viewbox)
            x, y = xform.apply_list(x, y)

        y = [self.flipy(yy) for yy in y]

        path = ET.SubElement(self.group, 'path')
        pointstr = f'M {fmt(x[0])},{fmt(y[0])} '
        pointstr += 'L '
        pointstr += ' '.join(f'{fmt(xx)},{fmt(yy)}' for xx, yy in zip(x[1:], y[1:]))
        path.attrib['d'] = pointstr
        path.attrib['stroke'] = color
        path.attrib['stroke-width'] = str(width)
        path.attrib['fill'] = 'none'
        if markerid is not None:
            path.attrib['marker-start'] = f'url(#{markerid})'
            path.attrib['marker-mid'] = f'url(#{markerid})'
            path.attrib['marker-end'] = f'url(#{markerid})'
        if startmarker is not None:
            path.attrib['marker-start'] = f'url(#{startmarker})'
        if endmarker is not None:
            path.attrib['marker-end'] = f'url(#{endmarker})'
        if stroke != '-' and stroke not in [None, 'none', '']:
            path.attrib['stroke-dasharray'] = getdash(stroke, width)
        if stroke in [None, 'none', '']:
            path.attrib['stroke'] = 'none'
        if self.clip:
            path.attrib['clip-path'] = f'url(#{self.clip})'

    def rect(self, x: float, y: float, w: float, h: float, fill: Optional[str] = None,
             strokecolor: str = 'black', strokewidth: float = 2,
             rcorner: float = 0, dataview: Optional[ViewBox] = None) -> ET.Element:
        ''' Add a rectangle to the canvas

            Args:
                x: Left side of rectangle
                y: Bottom side of rectangle
                w: Width of rectangle
                h: Height of rectangle
                fill: Fill color of rectangle
                strokecolor: Border color of rectangle
                strokewidth: Line width of rectangle border
                rcorner: Radius of rectangle corners
                dataview: ViewBox for transforming x, y data into SVG coordinates
        '''
        if dataview:
            # apply transform from dataview -> self.viewbox
            xform = Transform(dataview, self.viewbox)
            x2, y2 = xform.apply(x+w, y+h)
            x, y = xform.apply(x, y)
            w, h = x2-x, y2-y

        y = self.flipy(y) - h  # xy is top-left corner
        fill = 'none' if fill is None else fill
        attrib = {'x': fmt(x), 'y': fmt(y),
                  'width': fmt(w), 'height': fmt(h),
                  'fill': fill, 'stroke': strokecolor,
                  'stroke-width': str(strokewidth)}
        if rcorner:
            attrib['rx'] = str(rcorner)
        if self.clip:
            attrib['clip-path'] = f'url(#{self.clip})'

        rect = ET.SubElement(self.group, 'rect', attrib=attrib)
        return rect

    def circle(self, x: float, y: float, radius: float, color: str = 'black',
               strokecolor: str = 'red', strokewidth: float = 1,
               stroke: DashTypes = '-', dataview: Optional[ViewBox] = None):
        ''' Add a circle to the canvas

            Args:
                x: Center of circle
                y: Center of circle
                radius: Radius of circle
                color: Fill color of circle
                strokecolor: Color of circle border
                strokewidth: Line width of circle border
                stroke: Stroke/linestyle of circle border
        '''
        if dataview:
            xform = Transform(dataview, self.viewbox)
            x, y = xform.apply(x, y)
            radius = radius * self.viewbox.w/dataview.w

        y = self.flipy(y)
        attrib = {'cx': fmt(x), 'cy': fmt(y), 'r': fmt(radius),
                  'stroke': strokecolor, 'fill': color,
                  'stroke-width': str(strokewidth)}
        if stroke != '-' and stroke not in [None, 'none', '']:
            attrib['stroke-dasharray'] = getdash(stroke, strokewidth)
        if self.clip:
            attrib['clip-path'] = f'url(#{self.clip})'
        circ = ET.SubElement(self.group, 'circle', attrib=attrib)
        return circ

    def text(self, x: float, y: float, s: str,
             color: str = 'black',
             font: str = 'sans-serif',
             size: float = 12,
             halign: Halign = 'left',
             valign: Valign = 'bottom',
             rotate: Optional[float] = None,
             dataview: Optional[ViewBox] = None) -> None:
        ''' Add text to the canvas

            Args:
                x: X-position of text
                y: Y-position of text
                s: Text string
                color: Font color
                font: Font name
                size: Font size
                halign: Horizontal Alignment
                valign: Vertical Alignment
                rotate: Rotation angle in degrees
                dataview: ViewBox for transforming x, y into SVG coordinates
        '''
        if s == '':
            return

        if dataview:
            xform = Transform(dataview, self.viewbox)
            x, y = xform.apply(x, y)

        y = self.flipy(y)
        text.draw_text(x, y, s, self.group,
                       color=color,
                       font=font,
                       size=size,
                       halign=halign,
                       valign=valign,
                       rotate=rotate)

    def poly(self, points: Sequence[tuple[float, float]], color: str = 'black',
             strokecolor: str = 'red', strokewidth: float = 1, alpha: float = 1.0,
             dataview: Optional[ViewBox] = None):
        ''' Add a polygon to the canvas

            Args:
                points: List of (x,y) values for each vertex
                color: Fill color
                strokecolor: Border color
                strokewidth: Width of border
                alpha: Opacity (0-1) of fill color
        '''
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        if dataview:
            xform = Transform(dataview, self.viewbox)
            x, y = xform.apply_list(x, y)

        y = [self.flipy(yy) for yy in y]
        pointstr = ''
        for px, py in zip(x, y):
            pointstr += f'{fmt(px)},{fmt(py)} '
        attrib = {'points': pointstr,
                  'stroke': strokecolor,
                  'fill': color,
                  'stroke-width': str(strokewidth)}
        if alpha != 1:
            attrib['fill-opacity'] = str(alpha)
        if self.clip:
            attrib['clip-path'] = f'url(#{self.clip})'
        poly = ET.SubElement(self.group, 'polygon', attrib=attrib)
        return poly

    def wedge(self, cx: float, cy: float, radius: float, theta: float,
              starttheta: float = 0, color: str = 'red',
              strokecolor: str = 'black', strokewidth: float = 1) -> ET.Element:
        ''' Add a wedge/filled arc (ie pie chart slice)

            Args:
                cx: X-center of arc
                cy: Y-center of arc
                radius: Radius of arc
                theta: Arc length in radians
                starttheta: Starting angle of arc (going counter clockwise)
                color: Fill color of arc/wedge
                strokecolor: Border color
                strokewidth: Border width
        '''
        cy = self.flipy(cy)
        x1 = cx + radius * math.cos(starttheta)
        y1 = cy + radius * math.sin(starttheta)
        x2 = cx + radius * math.cos(starttheta + theta)
        y2 = cy + radius * math.sin(starttheta + theta)

        flag = 1 if theta > math.pi else 0
        path = ET.SubElement(self.group, 'path')
        pointstr = f'M {fmt(cx)},{fmt(cy)} L {fmt(x1)},{fmt(y1)} '
        pointstr += f'A {fmt(radius)} {fmt(radius)} 0 {flag} 1 {fmt(x2)} {fmt(y2)} Z'
        path.attrib['d'] = pointstr
        path.attrib['stroke'] = strokecolor
        path.attrib['stroke-width'] = str(strokewidth)
        path.attrib['fill'] = color
        if self.clip:
            path.attrib['clip-path'] = f'url(#{self.clip})'
        return path

    def arc(self, cx: float, cy: float, radius: float, theta1: float = 0,
            theta2: float = 3.14, strokecolor: str = 'black',
            strokewidth: float = 1, dataview: Optional[ViewBox] = None) -> ET.Element:
        ''' Add an open arc

            Args:
                cx: X-center of arc
                cy: Y-center of arc
                radius: Radius of arc
                starttheta: Starting angle of arc (degrees)
                stoptheta: End angle of arc (degrees)
                strokecolor: Border color
                strokewidth: Border width
        '''
        if dataview:
            xform = Transform(dataview, self.viewbox)
            cx, cy = xform.apply(cx, cy)
            radius = radius * self.viewbox.w / dataview.w
        cy = self.flipy(cy)

        theta1 = math.radians((theta1 + 360) % 360)
        theta2 = math.radians((theta2 + 360) % 360)

        x1 = cx + radius * math.cos(-theta1)
        y1 = cy + radius * math.sin(-theta1)
        x2 = cx + radius * math.cos(-theta2)
        y2 = cy + radius * math.sin(-theta2)

        flag = 1 if theta2-theta1 > math.pi else 0
        path = ET.SubElement(self.group, 'path')
        pointstr = f'M {fmt(x1)},{fmt(y1)} '
        pointstr += f'A {fmt(radius)} {fmt(radius)} 0 {flag} 0 {fmt(x2)} {fmt(y2)}'
        path.attrib['d'] = pointstr
        path.attrib['stroke'] = strokecolor
        path.attrib['stroke-width'] = str(strokewidth)
        path.attrib['fill'] = 'none'
        if self.clip:
            path.attrib['clip-path'] = f'url(#{self.clip})'
        return path
