Discrete Data
=============

Discrete data defined as arrays of x values and y values are plotted using
:py:class:`ziaplot.dataplots.polylines.PolyLine` or :py:class:`ziaplot.dataplots.polylines.Scatter`.

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


The most common data series is the :py:class:`ziaplot.dataplots.polylines.PolyLine`.
PolyLines can be drawn with different colors, strokes (dash style), or with markers, using
the chained method interface.

First, make up some data to plot.

.. jupyter-execute::

    x = [i*0.1 for i in range(11)]
    y = [math.exp(xi)-1 for xi in x]
    y2 = [yi*2 for yi in y]
    y3 = [yi*3 for yi in y]
    y4 = [yi*4 for yi in y]

Then, create an `AxesPlot` and add several lines to it.
Notice the color of each series cycles through the default set of theme colors if not specified manually.
Use of the context manager (`with` statement) makes every `PolyLine` created within the manager automatically added to the axis.

.. jupyter-execute::

    with zp.AxesPlot():
        zp.PolyLine(x, y)
        zp.PolyLine(x, y2).marker('round', radius=8)
        zp.PolyLine(x, y3).stroke('dashed')
        zp.PolyLine(x, y4).color('purple').strokewidth(4)

|

Line Options
************

The Color parameter can be an RGB string in the form `#FFFFFF` or a `CSS named color <https://developer.mozilla.org/en-US/docs/Web/CSS/color_value>`_.
Another option is to use the theme colors. Providing color `C1`, `C2`, etc. will use the first, second, etc. color in the theme cycle.


Stroke or dash-style is one of

- `-` (solid line)
- `dotted` (or `:`)
- `dashed` (or `--`)
- `dashdot` (or `-.` or `.-`)
- Any valid SVG `stroke-dasharray <https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray>`_ parameter.


Available markers include:

- `round` (or `o`)
- `square` (or `s`)
- `triangle` (or `^`)
- `triangled` (or `v`)
- `larrow` (or `<`)
- `arrow` (or `>`)
- `+`
- `x`
- `-`
- `|`
- `||`
- `|||`


Markers can also be oriented tangent to the data line, for example to show arrows pointing along the path.
Or different markers on each endpoint can be set using :py:meth:`ziaplot.dataplots.polylines.PolyLine.endmarkers`.

.. jupyter-execute::

    t = zp.linspace(-10, 10, 30)
    tsq = [ti**2 for ti in t]
    tsq2 = [tsqi+20 for tsqi in tsq]

    with zp.AxesPlot():
        zp.PolyLine(t, tsq).marker('arrow', orient=True)
        zp.PolyLine(t, tsq2).endmarkers(start='square', end='arrow')

|

Fading Colors
*************

Sometimes it is useful for different lines to fade between two colors.
This can be accomplishsed using the :py:meth:`ziaplot.axes.baseplot.BasePlot.colorfade` method of the axis object.
Color fading requires hex string colors.

.. jupyter-execute::

    xf = zp.linspace(0, 10, 10)
    with zp.AxesPlot() as p:
        p.colorfade('#0000FF', '#FF0000')
        for i in range(10):
            yf = [xi*(i+1) for xi in xf]
            zp.PolyLine(xf, yf)

|

Scatter Plots
---------------

In addition to `PolyLine`, a few other data series can be plotted.
:py:class:`ziaplot.dataplots.polylines.Scatter` is just a subclass of `PolyLine` that automatically sets the line color to 'none'
and adds a round marker.
:py:class:`ziaplot.geo.line.HLine` and :py:class:`ziaplot.geo.line.VLine` series are used to draw a line across the entire axis at a given data value.


.. jupyter-execute::

    with zp.AxesPlot():
        zp.Scatter(x, y)
        zp.HLine(.5).stroke('dotted')
        zp.VLine(.75).stroke('dashed')


Error-Bar Plots
---------------

