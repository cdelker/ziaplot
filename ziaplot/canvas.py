''' SVG-drawing functions '''
from __future__ import annotations
from typing import Sequence, Optional, Tuple
import math
from collections import namedtuple
import xml.etree.ElementTree as ET

from . import text
from .config import config
from .style import MarkerTypes, DashTypes, PointType

ViewBox = namedtuple('ViewBox', ['x', 'y', 'w', 'h'])
Borders = namedtuple('Borders', ['left', 'right', 'top', 'bottom'])
DataRange = namedtuple('DataRange', ['xmin', 'xmax', 'ymin', 'ymax'])

def fmt(f: float) -> str:
    ''' String format, stripping trailing zeros '''
    p = f'.{config.precision}f'
    s = format(float(f), p)
    return s.rstrip('0').rstrip('.')  # Strip trailing zeros


def getdash(dash: DashTypes = ':', linewidth: float = 2) -> str:
    ''' Convert dash style into a stroke-dasharray tag for SVG path '''
    if dash in [':', 'dotted']:
        dashstyle = f'{linewidth} {linewidth}'
    elif dash in ['--', 'dashed']:
        dashstyle = f'{linewidth*3} {linewidth*4}'
    elif dash in ['-.', '.-', 'dashdot']:
        dashstyle = f'{linewidth*3} {linewidth} {linewidth/2} {linewidth}'
    else:
        dashstyle = str(dash)
    return dashstyle


def set_color(color: str, elm: ET.Element, tag: str = 'stroke') -> None:
    ''' Add a color (with possible transparency) to the element '''
    assert tag in ['stroke', 'fill']
    if color.strip().endswith('%'):
        name, alpha = color.split(maxsplit=1)
        elm.set(tag, name)
        elm.set(f'{tag}-opacity', alpha)
    elif color in [None, '', 'none']:
        elm.set(tag, 'none')
    else:
        elm.set(tag, color)


