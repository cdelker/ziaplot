.. _Examples:

Examples
========

.. jupyter-execute::
    :hide-code:

    import math
    import random
    import ziaplot as zp
    zp.css('Canvas{width:400;height:300;}')
    


Functional Plots
----------------

.. jupyter-execute::

    with (zp.GraphQuad()
          .xticks(zp.ticker[0:1:.1])
          .yticks(zp.ticker[0:1:.1])
          .size(400, 400)) as g:
        f1 = zp.Function(lambda x: x*math.exp(x-1), (0,1)).color('red')
        f2 = zp.Line.from_slopeintercept(1, 0).color('teal')
        zp.IntegralFill(f1, f2, 0, 1).color('gray 30%')
        zp.Point.at(f1, .8).guidex().guidey()
        zp.Point.at(f1, .9).guidex().guidey()
        zp.Point.at(f1, .7).guidex().guidey()

|

.. jupyter-execute::

    with (zp.GraphQuad()
            .css(zp.CSS_BLACKWHITE+zp.CSS_NOGRID)
            .xrange(-1, 5).yrange(-1, 3)) as g:
        f = zp.Function(
            lambda x: 0.6*math.cos(4.5*(x-4)+2.1) - 1.2*math.sin(x-4)+.1*x+.2,
            (.35, 4.2)).color('black')
        zp.Point.at_minimum(f, 1, 2).color('olive').guidex().guidey()
        zp.Point.at_maximum(f, 2, 2.5).color('red').guidex().guidey()
        zp.Point.at_maximum(f, 3, 4).color('blue').guidex().guidey()

|

.. jupyter-execute::

    with (zp.GraphQuad()
          .xrange(0, 10)
          .yrange(0, 16)):
        f = zp.Function(lambda x: -(x-6)**2 + 12).color('teal')
        zp.Secant.to_function(f, 4, 8).color('orange')
        zp.Secant.to_function(f, 3, 6).color('red')
        m = zp.Point.at(f, 6).label('M', 'NW').color('black')
        d = zp.Point.at(f, 4).label('D', 'NW').color('black')
        e = zp.Point.at(f, 8).label('E', 'NE').color('black')
        l = zp.Point.at(f, 3).label('L', 'SE').color('black')
        zp.Segment((8, f.y(8)), (8, 0)).color('blue')
        zp.IntegralFill(f, x1=8, x2=9.5).color('red 20%')
        zp.TangentSegment.to(f, 5).trim(3, 7).color('plum')
        zp.Point.at(f, 5).color('yellow')

|

.. jupyter-execute::

    with zp.GraphQuad().equal_aspect():
        zp.Implicit(
            lambda x, y: x**2 + (5*y/4 - math.sqrt(abs(x)))**2 -1,
            xlim=(-1.5, 1.5),
            ylim=(-1.0, 1.5))

|


Discrete Data
-------------

.. jupyter-execute::

    highs = [49, 55, 63, 71, 81, 91, 92, 89, 83, 71, 58, 48]
    lows = [27, 30, 36, 43, 53, 62, 67, 65, 59, 46, 35, 27]
    means = [38, 42, 50, 57, 67, 77, 79, 77, 71, 59, 46, 37]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    with (zp.Graph()
            .title('Monthly Average Temperature, Albuquerque NM, USA')
            .axesnames(y='Degrees Fahrenheit').xticks(range(12), months)
            .size(600,300)):
        zp.LineFill(range(12), highs, lows)
        zp.PolyLine(range(12), means).color('C2')

|

