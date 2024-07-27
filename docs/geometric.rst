.. _Geometric:

Geometric Figures
=================

Geometric elements include Lines, Functions, Points, Circles, and Curves.

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp
    zp.css('Canvas{width:400;height:300;}')

.. _Point:

Point
-----

Place a single marker point in the coordinate plane.

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Point(3, 2).label('(3, 2)')
        zp.Point(1, 4).guidex().guidey().label('A')
        zp.Point(-4, 3).label('(-4, 3)').color('red').marker('square')

:py:class:`ziaplot.geo.point.Point`.


 .. tip::
    
    Use `.guidex()` and `.guidey()` to draw guiding lines to the x and y axis.

.. tip::

    Use `.label()` to add text annotation to a `Point`. The second parameter
    to `.label()` specifies the compass-direction to draw the label around the point,
    i.e. 'N', 'S', 'E', 'W', 'NE', 'NW', etc.


|

.. _Line:

Line
----

A straight line, filling the entire diagram.

Lines may be created from:

    1. A point on the line and the slope of the line
    2. Two points on the line (classmethod `from_points`)
    3. The slope and y-intercept of the line (classmethod `from_slopeintercept`)

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Line((1, 2), 1).color('red')
        zp.Line.from_points((-2, 2), (-1, -4)).color('blue')
        zp.Line.from_slopeintercept(-.75, 3).color('orange')

:py:class:`ziaplot.geo.line.Line`

.. note::

    Unlike some other elements, Lines do not change the data limits displayed by the graph.


HLine
-----

A horizontal line.

.. jupyter-execute::

    zp.HLine(0)


:py:class:`ziaplot.geo.line.HLine`


VLine
-----

A vertical line.

.. jupyter-execute::

    zp.VLine(0)

:py:class:`ziaplot.geo.line.VLine`


Segment
-------

A line segment, defined by its two endpoints.

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Segment((-2, 2), (3, 4))

:py:class:`ziaplot.geo.line.Segment`


.. tip::

    Place text along a segment using `.label`. The `loc` parameter specifies
    the relative position, from 0-1, along the segment. `align` provides
    the compass-direction to align the text relative to the point on the segment.

    .. jupyter-execute::

        with zp.Diagram().css(zp.CSS_BLACKWHITE):
            seg = zp.Segment((-1, 0), (1, 1))
            seg.label('A')
            seg.label('B', loc=1)
            seg.label('Segment', loc=.5, rotate=True)
            seg.label('SE alignment', loc=.5, rotate=False, align='SE')

.. tip::

    Use `.midmarker()` to add a single marker to the midpoint of a Segment.

    .. jupyter-execute::

        with zp.Graph().equal_aspect().xrange(-2, 5).yrange(-4, 4):
            zp.Segment((-1,0), (3, 2)).midmarker('>')
            zp.Segment((3,2), (4, -2)).midmarker('|').color('C0')
            zp.Segment((4,-2), (-1, 0)).midmarker('||').color('C0')

.. tip::

    Use `.endmarkers()` to add markers on each end of a Segment (or Function).


Vector
------

A line segment starting at the origin and ending with an arrow marker.


.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Vector(4, 4)

:py:class:`ziaplot.geo.line.Vector` 


BezierQuad
----------

Quadratic Bézier curve defined by 3 control points.

.. jupyter-execute::

    a1 = (0, 0)
    a2 = (4.5, 5)
    a3 = (4, 1)
    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.BezierQuad(a1, a2, a3)

:py:class:`ziaplot.geo.bezier.BezierQuad`


.. seealso::

    :ref:`curve`


BezierCubic
-----------

Cubic Bézier curve defined by 4 control points.

.. jupyter-execute::

    b1 = (0, 0)
    b2 = (-4, 0)
    b3 = (-4, 5)
    b4 = (-1, 3)
    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.BezierCubic(b1, b2, b3, b4)


:py:class:`ziaplot.geo.bezier.BezierQuad`


