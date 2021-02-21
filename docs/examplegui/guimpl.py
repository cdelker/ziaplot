''' Example of matplotlib in a Tkinter GUI

To build executable with pyinstaller:

    pyinstaller --windowed --onefile guimpl.py
    
~350 MB pyinstaller executable (using both conda/mkl and pip-installed numpy)
'''

import tkinter as tk
import random

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Window:
    def __init__(self, master):
        self.master = master
        master.title('Plot Example')
        self.button = tk.Button(self.master, text='Generate Data', command=self.makedata)
        self.button.pack()
        self.fig = Figure(figsize=(6,4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack()
    
        self.makedata()

    def makedata(self):
        ''' Generate some randomized data and plot it. Convert the plot
            to PNG bytes and encode in base64 for Tkinter.
        '''
        n = 15
        y = [(i*2) + random.normalvariate(10, 2) for i in range(n)]
        avg = sum(y)/len(y)
        x = list(range(n))
    
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        ax.plot(x, y, marker='o')
        ax.axhline(avg)
        self.canvas.draw()
    
        
root = tk.Tk()
gui = Window(root)
root.mainloop()