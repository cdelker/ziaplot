# ziaplot

Ziaplot is for easy, lightweight, and Pythonic plotting of data in SVG format.

In ziaplot, a diagram is made from one or more elements added to a Graph.
Below, a PolyLine is added to a Graph.

        import ziaplot as zp
        with zp.Graph():
            zp.PolyLine([1, 2, 3], [1, 4, 9])

Ziaplot can plot discrete XY data, geometric diagrams, callable functions, histograms, pie charts, and bar charts.
Data can also be displayed in polar form or on a Smith Chart.
