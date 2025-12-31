Animations
==========

.. jupyter-execute::
    :hide-code:

    import ziaplot as zp
    zp.config.text = 'text'
    zp.css('Canvas{width:200;height:200;}')

Ziaplot supports basic animaitons through SVG's Synchronized Multimedia Integration Language (SMIL) attributes.
Animation options include setting an SVG attribute at a specific time,
sweeping an attribute from one value to another,
moving an object along the path of another object,
or simulating a "draw" and "erase" of paths.

.. tip::

    The animations on this page are set to run some number of seconds after the page loads. If nothing appears to be happening, refresh the page.


The `svg` attribute of drawing elements contains methods for setting animations.

Setting an attribute
^^^^^^^^^^^^^^^^^^^^

To set an SVG attribute at a specific time, use :py:meth:`ziaplot.attributes.Animatable.animate_set`.

.. jupyter-execute::
    :emphasize-lines: 3

    with zp.Diagram():
        A = zp.Circle((0,0), .1).strokewidth(3)
        A.svg.animate_set('stroke', 'red', begin='2s', duration='2s')


Changing an Attribute
^^^^^^^^^^^^^^^^^^^^^

An SVG attribute may be animated over time through a range of values using :py:meth:`ziaplot.attributes.Animatable.animate`.
Here, the stroke-width attribute is swept from 2 to 10 every 2 seconds.

.. jupyter-execute::
    :emphasize-lines: 3

    with zp.Diagram():
        A = zp.Circle((0,0), .1).strokewidth(3)
        A.svg.animate('stroke-width', to='10', frm='2', begin='0s', duration='2s', repeat='indefinite')


Showing an element
^^^^^^^^^^^^^^^^^^

To show an element at a given time, use :py:meth:`ziaplot.attributes.Animatable.animate_show`.

.. jupyter-execute::
    :emphasize-lines: 3

    with zp.Diagram():
        A = zp.Circle((0,0), .1).strokewidth(3)
        A.svg.animate_show(begin='3s')


Simulated Drawing
^^^^^^^^^^^^^^^^^

To animate "drawing" an element, use :py:meth:`ziaplot.attributes.Animatable.animate_in`, and to erase an element, :py:meth:`ziaplot.attributes.Animatable.animate_out`.

.. jupyter-execute::
    :emphasize-lines: 3,4

    with zp.Diagram():
        A = zp.Circle((0,0), .1).strokewidth(3)
        A.svg.animate_in(begin='1s', duration='2s')
        A.svg.animate_out(begin='4s', duration='2s')


Annimating sub-elements
^^^^^^^^^^^^^^^^^^^^^^^

Some drawing components are made of multiple SVG elements, such as text or markers. For example a `Point` has the circle and optional text.
Animations will apply to the circle, but the text may also be animated using animation methods on the `svg.text` attribute.

.. jupyter-execute::
    :emphasize-lines: 3,4

    with zp.Diagram():
        A = zp.Point((0,0)).label('A')
        A.svg.animate_set('fill', 'red', begin='2s', duration='2s')
        A.svg.text.animate_set('font-size', '32', begin='3s', duration='2s')

Example
^^^^^^^

This real-world example demonstrates use of animations to illustrate constructing the perpendicular bisector of a line segment.

.. jupyter-execute::

    with zp.Diagram().size(400,300).xrange(-.35, 1).yrange(-.65, .65) as d:
        radius = .7  # Arbitrary compass radius
        line = zp.Segment((0,0), (1,0)).color('black')
        A = zp.Point(line.p1).label('A')
        B = zp.Point(line.p2).label('B')
        arc_a1 = zp.CompassArc(A, radius, 35, 20)
        arc_a2 = zp.CompassArc(A, radius, -55, 20)
        arc_b1 = zp.CompassArc(B, radius, 125, 20)
        arc_b2 = zp.CompassArc(B, radius, -145, 20)
        C = zp.Point.at_intersection(arc_a1, arc_b1).label('C', 'E')
        D = zp.Point.at_intersection(arc_a2, arc_b2).label('D', 'E')
        bisector = zp.Line.from_points(C, D)

        A.svg.animate_set('fill', to='red', begin='0s', duration='2s')
        arc_a1.svg.animate_in(begin='0s', duration='1s')
        arc_a2.svg.animate_in(begin='1s', duration='1s')
        B.svg.animate_set('fill', to='red', begin='2s', duration='2.25s')
        arc_b1.svg.animate_in(begin='2.25s', duration='1s')
        arc_b2.svg.animate_in(begin='3.25s', duration='1s')
        C.svg.animate_show(begin='5s')
        D.svg.animate_show(begin='5s')
        C.svg.text.animate_show(begin='5s')
        D.svg.text.animate_show(begin='5s')
        bisector.svg.animate_in(begin='5.5s', duration='0.5s')
