from __future__ import print_function, division

import numpy as np

import os

from clas12monitor.ui import QtGui, uic

class TBTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(QtGui.QTabWidget, self).__init__(parent)
        self.parent = parent 
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'TBTab.ui'), self)
        self.init_buttons()
 
    def init_buttons(self):

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
            def _check_sector(_,target=sector,parents=superlayers):
                is_checked = any([p.isChecked() for p in parents])
                target.setChecked(is_checked)

            for superlayer_id,superlayer in enumerate(superlayers):
                sector.clicked.connect(superlayer.setChecked)
               
                superlayer.clicked.connect(_check_sector)

                boards = self.boards[sector_id][superlayer_id]
                def _check_superlayer(_,target=superlayer,parents=boards):
                    is_checked = any([p.isChecked() for p in parents])
                    target.setChecked(is_checked)

                for board_id,board in enumerate(boards):
                    superlayer.clicked.connect(board.setChecked)
                    sector.clicked.connect(board.setChecked)
                    
                    board.clicked.connect(_check_superlayer)
                    board.clicked.connect(_check_sector)

                    slots = self.slots[sector_id][superlayer_id][board_id]
                    def _check_board(_,target=board,parents=slots):
                        is_checked = any([p.isChecked() for p in parents])
                        target.setChecked(is_checked)

                    for slot in slots:
                        board.clicked.connect(slot.setChecked)
                        superlayer.clicked.connect(slot.setChecked)
                        sector.clicked.connect(slot.setChecked)
                        
                        slot.clicked.connect(_check_board)
                        slot.clicked.connect(_check_superlayer)
                        slot.clicked.connect(_check_sector)
                        
        for sector_id,sector in enumerate(self.sectors):

            superlayers = self.superlayers[sector_id]
            

            for superlayer_id,superlayer in enumerate(superlayers):                
                sector.clicked.connect(self.sendTBArray)                
                boards = self.boards[sector_id][superlayer_id]       

                for board_id,board in enumerate(boards):                    
                    superlayer.clicked.connect(self.sendTBArray)
                    sector.clicked.connect(self.sendTBArray)                    
                    slots = self.slots[sector_id][superlayer_id][board_id]               

                    for slot in slots:
                        
                        board.clicked.connect(self.sendTBArray)
                        superlayer.clicked.connect(self.sendTBArray)
                        sector.clicked.connect(self.sendTBArray)
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

        fmt = 'sc{sector}_sl{super_layer}'

        buttons = []
        for sector in range(1,7):
                
            sl_buttons = []
            for super_layer in range(1,7):             
                        
                            
                opts = {    'sector' : sector,
                                'super_layer' : super_layer}
                b = getattr(self,fmt.format(**opts))                        
                sl_buttons += [b.isChecked()]
            buttons += [sl_buttons]

        return buttons
        
    def get_boards(self):

        fmt = 'sc{sector}_sl{super_layer}_b{board}'

        buttons = []
        for sector in range(1,7):
                
            sl_buttons = []
            for super_layer in range(1,7):

                b_buttons = []
                for board in range(1,8):                
                        
                            
                    opts = {    'sector' : sector,
                                'super_layer' : super_layer,
                                'board' : board }
                    b = getattr(self,fmt.format(**opts))                        
                    b_buttons += [b.isChecked()]
                sl_buttons += [b_buttons]
            buttons += [sl_buttons]

        return buttons
        
    def get_halfs(self):

        fmt = 'sc{sector}_sl{super_layer}_b{board}_{half}'

        buttons = []
        for sector in range(1,7):
            
            sl_buttons = []
            for super_layer in range(1,7):

                b_buttons = []
                for board in range(1,6):
                    
                    h_buttons = []                    
                    for half in range(1,3):
                        
                        opts = {    'sector' : sector,
                                'super_layer' : super_layer,
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
        super_layer_status   = self.get_superlayers()[sector_id]
        board_status         = self.get_boards()[sector_id]
        half_status          = self.get_halfs()[sector_id]
        
        print('\n\nsector id:',sector_id)
        print('supply boards:',board_status)

        mask = np.zeros((6,6,6,112), dtype=np.bool)
        if sector_status:
            for sl_i,sl in enumerate(super_layer_status):
                if sl:
                    for b_i,b in enumerate(board_status[sl_i]):
                        if b:
                            for h_i,h in enumerate(half_status[sl_i][b_i]):
                                if h:
                                    mask |= (dcw.trans_board_id==b_i) \
                                        & (dcw.trans_board_slot_id==h_i)
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

            self.tb_tab = TBTab()
            self.setCentralWidget(self.tb_tab)

            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


