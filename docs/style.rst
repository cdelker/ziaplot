.. _styles:

Plot Style
==========


.. jupyter-execute::
    :hide-code:

    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


Plotting style is set using a :py:class:`ziaplot.style.styletypes.Style` dataclass.
Individual drawing axes take a `style` argument to specify the style of the axis
and any data series it contains.
To customize the style, typically start with the base `Style` and modify its attributes:


.. jupyter-execute::

    sty = zp.styles.Style()
    sty.axis.bgcolor = '#d9f2fa'
    sty.canvasw = 300
    sty.canvash = 300
    zp.AxesPlot(style=sty)

To use the style for all plots, set the default style using :py:meth:`ziaplot.style.styles.setdefault`:

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
        p2 = zp.AxesGraph()
        p2 += zp.Function(lambda x: x**2).endmarkers()
        p2 += zp.Function(lambda x: x**3/2).endmarkers()
        p2 += zp.Function(lambda x: -x**4/20).endmarkers()

        x = zp.linspace(10, 20, 10)
        y = [math.exp(xi/10) for xi in x]
        p3 = zp.AxesPlot()
        p3 += zp.PolyLine(x, y).marker('round')
        p3 += zp.Scatter(x, [yi*2 for yi in y]).marker('square')
        p3 += zp.PolyLine(x, [yi*4 for yi in y]).marker('arrow', orient=True)
        p3 += zp.PolyLine(x, [yi*3 for yi in y]).stroke('--')

        p4 = zp.BarChartGrouped(groups=('a', 'b', 'c', 'd'))
        p4 += zp.BarSeries(2, 2, 4, 3)
        p4 += zp.BarSeries(2, 3, 1, 4)

        fig = zp.LayoutGrid(p3, p4, p2, p, columns=2)
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


Black and White
***************

.. code-block:: python

    zp.styles.setdefault(zp.styles.BlackWhite)

.. jupyter-execute::
    :hide-code:

    zp.styles.setdefault(zp.styles.BlackWhite)
    teststyle()


Style Dataclass
---------------


The style dictionary is a set of nested dataclasses.


.. autoclass:: ziaplot.style.styletypes.Style
    :members:

.. autoclass:: ziaplot.style.styletypes.SeriesStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.LineStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.MarkerStyle
    :members:
    
.. autoclass:: ziaplot.style.styletypes.TextStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.ErrorBarStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.AxisStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.TickStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.LegendStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.PolarStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.PieStyle
    :members:

.. autoclass:: ziaplot.style.styletypes.SmithStyle
    :members:

.. autoclass:: ziaplot.style.colors.ColorCycle
    :members:
