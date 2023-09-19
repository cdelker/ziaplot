Ziaplot
=======

Ziaplot is for easy, lightweight, and Pythonic plotting of data in SVG format.

.. jupyter-execute::
    :hide-code:

    import math
    import ziaplot as zp
    def teststyle():
        p = zp.Pie().wedges(3,2,3,2,4,2).names('a', 'b', 'c', 'd', 'e', 'f')
        p2 = zp.XyGraph()
        p2 += zp.Function(lambda x: x**2).endmarkers()
        p2 += zp.Function(lambda x: x**3/2).endmarkers()
        p2 += zp.Function(lambda x: -x**4/20).endmarkers()

        x = zp.linspace(10, 20, 10)
        y = [math.exp(xi/10) for xi in x]
        p3 = zp.XyPlot()
        p3 += zp.Line(x, y).marker('round')
        p3 += zp.Xy(x, [yi*2 for yi in y]).marker('square')
        p3 += zp.Line(x, [yi*4 for yi in y]).marker('arrow', orient=True)
        p3 += zp.Line(x, [yi*3 for yi in y]).stroke('--')

        p4 = zp.BarChartGrouped(('a', 'b', 'c', 'd'))
        p4.bar_series((2, 2, 4, 3))
        p4.bar_series((2, 3, 1, 4))

        l1 = zp.Hlayout(p3, p4)
        l2 = zp.Hlayout(p2, p)
        fig = zp.Vlayout(l1, l2)
        return fig
    teststyle()


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


Source code is available on `Bitbucket <https://bitbucket.org/cdelker/ziaplot>`_.

----




.. toctree::
   :maxdepth: 2
   :caption: Contents:

   start.rst
   xyplot.rst
   polar.rst
   charts.rst
   layout.rst
   style.rst
   gui.rst
   api.rst