The :py:class:`ziaplot.dataplots.polylines.ErrorBar` series draws lines with added x or y errorbars.
The :py:meth:`ziaplot.dataplots.polylines.ErrorBar.yerrmarker` and
:py:meth:`ziaplot.dataplots.polylines.ErrorBar.xerrmarker` methods control the errorbar end markers.

.. jupyter-execute::

    zp.ErrorBar(x, y, yerr=y2)

.. jupyter-execute::

    zp.ErrorBar(x, y, yerr=y2).yerrmarker('square', length=5, width=1)


And :py:class:`ziaplot.dataplots.polylines.LineFill` works like an `ErrorBar` but draws a filled region:

.. jupyter-execute::

    zp.LineFill(x, ymin=y, ymax=y2).color('black').fill('blue', alpha=.3)

|

Annotations
-----------

Calling :py:meth:`ziaplot.series.Series.name` on a series adds the series line to a legend on the axes, which is displayed
either to the left or right of the axes.
Plain text labels can be added at any data point using the :py:class:`ziaplot.dataplots.text.Text` series.
:py:class:`ziaplot.dataplots.polylines.Arrow` series are Lines with an arrowhead on one end, and optional text on the other.

.. jupyter-execute::

    with zp.AxesPlot(title='Title',
                   xname='Independent Variable',
                   yname='Dependent Variable'):
        zp.PolyLine(x, y).name('Line #1')
        zp.PolyLine(x, y2).name('Line #2')
        zp.Text(0.2, 2, 'Text', halign='center')
        zp.Arrow((.70, 2.3), (.6, 3)).label('Arrow', 'N').color('black')

If `ziamath <https://ziamath.readthedocs.io>`_ is installed, math expressions can be
drawn in any label. The expressions are entered in Latex style delimited by $..$.

.. jupyter-execute::

    zp.AxesPlot(title=r'Math: $\sqrt{a^2 + b^2}$',
              xname=r'Frequency, $\frac{1}{s}$',
              yname=r'Acceleration, $m/s^2$')

|


Histogram Series
----------------

While the :py:class:`ziaplot.dataplots.bars.Bars` series can be added directly to make bar plots, it is often easier to create
histogram bars using the :py:class:`ziaplot.dataplots.bars.Histogram` series, or use a :py:class:`ziaplot.charts.bar.BarChart` axis for qualitative x-value bar charts.
Histograms have parameters to specify the total number of bins, or a specific range of bin locations.
The data can also be weighted, or plotted as a probability density instead of data count.

.. jupyter-execute::

    import random
    v = [random.normalvariate(100, 5) for k in range(1000)]
    zp.Histogram(v)

Horizontal histograms may be created using :py:class:`ziaplot.dataplots.bars.HistogramHoriz`.

|

Contour Plots
-------------

Countour plots are made with 2-dimensional x, y and z data.
:py:class:`ziaplot.dataplots.contour.Contour` creates a contour plot.
It has parameters for the number of levels (or list of level values) and position
of a colorbar. The color palette is defined in the style `style.series.colorbar.colors`.


.. jupyter-execute::

    delta = .1
    x = zp.util.zrange(-2., 3., delta)
    y = zp.util.zrange(-2., 3., delta)
    z = [[2 * (math.exp(-xx**2 - yy**2) - math.exp(-(xx-1)**2 - (yy-1)**2)) for xx in x] for yy in y]

    with zp.AxesPlot().size(400,300):
        p = zp.Contour(x, y, z, levels=12, colorbar='right')


Note the data for the above plot may be genereated more efficiently using Numpy,
but Numpy is not a required dependency:

.. code-block:: python

    delta = 0.1
    x = np.arange(-2.0, 3.0, delta)
    y = np.arange(-2.0, 3.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X**2 - Y**2)
    Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
    Z = (Z1 - Z2) * 2

    with zp.AxesPlot().size(400,300):
        p = zp.Contour(x, y, Z, levels=12, colorbar='right')
