''' Annotations Angle and Arrow '''
from typing import Optional, Sequence, cast
import math

from .. import diagram_stack
from ..util import angle_mean
from ..style import MarkerTypes
from ..text import TextPosition, Halign, Valign, text_align_ofst
from ..canvas import Canvas, Borders, ViewBox
from ..element import Component
from ..geo.line import Line, LineLabel


class Annotation(Component):
    ''' Base class for annotations such as Arrows, Angles. Use to apply styling. '''


class Arrow(Annotation):
    ''' An arrow pointing to an XY location, with optional
        text annotation

        Args:
            xy: XY position to point at
            xytail: XY-position of arrow tail
            s: String to draw at tail of arrow
            strofst: XY offset between text and arrow tail
            marker: Arrowhead marker shape
            tailmarker: Arrowhead tail marker
    '''
    _step_color = False

    def __init__(self, xy: Sequence[float], xytail: Sequence[float],
                 marker: MarkerTypes = 'arrow',
                 tailmarker: Optional[MarkerTypes] = None):
        super().__init__()
        self.xy = xy
        self.xytail = xytail
        self._text: Optional[str] = None
        self._text_pos: Optional[TextPosition] = None
        self._tailmarker = tailmarker
        self._endmarker = marker

    def label(self, text: str,
              pos: TextPosition = 'NE') -> 'Arrow':
        ''' Add a text label to the point

            Args:
                text: Label
                text_pos: Position for label with repsect
                    to the point (N, E, S, W, NE, NW, SE, SW)
        '''
        self._text = text
        self._text_pos = pos
        return self

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        ''' Add XML elements to the canvas '''
        sty = self._build_style()
        color = sty.get_color()
        edgecolor = color
        if sty.edge_color not in [None, 'auto']:
            edgecolor = sty.edge_color

        tailmark = None
        endmark = None
        if self._tailmarker:
            tailmark = canvas.definemarker(self._tailmarker,
                                           sty.radius,
                                           color,
                                           edgecolor,
                                           sty.edge_width,
                                           orient=True)
        if self._endmarker:
            endmark = canvas.definemarker(self._endmarker,
                                          sty.radius,
                                          color,
                                          edgecolor,
                                          sty.edge_width,
                                          orient=True)
        
        x = self.xytail[0], self.xy[0]
        y = self.xytail[1], self.xy[1]
        canvas.path(x, y,
                    stroke=sty.stroke,
                    color=color,
                    width=sty.stroke_width,
                    startmarker=tailmark,
                    endmarker=endmark,
                    dataview=databox)

        if self._text:
            dx, dy, halign, valign = text_align_ofst(
                self._text_pos, sty.margin)

            tsty = self._build_style('Point.Text')
            canvas.text(self.xytail[0], self.xytail[1], self._text,
                        color=sty.get_color(),
                        font=tsty.font,
                        size=tsty.font_size,
                        halign=halign,
                        valign=valign,
                        pixelofst=(dx, dy),
                        dataview=databox)


class Angle(Annotation):
    ''' Draw angle between two Lines/Segments '''
    def __init__(self, line1: Line, line2: Line, quad: int = 1, arcs: int = 1):
        super().__init__()
        self.line1 = line1
        self.line2 = line2
        self.quad = quad
        self.arcs = arcs
        self._label: Optional[LineLabel] = None
        self.square_right = True

    def label(self, label: str, color: Optional[str] = None,
              size: Optional[float] = None) -> 'Angle':
        self._label = LineLabel(label, color=color, size=size)
        return self

    def color(self, color: str) -> 'Angle':
        ''' Sets the color of the angle arc '''
        self._style.color = color
        return self

    def strokewidth(self, width: float) -> 'Angle':
        ''' Sets the strokewidth of the angle arc '''
        self._style.stroke_width = width
        return self

    def radius(self, radius: float, text_radius: Optional[float] = None) -> 'Angle':
        ''' Sets the radius of the angle arc '''
        self._style.radius = radius
        if text_radius:
            self._style.margin = text_radius
        return self

    @classmethod
    def to_zero(cls, line: Line, quad: int = 1):
        ''' Create angle between line and y=0 '''
        diagram_stack.pause = True
        line2 = Line((0, 0), 0)
        diagram_stack.pause = False
        return cls(line, line2, quad=quad)

    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None,
             borders: Optional[Borders] = None) -> None:
        m1, m2 = self.line1.slope, self.line2.slope
        b1, b2 = self.line1.intercept, self.line2.intercept

        # Point of intersection
        x = (b2 - b1) / (m1 - m2)
        y = self.line1.y(x)
        if not math.isfinite(x):
            x = self.line1.point[0]
            y = self.line1.y(x)
        if not math.isfinite(y):
            y = self.line2.y(x)

        theta1 = math.atan(m1)
        theta2 = math.atan(m2)

        if m1 < m2:
            theta1, theta2 = theta2, theta1

        if self.quad == 2:
            theta2 += math.pi
            theta1 += math.pi
            theta2, theta1 = theta1, theta2

        elif self.quad == 3:
            theta1 += math.pi
        elif self.quad == 4:
            theta2, theta1 = theta1, theta2
        else:
            theta2 += math.pi

        theta1 = (theta1 + math.tau) % math.tau
        theta2 = (theta2 + math.tau) % math.tau

        # Calculate radius of angle arc in data coordinates
        assert databox is not None
        sty = self._build_style()
    
        r = sty.radius * databox.w / canvas.viewbox.w
        dtheta = abs(theta1 - theta2) % math.pi
        if self.square_right and math.isclose(dtheta, math.pi/2):
            # Right Angle
            r2 = r / math.sqrt(2)
            xpath = [x + r2 * math.cos(theta1),
                     x + r * math.cos(theta1+math.pi/4),
                     x + r2 * math.cos(theta2)]
            ypath = [y + r2 * math.sin(theta1),
                     y + r * math.sin(theta1+math.pi/4),
                     y + r2 * math.sin(theta2)]
            canvas.path(xpath, ypath,
                        color=sty.color,
                        width=sty.stroke_width,
                        dataview=databox
                        )
        else:
            dradius = sty.margin * databox.w / canvas.viewbox.w
            for i in range(self.arcs):
                canvas.arc(x, y, r - i * dradius,
                        math.degrees(theta1),
                        math.degrees(theta2),
                        strokecolor=sty.color,
                        strokewidth=sty.stroke_width,
                        dataview=databox
                        )

        if self._label:
            textstyle = self._build_style('Angle.Text')
            r = sty.radius + textstyle.margin
            color = self._label.color if self._label.color else textstyle.get_color()
            size = self._label.size if self._label.size else textstyle.font_size
            labelangle = angle_mean(theta1, theta2)
            dx = r * math.cos(labelangle)
            dy = r * math.sin(labelangle)

            if labelangle < math.tau/8 or labelangle > 7*math.tau/8:
                halign = 'left'
            elif 3 * math.tau / 8 < labelangle < 5 * math.tau / 8:
                halign = 'right'
            else:
                halign = 'center'

            if math.tau/8 < labelangle < 3 * math.tau / 8:
                valign = 'bottom'
            elif 5 * math.tau / 8 < labelangle < 7 * math.tau / 8:
                valign = 'top'
            else:
                valign = 'center'

            canvas.text(x, y, self._label.label,
                        color=color,
                        font=textstyle.font,
                        size=size,
                        halign=cast(Halign, halign),
                        valign=cast(Valign, valign),
                        pixelofst=(dx, dy),
                        dataview=databox)
