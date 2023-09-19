Charts (Pie and Bar)
====================

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp


In Ziaplot, the term "chart" is used for figures where the x value is qualitative. This includes Pie charts and bar charts.

|

Bar Chart
---------

A bar chart with a single series of data is made using :py:class:`ziaplot.bar.BarChart`, which takes x-values as strings and y-values (bar heights) for each bar.

.. jupyter-execute::

    p = zp.BarChart(xvalues=['January', 'February', 'March', 'April'],
                    yvalues=[3,5,4,8])
    p.xname = 'Month'
    p.yname = 'Number'
    p.title = 'Single Series Bar Chart'
    p


A :py:class:`ziaplot.bar.BarChartGrouped` creates a bar chart with multiple data series, grouped by x-value.
The x values must be provided when the BarChart is instantiated.
Sets of bars are then added using :py:meth:`ziaplot.bar.BarChart.bar_series`, which automatically creates and adds a :py:class:`ziaplot.dataseries.Bars` series.

.. jupyter-execute::

    p = zp.BarChartGrouped(['January', 'February', 'March', 'April'])
    p.bar_series((4, 4, 5, 6)).name('Apple')
    p.bar_series((3, 4, 4, 5)).name('Blueberry')
    p.bar_series((2, 1, 5, 4)).name('Cherry')
    p


Bar charts may also be drawn with horizontal bars.

.. jupyter-execute::

    p = zp.BarChartGrouped(['January', 'February', 'March', 'April'], horiz=True)
    p.bar_series((4, 4, 5, 6)).name('Apple')
    p.bar_series((3, 4, 4, 5)).name('Blueberry')
    p.bar_series((2, 1, 5, 4)).name('Cherry')
    p

|

Pie Chart
---------

:py:class:`ziaplot.pie.Pie` charts consist of wedges that are added to the pie using the :py:meth:`ziaplot.pie.Pie.wedge` method.
Note the use of `extrude` to pull a single pie wedge out from the center.

.. jupyter-execute::

    p = zp.Pie()
    p.wedge(3, 'a', extrude=True)
    p.wedge(10, 'b')
    p.wedge(5, 'c', color='green')
    p


Or multiple wedges added at once using `wedges`:

.. jupyter-execute::

    zp.Pie().wedges(20, 30, 40, 10).names('a', 'b', 'c', 'd')

