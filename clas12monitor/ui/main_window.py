import os

from clas12monitor import dc
from clas12monitor.ui import QtGui, uic

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'MainWindow.ui'), self)
        wid = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        wid.setLayout(vbox)

        self.dc_wire_stack = dc.plots.DCWireStack()

        vbox.addWidget(self.dc_wire_stack)

        self.setCentralWidget(wid)

        self.show()

    def openDataFile(self):
        pass
    def openReferenceFile(self):
        pass

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
