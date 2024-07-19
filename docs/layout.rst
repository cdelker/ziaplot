Layout and Subplots
===================

Multiple plots can be added to a single figure using layouts.
Inspired by QT's box layouts, :py:class:`ziaplot.layout.LayoutH` and :py:class:`ziaplot.layout.LayoutV` take any number
of Drawables, including other layouts, as arguments, and stack the plots
horizontally or vertically.



.. jupyter-execute::
    :hide-code:

    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)
    

.. jupyter-execute::

    with zp.LayoutH().size(400, 200):
        zp.Plot([1,3,5], [1,2,5]).marker('o')
        zp.Plot([1,3,5], [1,2,5]).marker('square')
        zp.Plot([1,3,5], [1,2,5]).marker('triangle')

Grid layouts arrange axes in rows and columns. The number of columns may be specified, and the rows
are automatically added as needed.

.. jupyter-execute::

    with zp.LayoutGrid(columns=2):
        zp.Plot([1,2,3], [1,2,5])
        zp.Plot([1,2,3], [1,2,5]).color('blue')
        zp.Plot([1,2,3], [1,2,5]).color('green')
        zp.Plot([1,2,3], [1,2,5]).color('orange')

Subplots may span multiple rows or columns using `.span`. The first parameter is the column span, the second is the row span.

.. jupyter-execute::

    with zp.LayoutGrid(columns=3).size(700, 400):
        zp.Plot([1,2,3], [1,2,5]).span(3)
        zp.Plot([1,2,3], [3,3,2]).color('blue').span(1, 2)
        zp.Plot([1,2,3], [4,1,3]).color('green')
        zp.Plot([1,2,3], [0,2,6]).color('orange')
        zp.Plot([1,2,3], [0,2,6]).color('cyan')
        zp.Plot([1,2,3], [0,2,6]).color('purple')


Use :py:class:`ziaplot.layout.LayoutEmpty` to leave an empty spot in a layout.

.. jupyter-execute::

    with zp.LayoutGrid(columns=2):
        zp.Plot([0, 1], [0, 1])
        zp.LayoutEmpty()
        zp.Plot([0, 1], [1, 1]).color('orange')
        zp.Plot([0, 1], [1, 0]).color('green')