.. jupyter-execute::

    x = [random.normalvariate(10, 1) for _ in range(500)]
    y = [xx/2 + random.normalvariate(0, .5) for xx in x]
    x2 = [random.normalvariate(11, .75) for _ in range(500)]
    y2 = [xx/2 + random.normalvariate(1.5, .5) for xx in x2]

    with zp.LayoutGrid(columns=2, column_gap=0, row_gap=0,
                    row_heights='1fr 2fr', column_widths='3fr 1fr'):
        with zp.Graph().xrange(6, 14).noxticks().noyticks() as graph1:
            zp.Histogram(x2, bins=40).color('#ba0c2f88')
            zp.Histogram(x, bins=40).color('#007a8688')

        zp.LayoutEmpty()

        with zp.Graph().match_x(graph1) as scatter:
            zp.Scatter(x2, y2).marker('o', 4).color('#ba0c2f88')
            zp.Scatter(x, y).marker('o', 4).color('#007a8688')

        with zp.Graph().match_y(scatter).noyticks().noxticks():
            zp.HistogramHoriz(y2, bins=30).color('#ba0c2f88')
            zp.HistogramHoriz(y, bins=30).color('#007a8688')

|

Geometric
---------

.. jupyter-execute::

    CSS = '''
        Angle {
            radius: 30;
            font_size: 14;
        }
    '''
    with (zp.Diagram()
          .css(zp.CSS_BLACKWHITE + CSS)
          .xrange(0, 1).yrange(0, math.sqrt(3)/2)
          .size(400, 400*math.sqrt(3)/2)) as g:
        a = zp.Segment((0, 0), (1, 0))
        b = zp.Segment((1, 0), (.5, math.sqrt(3)/2))
        c = zp.Segment((.5, math.sqrt(3)/2), (0, 0))
        a.midmarker('|')
        b.midmarker('|')
        c.midmarker('|')
        zp.Angle(a, b, quad=2).label('60°')
        zp.Angle(b, c, quad=3).label('60°')
        zp.Angle(a, c, quad=4).label('60°')

|

.. jupyter-execute::

    with zp.Diagram().css(zp.CSS_BLACKWHITE).xrange(0, 1).yrange(0, .6).size(300,200):
        c = zp.Segment((0, 0), (1, 0)).label('c', .5, 'S', color='blue')
        a = zp.Segment((1, 0), (.7, .6)).label('a', .5, 'E', color='blue')
        b = zp.Segment((.7, .6), (0, 0)).label('b', .5, 'NW', color='blue')
        zp.Angle(b, c, quad=4).color('red').label(r'$\alpha$', color='red')
        zp.Angle(a, c, quad=2).color('red').label(r'$\beta$', color='red')
        zp.Angle(a, b, quad=3).color('red').label(r'$\gamma$', color='red')

|

.. jupyter-execute::

    with zp.Diagram().css(zp.CSS_BLACKWHITE).xrange(-1, 1.1).yrange(-1., 1):
        c = zp.Circle(0, 0, 1)
        zp.Diameter(c, -15).color('maroon').label('Diameter', .2, 'N', rotate=True, color='maroon')
        zp.Radius(c, 40).color('teal').label('Radius', .5, rotate=True, color='teal')  
        zp.Chord(c, 160, 80).color('steelblue').label('Chord', .5, rotate=True, color='steelblue')
        zp.Secant(c, 180, 280).color('olivedrab').label('Secant', .25, rotate=True, color='olivedrab')
        zp.Tangent.to_circle(c, -15).color('darkviolet').label('Tangent', .4, 'SE', rotate=True, color='darkviolet')
        zp.Point(0, 0)

|

