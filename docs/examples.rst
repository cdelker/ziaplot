Examples
========

.. jupyter-execute::
    :hide-code:

    import math
    import random
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)
    


Functional Plots
----------------

.. jupyter-execute::

    with (zp.AxesGraph()
          .xticks(zp.ticker[0:1:.1])
          .yticks(zp.ticker[0:1:.1])
          .size(400, 400)) as g:
        f1 = zp.Function(lambda x: x*math.exp(x-1), (0,1)).color('red')
        f2 = zp.Line.from_slopeintercept(1, 0).color('teal')
        zp.IntegralFill(f1, f2, 0, 1).color('gray')
        zp.Point.at(f1, .8).guidex().guidey()
        zp.Point.at(f1, .9).guidex().guidey()
        zp.Point.at(f1, .7).guidex().guidey()

|

.. jupyter-execute::

    with (zp.AxesGraph(style=zp.styles.BlackWhite())
            .xrange(-1, 5).yrange(-1, 3)) as g:
        f = zp.Function(
            lambda x: 0.6*math.cos(4.5*(x-4)+2.1) - 1.2*math.sin(x-4)+.1*x+.2,
            (.35, 4.2)).color('black')
        zp.Point.at_minimum(f, 1, 2).color('olive').guidex().guidey()
        zp.Point.at_maximum(f, 2, 2.5).color('red').guidex().guidey()
        zp.Point.at_maximum(f, 3, 4).color('blue').guidex().guidey()

|

