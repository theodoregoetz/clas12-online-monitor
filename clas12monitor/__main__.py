import sys

from clas12monitor.ui import QtGui, MainWindow

app = QtGui.QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
