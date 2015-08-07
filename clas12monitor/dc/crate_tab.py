from __future__ import print_function, division

import os

import numpy as np

from clas12monitor.ui import QtGui, uic

class CrateTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(QtGui.QTabWidget, self).__init__(parent)
        self.parent = parent
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'ui','CrateTab.ui'), self)
        self.init_buttons()

    def init_buttons(self):

        ct_fmt = 'crate{crate}'
        sb_fmt = 'crate{crate}_SB{supply_board}'
        ss_fmt = 'crate{crate}_SB{supply_board}_subslot{subslot}'
        ch_fmt = 'crate{crate}_SB{supply_board}_subslot{subslot}_{channel}'

        self.crates = []
        self.supply_boards = []
        self.subslots = []
        self.channels = []

        for crate_id in range(1,5):
            fmt = dict(crate=crate_id)

            self.crates.append(getattr(self,ct_fmt.format(**fmt)))
            self.supply_boards.append([])
            self.subslots.append([])
            self.channels.append([])

            if crate_id < 3:
                sb_ids = range(1,6)
            else:
                sb_ids = range(1,11)

            for sb_id in sb_ids:
                fmt.update(supply_board=sb_id)

                self.supply_boards[-1].append(getattr(self,sb_fmt.format(**fmt)))
                self.subslots[-1].append([])
                self.channels[-1].append([])

                if (sb_id % 5):
                    ss_ids = range(1,4)
                else:
                    ss_ids = range(1,7)

                for ss_id in ss_ids:
                    fmt.update(subslot=ss_id)

                    self.subslots[-1][-1].append(getattr(self,ss_fmt.format(**fmt)))
                    self.channels[-1][-1].append([])

                    for ch_id in range(1,9):
                        fmt.update(channel=ch_id)

                        self.channels[-1][-1][-1].append(getattr(self,ch_fmt.format(**fmt)))

        for ct_id,ct in enumerate(self.crates):

            supply_boards = self.supply_boards[ct_id]
            def _ct(_,ct=ct,sbs=supply_boards):
                chkd = any([b.isChecked() for b in sbs])
                ct.setChecked(chkd)

            for sb_id,sb in enumerate(supply_boards):
                ct.clicked.connect(sb.setChecked)
                sb.clicked.connect(_ct)

                subslots = self.subslots[ct_id][sb_id]
                def _sb(_,sb=sb,sss=subslots):
                    chkd = any([s.isChecked() for s in sss])
                    sb.setChecked(chkd)

                for ss_id,ss in enumerate(subslots):
                    def _ss(ckd,ss=ss):
                        was_blocked = ss.signalsBlocked()
                        ss.blockSignals(True)
                        ss.setChecked(ckd)
                        ss.blockSignals(was_blocked)
                    sb.clicked.connect(_ss)
                    ct.clicked.connect(_ss)
                    ss.clicked.connect(_sb)
                    ss.clicked.connect(_ct)


                    channels = self.channels[ct_id][sb_id][ss_id]
                    def _ss(_,ss=ss,chs=channels):
                        chkd = any([c.isChecked() for c in chs])

                        was_blocked = ss.signalsBlocked()
                        ss.blockSignals(True)
                        ss.setChecked(chkd)
                        ss.blockSignals(was_blocked)

                    for ch_id,ch in enumerate(channels):
                        def _ch(ckd,ch=ch):
                            was_blocked = ch.signalsBlocked()
                            ch.blockSignals(True)
                            ch.setChecked(ckd)
                            ch.blockSignals(was_blocked)
                        ss.clicked.connect(_ch)
                        sb.clicked.connect(_ch)
                        ct.clicked.connect(_ch)
                        ch.clicked.connect(_ss)
                        ch.clicked.connect(_sb)
                        ch.clicked.connect(_ct)




        for ct_id,ct in enumerate(self.crates):
            ct.clicked.connect(self.sendCrateArray)

            supply_boards = self.supply_boards[ct_id]

            for sb_id,sb in enumerate(supply_boards):
                sb.clicked.connect(self.sendCrateArray)

                subslots = self.subslots[ct_id][sb_id]

                for ss_id,ss in enumerate(subslots):

                    ss.clicked.connect(self.sendCrateArray)

                    channels = self.channels[ct_id][sb_id][ss_id]

                    for ch_id,ch in enumerate(channels):

                        ch.clicked.connect(self.sendCrateArray)

        self.currentChanged.connect(self.sendCrateArray)

    def get_crate(self):

        fmt = 'crate{crate}'

        buttons = []
        for crate in range(1,5):

            opts = {    'crate' : crate
                        }
            b = getattr(self,fmt.format(**opts))
            buttons += [b.isChecked()]

        return buttons


    def get_supply_board(self):

        fmt = 'crate{crate}_SB{supply_board}'

        buttons = []
        for crate in range(1,5):

            sb_buttons = []
            if crate in range(1,3):
                slots = range(1,6)
            else:
                slots = range(1, 11)
            for supply_board in slots:


                opts = {    'crate' : crate,
                                'supply_board' : supply_board
                        }
                b = getattr(self,fmt.format(**opts))

                sb_buttons += [b.isChecked()]
            buttons += [sb_buttons]

        return buttons

    def get_subslots(self):

        fmt = 'crate{crate}_SB{supply_board}_subslot{subslot}'

        buttons = []
        for crate in range(1,5):

            sb_buttons = []
            if crate in range(1,3):
                slots = range(1,6)
            else:
                slots = range(1, 11)
            for supply_board in slots:

                ss_buttons = []
                if supply_board in range(1,5) or range(6,10):
                    subslots = range(1,4)
                else:
                    subslots = range(1,7)
                for subslot in subslots:



                    opts = {    'crate' : crate,
                                'supply_board' : supply_board,
                                'subslot' : subslot
                                }
                    b = getattr(self,fmt.format(**opts))
                    ss_buttons += [b.isChecked()]
                sb_buttons += [ss_buttons]
            buttons += [sb_buttons]

        return buttons

    def get_channels(self):

        fmt = 'crate{crate}_SB{supply_board}_subslot{subslot}_{channel}'

        buttons = []
        for crate in range(1,5):

            sb_buttons = []
            if crate in range(1,3):
                slots = range(1,6)
            else:
                slots = range(1, 11)
            for supply_board in slots:

                ss_buttons = []
                if supply_board in range(1,5) or range(6,10):
                    subslots = range(1,4)
                else:
                    subslots = range(1,7)
                for subslot in subslots:

                    ch_buttons = []
                    for channel in range(1,9):

                        opts = {    'crate' : crate,
                                    'supply_board' : supply_board,
                                    'subslot' : subslot,
                                    'channel' : channel
                                    }
                        b = getattr(self,fmt.format(**opts))
                        ch_buttons += [b.isChecked()]
                    ss_buttons += [ch_buttons]
                sb_buttons += [ss_buttons]
            buttons += [sb_buttons]

        return buttons


    def sendCrateArray(self,*args):
        main_window = self.parent
        dcw = main_window.dcwires
        wiremaps = main_window.wiremaps

        crate_id            = self.currentIndex()
        crate_status        = self.get_crate()[crate_id]
        supply_board_status = self.get_supply_board()[crate_id]
        subslot_status      = self.get_subslots()[crate_id]
        channel_status      = self.get_channels()[crate_id]

        print('\n\ncrate id:',crate_id)
        print('supply boards:',supply_board_status)

        mask = np.zeros((6,6,6,112), dtype=np.bool)
        if crate_status:
            for sb_i,sb in enumerate(supply_board_status):
                if sb:
                    for ss_i,ss in enumerate(subslot_status[sb_i]):
                        if ss:
                            for ch_i,ch in enumerate(channel_status[sb_i][ss_i]):
                                if ch:
                                    mask |= (dcw.crate_id==crate_id) \
                                        & (dcw.slot_id==sb_i) \
                                        & (dcw.subslot_id==ss_i) \
                                        & (dcw.subslot_channel_id==ch_i)

        wiremaps.mask = mask
        print('complete')


if __name__ == '__main__':
    import sys

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            self.crate_tab = CrateTab()
            self.setCentralWidget(self.crate_tab)
            print(self.crate_tab.get_crate())

            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
