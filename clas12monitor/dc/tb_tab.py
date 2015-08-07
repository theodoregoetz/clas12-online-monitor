from __future__ import print_function, division

import numpy as np

import os

from clas12monitor.ui import QtGui, uic

class TBTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(QtGui.QTabWidget, self).__init__(parent)
        self.parent = parent
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'ui','TBTab.ui'), self)
        self.init_buttons()

    def init_buttons(self):

        self.currentChanged.connect(lambda sec: self.parent.wiremaps.setCurrentIndex(sec+1))

        sector_fmt     = 'sc{sector}'
        superlayer_fmt = 'sc{sector}_sl{superlayer}'
        board_fmt      = 'sc{sector}_sl{superlayer}_b{board}'
        slot_fmt       = 'sc{sector}_sl{superlayer}_b{board}_{slot}'

        self.sectors = []
        self.superlayers = []
        self.boards = []
        self.slots = []

        for sector_id in range(1,7):
            fmt = dict(sector=sector_id)

            self.sectors.append(getattr(self,sector_fmt.format(**fmt)))
            self.superlayers.append([])
            self.boards.append([])
            self.slots.append([])

            superlayer_ids = range(1,7)

            for superlayer_id in superlayer_ids:
                fmt.update(superlayer=superlayer_id)

                self.superlayers[-1].append(getattr(self,superlayer_fmt.format(**fmt)))
                self.boards[-1].append([])
                self.slots[-1].append([])

                board_ids = range(1,8)

                for board_id in board_ids:
                    fmt.update(board=board_id)

                    self.boards[-1][-1].append(getattr(self,board_fmt.format(**fmt)))
                    self.slots[-1][-1].append([])

                    if board_id < 6:
                        slot_ids = range(1,3)
                    else :
                        slot_ids = range(1, 1)

                    for slot_id in slot_ids:
                        fmt.update(slot=slot_id)

                        self.slots[-1][-1][-1].append(getattr(self,slot_fmt.format(**fmt)))

        for sector_id,sector in enumerate(self.sectors):

            superlayers = self.superlayers[sector_id]
            def _sc(_,sector=sector,sls = superlayers):
                chkd = any([b.isChecked() for b in sls])
                sector.setChecked(chkd)


            for superlayer_id,superlayer in enumerate(superlayers):
                sector.clicked.connect(superlayer.setChecked)
                superlayer.clicked.connect(_sc)

                boards = self.boards[sector_id][superlayer_id]
                def _sl(_,superlayer=superlayer, bs=boards):
                    chkd = any([p.isChecked() for p in bs])
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

                    slots = self.slots[sector_id][superlayer_id][board_id]
                    def _b(_,board=board, sls = slots):
                        chkd = any([c.isChecked() for c in sls])
                        was_blocked = board.signalsBlocked()
                        board.blockSignals(True)
                        board.setChecked(chkd)
                        board.blockSignals(was_blocked)

                    for slot_id, slot in enumerate(slots):
                        def _s(ckd, slot=slot):
                            was_blocked = slot.signalsBlocked()
                            slot.blockSignals(True)
                            slot.setChecked(ckd)
                            slot.blockSignals(was_blocked)
                        board.clicked.connect(_s)
                        superlayer.clicked.connect(_s)
                        sector.clicked.connect(_s)
                        slot.clicked.connect(_b)
                        slot.clicked.connect(_sl)
                        slot.clicked.connect(_sc)


        for sector_id,sector in enumerate(self.sectors):
            sector.clicked.connect(self.sendTBArray)
            superlayers = self.superlayers[sector_id]

            for superlayer_id,superlayer in enumerate(superlayers):
                superlayer.clicked.connect(self.sendTBArray)
                boards = self.boards[sector_id][superlayer_id]

                for board_id,board in enumerate(boards):
                    board.clicked.connect(self.sendTBArray)
                    slots = self.slots[sector_id][superlayer_id][board_id]

                    for slot_id, slot in enumerate(slots):
                        slot.clicked.connect(self.sendTBArray)


        self.currentChanged.connect(self.sendTBArray)

    def get_sectors(self):

        fmt = 'sc{sector}'

        buttons = []
        for sector in range(1,7):


            opts = {    'sector' : sector}
            b = getattr(self,fmt.format(**opts))

            buttons += [b.isChecked()]

        return buttons
    def get_superlayers(self):

        fmt = 'sc{sector}_sl{superlayer}'

        buttons = []
        for sector in range(1,7):

            sl_buttons = []
            for superlayer in range(1,7):


                opts = {    'sector' : sector,
                                'superlayer' : superlayer}
                b = getattr(self,fmt.format(**opts))
                sl_buttons += [b.isChecked()]
            buttons += [sl_buttons]

        return buttons

    def get_boards(self):

        fmt = 'sc{sector}_sl{superlayer}_b{board}'

        buttons = []
        for sector in range(1,7):

            sl_buttons = []
            for superlayer in range(1,7):

                b_buttons = []
                for board in range(1,8):


                    opts = {    'sector' : sector,
                                'superlayer' : superlayer,
                                'board' : board }
                    b = getattr(self,fmt.format(**opts))
                    b_buttons += [b.isChecked()]
                sl_buttons += [b_buttons]
            buttons += [sl_buttons]

        return buttons

    def get_halfs(self):

        fmt = 'sc{sector}_sl{superlayer}_b{board}_{half}'

        buttons = []
        for sector in range(1,7):

            sl_buttons = []
            for superlayer in range(1,7):

                b_buttons = []
                for board in range(1,6):

                    h_buttons = []
                    for half in range(1,3):

                        opts = {    'sector' : sector,
                                'superlayer' : superlayer,
                                'board' : board,
                                'half' : half
                                }
                        b = getattr(self,fmt.format(**opts))
                        h_buttons += [b.isChecked()]
                    b_buttons += [h_buttons]
                sl_buttons += [b_buttons]
            buttons += [sl_buttons]

        return buttons



    def sendTBArray(self,*args):
        main_window = self.parent
        dcw = main_window.dcwires
        wiremaps = main_window.wiremaps

        sector_id            = self.currentIndex()
        sector_status         = self.get_sectors()[sector_id]
        superlayer_status   = self.get_superlayers()[sector_id]
        board_status         = self.get_boards()[sector_id]
        slot_status          = self.get_halfs()[sector_id]

        print('\n\nsector id:',sector_id)
        print('supply boards:',board_status)

        mask = np.zeros((6,6,6,112), dtype=np.bool)


        if sector_status:
            for superlayer_i in range(6):

                if superlayer_status[superlayer_i]:
                    for b_i,board in enumerate(board_status[superlayer_i]):
                        if board:
                            if b_i < 5:
                                for slot_i,slot in enumerate(slot_status[superlayer_i][b_i]):
                                    if slot:
                                        mask |= (dcw.sector_id==sector_id) \
                                            & (dcw.superlayer_id==superlayer_i) \
                                            & (dcw.trans_board_id==b_i) \
                                            & (dcw.trans_board_slot_id==slot_i)
                            else:
                                mask |= (dcw.sector_id==sector_id) \
                                    & (dcw.superlayer_id==superlayer_i) \
                                    & (dcw.trans_board_id==b_i)



        wiremaps.mask = mask
        print('complete')

if __name__ == '__main__':
    import sys

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            self.tb_tab = TBTab()
            self.setCentralWidget(self.tb_tab)

            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


