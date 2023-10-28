# ziaplot

Ziaplot is for easy, lightweight, and Pythonic plotting of data in SVG format.

In ziaplot, a plot is made from one or more Series added to an Axis.
Below, a Line series is added to an XyPlot axis.

        import ziaplot as zp
        with zp.XyPlot():
            zp.Line([1, 2, 3], [1, 4, 9])

Ziaplot can plot discrete XY data, callable functions, histograms, pie charts, and bar charts.
Data can also be displayed in polar form or on a Smith Chart.
