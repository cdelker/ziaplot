''' Dataclasses defining plot style '''

from typing import Optional, Literal, Union

from dataclasses import dataclass, field
from .colors import ColorCycle, ColorFade
from .smithstyle import SmithStyle

MarkerTypes = Literal['round', 'o', 'square', 's', 'triangle', '^',
                      'triangled', 'v', 'larrow', '<', 'arrow', '>',
                      '+', 'x', '-', '|', 'undefined', None]
DashTypes = Union[Literal['-', ':', 'dotted', '--', 'dashed', '-.', '.-', 'dashdot'], str]


@dataclass
class MarkerStyle:
    ''' Line Marker Style

        Args:
            shape: Shape of marker
            color: Marker color
            strokecolor: Color for border
            strokewidth: Width of border
            radius: Pixel radius (or half-width) of marker
            orient: Orient the marker along the line (ie for arrowheads)
    '''
    shape: MarkerTypes = None
    color: str = 'undefined'  # Revert to LineStyle
    strokecolor: str = 'black'
    strokewidth: float = 1
    radius: float = 7.0
    orient: bool = False


@dataclass
class LineStyle:
    ''' Line Style

        Args:
            color: Line color
            stroke: Line style, name or SVG dash-array specification
            width: Line width
    '''
    color: str = 'undefined'  # Revert to AxisStyle
    stroke: DashTypes = '-'
    width: float = 2.0


@dataclass
class GuideStyle:
    ''' Guide line style

        Args:
            color: Line color
            stroke: Line style, name or SVG dash-array specification
            width: Line width
    '''
    color: str = 'black'
    stroke: DashTypes = ':'
    width: float = 1.5


@dataclass
class PointMarkerStyle:
    ''' Point Marker Style

        Args:
            shape: Shape of marker
            color: Marker color
            strokecolor: Color for border
            strokewidth: Width of border
            radius: Pixel radius (or half-width) of marker
    '''
    shape: MarkerTypes = 'round'
    color: str = '#007a86'
    strokecolor: str = 'black'
    strokewidth: float = 1
    radius: float = 4.0


@dataclass
class BorderStyle:
    ''' Border Style for bars and pie slices
    
        Args:
            color: border color
            width: border stroke width
    '''
    color: str = 'black'
    width: float = 1.

        
@dataclass
class TextStyle:
    ''' Text Style

        Args:
            font: Font family
            size: Font point size
            color: Font color
    '''
    font: str = 'sans'
    size: float = 16
    color: str = 'black'


@dataclass
class PointStyle:
    ''' Point Style

        Args:
            marker: Marker Style
            text: Text Label Style
            text_ofst: Pixel offset between point and text    
            guidex: Line style for x guide-lines
            guidey: Line style for y guide-lines
    '''
    marker: PointMarkerStyle = field(default_factory=PointMarkerStyle)
    text: TextStyle = field(default_factory=lambda: TextStyle(size=14))
    text_ofst: float = 8
    guidex: GuideStyle = field(default_factory=GuideStyle)
    guidey: GuideStyle = field(default_factory=GuideStyle)


@dataclass
class ErrorBarStyle:
    ''' Style for Error Bars

        Args:
            marker: Marker shape
            stroke: Stroke/linestyle
            length: Length of errorbar caps
            width: Width of line between errorbar caps
    '''
    marker: MarkerTypes = '-'
    stroke: DashTypes = '-'
    length: float = 7.0
    width: float = 2.0
    

@dataclass
class ColorBarStyle:
    ''' Style for contour colorbars
    
        Args:
            text: Text style
            bordercolor: Color for colorbar border
            borderwidth: Width of colorbar border
            width: Pixel width of colorbar
            xpad: Horizontal distance from colorbar to axis
            ypad: Vertical distance from colorbar to axis
            formatter: Text format for colorbar labels
    '''
    text: TextStyle = field(default_factory=lambda: TextStyle(size=12))
    colors: ColorFade = field(default_factory=lambda: ColorFade('#007a86', '#ba0c2f'))
    bordercolor: str = 'black'
    borderwidth: float = 1.0
    width: float = 20.
    xpad: float = 20.
    ypad: float = 5.
    formatter = '.3g'


@dataclass
class ShapeStyle:
    ''' Style for shapes '''
    color: str = 'none'
    strokecolor: str = 'black'
    strokewidth: float = 2.0


@dataclass
class AngleStyle:
    ''' Style for angle indicators '''
    text: TextStyle = field(default_factory=lambda: TextStyle(size=12))
    radius: float = 15
    text_radius: float = 20
    color: str = 'black'
    strokewidth: float = 1.5
    arcgap: float = 4.0


@dataclass
class SeriesStyle:
    ''' Style for generic data series

        Args:
            line: Style of lines
            marker: Style of markers
            text: Style of text
            yerror: Style of Y-error bars
            xerror: Style of X-error bars
            fillcolor: Style for filled LineFill series
            fillalpha: Transparency factor (0-1) for LineFill series
    '''
    line: LineStyle = field(default_factory=LineStyle)
    border: BorderStyle = field(default_factory=BorderStyle)
    marker: MarkerStyle = field(default_factory=MarkerStyle)
    point: PointStyle = field(default_factory=PointStyle)
    shape: ShapeStyle = field(default_factory=ShapeStyle)
    text: TextStyle = field(default_factory=TextStyle)
    angle: AngleStyle = field(default_factory=AngleStyle)
    yerror: ErrorBarStyle = field(default_factory=ErrorBarStyle)
    xerror: ErrorBarStyle = field(default_factory=lambda: ErrorBarStyle(marker='|'))
    fillcolor: Optional[str] = None  # Fill for LineFill areas
    fillalpha: float = 0.3  # Alpha for LineFill areas
    colorbar: ColorBarStyle = field(default_factory=ColorBarStyle)


