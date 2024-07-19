Functions and Geometric Figures
===============================

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)

Ziaplot can easily make graphs of basic geometric lines, points, curves, and functions,
without first needing to discretize the curve into x, y coordinates.


Points
------

Points are created from an (x, y) coordinate using :py:class:`ziaplot.geo.point.Point`.
They can be annotated with `.label()`. Use `.xguide()` and `.yguide()` to draw dotted
lines from the point to the x- and y- axis.
Points also use `.color()` and `.marker()`.

.. jupyter-execute::

    with zp.AxesGraph().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Point(3, 2).label('(3, 2)')
        zp.Point(1, 4).guidex().guidey().label('A')
        zp.Point(-4, 3).label('(-4, 3)').color('red').marker('square')

|

Lines
-----

Straight lines (in the Euclidean geometry sense) are drawn using :py:class:`ziaplot.geo.line.Line`.
They may be created from a point on the line and its slope, from two points on the line, or from a slope
y-intercept. Lines fill the entire axes, but do not affect the data range displayed.

.. jupyter-execute::

    with zp.AxesGraph().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Line((1, 2), 1).color('red')
        zp.Line.from_points((-2, 2), (-1, -4)).color('blue')
        zp.Line.from_slopeintercept(-.75, 3).color('orange')


:py:class:`ziaplot.geo.line.HLine` and :py:class:`ziaplot.geo.line.VLine` are shortcuts for making
horizontal and vertical lines.

|

Segments and Vectors
--------------------

A line segment, :py:class:`ziaplot.geo.line.Segment` is defined by its two endpoints.
A vector,  :py:class:`ziaplot.geo.line.Vector` is just a segment with one point at (0, 0)
and an arrow marker on the other.


.. jupyter-execute::

    with zp.AxesGraph().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Segment((-2, 2), (3, 4))
        zp.Vector(1, 2)

|

Curves
------

Bezier curves are drawn with either :py:class:`ziaplot.geo.bezier.BezierQuad` or
:py:class:`ziaplot.geo.bezier.BezierCubic`, using 3 or 4 control points, respectively.

.. jupyter-execute::

    a1 = (0, 0)
    a2 = (4.5, 5)
    a3 = (4, 1)
    b1 = (0, 0)
    b2 = (-4, 0)
    b3 = (-4, 5)
    b4 = (-1, 3)
    with zp.AxesGraph().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.BezierQuad(a1, a2, a3).color('red')
        zp.BezierCubic(b1, b2, b3, b4).color('blue') 


Two additional classes simplify the process for setting up curves.
:py:class:`ziaplot.geo.bezier.Curve` provides a means to create a
symmetric quadratic Bezier curve from the two endpoints and a deeflection constant.
:py:class:`ziaplot.geo.bezier.CurvevThreePoint` sets up a curve that passes through
the three given points on the curve itself.

.. jupyter-execute::

    a1 = (-1, 1)
    a2 = (3, 4)
    a3 = (4, 1)
    with zp.AxesGraph().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.CurveThreePoint(a1, a3, a2)
        zp.Point(*a1)
        zp.Point(*a2)
        zp.Point(*a3)
        zp.Curve((-2, -2), (2, -2), k=.5)

|

Functions
---------

The :py:class:`ziaplot.geo.function.Function` series takes a callable Python function and graphs it over the given data range.
The function must take one float argument (the x value) and return a float (the y value).

.. jupyter-execute::

    with zp.AxesGraph():
        zp.Function(math.sin, (-2*math.pi, 2*math.pi))
        zp.Function(math.cos, (-2*math.pi, 2*math.pi))

Lambda functions work well here, such as

.. jupyter-input::

    zp.Function(lambda x: x**2)

|

Shapes
------

Circles, Ellipses, and Rectangles may be drawn using
:py:class:`ziaplot.shapes.shapes.Circle`,
:py:class:`ziaplot.shapes.shapes.Ellipse`, and
:py:class:`ziaplot.shapes.shapes.Rectangle`.

.. jupyter-execute::

    with zp.AxesGraph().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Circle(0, 0, radius=2)
        zp.Ellipse(3, 3, r1=1, r2=2, theta=30)
        zp.Rectangle(-4, 2, width=1, height=2)

|

Tangents and Normals
--------------------

Tangent and Normal lines and segments may be easily drawn on several of the above shapes.
To draw Lines, use :py:class:`ziaplot.geo.tangents.Tangent` and :py:class:`ziaplot.geo.tangents.Normal`.
To draw Segments, use :py:class:`ziaplot.geo.tangents.TangentSegment` and :py:class:`ziaplot.geo.tangents.NormalSegment`.
Each contains class methods for placing the line or segment on circles, ellipses, lines, and functions.

With Segments, the `d1` and `d2` parameters specify how far to extend the segment in each direction.
Alternatively, `.trim()` may be used to trim a segment to a specified x value.

Here, tangents and normals are placed on a Function, where the `x` parameter specifies
the x-value of the function at which to add the tangent or normal:

.. jupyter-execute::

    with zp.AxesPlot().equal_aspect().xrange(-10, 5).yrange(-2, 10):
        ff = zp.Function(lambda x: x**3/20 + x**2 /2, xrange=(-10, 5))
        zp.Tangent.to(ff, x=-8).color('orange')
        zp.TangentSegment.to(ff, x=1, d1=2, d2=2).color('blue')
        zp.NormalSegment.to(ff, x=1).trim(0, 4).color('green')