.. jupyter-execute::

    with (zp.GraphQuad()
            .css(zp.CSS_BLACKWHITE+zp.CSS_NOGRID)
            .size(500, 500)
            .xrange(-2, 2).xticks(zp.ticker[-2:2:1], minor=zp.ticker[-2:2:.1])
            .yrange(-2, 2).yticks(zp.ticker[-2:2:1], minor=zp.ticker[-2:2:.1])) as d:
        theta = 40
        circ = zp.Circle(0, 0, 1)
        xaxis = zp.HLine(0)
        x1 = zp.VLine(1).stroke('--').label('x=1', .25, 'E')
        y1 = zp.HLine(1).stroke('--').label('y=1', .25, 'N')
        hyp = zp.Line((0,0), math.tan(math.radians(theta)))
        tan = zp.Tangent.to_circle(circ, theta)
        
        zp.Point(0, 0).label('O', 'SE').color('red')
        A = zp.Point.at_intersection(hyp, tan).label('A', 'E').color('red')
        B = zp.Point.at_intersection(x1, hyp).label('B', 'W').color('red')
        C = zp.Point.at_intersection(y1, hyp).label('C', 'N').color('red')
        D = zp.Point.at(tan, x=0).label('D', 'E').color('red')
        E = zp.Point.at_y(tan, y=0).label('E', 'SW').color('red')

        cot = zp.Segment.horizontal(C.point).strokewidth(4).color('green').label('cot θ', .4, 'N', color='green')
        sin = zp.Segment.vertical(A.point).strokewidth(4).color('cyan').label('sin θ', .6, 'W', color='cyan')
        sec = zp.Segment((0, 0), E.point).strokewidth(4).color('purple').label('sec θ', .5, 'S', color='purple')
        csc = zp.Segment((0, 0), D.point).strokewidth(4).color('orange').label('csc θ', .5, 'W', color='orange')
        tan = zp.Segment.vertical(B.point).strokewidth(4).color('blue').label('tan θ', .6, 'E', color='blue')
        cos = zp.Segment.horizontal(A.point).strokewidth(4).color('lime').label('cos θ', .6, 'N', color='lime')
        zp.Angle.to_zero(hyp, quad=4).label('θ')

(`Based on Unit Circle from Wikipedia <https://en.wikipedia.org/wiki/Trigonometric_functions#/media/File:Unit_Circle_Definitions_of_Six_Trigonometric_Functions.svg>`_)


|

.. jupyter-execute::

    with zp.Diagram().css(zp.CSS_BLACKWHITE):
        circle = zp.Circle(0, 0, 1)
        theta = 56  # Angle for point B
        zp.Diameter(circle)
        side1 = zp.Chord(circle, 180, theta)
        side2 = zp.Chord(circle, 0, theta)
        a = zp.Point.on_circle(circle, 180).label('A', 'W')
        c = zp.Point.on_circle(circle, 0).label('C', 'E')
        b = zp.Point.on_circle(circle, theta).label('B', 'NE')
        zp.Point(0, 0).label('O', 'S')
        zp.Angle(side1, side2, quad=3)

    # Test Thales's Theorem!
    math.isclose(zp.angle_of_intersection(side1, side2), 90)

|

.. jupyter-execute::

    with (zp.GraphQuad()
            .axesnames('Volume', 'Pressure')
            .css(zp.CSS_BLACKWHITE)
            .xrange(0, 1).yrange(0, 1)
            .noxticks().noyticks()
            .equal_aspect()):
        p1 = zp.Point(.1, .9).label('1', 'NW')
        p2 = zp.Point(.6, .6).label('2', 'NE')
        p3 = zp.Point(.8, .1).label('3', 'E')
        p4 = zp.Point(.3, .3).label('4', 'SW')
        zp.Curve(p2.point, p1.point).midmarker('>')
        zp.Curve(p3.point, p2.point).midmarker('>')
        zp.Curve(p3.point, p4.point).midmarker('<')
        zp.Curve(p4.point, p1.point).midmarker('<')

|

Contour Plots
-------------

.. jupyter-execute::

    with zp.GraphQuad().equal_aspect():
        for c in zp.linspace(-3, 3, 8):
            zp.Implicit(lambda x, y: .25*(5*x**2 + y**2 -4)*(x**2+5*y**2 - 4) - c,
                        xlim=(-3, 3), ylim=(-3, 3))

|

.. jupyter-execute::

    CSS = '''
        Contour {
            colorcycle: #4361EE, #F72585;
        }
    '''
    delta = .1
    x = zp.util.zrange(-2, 3, delta)
    y = zp.util.zrange(-2, 3, delta)
    z = [[2 * (math.sin(-xx**2 - yy**2) - math.cos(-(xx-1)**2 - (yy-1)**2)) for xx in x] for yy in y]
    with zp.Graph().css(CSS).size(400,300):
        p = zp.Contour(x, y, z, levels=12)
