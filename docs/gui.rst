.. _ziagui:

Embedding in a GUI
==================


Tkinter
-------

Because Tkinter does not (yet) natively support SVG graphics, to use Ziaplot in a Tkinter user interface requires the `cairosvg` package to convert to PNG images.
Tk's `PhotoImage` reads the PNG, which must be encoded in base-64.

Note: cairosvg needs extra import hooks to work with PyInstaller. See `guitk.py` in the docs/examplegui folder for more information.

.. code-block:: python

    import tkinter as tk
    import random
    import base64
    import ziaplot as zp


    class Window:
        def __init__(self, master):
            self.master = master
            master.title('Ziaplot in Tkinter')
            self.button = tk.Button(self.master, text='Generate Data', command=self.makedata)
            self.button.pack()
            self.plot = tk.PhotoImage()
            self.label = tk.Label(image=self.plot, height=400, width=600)
            self.label.pack()
            self.makedata()

        def makedata(self):
            ''' Generate some randomized data and plot it. Convert the plot
                to PNG bytes and encode in base64 for Tkinter.
            '''
            n = 15
            y = [(i*2) + random.normalvariate(10, 2) for i in range(n)]
            avg = sum(y)/len(y)
            x = list(range(n))

            p = zp.XyPlot()
            p += zp.Line(x, y).marker('o')
            p += zp.HLine(avg)
            img = base64.encodebytes(p.imagebytes('png'))
            self.plot = tk.PhotoImage(data=img)
            self.label.configure(image=self.plot)

    root = tk.Tk()
    gui = Window(root)
    root.mainloop()

|

PyQt5
-----

PyQt5 has a built-in SVG renderer in `QtSvg.QSvgWidget()`.
It can load Ziaplot `imagebytes()` directly.


.. code-block:: python

    import sys
    import random
    from PyQt5 import QtWidgets, QtSvg

    import ziaplot as zp


    class MainGUI(QtWidgets.QMainWindow):
        ''' Main Window '''

        def __init__(self, parent=None):
            super(MainGUI, self).__init__(parent)
            self.setWindowTitle('Ziaplot in QT')

            self.button = QtWidgets.QPushButton('Generate Data')
            self.button.clicked.connect(self.makedata)
            self.image = QtSvg.QSvgWidget()
            self.image.setMinimumWidth(600)
            self.image.setMinimumHeight(400)

            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.button)
            layout.addWidget(self.image)

            centralWidget = QtWidgets.QWidget(self)          
            centralWidget.setLayout(layout)
            self.setCentralWidget(centralWidget) 

        def makedata(self):
            ''' Generate some randomized data and plot it, then
                display using QSvgWidget. '''
            n = 15
            y = [(i*2) + random.normalvariate(10, 2) for i in range(n)]
            avg = sum(y)/len(y)
            x = list(range(n))
            p = zp.XyPlot()
            p += zp.Line(x, y).marker('o')
            p += zp.HLine(avg)
            self.image.load(p.imagebytes())


    app = QtWidgets.QApplication(sys.argv)
    main = MainGUI()
    main.show()
    app.exec_()
