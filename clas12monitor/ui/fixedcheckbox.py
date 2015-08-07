from clas12monitor.ui import QtGui

class FixedCheckBox(QtGui.QCheckBox):
    def __init__(self,parent=None):
        super(FixedCheckBox,self).__init__(parent)

    def setCheckByValue(self,val):
        if val:
            self.setChecked(True)
        else:
            self.setChecked(False)