.. jupyter-execute::

    with (zp.AxesGraph()
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
        zp.IntegralFill(f, x1=8, x2=9.5).color('red').alpha(.2)
        zp.TangentSegment.to(f, 5).trim(3, 7).color('plum')
        zp.Point.at(f, 5).color('yellow')

|

.. jupyter-execute::

    with zp.AxesGraph().equal_aspect():
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

    with zp.AxesPlot(
            title='Monthly Average Temperature, Albuquerque NM, USA',
            yname='Degrees Fahrenheit').xticks(range(12), months).size(600,300):
        zp.LineFill(range(12), highs, lows)
        zp.PolyLine(range(12), means).color('C2')

|

.. jupyter-execute::

    x = [random.normalvariate(10, 1) for _ in range(500)]
    y = [xx/2 + random.normalvariate(0, .5) for xx in x]
    x2 = [random.normalvariate(11, .75) for _ in range(500)]
    y2 = [xx/2 + random.normalvariate(1.5, .5) for xx in x2]

    with zp.LayoutGrid(columns=2, row_heights='1fr 2fr', column_widths='3fr 1fr'):
        with zp.AxesPlot().xrange(6, 14).noxticks().noyticks() as plot1:
            zp.Histogram(x2, bins=40).color('#ba0c2f88')
            zp.Histogram(x, bins=40).color('#007a8688')

        zp.LayoutEmpty()
        
        with zp.AxesPlot().match_x(plot1) as scatter:
            zp.Scatter(x2, y2).marker('o', 4).color('#ba0c2f88')
            zp.Scatter(x, y).marker('o', 4).color('#007a8688')

        with zp.AxesPlot().match_y(scatter).noyticks().noxticks():
            zp.HistogramHoriz(y2, bins=30).color('#ba0c2f88')
            zp.HistogramHoriz(y, bins=30).color('#007a8688')


|

Geometric
---------

.. jupyter-execute::

    with (zp.AxesBlank(style=zp.styles.BlackWhite())
          .xrange(0, 1).yrange(0, math.sqrt(3)/2)
          .size(400, 400*math.sqrt(3)/2)) as g:
        g.style.series.angle.radius = 30
        g.style.series.angle.text_radius = 35
        g.style.series.angle.text.size = 14
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

    with zp.AxesBlank(style=zp.styles.BlackWhite()).xrange(0, 1).yrange(0, .6).size(300,200):
        c = zp.Segment((0, 0), (1, 0)).label('c', .5, 'S', color='blue')
        a = zp.Segment((1, 0), (.7, .6)).label('a', .5, 'E', color='blue')
        b = zp.Segment((.7, .6), (0, 0)).label('b', .5, 'NW', color='blue')
        zp.Angle(b, c, quad=4).color('red').label(r'$\alpha$', color='red')
        zp.Angle(a, c, quad=2).color('red').label(r'$\beta$', color='red')
        zp.Angle(a, b, quad=3).color('red').label(r'$\gamma$', color='red')

|

.. jupyter-execute::

    with zp.AxesBlank(style=zp.styles.BlackWhite()).xrange(-1, 1.1).yrange(-1., 1):
        c = zp.Circle(0, 0, 1)
        zp.Diameter(c, -15).color('maroon').label('Diameter', .2, 'N', rotate=True, color='maroon')
        zp.Radius(c, 40).color('teal').label('Radius', .5, rotate=True, color='teal')  
        zp.Chord(c, 160, 80).color('steelblue').label('Chord', .5, rotate=True, color='steelblue')
        zp.Secant(c, 180, 280).color('olivedrab').label('Secant', .25, rotate=True, color='olivedrab')
        zp.Tangent.to_circle(c, -15).color('darkviolet').label('Tangent', .4, 'SE', rotate=True, color='darkviolet')
        zp.Point(0, 0)

|

.. jupyter-execute::

    with (zp.AxesGraph(style=zp.styles.BlackWhite())
            .size(500, 500)
            .xrange(-2, 2).xticks(zp.ticker[-2:2:1], minor=zp.ticker[-2:2:.1])
            .yrange(-2, 2).yticks(zp.ticker[-2:2:1], minor=zp.ticker[-2:2:.1])):
        theta = 40
        circ = zp.Circle(0, 0, 1)
        xaxis = zp.HLine(0)
        x1 = zp.VLine(1).stroke('--').label('x=1', .25, 'E')
        y1 = zp.HLine(1).stroke('--').label('y=1', .25, 'N')
        hyp = zp.Line((0,0), math.tan(math.radians(theta)))
        tan = zp.Tangent.to_circle(circ, theta)
        # Find point locations, but draw them later so they stay on top
        E = zp.x_intercept(tan)
        D = zp.y_intercept(tan)
        C = zp.line_intersection(y1, hyp)
        B = zp.line_intersection(x1, hyp)
        A = zp.line_intersection(hyp, tan)
        sec = zp.Segment((0, 0), E).strokewidth(4).color('purple').label(r'$\sec\theta$', .5, 'S', color='purple')
        csc = zp.Segment((0, 0), D).strokewidth(4).color('orange').label(r'$\csc\theta$', .5, 'W', color='orange')
        cot = zp.Segment.horizontal(C).strokewidth(4).color('green').label(r'$\cot\theta$', .4, 'N', color='green')
        tan = zp.Segment.vertical(B).strokewidth(4).color('blue').label(r'$\tan\theta$', .6, 'E', color='blue')
        cos = zp.Segment.horizontal(A).strokewidth(4).color('lime').label(r'$\cos\theta$', .6, 'N', color='lime')
        sin = zp.Segment.vertical(A).strokewidth(4).color('cyan').label(r'$\sin\theta$', .6, 'W', color='cyan')
        zp.Angle.to_zero(hyp, quad=4).label(r'$\theta$')
        zp.Point(0, 0).label('O', 'SE').color('red')
        zp.Point(*A).label('A', 'E').color('red')
        zp.Point(*B).label('B', 'W').color('red')
        zp.Point(*C).label('C', 'N').color('red')
        zp.Point(*D).label('D', 'E').color('red')
        zp.Point(*E).label('E', 'SW').color('red')

(`Based on Unit Circle from Wikipedia <https://en.wikipedia.org/wiki/Trigonometric_functions#/media/File:Unit_Circle_Definitions_of_Six_Trigonometric_Functions.svg>`_)


|

.. jupyter-execute::

    with (zp.AxesGraph(xname='Volume', yname='Pressure',
                       style=zp.styles.BlackWhite())
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

    with zp.AxesGraph().equal_aspect() as g:
        g.colorfade('#ed8b00', '#007a86')
        for c in zp.linspace(-3, 3, 8):
            zp.Implicit(lambda x, y: .25*(5*x**2 + y**2 -4)*(x**2+5*y**2 - 4) - c,
                        xlim=(-3, 3), ylim=(-3, 3))

|

.. jupyter-execute::

    delta = .1
    x = zp.util.zrange(-2, 3, delta)
    y = zp.util.zrange(-2, 3, delta)
    z = [[2 * (math.sin(-xx**2 - yy**2) - math.cos(-(xx-1)**2 - (yy-1)**2)) for xx in x] for yy in y]
    with zp.AxesPlot().size(400,300):
        p = zp.Contour(x, y, z, levels=12, colorbar='right')
        p.style.colorbar.colors = zp.style.colors.ColorFade('#DB5A42', '#9D69A3', '#0F4C5C')