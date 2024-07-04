Cartesian Plots
===============

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


Data in Cartesian coordinate plots are defined by x and y quantities.
Ziaplot has two types of Cartesian axes.
:py:class:`ziaplot.axes.XyPlot` draws the x and y axes lines along the bottom and left sides of the frame.
The (0, 0) origin can be anywhere, even outside the plot area.
:py:class:`ziaplot.axes.XyGraph` always draws the x and y axis lines through the (0, 0) origin and includes arrowheads at the end of the axis lines.
`XyPlot` is commonly used to plot discrete x and y values, where `XyGraph` is used to plot functions.

.. jupyter-execute::
    :hide-code:

    p1 = zp.XyPlot(title='XyPlot')
    p2 = zp.XyGraph(title='XyGraph')
    zp.Hlayout(p1, p2, width=700, height=300, sep=-20)

In terms of adding and displaying data series, the two are identical.

|

Basic Plotting
--------------

The most common data series is the :py:class:`ziaplot.dataplots.polylines.PolyLine`.
Typically, an axis will be created first, then one or more PolyLines added to it.
PolyLines can be drawn with different colors, strokes (dash style), or with markers, using
the chained method interface.

First, make up some data to plot.

.. jupyter-execute::

    x = [i*0.1 for i in range(11)]
    y = [math.exp(xi)-1 for xi in x]
    y2 = [yi*2 for yi in y]
    y3 = [yi*3 for yi in y]
    y4 = [yi*4 for yi in y]

Then, create an XyPlot and add several lines to it.
Notice the color of each series cycles through the default set of theme colors if not specified manually.
Use of the context manager (`with` statement) makes every PolyLine created within the manager automatically added to the axis.

.. jupyter-execute::

    with zp.XyPlot():
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


Markers can also be oriented tangent to the data line, for example to show arrows pointing along the path. Or different markers on each endpoint can be set using :py:meth:`ziaplot.dataseries.Line.endmarkers`.

.. jupyter-execute::

    t = zp.linspace(-10, 10, 30)
    tsq = [ti**2 for ti in t]
    tsq2 = [tsqi+20 for tsqi in tsq]

    with zp.XyPlot():
        zp.PolyLine(t, tsq).marker('arrow', orient=True)
        zp.PolyLine(t, tsq2).endmarkers(start='square', end='arrow')

|

Fading Colors
*************

Sometimes it is useful for different lines to fade between two colors.
This can be accomplishsed using the :py:meth:`ziaplot.axes.BasePlot.colorfade` method of the axis object.
Color fading requires hex string colors.

.. jupyter-execute::

    xf = zp.linspace(0, 10, 10)
    with zp.XyPlot() as p:
        p.colorfade('#0000FF', '#FF0000')
        for i in range(10):
            yf = [xi*(i+1) for xi in xf]
            zp.PolyLine(xf, yf)

|

X-Y Data Series
---------------

In addition to :py:class:`ziaplot.dataseries.Line`, a few other data series can be plotted.
:py:class:`ziaplot.dataseries.Xy` is just a subclass of `Line` that automatically sets the line color to 'none'
and adds a round marker.
:py:class:`ziaplot.dataseries.HLine` and :py:class:`ziaplot.dataseries.VLine` series are used to draw a line across the entire axis at a given data value.


.. jupyter-execute::

    with zp.XyPlot():
        zp.Xy(x, y)
        zp.HLine(.5).stroke('dotted')
        zp.VLine(.75).stroke('dashed')

The :py:class:`ziaplot.dataseries.ErrorBar` series draws lines with added x or y errorbars.
The :py:meth:`ziaplot.dataseries.ErrorBar.yerrmarker` and :py:meth:`ziaplot.dataseries.ErrorBar.xerrmarker` methods control the errorbar end markers.

.. jupyter-execute::

    zp.ErrorBar(x, y, yerr=y2)

.. jupyter-execute::

    zp.ErrorBar(x, y, yerr=y2).yerrmarker('square', length=5, width=1)


And :py:class:`ziaplot.dataseries.LineFill` works like an errorbar but draws a filled region:

.. jupyter-execute::

    zp.LineFill(x, ymin=y, ymax=y2).color('black').fill('blue', alpha=.3)

|

Annotations
-----------

To set the axes title and labels for the x and y variables, provide the
`title`, `xname`, and `yname` arguments to `XyPlot` or `XyGraph`.
Calling :py:meth:`ziaplot.series.Series.name` on a series adds the series line to a legend on the axes, which is displayed
either to the left or right of the axes.
Plain text labels can be added at any data point using the :py:class:`ziaplot.dataseries.Text` series.
:py:class:`ziaplot.dataseries.Arrow` series are Lines with an arrowhead on one end, and optional text on the other.

