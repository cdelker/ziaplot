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

A bar chart with a single series of data is made using :py:class:`ziaplot.bar.BarChart`. Using the chart's context
manager, each bar is added using :py:class:`ziaplot.bar.BarSingle`.

.. jupyter-execute::

    with zp.BarChart() as p:
        zp.BarSingle(3).name('January')
        zp.BarSingle(5).name('February')
        zp.BarSingle(4).name('March')
        zp.BarSingle(8).name('April')
        p.xname = 'Month'
        p.yname = 'Number'
        p.title = 'Single Series Bar Chart'

Alternatively, bar charts may be created from using the `fromdict` class method:

.. jupyter-execute::

    items = {'January': 4,
             'February': 6,
             'March': 2,
             'April': 5}
    zp.BarChart.fromdict(
         items,
         xname='Month',
         yname='Number',
         title='Bar Chart From Dictionary')


A :py:class:`ziaplot.bar.BarChartGrouped` creates a bar chart with multiple data series, grouped by x-value.
The group value names are provided when the BarChart is instantiated.
Sets of bars are then added as :py:class:`ziaplot.bar.BarChart.BarSeries`.

.. jupyter-execute::

    with zp.BarChartGrouped(groups=['January', 'February', 'March', 'April']):
        zp.BarSeries(4, 4, 5, 6).name('Apple')
        zp.BarSeries(3, 4, 4, 5).name('Blueberry')
        zp.BarSeries(2, 1, 5, 4).name('Cherry')


Bar charts may also be drawn with horizontal bars.

.. jupyter-execute::

    with zp.BarChartGrouped(groups=['January', 'February', 'March', 'April'], horiz=True):
        zp.BarSeries(4, 4, 5, 6).name('Apple')
        zp.BarSeries(3, 4, 4, 5).name('Blueberry')
        zp.BarSeries(2, 1, 5, 4).name('Cherry')

Or from a dictionary:

.. jupyter-execute::

    items = {'Apple': (4, 4, 5, 6),
             'Blueberry': (3, 4, 4, 5),
             'Cherry': (2, 2, 5, 4)}
    zp.BarChartGrouped.fromdict(
        items,
        groups=['January', 'February', 'March', 'April'])


|

Pie Chart
---------

:py:class:`ziaplot.pie.Pie` charts consist of wedges that are added to the pie as :py:class:`ziaplot.pie.Pie.PieSlice`.
Note the use of `extrude` to pull a single pie wedge out from the center.
The slice values are normalized so the pie will always fill to 100\%.

.. jupyter-execute::

    with zp.Pie(labelmode='percent'):
        zp.PieSlice(3).name('a').extrude(True)
        zp.PieSlice(10).name('b')
        zp.PieSlice(5).name('c').color('green')


Pie Charts may also be made from dictionaries or from lists.

.. jupyter-execute::

    zp.Pie().fromdict({'a': 20, 'b': 30, 'c': 40, 'd': 10}, labelmode='name')

.. jupyter-execute::

    zp.Pie().fromlist((3, 4, 2, 2, 5, 1), labelmode='value')


The `labelmode` parameter changes what is displayed outside each slice, and may be `name`, `value`, `percent`, or `none`.
