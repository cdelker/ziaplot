''' Base TK program with no dependencies '''

import tkinter as tk

class Window:
    def __init__(self, master):
        self.master = master
        master.title('Plot Example')
        self.button = tk.Button(self.master, text='Do nothing')
        self.button.pack()
        
root = tk.Tk()
gui = Window(root)
root.mainloop()