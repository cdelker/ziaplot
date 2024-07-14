''' Ziaplot in QT example '''

import sys
import random
from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg

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
        p = zp.AxesPlot()
        p += zp.Line(x, y).marker('o')
        p += zp.HLine(avg)
        self.image.load(p.imagebytes())


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainGUI()
    main.show()
    app.exec_()
    
if __name__ == '__main__':
    main()
