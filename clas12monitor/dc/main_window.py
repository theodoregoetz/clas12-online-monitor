from __future__ import print_function, division

import sys
import os
import numpy as np
from clas12monitor.ui import QtGui, uic
from clas12monitor.dc import plots, DCComponents, dc_wire_occupancy 

from clas12monitor.dc import CrateTab, DBTab, TBTab, SetRunDialogue, DCRB, STBTab


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'MainWindow.ui'), self)
        self.dcwires = DCComponents()
        self.loadRun(1)
        #self.dcwires.initialize_session()



        #self.run_number.setValue(int(DCWires.runnum))
        #self.run_number.valueChanged.connect(self.run_number.show)

        #if (self.run_number.value.Changed() :
            #print(self.run_number.value())


        ### Explorer Tabs
        self.explorer_tabs = QtGui.QTabWidget()


        TBTab.stateChanged = self.sendTBArray
        DBTab.stateChanged = self.sendDBArray
        STBTab.stateChanged = self.sendSTBArray
        DCRB.stateChanged = self.sendDCRBArray

        self.crate = CrateTab(self)
        self.crate.setMinimumWidth(750)
        self.crate.setMaximumHeight(1000)
        crate_vbox = QtGui.QVBoxLayout(self.crate)
        self.explorer_tabs.addTab(self.crate, 'Crates')


        self.dboard = DBTab()
        self.dboard.setMinimumWidth(750)
        dboard_vbox = QtGui.QVBoxLayout(self.dboard)
        self.explorer_tabs.addTab(self.dboard, 'Distribution Boards')


        self.tboard = TBTab()
        self.tboard.setMinimumWidth(750)
        tboard_vbox = QtGui.QVBoxLayout(self.tboard)
        self.explorer_tabs.addTab(self.tboard, 'Translation Boards')

        self.dcrb = DCRB()
        self.dcrb.setMinimumWidth(750)
        dcrb_vbox = QtGui.QVBoxLayout(self.dcrb)
        self.explorer_tabs.addTab(self.dcrb, 'Drift Chamber Readout Board')

        self.stb = STBTab()
        self.stb.setMinimumWidth(750)
        stb_vbox = QtGui.QVBoxLayout(self.stb)
        self.explorer_tabs.addTab(self.stb, 'Signal Translation Board')

        self.explorer_tabs.setMinimumWidth(750)
        self.explorer_tabs.setSizePolicy(
                                   QtGui.QSizePolicy.Fixed,
                                   QtGui.QSizePolicy.Expanding)


        explorer_vbox = QtGui.QVBoxLayout()
        explorer_vbox.addWidget(self.explorer_tabs)
        self.explorer_holder.setLayout(explorer_vbox)

        ### Chooser Sidebar
        #self.sidebar = Sidebar(self.session)
        #sidebar_vbox = QtGui.QVBoxLayout()
        #sidebar_vbox.addWidget(self.sidebar)
        #self.chooser_holder.setLayout(sidebar_vbox)

        ### Wiremap
        self.wiremaps = plots.DCWireStack(self)
        wmap_vbox = QtGui.QVBoxLayout()
        wmap_vbox.addWidget(self.wiremaps)
        self.wiremap_holder.setLayout(wmap_vbox)

        def update_wiremap(sec,data):
            if sec is not None:
                self.wiremaps.setCurrentIndex(sec+1)
            else:
                self.wiremaps.setCurrentIndex(0)
            self.wiremaps.data = data

        #self.sidebar.post_update = update_wiremap

        for i in [self.dboard, self.tboard, self.dcrb, self.stb]:
            i.currentChanged.connect(lambda x: self.wiremaps.setCurrentIndex(x+1))



        def f(i):
            if (i == 0):
                self.wiremaps.setCurrentIndex(0)
            else:
                self.wiremaps.setCurrentIndex(self.explorer_tabs.currentWidget().currentIndex() + 1)

        self.explorer_tabs.currentChanged.connect(f)
        self.setModeExplorer()
        self.show()

    def setModeExplorer(self):
        self.actionExplorer.setChecked(True)
        self.actionChooser.setChecked(False)
        self.left_stacked_widget.setCurrentIndex(0)

    def setModeChooser(self):
        self.actionExplorer.setChecked(False)
        self.actionChooser.setChecked(True)
        self.left_stacked_widget.setCurrentIndex(1)

    def setRunDialogue(self):
        run,ok = SetRunDialogue.getRunNum()
        if ok:
            self.loadRun(run)

    def loadRun(self, runnumber):
        self.rundisplay.setNum(runnumber)
        self.dcwires.run = runnumber
        self.dcwires.fetch_data()


    def sendTBArray(*args):
        return main_window.tboard.get_sectors(),
        main_window.tboard.get_superlayers(),
        main_window.tboard.get_boards(),
        main_window.tboard.get_halfs()

    def sendDBArray(*args):
        return main_window.dboard.get_sector(),
        main_window.dboard.get_super_layer(),
        main_window.dboard.get_direction(),
        main_window.dboard.get_box(),
        main_window.dboard.get_quad(),
        main_window.dboard.get_doublet()

    def sendSTBArray(*args):
        return main_window.stb.get_board(),
        main_window.stb.get_superlayer(),
        main_window.stb.get_sector()

    def sendDCRBArray(*args):
        print(main_window.dcrb.get_board())
        print(main_window.dcrb.get_superlayer())
        print(main_window.dcrb.get_sector())

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
