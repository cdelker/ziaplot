API
====


Base Classes
------------

.. autoclass:: ziaplot.drawable.Drawable
    :members:

.. autoclass:: ziaplot.container.Container

.. autoclass:: ziaplot.element.Element
    :members:

|

Diagrams and Graphs
-------------------

.. autoclass:: ziaplot.diagrams.diagram.Diagram
    :members:

.. autoclass:: ziaplot.diagrams.graph.Graph
    :members:

.. autoclass:: ziaplot.diagrams.graph.GraphQuad
    :members:

.. autoclass:: ziaplot.diagrams.graph.GraphQuadCentered
    :members:

.. autoclass:: ziaplot.diagrams.graphlog.GraphLogY
    :members:

.. autoclass:: ziaplot.diagrams.graphlog.GraphLogX
    :members:

.. autoclass:: ziaplot.diagrams.graphlog.GraphLogXY
    :members:

.. autoclass:: ziaplot.diagrams.polar.GraphPolar
    :members:

.. autoclass:: ziaplot.diagrams.smith.GraphSmith
    :members:

.. autoclass:: ziaplot.diagrams.ticker._Ticker
    :members:

|

Discrete Plot Types
-------------------

.. autoclass:: ziaplot.discrete.polylines.PolyLine
    :members:

.. autoclass:: ziaplot.discrete.polylines.Scatter
    :members:

.. autoclass:: ziaplot.discrete.polylines.ErrorBar
    :members:

.. autoclass:: ziaplot.discrete.polylines.LineFill
    :members:

.. autoclass:: ziaplot.discrete.bars.Bars
    :members:

.. autoclass:: ziaplot.discrete.bars.BarsHoriz
    :members:

.. autoclass:: ziaplot.discrete.bars.Histogram
    :members:

.. autoclass:: ziaplot.discrete.bars.HistogramHoriz
    :members:

.. autoclass:: ziaplot.discrete.polar.LinePolar
    :members:
    
.. autoclass:: ziaplot.discrete.contour.Contour
    :members:
    
.. autoclass:: ziaplot.diagrams.smith.SmithConstResistance
    :members:

.. autoclass:: ziaplot.diagrams.smith.SmithConstReactance
    :members:


|

Geometric Figures
-----------------

.. autoclass:: ziaplot.figures.function.Function
    :members:

.. autoclass:: ziaplot.figures.implicit.Implicit
    :members:

.. autoclass:: ziaplot.figures.line.Line
    :members:

.. autoclass:: ziaplot.figures.line.VLine
    :members:

.. autoclass:: ziaplot.figures.line.HLine
    :members:

.. autoclass:: ziaplot.figures.line.Segment
    :members:

.. autoclass:: ziaplot.figures.line.Vector
    :members:

.. autoclass:: ziaplot.figures.point.Point
    :members:

.. autoclass:: ziaplot.figures.bezier.Bezier
    :members:

.. autoclass:: ziaplot.figures.bezier.Curve
    :members:

.. autoclass:: ziaplot.figures.bezier.CurveThreePoint
    :members:

.. autoclass:: ziaplot.figures.integral.IntegralFill
    :members:

.. autoclass:: ziaplot.figures.shapes.Circle
    :members:

.. autoclass:: ziaplot.figures.shapes.Ellipse
    :members:

.. autoclass:: ziaplot.figures.shapes.Rectangle
    :members:

|


Charts 
------

.. autoclass:: ziaplot.charts.pie.Pie
    :members:

.. autoclass:: ziaplot.charts.pie.PieSlice
    :members:

.. autoclass:: ziaplot.charts.bar.BarChart
    :members:

.. autoclass:: ziaplot.charts.bar.Bar
    :members:

.. autoclass:: ziaplot.charts.bar.BarChartGrouped
    :members:

.. autoclass:: ziaplot.charts.bar.BarSeries
    :members:

|

Annotations
-----------

.. autoclass:: ziaplot.annotations.text.Text
    :members:

.. autoclass:: ziaplot.annotations.annotations.Arrow
    :members:

.. autoclass:: ziaplot.annotations.annotations.Angle
    :members:

|

Layouts
-------

.. autoclass:: ziaplot.layout.LayoutH
    :members:

.. autoclass:: ziaplot.layout.LayoutV
    :members:

.. autoclass:: ziaplot.layout.LayoutGrid
    :members:

.. autoclass:: ziaplot.layout.LayoutEmpty
    :members:



Global Themes and CSS
---------------------

.. autofunction:: ziaplot.style.themes.css

.. autofunction:: ziaplot.style.themes.theme

.. autofunction:: ziaplot.style.themes.theme_list



General Functions
-----------------

.. autofunction:: ziaplot.container.save


Geometric Calculations
----------------------

A few calculation functions are made available to the user.

.. autofunction:: ziaplot.geometry.distance

.. autofunction:: ziaplot.geometry.isclose

.. autofunction:: ziaplot.geometry.midpoint

.. autofunction:: ziaplot.geometry.translate

.. autofunction:: ziaplot.geometry.reflect

.. autofunction:: ziaplot.geometry.rotate

.. autofunction:: ziaplot.geometry.image

.. autofunction:: ziaplot.geometry.angle_mean

.. autofunction:: ziaplot.geometry.angle_diff

.. autofunction:: ziaplot.geometry.angle_isbetween

.. autofunction:: ziaplot.geometry.line.slope

.. autofunction:: ziaplot.geometry.line.intercept

.. autofunction:: ziaplot.geometry.line.xintercept

.. autofunction:: ziaplot.geometry.line.yvalue

.. autofunction:: ziaplot.geometry.line.xvalue

.. autofunction:: ziaplot.geometry.line.normal_distance

.. autofunction:: ziaplot.geometry.line.bisect

.. autofunction:: ziaplot.geometry.line.bisect_points

.. autofunction:: ziaplot.geometry.circle.point

.. autofunction:: ziaplot.geometry.circle.tangent_angle

.. autofunction:: ziaplot.geometry.circle.tangent_at

.. autofunction:: ziaplot.geometry.circle.tangent_points

.. autofunction:: ziaplot.geometry.circle.tangent

.. autofunction:: ziaplot.geometry.ellipse.point

.. autofunction:: ziaplot.geometry.ellipse.tangent_points

.. autofunction:: ziaplot.geometry.ellipse.tangent_angle

.. autofunction:: ziaplot.geometry.function.local_max

.. autofunction:: ziaplot.geometry.function.local_min

.. autofunction:: ziaplot.geometry.function.tangent

.. autofunction:: ziaplot.geometry.function.normal

.. autofunction:: ziaplot.geometry.bezier.xy

.. autofunction:: ziaplot.geometry.bezier.tangent_slope

.. autofunction:: ziaplot.geometry.bezier.tangent_angle

.. autofunction:: ziaplot.geometry.bezier.length

.. autofunction:: ziaplot.geometry.bezier.equal_spaced_points

.. autofunction:: ziaplot.geometry.intersect.lines

.. autofunction:: ziaplot.geometry.intersect.line_angle

.. autofunction:: ziaplot.geometry.intersect.line_circle

.. autofunction:: ziaplot.geometry.intersect.circles

.. autofunction:: ziaplot.geometry.intersect.line_arc

.. autofunction:: ziaplot.geometry.intersect.functions







.. autofunction:: ziaplot.util.linspace
