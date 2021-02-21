Getting Started
===============


Installing
----------

Ziaplot can be installed using pip:

.. code-block:: bash

    pip install ziaplot


For the optional cairosvg dependency (for saving images in formats other than SVG), install using:

.. code-block:: bash

    pip install ziaplot[cairosvg]

.. jupyter-execute::
    :hide-code:

    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)


Quick Example
-------------

Figures in Ziaplot are made from Series objects, which represent individual x-y data, added to Axes on which the Series are drawn.
Here, an `XyPlot` axis is created, and a `Line` is added to it.

.. jupyter-execute::

    import ziaplot as zp
    
    x = list(range(6))
    y = [xi**2 for xi in x]

    p = zp.XyPlot()
    p += zp.Line(x, y)
    p


Note the x and y arrays could more easily be created as Numpy arrays, but Ziaplot does not require Numpy as a dependency so this documentation does not use it.


Use in Jupyter Notebooks
------------------------

Ziaplot is optimized for use in Jupyter, as every drawable object has a Jupyter representer function, so the final line `p` in the example above will display the figure inline.

Nearly everything in Ziaplot can be drawn (inherits from the `Drawable` class). A `Line` can be drawn by itself from the representation of zp.Line, but in this case, the Line will be added to an empty XyPlot.


Use outside Jupyter
-------------------

Outside Jupyter, the raw SVG output can be accessed by calling `p.svg()`.
Other image formats can be obtained if the `cairosvg <https://cairosvg.org/>`_ package is installed.
Byte-data for all supported formats can be obtained by calling `p.imagebytes()`.


Customizing
-----------

In general, the drawing style of individual series and axes can be customized using a chained method interface. For example, the `marker`, `color`, and `stroke` methods below
all return the Line instance itself, so the series can be set up on a single line of code:

.. jupyter-execute::

    zp.Line(x, y).marker('round', radius=8).color('orange').stroke('dashed')


See :ref:`styles` for additional styling options and global plot themes.


Why another plotting library?
-----------------------------

Anyone who has been around Python long enough should be familiSar with Matplotlib, the de facto standard for data visualization with Python.
Matplotlib is powerful and flexible - it can plot anything. But face it, it has a terrible, non-Pythonic programming interface.
What's the difference between a `figure()` and `Figure()`?
Why does documentation sometimes use `plt..`, sometimes `ax..`, and sometimes the truly awful `from pylab import *`?
It is also a huge dependency, requiring Numpy libraries and usually bundling several UI backends along with it.
A simple Tkinter UI experiment (see :ref:`ziagui`), built into an executable with Pyinstaller, was 16 MB when the data was plotted with Ziaplot, but over 340 MB using Matplotlib!

There are some Matplotlib alternatives. Seaborn just wraps Matplotlib to improve its interface. Plotly and Bokeh focus on interactivity and web applications.

Ziaplot was created as a light-weight, easy to use, fast, and Pythonic alternative for making static plots in SVG format.