For circles, the `.to_circle()` method is used, with a `theta` parameter specifying the angle
on the circle:

.. jupyter-execute::

    with zp.AxesPlot().equal_aspect().xrange(-5, 5).yrange(-5, 5):
        circ = zp.Circle(1, 1, 2)
        zp.TangentSegment.to_circle(circ, theta=45).color('red')
        zp.NormalSegment.to_circle(circ, theta=160).color('blue')


On Bezier curves, use `.to_bezier()` and specify the parameter `t` from 0-1 along the curve
at which to place the tangent or normal:

.. jupyter-execute::

    with zp.AxesPlot().equal_aspect().xrange(-5, 5).yrange(-5, 5):
        b = zp.Curve((-2, 0), (3, 1), k=1)
        zp.Tangent.to_bezier(b, t=.4).color('orange')
        zp.Normal.to_bezier(b, t=.4).color('blue')

|


Annotations
-----------

Points on a line
****************

Points may also be easily placed along Lines, Functions, Curves, and Shapes.
Method `.at` places the Point on a line or function at the given x value, while
method `.at_y` places it at the (first occurence of) the given y value.
Use `.on_circle` and `.on_bezier` to place a point on Circles an Curves.
`.at_intersection` takes two curves and places a point where they cross.
`.at_minimum` and `.at_maximum` place a point at the local minimum or local maximum, respectively.
Methods `.at_intersection`, `.at_minimum`, and `.at_maximum` require `x1` and `x2`
parameters to bound the bisection algorithm search for the location of interest.

.. jupyter-execute::

    with zp.AxesPlot().equal_aspect().xrange(-5, 5).yrange(-5, 5):
        func = zp.Function(lambda x: x*math.sin(x), (-2, 6)).color('red')
        curve = zp.CurveThreePoint((1, 6), (2, 3), (4, 3)).color('blue')
        circle = zp.Circle(-2, 4, 1)
        line = zp.Line((-4, -2), .1)
        zp.Point.at(func, x=3).label('A')
        zp.Point.at(line, x=-2).label('B')
        zp.Point.on_circle(circle, theta=45).label('C')
        zp.Point.on_bezier(curve, t=.25).label('D')
        zp.Point.at_intersection(line, func, x1=2, x2=6).label('X')
        zp.Point.at_minimum(func, -2, 2).label('min', 'S')
        zp.Point.at_maximum(func, 0, 3).label('max', 'N')

|

Labels
******

Labels may be added to Segments using `.label()`. A `loc` parameter accepts values
from 0 to 1, indicating the relative position along the line. The `align` parameter
positions and aligns the text using the 8 compass directions

.. jupyter-execute::

    with zp.AxesBlank(style=zp.styles.BlackWhite()).equal_aspect() as g:
        seg = zp.Segment((-1, 0), (1, 1))
        seg.label('A')
        seg.label('B', loc=1)
        seg.label('Segment', loc=.5, rotate=True)
        seg.label('SE alignment', loc=.5, rotate=False, align='SE')


Angles
******

Angles formed by two lines or segments may be marked with arcs using :py:class:`ziaplot.geo.line.Angle`. 
Because a pair of crossing lines forms 4 angles, the `quad` parameter specifies which one to mark. The
`arcs` parameter specifies the number of arcs to draw.

.. jupyter-execute::

    with zp.AxesPlot().equal_aspect():
        line1 = zp.Line((0,0), 0)
        line2 = zp.Line((0,0), 1.5)
        zp.Angle(line1, line2, quad=4).label(r'$\theta$')
        zp.Angle(line1, line2, quad=2, arcs=2).label(r'$\phi$')

|

Midmarkers
**********

A marker may be placed at the midpoint of a segment or curve with `.midmarker()`. Useful for adding
directional arrows or marking similar or dissimilar sides of a shape.

.. jupyter-execute::

    with zp.AxesPlot().equal_aspect().xrange(-2, 5).yrange(-4, 4):
        zp.Segment((-1,0), (3, 2)).midmarker('>')
        zp.Segment((3,2), (4, -2)).midmarker('|').color('C0')
        zp.Segment((4,-2), (-1, 0)).midmarker('||').color('C0')

|

Lines on a Circle
*****************

Circles may be annotated with Diameter, Radius, Chords, Secants, and Sagitta (the line perpendicular to a chord).

.. jupyter-execute::

    with zp.AxesBlank(style=zp.styles.BlackWhite()).equal_aspect() as g:
        circ = zp.Circle(0, 0, 2)
        ch = zp.Chord(circ, 10, 135).label('A', 0, 'E').label('B', 1, 'NW').label('Chord', .8, rotate=True)
        sg = zp.Sagitta(circ, 10, 135).label('C', 0, 'N').label('Sagitta', .6, 'E')
        zp.Angle(ch, sg, quad=4)
        zp.Diameter(circ, 0).label('Diameter', .8)
        zp.Radius(circ, -30).label('Radius', .6, rotate=True)



IntegralFill
************

The area under a Function may be filled in using :py:class:`ziaplot.geo.integral.IntegralFill`.

.. jupyter-execute::

    with zp.AxesPlot().xrange(0, 20).yrange(0, 160):
        ff = zp.Function(lambda x: 80*x*math.exp(-.2*x), xrange=(1,20))
        zp.IntegralFill(ff, x1=2.5, x2=12.5).color('lightblue').alpha(.5)
