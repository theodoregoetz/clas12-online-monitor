from __future__ import print_function, division

import os
from contextlib import contextmanager

@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)

from clas12monitor.ui import QtGui, uic, FixedCheckBox

class Sidebar(QtGui.QWidget):
    def __init__(self,session,parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        curdir = os.path.dirname(os.path.realpath(__file__))
        with pushd(os.path.join(curdir,'ui')):
            uic.loadUi('Sidebar.ui', self)

        self.session = session
        self.post_update = None

        # fixe wire type to "sense"
        self.wire_type.blockSignals(True)
        self.wire_type_fixed.blockSignals(True)
        self.wire_type.setCurrentIndex(1)
        self.wire_type.setEnabled(False)
        self.wire_type_fixed.setChecked(True)
        self.wire_type_fixed.setEnabled(False)
        self.wire_type_nopts.setText('')

        self.updating = False
        dc_fill_tables(self.session)

    @property
    def fixed_parms(self):
        attrs = ['wire_type','sector','superlayer','layer','wire',
                 'crate','supply_board','subslot','distr_box_type',
                 'quad','doublet','trans_board','trans_slot',]

        _parms = {}
        for a in attrs:
            attr = getattr(self,a)
            attr_fixed = getattr(self,a+'_fixed')
            if attr_fixed.isChecked():
                if isinstance(attr,QtGui.QSpinBox):
                    if attr.value() > 0:
                        _parms[a] = attr.value() - 1
                elif isinstance(attr,QtGui.QComboBox):
                    if attr.currentIndex() > 0:
                        _parms[a] =  str(attr.currentText()).lower()

        return _parms

    @property
    def parms(self):
        attrs = ['wire_type','sector','superlayer','layer','wire',
                 'crate','supply_board','subslot','distr_box_type',
                 'quad','doublet','trans_board','trans_slot',]

        _parms = {}
        for a in attrs:
            attr = getattr(self,a)
            if isinstance(attr,QtGui.QSpinBox):
                if attr.value() > 0:
                    _parms[a] = attr.value() - 1
            elif isinstance(attr,QtGui.QComboBox):
                if attr.currentIndex() > 0:
                    _parms[a] =  str(attr.currentText()).lower()

        return _parms


    def update_parameters(self):
        if not self.updating:
            self.updating = True

            opts = dict(
                wire_type = ['any','sense','field','guard'],
                distr_box_type = ['any','forward','backward'],)

            fixed, nopts = dc_find_connections(self.session, **self.fixed_parms)

            for k in fixed:
                attr = getattr(self,k,None)
                if attr is not None:
                    was_blocked = attr.signalsBlocked()
                    attr.blockSignals(True)
                    if isinstance(attr,QtGui.QSpinBox):
                        attr.setValue(fixed[k]+1)
                    elif isinstance(attr,QtGui.QComboBox):
                        attr.setCurrentIndex(opts[k].index(fixed[k]))
                    attr.blockSignals(was_blocked)
                    getattr(self,k+'_nopts').setText('')
            for k in nopts:
                attr_fixed = getattr(self,k+'_fixed',None)
                if attr_fixed is not None:
                    getattr(self,k+'_nopts').setText(str(nopts[k]))
                    if not attr_fixed.isChecked():
                        attr = getattr(self,k,None)
                        if isinstance(attr,QtGui.QSpinBox):
                            getattr(self,k).setValue(0)
                        elif isinstance(attr,QtGui.QComboBox):
                            getattr(self,k).setCurrentIndex(0)

            if self.post_update is not None:
                p = self.parms
                self.post_update(p.get('sector',None),
                    dc_wire_status(self.session,**p))

            self.updating = False



if __name__ == '__main__':
    import sys

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            self.session = initialize_session()

            self.sidebar = Sidebar(self.session)
            self.setCentralWidget(self.sidebar)

            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