.. seealso::

    :ref:`curve`


.. _curve:

Curve
-----

A symmetric quadratic Bézier curve defined by its endpoints and a deflection constant.

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Curve((-2, 0), (2, 0), k=1)


:py:class:`ziaplot.geo.bezier.Curve`


CurveThreePoint
---------------

A quadratic Bézier curve passing through three defined points.


.. jupyter-execute::

    a1 = (-1, 1)
    a2 = (3, 4)
    a3 = (4, 1)
    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.CurveThreePoint(a1, a3, a2)
        zp.Point(*a1)
        zp.Point(*a2)
        zp.Point(*a3)

:py:class:`ziaplot.geo.bezier.CurveThreePoint`


|

Function
--------

Plot y = f(x), where f is a Python callable function of one variable (x) returning
one variable (y).

.. jupyter-execute::

    with zp.GraphQuad().xrange(-2*math.pi, 2*math.pi):
        zp.Function(math.sin, (-2*math.pi, 2*math.pi))


:py:class:`ziaplot.geo.function.Function`


.. tip::

    Use lambda functions to help define the callable, such as:

    .. jupyter-input::

        zp.Function(lambda x: x**2)

|

Implicit
--------

Plot an implicit function f(x, y) = 0, where f is a Python callable of two variables (x and y)
returning a value. Points where the value is found to be zero are plotted.

.. note::

    `xlim` and `ylim` must be provided to define the domain over which to plot.

.. jupyter-execute::

    with zp.GraphQuad().equal_aspect():
        zp.Implicit(
            lambda x, y: x**2 + y**2 - 1,
            xlim=(-1.5, 1.5),
            ylim=(-1.5, 1.5))


:py:class:`ziaplot.geo.implicit.Implicit`


Circle
------

Draw a circle.

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Circle(0, 0, radius=2)

:py:class:`ziaplot.shapes.shapes.Circle`

.. tip::

    Use `.equal_aspect()` on the graph to ensure the circle is not
    stretched into an ellipse.


Ellipse
-------

Draw an ellipse.

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Ellipse(3, 3, r1=1, r2=2, theta=30)


:py:class:`ziaplot.shapes.shapes.Ellipse`




Rectangle
---------

Draw a rectangle at (x, y) with a width and height.

.. jupyter-execute::

    with zp.GraphQuad().xrange(-5, 5).yrange(-5, 5).equal_aspect():
        zp.Rectangle(-4, 2, width=1, height=2)

:py:class:`ziaplot.shapes.shapes.Rectangle`.


|

Tangents and Normals
--------------------

Tangent is a helper class that creates Lines tangent to
Functions, Circles, or Curves.


:py:class:`ziaplot.geo.tangents.Tangent`


TangentSegment creates Segments tangent to Functions, Circles, or Curves.

:py:class:`ziaplot.geo.tangents.TangentSegment`

Normal is a helper class that creates Lines normal (perpendicular) to
Functions, Circles, or Curves.


:py:class:`ziaplot.geo.tangents.Normal`


NormalSegment creates Segments normal to Functions, Circles, or Curves.

:py:class:`ziaplot.geo.tangents.NormalSegment`


.. note::

    The `d1` and `d2` parameters to `TangentSegment` and `NormalSegment`
    specify how far to extend the segment in each direction.

    The Segment's `.trim()` method changes its endpoints, which is useful for
    stopping it at a desired x value without calculating the exact `d1` and `d2`.


to Circles and Ellipses
***********************

Use `.to_circle`. Specify the angle theta around the circle.

.. jupyter-execute::

    with zp.Graph().equal_aspect().xrange(-4, 4).yrange(-4, 4):
        circ = zp.Circle(1, 1, 2)
        zp.TangentSegment.to_circle(circ, theta=45).color('red')
        zp.NormalSegment.to_circle(circ, theta=160).color('blue')


to Functions
************

Use `.to`. Specify the x value.

