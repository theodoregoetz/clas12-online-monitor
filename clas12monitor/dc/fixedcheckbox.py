from clas12monitor.ui import QtGui

class FixedCheckBox(QtGui.QCheckBox):
    def __init__(self,parent):
        super(QtGui.QCheckBox, self).__init__(parent)

    def setCheckByValue(self,val):
        if val == 0:
            self.setChecked(False)
        else:
            self.setChecked(True)