@dataclass
class AxisStyle:
    ''' Style for X/Y Axis

        Args:
            xname: Text style for x-axis label
            yname: Text style for y-axis label
            title: Text style for axis title
            color: Color of axis lines and ticks
            bgcolor: Fill color for axis background
            xgrid: Show grid along x direction
            ygrid: Show grid along y direction
            framelinewidth: Width of axis frame/border
            fullbox: Draw full rectangle around box
            gridcolor: Color for grid lines
            gridlinewidth: Width of grid lines
            gridstroke: Line style or SVG dash-array specification for grid
            xtickpad: Fraction of a tick to expand the data range
            ytickpad: Fraction of a tick to expand the data range
    '''
    xname: TextStyle = field(default_factory=TextStyle)
    yname: TextStyle = field(default_factory=TextStyle)
    title: TextStyle = field(default_factory=TextStyle)
    color: str = 'black'
    bgcolor: str = '#F6F6F6'
    xgrid: bool = True
    ygrid: bool = True
    framelinewidth: float = 2.0
    fullbox: bool = False
    gridcolor: str = 'lightgray'
    gridlinewidth: float = 1.0
    gridstroke: DashTypes = 'dashed'
    xtickpad: float = 0.2
    ytickpad: float = 0.2

        
@dataclass
class TickStyle:
    ''' Style for tick marks

        Args:
            length: Length of tick marks
            width: Line width of tick marks
            text: Text style for tick labels
            textofst: Distance between tick and text
            xstrformat: String formatter for x tick labels
            ystrformat: String formatter for y tick labels
            xminordivisions: Number of minor tick divisions between labeled ticks
            yminordivisions: Number of minor tick divisions between labeled ticks
            xlogdivisions: Number of minor divisions for logscale plots (2, 5, or 10)
            ylogdivisions: Number of minor divisions for logscale plots (2, 5, or 10)
            minorwidth: Line width of minor ticks
            minorlength: Length of minor ticks
            maxticksx: Maximum number of ticks allowed on x axis
            maxticksy: Maximum number of ticks allowed on y axis
    '''
    length: float = 9.0
    width: float = 2.0
    text: TextStyle = field(default_factory=lambda: TextStyle(size=16))
    textofst: float = 4
    xstrformat: str = 'g'
    ystrformat: str = 'g'
    xminordivisions: int = 0
    yminordivisions: int = 0
    xlogdivisions: int = 10
    ylogdivisions: int = 10
    minorwidth: float = 1.0
    minorlength: float = 5.0
    maxticksx: int = 9
    maxticksy: int = 9


@dataclass
class LegendStyle:
    ''' Style for plot legend

        Args:
            text: Text style
            linespacing: Spacing between lines as multiplier of font size
            border: Color for legend box border
            fill: Fill color for legend box
            pad: Padding between axis and legend box
            margin: Distance from legend box to legend contents
    '''
    text: TextStyle = field(default_factory=TextStyle)
    linespacing: float = 1.2
    border: str = 'black'
    fill: str = 'none'
    pad: float = 10
    margin: float = 4


@dataclass
class PieStyle:
    ''' Style for pie charts

        Args:
            legend: Legend style
            edgepad: Distance from canvas edge to pie
            extrude: Distance to extrude slices
            title: Text style for title
            label: Text style for wedge labels
            labelpad: Distance from pie to wedge label
    '''
    legend: LegendStyle = field(default_factory=LegendStyle)
    edgepad: float = 10
    extrude: float = 20
    title: TextStyle = field(default_factory=TextStyle)
    label: TextStyle = field(default_factory=TextStyle)
    labelpad: float = 4


@dataclass
class PolarStyle:
    ''' Style for Polar plots

        Args:
            rlabeltheta: Angle (degrees) for drawing r-value labels
            edgepad: Distance between frame and canvas border
            labelpad: Distance between frame and theta labels
            title: Text style for title
    '''
    rlabeltheta: float = 0
    edgepad: float = 10
    labelpad: float = 4
    title: TextStyle = field(default_factory=TextStyle)


@dataclass
class Style:
    ''' Main Ziaplot Style

        Args:
            series: Style for Series (lines, markers)
            axis: Style for the axis
            tick: Style for tick marks and labels
            legend: Style for plot legend
            pie: Style for pie charts
            polar: Style for polar plots
            smith: Style for Smith charts
            canvasw: Width of full image
            canvash: Height of full image
            bgcolor: Color of background
            colorcycle: Automatic colors for multiple lines
    '''
    series: SeriesStyle = field(default_factory=SeriesStyle)
    axis: AxisStyle = field(default_factory=AxisStyle)
    tick: TickStyle = field(default_factory=TickStyle)
    legend: LegendStyle = field(default_factory=LegendStyle)
    pie: PieStyle = field(default_factory=PieStyle)
    polar: PolarStyle = field(default_factory=PolarStyle)
    smith: SmithStyle = field(default_factory=SmithStyle)
    canvasw: float = 600
    canvash: float = 400
    bgcolor: str = 'none'
    colorcycle: ColorCycle = field(default_factory=ColorCycle)

    @property
    def size(self):
        return self.canvasw, self.canvash

    @size.setter
    def size(self, wh):
        self.canvasw, self.canvash = wh