Layout and Subplots
===================

Multiple plots can be added to a single figure using layouts.
Inspired by QT's box layouts, :py:class:`ziaplot.layout.Hlayout` and :py:class:`ziaplot.layout.Vlayout` take any number
of Drawables, including other layouts, as arguments, and stack the plots
horizontally or vertically. Note the same line or axis can be added to multiple layouts.



.. jupyter-execute::
    :hide-code:

    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)
    

.. jupyter-execute::

    line = zp.Line([1,2,3], [1,2,5])
    zp.Hlayout(line, line, height=200)


Layouts can be stacked together to create more complex figures.
Here, two columns are created, each using Vlayouts. Then the two Vlayouts are arranged in a horizontal row using Hlayout.

.. jupyter-execute::

    col1 = zp.Vlayout(line, line)
    col2 = zp.Vlayout(line, line, line)
    zp.Hlayout(col1, col2)