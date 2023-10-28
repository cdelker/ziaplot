.. _styles:

Plot Style
==========


.. jupyter-execute::
    :hide-code:

    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


Plotting style is set using a :py:class:`ziaplot.styletypes.Style` dataclass.
Individual drawing axes take a `style` argument to specify the style of the axis
and any data series it contains.
To customize the style, typically start with the base `Style` and modify its attributes:


.. jupyter-execute::

    sty = zp.styles.Style()
    sty.axis.bgcolor = '#d9f2fa'
    sty.canvasw = 300
    sty.canvash = 300
    zp.XyPlot(style=sty)

To use the style for all plots, set the default style using :py:meth:`ziaplot.styles.setdefault`:

.. code-block:: python

    zp.styles.setdefault(sty)

|

Themes
------

A number of predefined styles (or themes) are built-in to Ziaplot.
For example, to enable the "Taffy" theme for all plots, use:

.. code-block:: python

    zp.styles.setdefault(zp.styles.Taffy)


.. jupyter-execute::
    :hide-code:

    def teststyle():
        p = zp.Pie().fromdict({'a':3, 'b':2, 'c':3, 'd':2, 'e':4, 'f':2}, legend='none')
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

        p4 = zp.BarChartGrouped(groups=('a', 'b', 'c', 'd'))
        p4 += zp.BarSeries(2, 2, 4, 3)
        p4 += zp.BarSeries(2, 3, 1, 4)

        l1 = zp.Hlayout(p3, p4)
        l2 = zp.Hlayout(p2, p)
        fig = zp.Vlayout(l1, l2)
        return fig

|

Default
*******

.. code-block:: python

    zp.styles.setdefault(zp.styles.Default)


.. jupyter-execute::
    :hide-code:
    
    teststyle()

|

Taffy
*****

.. code-block:: python

    zp.styles.setdefault(zp.styles.Taffy)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.Taffy)
    teststyle()

|

Pastel
******

.. code-block:: python

    zp.styles.setdefault(zp.styles.Pastel)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.Pastel)
    teststyle()

|

Bold
*****

.. code-block:: python

    zp.styles.setdefault(zp.styles.Bold)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.Bold)
    teststyle()

|

Dark
*****

.. code-block:: python

    zp.styles.setdefault(zp.styles.Dark)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.Dark)
    teststyle()

|

Dark Taffy
**********

.. code-block:: python

    zp.styles.setdefault(zp.styles.DarkTaffy)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.DarkTaffy)
    teststyle()

|

Dark Bold
*********

.. code-block:: python

    zp.styles.setdefault(zp.styles.DarkBold)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.DarkBold)
    teststyle()

|

Style Dataclass
---------------


The style dictionary is a set of nested dataclasses.


.. autoclass:: ziaplot.styletypes.Style
    :members:

.. autoclass:: ziaplot.styletypes.SeriesStyle
    :members:

.. autoclass:: ziaplot.styletypes.LineStyle
    :members:

.. autoclass:: ziaplot.styletypes.MarkerStyle
    :members:
    
.. autoclass:: ziaplot.styletypes.TextStyle
    :members:

.. autoclass:: ziaplot.styletypes.ErrorBarStyle
    :members:

.. autoclass:: ziaplot.styletypes.AxisStyle
    :members:

.. autoclass:: ziaplot.styletypes.TickStyle
    :members:

.. autoclass:: ziaplot.styletypes.LegendStyle
    :members:

.. autoclass:: ziaplot.styletypes.PolarStyle
    :members:

.. autoclass:: ziaplot.styletypes.PieStyle
    :members:

.. autoclass:: ziaplot.styletypes.SmithStyle
    :members:

.. autoclass:: ziaplot.colors.ColorCycle
    :members:
