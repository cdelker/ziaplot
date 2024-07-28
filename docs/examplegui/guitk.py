''' Example of ziaplot in a Tkinter GUI

To build executable with pyinstaller:

    pyinstaller --onefile guitk.py

If/when tkinter natively supports svg (proposed for Tk 8.7), cairosvg won't be necessary.
'''

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

        p = zp.Graph()
        p += zp.PolyLine(x, y).marker('o')
        p += zp.HLine(avg)
        img = base64.encodebytes(p.imagebytes('png'))
        self.plot = tk.PhotoImage(data=img)
        self.label.configure(image=self.plot)

root = tk.Tk()
gui = Window(root)
root.mainloop()
