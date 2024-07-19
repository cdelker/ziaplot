Polar Plots and Smith Charts
============================

.. jupyter-execute::
    :hide-code:
    
    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


Plots in polar coordinates are drawn on :py:class:`ziaplot.axes.polar.AxesPolar` axes.
While a :py:class:`ziaplot.dataplots.polylines.PolyLine` can be drawn on a polar axis,
the x and y values are Cartesian.
To add a line in polar (radius and angle) form, use the :py:class:`ziaplot.polar.LinePolar` series, which can take angles in degrees or radians.

The `style.polar.rlabeltheta` style parameter can be useful to align the radius/magnitude tick labels so they don't get hidden by data.


.. jupyter-execute::

    th = zp.linspace(0, 2*math.pi, 500)
    r = [math.cos(7*t+math.pi/6) for t in th]

    with zp.AxesPolar() as p:
        p.style.polar.rlabeltheta = 15
        zp.LinePolar(r, th)

|

Smith Charts
------------

Normalized Smith Charts are created using :py:class:`ziaplot.axes.smith.AxesSmith`. The grid density can be changed using the `grid` argument.

.. jupyter-execute::
    :hide-code:
    
    coarse = zp.AxesSmith(grid='coarse', title='coarse')
    med = zp.AxesSmith(grid='medium', title='medium')
    fine = zp.AxesSmith(grid='fine', title='fine')
    extrafine = zp.AxesSmith(grid='extrafine', title='extrafine')
    zp.LayoutGrid(coarse, med, fine, extrafine, columns=2, width=800, height=800)    

Discrete data may be plotted on Smith charts using either :py:class:`ziaplot.dataplots.polylines.PolyLine` or :py:class:`ziaplot.dataplots.polar.LinePolar`, depending on the data format.
Alternatively, curves of constant resistance and constant reactance may be drawn with :py:class:`ziaplot.axes.smith.SmithConstResistance` and :py:class:`ziaplot.axes.smith.SmithConstReactance`.


.. jupyter-execute::

    with zp.AxesSmith(grid='coarse'):
        zp.SmithConstReactance(0.5)
        zp.SmithConstResistance(1)
