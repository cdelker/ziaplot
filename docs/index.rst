Ziaplot
=======

Ziaplot is for easy, lightweight, and Pythonic creation of geometric diagrams, data plots,
and charts in SVG format.
It can graph functional relationships, geometric figures, implicit functions, discrete (x, y) data,
histograms, and pie and bar charts.


.. jupyter-execute::
    :hide-code:

    import math
    import random
    import ziaplot as zp
    zp.css('Canvas{width:300;height:250;}')

    random.seed(827243)
    x = zp.linspace(0, 10, 15)
    y = [0.5 * xx + random.random() for xx in x]
    x2 = zp.linspace(0, 10, 25)
    y2 = [.5 + .9 * xx + random.random() for xx in x2]

    with zp.LayoutGrid(columns=2).size(700, 800):
        with zp.Graph():
            zp.PolyLine(x, y).marker('o')
            zp.PolyLine(x2, y2).marker('^')

        with (zp.GraphQuad().css(zp.CSS_BLACKWHITE+zp.CSS_NOGRID)
                .size(300, 250)
                .xrange(-1, 5).yrange(-1, 3)) as g:
            g.xticks(zp.ticker[0:5:1], minor=zp.ticker[0:5:.125])
            g.yticks(zp.ticker[0:3:.5], minor=zp.ticker[0:2.75:.125])
            f = zp.Function(lambda x: 0.6*math.cos(4.5*(x-4)+2.1) - 1.2*math.sin(x-4)+.1*x+.2,
                            (.35, 4.2)).color('black')
            zp.Point.at_minimum(f, 1, 2).color('olive').guidex().guidey()
            zp.Point.at_maximum(f, 2, 2.5).color('red').guidex().guidey()
            zp.Point.at_maximum(f, 3, 4).color('blue').guidex().guidey()
        
        with (zp.GraphQuad()
                .axesnames('V', 'P')
                .css(zp.CSS_BLACKWHITE)
                .xrange(0, .9).yrange(0, 1)
                .noxticks().noyticks()
                .equal_aspect()):
            p1 = zp.Point(.1, .9).label('1', 'NE')
            p2 = zp.Point(.6, .6).label('2', 'NE')
            p3 = zp.Point(.8, .1).label('3', 'E')
            p4 = zp.Point(.3, .3).label('4', 'SW')
            zp.Curve(p2.point, p1.point).midmarker('>')
            zp.Curve(p3.point, p2.point).midmarker('>')
            zp.Curve(p3.point, p4.point).midmarker('<')
            zp.Curve(p4.point, p1.point).midmarker('<')
            
        with (zp.GraphQuad().css(zp.CSS_BLACKWHITE)
                .equal_aspect()
                .xticks((-1.2, 1.2)).yticks((-1.2, 1.2))
                .noxticks().noyticks()):
            c = zp.Circle(0, 0, 1)
            r = zp.Radius(c, 65).label('1', 0.6, 'NW').color('blue')
            b = zp.Segment((0, 0), (r.p2[0], 0)).label('cos(θ)', .6, 'S')
            zp.Segment(r.p2, (r.p2[0], 0)).label('sin(θ)', .75, 'E').color('blue')
            zp.Angle(r, b, quad=4).label('θ', color='red').color('red')
            zp.Point.on_circle(c, 65)

        zp.Pie.fromdict({'a':3, 'b':2, 'c':3, 'd':2, 'e':4, 'f':2}).legend('none')

        with zp.BarChartGrouped(groups=('a', 'b', 'c', 'd')):
            zp.BarSeries(2, 2, 4, 3)
            zp.BarSeries(2, 3, 1, 4)


|

See the :ref:`Examples` for more, or jump in to the :ref:`Start`.

Ziaplot is written in pure-Python, with no dependencies.
An optional dependency of `cairosvg` can be installed to convert
ziaplot's SVG images into PNG or other formats.


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

   intro.rst
   guide.rst
   graphs.rst
   geometric.rst
   discrete.rst
   charts.rst
   layout.rst
   style.rst
   examples.rst
   gui.rst
   api.rst