.. jupyter-execute::

    with zp.XyPlot(title='Title',
                   xname='Independent Variable',
                   yname='Dependent Variable'):
        zp.PolyLine(x, y).name('Line #1')
        zp.PolyLine(x, y2).name('Line #2')
        zp.Text(0.2, 2, 'Text', halign='center')
        zp.Arrow((.70, 2.3), (.6, 3), 'Arrow', strofst=(-.05, .1)).color('black')

If `ziamath <https://ziamath.readthedocs.io>`_ is installed, math expressions can be
drawn in any label. The expressions are entered in Latex style delimited by $..$.

.. jupyter-execute::

    zp.XyPlot(title=r'Math: $\sqrt{a^2 + b^2}$',
              xname=r'Frequency, $\frac{1}{s}$',
              yname=r'Acceleration, $m/s^2$')

|

Function Series
---------------

The :py:class:`ziaplot.dataseries.Function` series takes a callable Python function and plots it over a given data range.
Often plotted on an `XyGraph` axis to represent a functional relationship rather than discrete or measured data points.
The function must take one float argument (the x value) and return a float (the y value).

.. jupyter-execute::

    with zp.XyGraph():
        zp.Function(math.sin, xmin=-2*math.pi, xmax=2*math.pi).name('sine')
        zp.Function(math.cos, xmin=-2*math.pi, xmax=2*math.pi).name('cosine')

Lambda functions work well here, such as

.. jupyter-input::

    zp.Function(lambda x: x**2)

|

Histogram Series
----------------

While the :py:class:`ziaplot.dataseries.Bars` series can be added directly to make bar plots, it is often easier to create
histogram bars using the :py:class:`ziaplot.dataseries.Histogram` series, or use a :py:class:`ziaplot.bar.BarChart` axis for qualitative x-value bar charts.
Histograms have parameters to specify the total number of bins, or a specific range of bin locations.
The data can also be weighted, or plotted as a probability density instead of data count.

.. jupyter-execute::

    import random
    v = [random.normalvariate(100, 5) for k in range(1000)]
    zp.Histogram(v)

|

Log-scale Axes
--------------

Data can be plotted on logscales using axes :py:class:`ziaplot.axeslog.LogYPlot`, :py:class:`ziaplot.axeslog.LogXPlot`, and :py:class:`ziaplot.axeslog.LogXYPlot`.

.. jupyter-execute::
    :hide-code:
    
    x2 = zp.linspace(.1, 1000)
    y2 = x2
    line = zp.PolyLine(x2, y2)
    p1 = zp.XyPlot(title='XyPlot')
    p1 += line
    p2 = zp.LogYPlot(title='LogYPlot')
    p2 += line
    p3 = zp.LogXPlot(title='LogXPlot')
    p3 += line
    p4 = zp.LogXYPlot(title='LogXYPlot')
    p4 += line
    zp.GridLayout(p1, p3, p2, p4, gutter=-20, columns=2)

|

Data Limits and Ticks
---------------------

By default, the axes are scaled to show all the data in all series.
To manually set the data range, use :py:meth:`ziaplot.axes.BasePlot.xrange` and :py:meth:`ziaplot.axes.BasePlot.yrange`.

.. jupyter-execute::

    x = [i*0.1 for i in range(11)]
    y = [xi**2 for xi in x]

    with zp.XyPlot() as p:
        zp.PolyLine(x, y)
        p.xrange(.5, 1).yrange(.3, 1)


Tick locations are also automatically determined. To override, call
:py:meth:`ziaplot.axes.BasePlot.xticks` or :py:meth:`ziaplot.axes.BasePlot.yticks`, providing a tuple of tick values and optional
names.

.. jupyter-execute::

    with zp.XyPlot() as p:
        zp.PolyLine(x, y)
        p.xticks((0, .25, .75, 1))
        p.yticks((0, .5, 1), names=('Low', 'Medium', 'High'))

To keep the default ticks but change the number formatter, use :py:class:`ziaplot.styletypes.TickStyle` with a standard format specification used in Python's `format() <https://docs.python.org/3/library/stdtypes.html#str.format>`_.

.. jupyter-execute::

    with zp.XyPlot() as p:
        p.style.tick.ystrformat = '.1e'
        zp.PolyLine(x, y)


Minor ticks, without a number label, can also be added between the major, labeled, ticks.

.. jupyter-execute::

    with zp.XyPlot() as p:
        zp.PolyLine(x, y)
        p.xticks(values=(0, .2, .4, .6, .8, 1),
                 minor=(zp.linspace(0, 1, 21)))
