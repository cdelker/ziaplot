from .dataplots import PolyLine, Plot, Xy, Scatter, Text, LinePolar, Bars, BarsHoriz, Histogram, ErrorBar, LineFill, Arrow, Contour
from .geo import Function, Line, HLine, VLine, Tangent, Normal, Point, Segment, TangentSegment, NormalSegment, Vector, IntegralFill, BezierQuad, BezierCubic, Curve, Diameter, Radius, Secant, Chord, Sagitta, Angle
from .axes import AxesPlot, AxesGraph, AxesLogY, AxesLogX, AxesLogXY, AxesPolar, AxesSmith, SmithConstResistance, SmithConstReactance, ticker, AxesBlank
from .charts import Pie, PieSlice, BarChart, BarSingle, BarChartGrouped, BarSeries
from .layout import LayoutH, LayoutV, LayoutGrid, LayoutEmpty
from .shapes import Circle, Ellipse, Rectangle
from .style import styles
from .text import settextmode
from .config import config
from .util import linspace
from .find import line_intersection, func_intersection, local_max, local_min

__version__ = '0.6a0'