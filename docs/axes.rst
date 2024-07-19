Axes
====

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


All Ziaplot figures start on an Axes instance on which to draw.
The two most common Axes types are 
:py:class:`ziaplot.axes.axes.AxesPlot`, which draws the x and y axes lines along the bottom and
left sides of the frame, and :py:class:`ziaplot.axes.axes.AxesGraph`, which  draws the x and y axis
lines through the (0, 0) origin and includes arrowheads at the end of the axis lines.

`AxesPlot` is commonly used to plot discrete x and y values, where `AxesGraph` is used to plot functions.

.. jupyter-execute::
    :hide-code:

    p1 = zp.AxesPlot(title='AxesPlot')
    p2 = zp.AxesGraph(title='AxesGraph')
    zp.LayoutH(p1, p2).size(700, 350)

In terms of adding and displaying data series, the two are identical.


Blank Axes
----------

For geometric drawings, :py:class:`ziaplot.axes.axes.AxesBlank` provides a drawing
surface without adding any axis lines, tick marks, etc. Here, an `AxesBlank` is
used to draw a :py:class:`ziaplot.shapes.shapes.Circle`.

.. jupyter-execute::
    :hide-code:

    with zp.AxesBlank().size(150, 150).equal_aspect():
        zp.Circle(0, 0, .9)


Log Scale
---------

Data can be plotted on logarithmic scales using axes :py:class:`ziaplot.axes.axeslog.AxesLogY`,
:py:class:`ziaplot.axes.axeslog.AxesLogX`, and :py:class:`ziaplot.axes.axeslog.AxesLogXY`.

.. jupyter-execute::
    :hide-code:
    
    x2 = zp.linspace(.1, 1000)
    y2 = x2
    line = zp.PolyLine(x2, y2)
    p1 = zp.AxesPlot(title='AxesPlot')
    p1 += line
    p2 = zp.AxesLogY(title='AxesLogY')
    p2 += line
    p3 = zp.AxesLogX(title='AxesLogX')
    p3 += line
    p4 = zp.AxesLogXY(title='AxesLogXY')
    p4 += line
    zp.LayoutGrid(p1, p3, p2, p4, gutter=-20, columns=2)

|


Customizing Axes
----------------

When Axes are created, a title and captions for the x and y axis may be specified:

.. jupyter-execute::

    zp.AxesPlot(
        title='My Plot Title',
        xname='The X-Axis',
        yname='The Y-Axis'
    )

Axes size
*********

The pixel size of Axes is set using :py:meth:`ziaplot.axes.baseplot.BasePlot.size`:

.. jupyter-execute::

    zp.AxesPlot().size(240, 120)


Use :py:meth:`ziaplot.axes.baseplot.BasePlot.equal_aspect` to force the x- and y-
scales to be equal, such that circles are drawn as circles and not ellipses.


.. jupyter-execute::

    with zp.AxesPlot().size(500, 250):  # No equal aspect
        zp.Circle(0, 0, .85)


.. jupyter-execute::

    with zp.AxesPlot().size(500, 250).equal_aspect():
        zp.Circle(0, 0, .85)


Data range and Ticks
********************


By default, the axes are scaled to show all the data in all series.
To manually set the data range, use :py:meth:`ziaplot.axes.baseplot.BasePlot.xrange`
and :py:meth:`ziaplot.axes.baseplot.BasePlot.yrange`.

.. jupyter-execute::

    x = [i*0.1 for i in range(11)]
    y = [xi**2 for xi in x]

    with zp.AxesPlot().xrange(.5, 1).yrange(.3, 1) as p:
        zp.PolyLine(x, y)


Tick locations are also automatically determined. To override, call
:py:meth:`ziaplot.axes.baseplot.BasePlot.xticks` or :py:meth:`ziaplot.axes.baseplot.BasePlot.yticks`,
providing a tuple of tick values and optional names.

.. jupyter-execute::

    with (zp.AxesPlot()
            .xticks((0, .25, .75, 1))
            .yticks((0, .5, 1), names=('Low', 'Medium', 'High'))) as p:
        zp.PolyLine(x, y)

To keep the default ticks but change the number formatter, use :py:class:`ziaplot.style.styletypes.TickStyle` with a standard format specification used in Python's `format() <https://docs.python.org/3/library/stdtypes.html#str.format>`_.

.. jupyter-execute::

    with zp.AxesPlot() as p:
        p.style.tick.ystrformat = '.1e'
        zp.PolyLine(x, y)


Minor ticks, without a number label, can also be added between the major, labeled, ticks.

.. jupyter-execute::

    with (zp.AxesPlot()
            .xticks(values=(0, .2, .4, .6, .8, 1),
                    minor=(zp.linspace(0, 1, 21)))) as p:
        zp.PolyLine(x, y)


Ticker
^^^^^^

:py:class:`ziaplot.axes.ticker._Ticker` provides shortcut to making a range of tick
marks using Python slicing notation. `zp.ticker[10:20:2]` provides ticks
starting at 10, ending at 20, with increments of 2:

.. jupyter-execute::

    zp.AxesPlot().xticks(zp.ticker[10:20:2]).yticks(zp.ticker[0:.75:.125])

