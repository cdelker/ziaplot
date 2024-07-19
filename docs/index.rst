Ziaplot
=======

Ziaplot is for easy, lightweight, and Pythonic plotting of data and geometric diagrams
in SVG format. It can graph functional relationships, and geometric diagrams,
and discrete (x, y) data.


.. jupyter-execute::
    :hide-code:

    import math
    import random
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)

    random.seed(827243)
    x = zp.linspace(0, 10, 15)
    y = [0.5 * xx + random.random() for xx in x]
    x2 = zp.linspace(0, 10, 25)
    y2 = [.5 + .9 * xx + random.random() for xx in x2]

    with zp.LayoutGrid(columns=2).size(800, 600):
        with zp.AxesPlot():#.size(400, 300):
            zp.PolyLine(x, y).marker('o')
            zp.PolyLine(x2, y2).marker('^')
        with zp.AxesPlot().xrange(-1, 3.5).yrange(0, 4):
            zp.Function(lambda x: math.exp(-x*2), (-.65, 3.5)).endmarkers('<', '>')

        with (zp.AxesGraph()
                .size(400, 300)
                .xrange(-1, 5).yrange(-1, 3)) as g:
            g.style.axis.bgcolor = 'none'
            g.style.axis.gridcolor = 'none'
            g.xticks(zp.ticker[0:5:1], minor=zp.ticker[0:5:.125])
            g.yticks(zp.ticker[0:3:.5], minor=zp.ticker[0:2.75:.125])
            f = zp.Function(lambda x: 0.6*math.cos(4.5*(x-4)+2.1) - 1.2*math.sin(x-4)+.1*x+.2,
                            (.35, 4.2)).color('black')
            zp.Point.at_minimum(f, 1, 2).color('olive').guidex().guidey()
            zp.Point.at_maximum(f, 2, 2.5).color('red').guidex().guidey()
            zp.Point.at_maximum(f, 3, 4).color('blue').guidex().guidey()
        
        with (zp.AxesGraph(style=zp.styles.BlackWhite())
                .equal_aspect()
                .size(300, 300)
                .xticks((-1.2, 1.2)).yticks((-1.2, 1.2))
                .noxticks().noyticks()) as g:
            c = zp.Circle(0, 0, 1)
            r = zp.Radius(c, 65).label('1', 0.6, 'NW').color('blue')
            b = zp.Segment((0, 0), (r.p2[0], 0)).label(r'$\cos(\theta)$', .6, 'S')
            zp.Segment(r.p2, (r.p2[0], 0)).label(r'$\sin(\theta)$', .75, 'E').color('blue')
            zp.Angle(r, b, quad=4).label(r'$\theta$', color='red').color('red')
            zp.Point.on_circle(c, 65)

|

Ziaplot can also create bar and pie charts:

.. jupyter-execute::
    :hide-code:

    p = zp.Pie().fromdict({'a':3, 'b':2, 'c':3, 'd':2, 'e':4, 'f':2}, legend='none')
    p2 = zp.BarChartGrouped(groups=('a', 'b', 'c', 'd'))
    p2 += zp.BarSeries(2, 2, 4, 3)
    p2 += zp.BarSeries(2, 3, 1, 4)
    zp.LayoutH(p2, p).size(800, 300)

|

Ziaplot is written in pure-Python, with no dependencies.
An optional dependency of `cairosvg` can be installed to convert
ziaplot's SVG figures into PNG or other formats.

|

Support
-------

If you appreciate Ziaplot, buy me a coffee to show your support!

.. raw:: html

    <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="cdelker" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>

|


Source code is available on `Github <https://github.com/cdelker/ziaplot>`_.

----




.. toctree::
   :maxdepth: 2
   :caption: Contents:

   start.rst
   axes.rst
   discrete.rst
   geometric.rst
   polar.rst
   charts.rst
   layout.rst
   style.rst
   examples.rst
   gui.rst
   api.rst