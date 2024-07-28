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

Geometric
---------

.. autoclass:: ziaplot.geo.Function
    :members:

.. autoclass:: ziaplot.geo.implicit.Implicit
    :members:

.. autoclass:: ziaplot.geo.line.Line
    :members:

.. autoclass:: ziaplot.geo.line.VLine
    :members:

.. autoclass:: ziaplot.geo.line.HLine
    :members:

.. autoclass:: ziaplot.geo.line.Segment
    :members:

.. autoclass:: ziaplot.geo.line.Vector
    :members:

.. autoclass:: ziaplot.geo.point.Point
    :members:

.. autoclass:: ziaplot.geo.bezier.BezierQuad
    :members:

.. autoclass:: ziaplot.geo.bezier.BezierCubic
    :members:

.. autoclass:: ziaplot.geo.bezier.Curve
    :members:

.. autoclass:: ziaplot.geo.tangents.Tangent
    :members:

.. autoclass:: ziaplot.geo.tangents.TangentSegment
    :members:

.. autoclass:: ziaplot.geo.tangents.Normal
    :members:

.. autoclass:: ziaplot.geo.tangents.NormalSegment
    :members:

.. autoclass:: ziaplot.geo.tangents.Diameter
    :members:

.. autoclass:: ziaplot.geo.tangents.Secant
    :members:

.. autoclass:: ziaplot.geo.tangents.Chord
    :members:

.. autoclass:: ziaplot.geo.tangents.Sagitta
    :members:

.. autoclass:: ziaplot.geo.integral.IntegralFill
    :members:

.. autoclass:: ziaplot.shapes.shapes.Circle
    :members:

.. autoclass:: ziaplot.shapes.shapes.Ellipse
    :members:

.. autoclass:: ziaplot.shapes.shapes.Rectangle
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


Tools
-----

A few calculation functions are made available to the user.

.. autofunction:: ziaplot.calcs.line_intersection

.. autofunction:: ziaplot.calcs.angle_of_intersection

.. autofunction:: ziaplot.calcs.y_intercept

.. autofunction:: ziaplot.calcs.x_intercept

.. autofunction:: ziaplot.calcs.func_intersection

.. autofunction:: ziaplot.calcs.local_max

.. autofunction:: ziaplot.calcs.local_min

.. autofunction:: ziaplot.util.linspace
