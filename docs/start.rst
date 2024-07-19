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

Or to enable math expression rendering (via `ziamath <https://ziamath.readthedocs.io>`_), install using:

.. code-block:: bash

    pip install ziaplot[math]

Math rendering interprets any string label enclosed in $..$ to be Latex math.


.. jupyter-execute::
    :hide-code:

    import math
    import ziaplot as zp
    zp.styles.setdefault(zp.styles.DocStyle)

|

Quick Example
-------------

To create a figure, first define the Axes on which to plot, then add Series representing data
and other geometric objects.


Discrete data
*************

Discrete (x, y) data may be plotted using `PolyLine` or `Scatter`. Here, a `AxesPlot` is
created and a `PolyLine` added with the x and y values.

.. jupyter-execute::

    import ziaplot as zp
    import math

    x = list(range(6))
    y = [xi**2 for xi in x]

    with zp.AxesPlot():
        zp.PolyLine(x, y)

|


Functions
*********

To plot a mathematical function, a `Function` is created with a Python callable
function to plot. The function must take a single x-value argument and return
the y-value at that point. A range of x values may also be specified. Here, 
a sine function is plotted between -2π and 2π.

.. jupyter-execute::

    with zp.AxesGraph():
        zp.Function(math.sin, (-math.tau, math.tau))

This function was plotted on an `AxesGraph`, which is similar to `AxesPlot` but
uses a different tick style and keeps the (0, 0) origin always in view.


Any Series created within an Axes context manager are automatically added to the Axes.
Series may also be added using the += operator, with the same results:

.. jupyter-input::

    p = zp.AxesGraph()
    p += zp.Function(math.sin, (-math.tau, math.tau))

|

Customizing
-----------

In general, the drawing style of individual series and axes can be customized using a chained method interface.
For example, the `marker`, `color`, and `stroke` methods below
all return the PolyLine instance itself, so the series can be set up on a single line of code.

.. jupyter-execute::

    zp.PolyLine(x, y).marker('round', radius=8).color('orange').stroke('dashed')


See :ref:`styles` for additional styling options and global plot themes.

|

Use in Jupyter Notebooks
------------------------

Ziaplot is optimized for use in Jupyter, as every drawable object has a Jupyter representer function.
In Jupyter, leaving the `with` block automatically draws the plot.

Nearly everything in Ziaplot can be drawn (inherits from the `Drawable` class). A `PolyLine` not added to an Axes
will still be drawn using a Jupyter representer, but in this case, the `PolyLine`` will be added to an empty `AxesPlot`.

|

Use outside Jupyter
-------------------

Outside Jupyter, the raw SVG output can be accessed by calling `.svg()`, and saved to an svg file
by calling `.save(fname)`.

Other image formats, such as PNG, can be obtained if the `cairosvg <https://cairosvg.org/>`_ package is installed.
Byte-data for all supported formats can be obtained by calling `.imagebytes()`.

|

SVG Version Compatibility
-------------------------

Some SVG renderers, including recent versions of Inkscape and some OS built-in image viewers, are not fully compatible with the SVG 2.0 specification.
Set `svg2=False` using `settextmode` to use SVG 1.x specifications for better compatibility.
This may result in larger file sizes as each glyph is included as its own <path> element rather than being reused with <symbol> and <use> elements.

.. code-block:: python

    zp.settextmode('path', svg2=False)  # Draw text as <path> using SVG1.x

|


Why another plotting library?
-----------------------------

Anyone who has been around Python long enough should be familiar with Matplotlib, the de facto standard for data visualization with Python.
Matplotlib is powerful and flexible - it can plot anything.
However, it was designed for plotting empirical data in the form of arrays of x and y values, so graphing true mathematical functions or
geometric objects (lines, circles, segments, etc.) becomes a chore of discretizing the function or shape into an array first.

Additionally, Matplotlib has a confusing, non-Pythonic programming interface.
What's the difference between a `figure()` and `Figure()`?
Why does documentation sometimes use `plt..`, sometimes `ax..`, and sometimes the awful `from pylab import *`?
It is also a huge dependency, requiring Numpy libraries and usually bundling several UI backends along with it.
A simple Tkinter UI experiment (see :ref:`ziagui`), built into an executable with Pyinstaller, was 25 MB when the data was plotted with Ziaplot, but over 500 MB using Matplotlib!
There are some Matplotlib alternatives. Seaborn just wraps Matplotlib to improve its interface. Plotly and Bokeh focus on interactivity and web applications.

Ziaplot was created as a light-weight, easy to use, fast, and Pythonic alternative for making static plots in SVG format.
It also treats mathematical functions and Euclidean geometric objects as first-class citizens.
