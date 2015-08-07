from __future__ import print_function, division

import os

import numpy as np

from clas12monitor.ui import QtGui, uic

class STBTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(QtGui.QTabWidget, self).__init__(parent)
        self.parent =  parent
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'ui','STBTab.ui'), self)
        self.init_buttons()

    def init_buttons(self):

        self.currentChanged.connect(lambda sec: self.parent.wiremaps.setCurrentIndex(sec+1))

        sector_fmt     = 'sc{sector}'
        superlayer_fmt = 'sc{sector}_sl{superlayer}'
        board_fmt      = 'sc{sector}_sl{superlayer}_b{board}'


        self.sectors = []
        self.superlayers = []
        self.boards = []

        for sector_id in range(1,7):

            fmt = dict(sector=sector_id)

            self.sectors.append(getattr(self,sector_fmt.format(**fmt)))
            self.superlayers.append([])
            self.boards.append([])

            superlayer_ids = range(1,7)

            for superlayer_id in superlayer_ids:
                fmt.update(superlayer=superlayer_id)

                self.superlayers[-1].append(getattr(self,superlayer_fmt.format(**fmt)))
                self.boards[-1].append([])

                board_ids = range(1,8)

                for board_id in board_ids:
                    fmt.update(board=board_id)

                    self.boards[-1][-1].append(getattr(self,board_fmt.format(**fmt)))


        for sector_id,sector in enumerate(self.sectors):

            superlayers = self.superlayers[sector_id]
            def _sc(_,sector=sector,sls = superlayers):
                chkd = any([p.isChecked() for p in sls])
                sector.setChecked(chkd)

            for superlayer_id,superlayer in enumerate(superlayers):
                sector.clicked.connect(superlayer.setChecked)
                superlayer.clicked.connect(_sc)

                boards = self.boards[sector_id][superlayer_id]
                def _sl(_,superlayer=superlayer,bs=boards):
                    is_checked = any([p.isChecked() for p in bs])
                    superlayer.setChecked(chkd)

                for board_id,board in enumerate(boards):
                    def _b(ckd, board=board):
                        was_blocked = board.signalsBlocked()
                        board.blockSignals(True)
                        board.setChecked(ckd)
                        board.blockSignals(was_blocked)

                    superlayer.clicked.connect(_b)
                    sector.clicked.connect(_b)
                    board.clicked.connect(_sl)
                    board.clicked.connect(_sc)


            for sector_id,sector in enumerate(self.sectors):
                sector.clicked.connect(self.sendSTBArray)
                superlayers = self.superlayers[sector_id]
                for superlayer_id,superlayer in enumerate(superlayers):
                    superlayer.clicked.connect(self.sendSTBArray)
                    boards = self.boards[sector_id][superlayer_id]
                    for board_id,board in enumerate(boards):
                        board.clicked.connect(self.sendSTBArray)

        self.currentChanged.connect(self.sendSTBArray)

    def get_sector(self):
        return [i.isChecked() for i in self.sectors]

    def get_superlayer(self):

        fmt = 'sc{sector}_sl{super_layer}'

        buttons = []
        for sector in range(1,7):

            sl_buttons = []
            for super_layer in range(1,7):
                opts = {
                                'sector' : sector,
                                'super_layer' : super_layer
                            }
                b = getattr(self,fmt.format(**opts))
                sl_buttons += [b.isChecked()]
            buttons += [sl_buttons]

        return buttons

    def get_board(self):

        fmt = 'sc{sector}_sl{super_layer}_b{board}'

        buttons = []
        for sector in range(1,7):

            sl_buttons = []
            for super_layer in range(1,7):

                b_buttons = []
                for board in range(1,8):
                    opts = {
                                'sector' : sector,
                                'super_layer' : super_layer,
                                'board' : board}
                    b = getattr(self,fmt.format(**opts))
                    b_buttons += [b.isChecked()]
                sl_buttons += [b_buttons]
            buttons += [sl_buttons]

        return buttons

    def sendSTBArray(self,*args):
        main_window = self.parent
        dcw = main_window.dcwires
        wiremaps = main_window.wiremaps

        sector_id            = self.currentIndex()
        sector_status        = self.get_sector()[sector_id]
        superlayer_status = self.get_superlayer()[sector_id]
        board_status      = self.get_board()[sector_id]

        print('\n\ncrate id:',sector_id)
        print('supply boards:',superlayer_status)

        mask = np.zeros((6,6,6,112), dtype=np.bool)
        if sector_status:
            for sl_i,sl in enumerate(superlayer_status):
                if sl:
                    for b_i,b in enumerate(board_status[sl_i]):
                        if b:
                            mask |= (dcw.sector_id==sector_id) \
                                & (dcw.superlayer_id==sl_i) \
                                #& (dcw.signal_cable_board_id==b_i)

        wiremaps.mask = mask
        print('complete')
if __name__ == '__main__':
    import sys

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            self.stb_tab = STBTab()
            self.setCentralWidget(self.stb_tab)
            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