.. jupyter-execute::

    with zp.Graph().equal_aspect().xrange(-10, 5).yrange(-2, 10):
        ff = zp.Function(lambda x: x**3/20 + x**2 /2, xrange=(-10, 5))
        zp.Tangent.to(ff, x=-8).color('orange')
        zp.TangentSegment.to(ff, x=1, d1=2, d2=2).color('blue')
        zp.NormalSegment.to(ff, x=1).trim(0, 4).color('green')

to Bézier Curves
****************

Use `.to_bezier`. Specify the parameter t (from 0-1) along the curve.

.. jupyter-execute::

    with zp.Graph().equal_aspect().xrange(-5, 5).yrange(-5, 5):
        b = zp.Curve((-2, 0), (3, 1), k=1)
        zp.Tangent.to_bezier(b, t=.4).color('orange')
        zp.Normal.to_bezier(b, t=.4).color('blue')




Placing Points
--------------


* **Point.at(f, x)**: Place a point on a Line or Function f at the x value.
* **Point.at_y(f, y)**: Place a point on a Line or Function f at the y value.
* **Point.on_circle(c, theta)**: Place a point on Circle or Ellipse c at an angle theta.
* **Point.on_bezier(c, t)**: Place a point on the Bézier curve at parameter t.
* **Point.at_intersection(f1, f2)**: Place a point at the intersection of two Functions or Lines
* **Point.at_minimum(f, x1, x2)**: Place a point at the local minimum of f between x1 and x2
* **Point.at_maximum(f, x1, x2)**: Place a point at the local maximum of f between x1 and x2

.. jupyter-execute::

    with zp.Graph().equal_aspect().xrange(-5, 5).yrange(-5, 5):
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


Angles
------

Draw the arc of an angle between two lines.

.. jupyter-execute::

    with zp.Graph().equal_aspect():
        line1 = zp.Line((0,0), 0)
        line2 = zp.Line((0,0), 1.5)
        zp.Angle(line1, line2, quad=4).label('θ')
        zp.Angle(line1, line2, quad=2, arcs=2).label('Φ')

:py:class:`ziaplot.annotations.annotations.Angle`


.. note::

    Use `quad` to specify which of the four quadrants (1-4) to put the arc in.

    Use `arcs` to specify the number of arcs to draw


|

Lines on a Circle
-----------------

Draw Segments associated with a circle.
`Diameter`, `Radius`, `Chord`, `Secant`, `Sagitta` (the line perpendicular to a chord)
subclasss from `Segment`.

.. jupyter-execute::

    with zp.Diagram().css(zp.CSS_BLACKWHITE).equal_aspect() as g:
        zp.Point(0, 0)
        circ = zp.Circle(0, 0, 2)
        ch = zp.Chord(circ, 10, 135).label('A', 0, 'E').label('B', 1, 'NW').label('Chord', .8, rotate=True)
        sg = zp.Sagitta(circ, 10, 135).label('C', 0, 'N').label('Sagitta', .6, 'E')
        zp.Angle(ch, sg, quad=4)
        zp.Diameter(circ, 0).label('Diameter', .8)
        zp.Radius(circ, -30).label('Radius', .6, rotate=True)



IntegralFill
------------

Fill the area under a Function between two x values. Or fill the area
between two Functions.

.. jupyter-execute::

    with zp.Graph().xrange(0, 20).yrange(0, 160):
        ff = zp.Function(lambda x: 80*x*math.exp(-.2*x), xrange=(1,20))
        zp.IntegralFill(ff, x1=2.5, x2=12.5).color('lightblue 50%')

.. jupyter-execute::

        with zp.Graph().xrange(0, 20).yrange(0, 160):
            ff = zp.Function(lambda x: 80*x*math.exp(-.2*x))
            f2 = zp.Line.from_slopeintercept(-1, 90)
            zp.IntegralFill(ff, f2).color('lightblue 50%')


:py:class:`ziaplot.geo.integral.IntegralFill`