def set_clip(elm: ET.Element, clip: str|None) -> None:
    ''' Set clip-path on element if defined '''
    if clip:
        elm.set('clip-path', f'url(#{clip})')



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

    def apply(self, x: float, y: float) -> PointType:
        ''' Apply the transformation to the x, y point '''
        return (x*self.xscale + self.xshift,
                y*self.yscale + self.yshift)

    def apply_list(self, x: Sequence[float], y: Sequence[float]) -> Tuple[list[float], list[float]]:
        ''' Apply the transofrmation to a list of x, y points '''
        xy = [self.apply(xx, yy) for xx, yy in zip(x, y)]
        x = [z[0] for z in xy if math.isfinite(z[0]) and math.isfinite(z[1])]
        y = [z[1] for z in xy if math.isfinite(z[0]) and math.isfinite(z[1])]
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
        self.root = ET.Element(
            'svg',
            attrib={'xmlns': 'http://www.w3.org/2000/svg',
                   'height': str(height),
                   'width': str(width),
                   'viewBox': f'0 0 {fmt(width)} {fmt(height)}'})
        if fill:
            rect = ET.SubElement(self.root, 'rect',
                                 attrib={'width': '100%', 'height': '100%'})
            set_color(fill, rect, 'fill')
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

        name = 'diagclip{}'.format(len(self._clipnames)+1)
        self._clipnames.append(name)
        clip = ET.SubElement(self.defs, 'clipPath', attrib={'id': name})
        y = self.flipy(self.viewbox.y) - self.viewbox.h

        ET.SubElement(
            clip, 'rect',
            attrib={'x': fmt(self.viewbox.x-clippad),
                    'y': str(y-clippad),
                    'width': fmt(self.viewbox.w+2*clippad),
                    'height': fmt(self.viewbox.h+2*clippad)})
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
        mark.set('id', name)
        mark.set('viewBox', f'{-strokewidth} {-strokewidth} {rstroke*2} {rstroke*2}')
        mark.set('refX', f'{radius}')
        mark.set('refY', f'{radius}')
        mark.set('markerWidth', f'{diam}')
        mark.set('markerHeight', f'{diam}')
        mark.set('markerUnits', 'userSpaceOnUse')

        if shape in ['round', 'o']:
            sh = ET.SubElement(mark, 'circle')
            sh.set('cx', f'{radius}')
            sh.set('cy', f'{radius}')
            sh.set('r', f'{radius}')
        elif shape in ['square', 's']:
            sh = ET.SubElement(mark, 'polygon')
            sh.set('points', f'0,0 0,{diam}, {diam},{diam}, {diam},0')
        elif shape in ['triangle', '^']:
            sh = ET.SubElement(mark, 'polygon')
            sh.set('points', f'0,{diam} {diam},{diam} {radius},0')
        elif shape in ['triangled', 'v']:
            sh = ET.SubElement(mark, 'polygon')
            sh.set('points', f'{diam},0 0,0 {radius},{diam}')
        elif shape in ['larrow', '<']:
            sh = ET.SubElement(mark, 'polygon')
            sh.set('points', f'0,{radius} {diam},0 {diam},{diam}')
        elif shape in ['arrow', '>']:
            sh = ET.SubElement(mark, 'polygon')
            sh.set('points', f'0,0 0,{diam} {diam},{radius}')
        elif shape == '-':
            sh = ET.SubElement(mark, 'path')
            sh.set('d', f'M 0,{radius} L {diam},{radius}')
        elif shape == '|':
            sh = ET.SubElement(mark, 'path')
            sh.set('d', f'M {radius},{diam} L {radius},0')
            sh.set('stroke-width', str(radius/4))
        elif shape == '||':
            sh = ET.SubElement(mark, 'path')
            sh.set('d', f'M {radius/2},{diam} L {radius/2},0 M {3*radius/2},{diam} L {3*radius/2},0')
            sh.set('stroke-width', str(radius/4))
        elif shape == '|||':
            sh = ET.SubElement(mark, 'path')
            sh.set('d', f'M 0,{diam} L 0,0 M {radius},{diam} L {radius},0 M {diam},{diam} L {diam},0')
            sh.set('stroke-width', str(radius/4))
        elif shape in ['+', 'x']:
            sh = ET.SubElement(mark, 'polygon')
            k = diam/3
            ks = fmt(k)
            ks2 = fmt(k*2)
            sh.set('points', (f'{ks},0 {ks2},0 {ks2},{ks}, {diam},{ks} '
                              f'{diam},{ks2} {ks2},{ks2} {ks2},{diam} {ks},{diam} '
                              f'{ks},{ks2} 0,{ks2} 0,{ks} {ks},{ks}'))
            if shape == 'x':
                sh.set('transform', f'rotate(45 {radius} {radius})')
        else:
            raise ValueError(f'Unknown marker type {shape}')

        if orient:
            mark.set('orient', 'auto')

        if shape not in ['-', '|', '||', '|||']:
            set_color(color, sh, 'fill')
            set_color(strokecolor, sh, 'stroke')
            sh.set('stroke-width', str(strokewidth))
        else:
            set_color(color, sh, 'stroke')

        return name

    def flipy(self, y: float) -> float:
        ''' Flip the y coordinate because SVG defines y=0 at the top '''
        return self.canvasheight - y

    def path(self, x: Sequence[float], y: Sequence[float], stroke: DashTypes = '-',
             color: str = 'black', width: float = 2, markerid: Optional[str] = None,
             startmarker: Optional[str] = None, endmarker: Optional[str] = None,
             dataview: Optional[ViewBox] = None) -> None:
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
        path.set('d', pointstr)
        set_color(color, path, 'stroke')
        path.set('stroke-width', str(width))
        path.set('fill', 'none')
        if markerid is not None:
            path.set('marker-start', f'url(#{markerid})')
            path.set('marker-mid', f'url(#{markerid})')
            path.set('marker-end', f'url(#{markerid})')
        if startmarker is not None:
            path.set('marker-start', f'url(#{startmarker})')
        if endmarker is not None:
            path.set('marker-end', f'url(#{endmarker})')
        if stroke not in ['-', 'solid', None, 'none', '']:
            path.set('stroke-dasharray', getdash(stroke, width))
        set_clip(path, self.clip)

    def rect(self, x: float, y: float, w: float, h: float, fill: Optional[str] = None,
             strokecolor: str = 'black', strokewidth: float = 2,
             rcorner: float = 0, dataview: Optional[ViewBox] = None) -> None:
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
        rect = ET.SubElement(
            self.group, 'rect',
            attrib={'x': fmt(x), 'y': fmt(y),
                    'width': fmt(w), 'height': fmt(h),
                    'fill': fill,
                    'stroke-width': str(strokewidth)})
        set_color(strokecolor, rect, 'stroke')
        if rcorner:
            rect.set('rx', str(rcorner))
        set_clip(rect, self.clip)

    def circle(self, x: float, y: float, radius: float, color: str = 'black',
               strokecolor: str = 'red', strokewidth: float = 1,
               stroke: DashTypes = '-', dataview: Optional[ViewBox] = None) -> None:
        ''' Add a circle to the canvas (always a circle, the width/height
            will not be scaled to data coordinates).

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
        circ = ET.SubElement(
            self.group, 'circle',
            attrib={'cx': fmt(x), 'cy': fmt(y), 'r': fmt(radius),
                    'stroke-width': str(strokewidth)})
        set_color(strokecolor, circ, 'stroke')
        set_color(color, circ, 'fill')
        if stroke not in ['-', None, 'none', '']:
            circ.set('stroke-dasharray', getdash(stroke, strokewidth))
        set_clip(circ, self.clip)

    def text(self, x: float, y: float, s: str,
             color: str = 'black',
             font: str = 'sans-serif',
             size: float = 12,
             halign: text.Halign = 'left',
             valign: text.Valign = 'bottom',
             rotate: Optional[float] = None,
             pixelofst: Optional[PointType] = None,
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
                pixelofst: Offset to apply to shift text in SVG/pixel coordinates
                dataview: ViewBox for transforming x, y into SVG coordinates
        '''
        if s == '':
            return

        if dataview:
            xform = Transform(dataview, self.viewbox)
            x, y = xform.apply(x, y)

        if pixelofst:
            # Apply offset in pixel coordinates, without transform
            x += pixelofst[0]
            y += pixelofst[1]

        y = self.flipy(y)
        text.draw_text(x, y, s, self.group,
                       color=color,
                       font=font,
                       size=size,
                       halign=halign,
                       valign=valign,
                       rotate=rotate)

    def poly(self, points: Sequence[PointType], color: str = 'black',
             strokecolor: str = 'red', strokewidth: float = 1,
             dataview: Optional[ViewBox] = None) -> None:
        ''' Add a polygon to the canvas

            Args:
                points: List of (x,y) values for each vertex
                color: Fill color
                strokecolor: Border color
                strokewidth: Width of border
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

        poly = ET.SubElement(
            self.group, 'polygon',
            attrib={'points': pointstr,
                    'stroke-width': str(strokewidth)})
        set_color(strokecolor, poly, 'stroke')
        set_color(color, poly, 'fill')
        set_clip(poly, self.clip)

    def wedge(self, cx: float, cy: float, radius: float, theta: float,
              starttheta: float = 0, color: str = 'red',
              strokecolor: str = 'black', strokewidth: float = 1) -> None:
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
        path.set('d', pointstr)
        set_color(strokecolor, path, 'stroke')
        set_color(color, path, 'fill')
        path.set('stroke-width', str(strokewidth))
        set_clip(path, self.clip)

    def arc(self, cx: float, cy: float, radius: float, theta1: float = 0,
            theta2: float = 180, strokecolor: str = 'black',
            strokewidth: float = 1, dataview: Optional[ViewBox] = None) -> None:
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
        path.set('d', pointstr)
        path.set('stroke-width', str(strokewidth))
        path.set('fill', 'none')
        set_color(strokecolor, path, 'stroke')
        set_clip(path, self.clip)

    def ellipse(self, cx: float, cy: float, r1: float, r2: float,
                theta: float = 0, color: str = 'black',
                strokecolor: str = 'black', strokewidth: float = 1,
                dataview: Optional[ViewBox] = None) -> None:
        ''' Add an ellipse

            Args:
                cx: X-center of arc
                cy: Y-center of arc
                rx: X-Radius of arc
                ry: Y-Radius of arc
                theta: Rotation of ellipse
                strokecolor: Border color
                strokewidth: Border width
        '''
        if dataview:
            xform = Transform(dataview, self.viewbox)
            cx, cy = xform.apply(cx, cy)
            r1 = r1 * self.viewbox.w / dataview.w
            r2 = r2 * self.viewbox.h / dataview.h
        cy = self.flipy(cy)

        ellipse = ET.SubElement(self.group, 'ellipse')
        ellipse.set('cx', str(cx))
        ellipse.set('cy', str(cy))
        ellipse.set('rx', str(r1))
        ellipse.set('ry', str(r2))
        ellipse.set('stroke-width', str(strokewidth))
        set_color(strokecolor, ellipse, 'stroke')
        set_color(color, ellipse, 'fill')

        if theta:
            ellipse.set('transform', f'rotate({-theta} {cx} {cy})')
        set_clip(ellipse, self.clip)

    def bezier(self,
               p1: PointType, p2: PointType,
               p3: PointType, p4: Optional[PointType] = None,
               stroke: DashTypes = '-',
               color: str = 'black', width: float = 2, markerid: Optional[str] = None,
               startmarker: Optional[str] = None, endmarker: Optional[str] = None,
               dataview: Optional[ViewBox] = None) -> None:
        ''' Add a bezier curve to the SVG

            Args:
                p1, p2, p3: Control Points
                p4: Optional control point for Cubic curve
                stroke: Stroke/linestyle of hte path
                color: Path color
                width: Width of path line
                startmarker: ID name of marker for start point of path
                endmarker: ID name of marker for end point of path
                dataview: Viewbox for transforming x, y data into SVG coordinates
        '''
        if dataview:  # apply transform from dataview -> self.viewbox
            xform = Transform(dataview, self.viewbox)
            p1 = xform.apply(*p1)
            p2 = xform.apply(*p2)
            p3 = xform.apply(*p3)
            p4 = xform.apply(*p4) if p4 is not None else p4

        p1 = p1[0], self.flipy(p1[1])
        p2 = p2[0], self.flipy(p2[1])
        p3 = p3[0], self.flipy(p3[1])
        if p4 is not None:
            p4 = p4[0], self.flipy(p4[1])

        path = ET.SubElement(self.group, 'path')
        pointstr = f'M {fmt(p1[0])},{fmt(p1[1])} '
        pointstr += 'C ' if p4 is not None else 'Q '
        pointstr += f'{fmt(p2[0])},{fmt(p2[1])}'
        pointstr += f' {fmt(p3[0])},{fmt(p3[1])}'
        if p4 is not None:
            pointstr += f' {fmt(p4[0])},{fmt(p4[1])}'

        set_color(color, path, 'stroke')
        path.set('d', pointstr)
        path.set('stroke-width', str(width))
        path.set('fill', 'none')
        if startmarker is not None:
            path.set('marker-start', f'url(#{startmarker})')
        if endmarker is not None:
            path.set('marker-end', f'url(#{endmarker})')
        if stroke not in ['-', None, 'none', '']:
            path.set('stroke-dasharray', getdash(stroke, width))
        set_clip(path, self.clip)
