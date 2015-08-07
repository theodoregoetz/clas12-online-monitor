from __future__ import print_function, division

import os

import numpy as np

from clas12monitor.ui import QtGui, uic

class DBTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(QtGui.QTabWidget, self).__init__(parent)
        self.parent = parent
        curdir = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(os.path.join(curdir,'DBTab.ui'), self)
        self.init_buttons()

    def init_buttons(self):

        sector_fmt     = 'sc{sector}'
        superlayer_fmt = 'sc{sector}_sl{superlayer}'
        direction_fmt  = 'sc{sector}_{direction}' #f or b
        box_fmt        = 'sc{sector}_{direction}_b{box}'
        quad_fmt       = 'sc{sector}_{direction}_b{box}_q{quad}'
        doublet_fmt    = 'sc{sector}_{direction}_b{box}_q{quad}_{doublet}'

        self.sectors = []
        self.superlayers = []
        self.directions = []
        self.boxes = []
        self.quads = []
        self.doublets = []

        for sector_id in range(1,7):

            fmt = dict(sector=sector_id)

            self.sectors.append(getattr(self,sector_fmt.format(**fmt)))
            self.superlayers.append([])
            self.directions.append([])
            self.boxes.append([])
            self.quads.append([])
            self.doublets.append([])

            for superlayer_id in range(1,7):
                fmt_slyr = fmt
                fmt_slyr.update(superlayer=superlayer_id)

                self.superlayers[-1].append(getattr(self,superlayer_fmt.format(**fmt_slyr)))

            for direction_id in ['f','b'] :
                fmt.update(direction=direction_id)

                self.directions[-1].append(getattr(self,direction_fmt.format(**fmt)))
                self.boxes[-1].append([])
                self.quads[-1].append([])
                self.doublets[-1].append([])

                box_ids = range(1,7)

                for box_id in box_ids:
                    fmt.update(box = box_id)

                    self.boxes[-1][-1].append(getattr(self, box_fmt.format(**fmt)))
                    self.quads[-1][-1].append([])
                    self.doublets[-1][-1].append([])

                    quad_ids = range(1,4)

                    for quad_id in quad_ids:
                        fmt.update(quad = quad_id)

                        self.quads[-1][-1][-1].append(getattr(self,quad_fmt.format(**fmt)))
                        self.doublets[-1][-1][-1].append([])

                        for doublet_id in [1,2]:
                            fmt.update(doublet = doublet_id)

                            self.doublets[-1][-1][-1][-1].append(getattr(self,doublet_fmt.format(**fmt)))

        for sector_id,sector in enumerate(self.sectors):

            directions = self.directions[sector_id]

            def _sc(_,sector=sector,dirs =directions):
                chkd = any([p.isChecked() for p in dirs])
                was_blocked = sector.signalsBlocked()
                sector.blockSignals(True)
                sector.setChecked(_sc)
                sector.blockSignals(was_blocked)

            for direction_id, direction in enumerate(directions):
                sector.clicked.connect(direction.setChecked)
                direction.clicked.connect(_sc)

                boxes = self.boxes[sector_id][direction_id]
                def _dir(_,direction=direction,bxs =boxes):
                    chkd = any([p.isChecked() for p in bxs])
                    was_blocked = direction.signalsBlocked()
                    direction.blockSignals(True)
                    direction.setChecked(chkd)
                    direction.blockSignals(was_blocked)

                for box_id,box in enumerate(boxes):
                    def _bx(ckd, box=box):
                        was_blocked = box.signalsBlocked()
                        box.blockSignals(True)
                        box.setChecked(ckd)
                        box.blockSignals(was_blocked)

                    direction.clicked.connect(_bx)
                    sector.clicked.connect(_bx)
                    box.clicked.connect(_dir)
                    box.clicked.connect(_sc)

                    quads = self.quads[sector_id][direction_id][box_id]
                    def _bx(_,box=box,qs=quads):
                        chkd = any([p.isChecked() for p in qs])

                        was_blocked = box.signalsBlocked()
                        box.blockSignals(True)
                        box.setChecked(chkd)
                        box.blockSignals(was_blocked)



                    for quad_id,quad in enumerate(quads):
                        def _qu(ckd, quad=quad):
                            was_blcoked = quad.signalsBlocked()
                            quad.blockSignals(True)
                            quad.setChecked(ckd)
                            quad.blockSignals(was_blocked)

                        box.clicked.connect(_qu)
                        direction.clicked.connect(_qu)
                        sector.clicked.connect(_qu)
                        quad.clicked.connect(_bx)
                        quad.clicked.connect(_dir)
                        quad.clicked.connect(_sc)

                        doublets = self.doublets[sector_id][direction_id][box_id][quad_id]
                        def _qu(_, quad=quad,dbs=doublets):
                            chkd = any([p.isChecked() for p in dbs])

                            was_blocked = quad.signalsBlocked()
                            quad.blockSignals(True)
                            quad.setChecked(chkd)
                            quad.blockSignals(was_blocked)


                        for doublet in doublets:
                            def _db(ckd, doublet = doublet):
                                was_blocked = doublet.signalsBlocked()
                                doublet.blockSignals(True)
                                doublet.setChecked(ckd)
                                doublet.blockSignals(was_blocked)

                            quad.clicked.connect(_db)
                            box.clicked.connect(_db)
                            direction.clicked.connect(_db)
                            sector.clicked.connect(_db)
                            doublet.clicked.connect(_qu)
                            doublet.clicked.connect(_bx)
                            doublet.clicked.connect(_dir)
                            doublet.clicked.connect(_sc)

            for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                sector.clicked.connect(superlayer.setChecked)

                boxes = [x[superlayer_id] for x in self.boxes[sector_id]]
                def _sl(_, superlayer=superlayer,bxs=boxes):
                    chkd = any([p.isChecked() for p in bxs])

                    was_blocked = superlayer.signalsBlocked()
                    superlayer.blockSignals(True)
                    superlayer.setChecked(chkd)
                    superlayer.blockSignals(was_blocked)

                for direction_id, direction in enumerate(directions):
                    direction.clicked.connect(_sl)

                    boxes = self.boxes[sector_id][direction_id]

                    for box_id,box in enumerate(boxes):
                        if box_id == superlayer_id:
                            superlayer.clicked.connect(box.setChecked)
                            box.clicked.connect(_sl)

                            quads = self.quads[sector_id][direction_id][box_id]

                            for quad_id,quad in enumerate(quads):
                                superlayer.clicked.connect(quad.setChecked)
                                quad.clicked.connect(_sl)
                                doublets = self.doublets[sector_id][direction_id][box_id][quad_id]

                                for doublet in doublets:
                                    superlayer.clicked.connect(doublet.setChecked)
                                    doublet.clicked.connect(_sl)

            for direction_id, direction in enumerate(directions):
                boxes = self.boxes[sector_id][direction_id]
                def _dir(_,direction=direction,bxs=boxes):
                    chkd = any([p.isChecked() for p in bxs])
                    was_blocked = direction.signalsBlocked()
                    direction.blockSignals(True)
                    direction.setChecked(chkd)
                    direction.blockSignals(was_blocked)

                for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                    superlayer.clicked.connect(_dir)

            for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                superlayer.clicked.connect(_sc)

        #Sending DBArray Loop
        for sector_id,sector in enumerate(self.sectors):
            sector.clicked.connect(self.sendDBArray)
            directions = self.directions[sector_id]

            for direction_id, direction in enumerate(directions):
                direction.clicked.connect(self.sendDBArray)
                boxes = self.boxes[sector_id][direction_id]


                for box_id,box in enumerate(boxes):

                    box.clicked.connect(self.sendDBArray)
                    quads = self.quads[sector_id][direction_id][box_id]


                    for quad_id,quad in enumerate(quads):
                        quad.clicked.connect(self.sendDBArray)

                        doublets = self.doublets[sector_id][direction_id][box_id][quad_id]
                        for doublet in doublets:
                            doublet.clicked.connect(self.sendDBArray)


            for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                sector.clicked.connect(self.sendDBArray)

                boxes = [x[superlayer_id] for x in self.boxes[sector_id]]

                for direction_id, direction in enumerate(directions):
                    direction.clicked.connect(self.sendDBArray)
                    boxes = self.boxes[sector_id][direction_id]

                    for box_id,box in enumerate(boxes):
                        if box_id == superlayer_id:
                            superlayer.clicked.connect(self.sendDBArray)
                            box.clicked.connect(self.sendDBArray)
                            quads = self.quads[sector_id][direction_id][box_id]

                            for quad_id,quad in enumerate(quads):
                                superlayer.clicked.connect(self.sendDBArray)
                                quad.clicked.connect(self.sendDBArray)
                                doublets = self.doublets[sector_id][direction_id][box_id][quad_id]

                                for doublet in doublets:
                                    superlayer.clicked.connect(doublet.setChecked)
                                    doublet.clicked.connect(self.sendDBArray)

            for direction_id, direction in enumerate(directions):
                boxes = self.boxes[sector_id][direction_id]

                for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                    superlayer.clicked.connect(self.sendDBArray)

            for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                superlayer.clicked.connect(self.sendDBArray)

        self.currentChanged.connect(self.sendDBArray)


    def getSec(self):

        fmt = 'sc{sector}'

        buttons = []
        for sector in range(1,7):
            opts = {    'sector' : sector
                    }
            b = getattr(self,fmt.format(**opts))
            buttons += [b.isChecked()]
        return buttons

    def get_superlayer(self):

        fmt = 'sc{sector}_sl{superlayer}'

        buttons = []
        for sector in range(1,7):
            sl_buttons = []
            for superlayer in range(1,7):
                opts = {    'sector' : sector,
                            'superlayer' : superlayer
                            }
                b = getattr(self,fmt.format(**opts))
                sl_buttons += [b.isChecked()]
            buttons += [sl_buttons]
        return buttons

    def get_direction(self):

        fmt = 'sc{sector}_{direction}'

        buttons = []
        for sector in range(1,7):
            for superlayer in range(1,7):

                d_buttons = []
                for direction in ['f','b']:
                    opts = {    'sector' : sector,
                                'direction' : direction
                                }
                    b = getattr(self,fmt.format(**opts))
                    d_buttons += [b.isChecked()]
                buttons += [d_buttons]
        return buttons
    def get_box(self):

        fmt = 'sc{sector}_{direction}_b{box}'
        buttons = []
        for sector in range(1,7):

            d_buttons = []
            for direction in ['f','b']:

                b_buttons = []
                for box in range(1,7):

                    opts = {
                                    'sector' : sector,
                                    'direction' : direction,
                                    'box' : box
                                    }
                    b = getattr(self,fmt.format(**opts))
                    b_buttons += [b.isChecked()]
                d_buttons += [b_buttons]
            buttons += [d_buttons]
        return buttons

    def get_quad(self):

        fmt = 'sc{sector}_{direction}_b{box}_q{quad}'
        buttons = []
        for sector in range(1,7):

            d_buttons = []
            for direction in ['f','b']:

                b_buttons = []
                for box in range(1,7):

                    q_buttons = []
                    for quad in range(1,4):


                        opts = {
                                    'sector' : sector,
                                    'direction' : direction,
                                    'box' : box,
                                    'quad' : quad
                                    }
                        b = getattr(self,fmt.format(**opts))
                        q_buttons += [b.isChecked()]
                    b_buttons += [q_buttons]
                d_buttons += [b_buttons]
            buttons += [d_buttons]
        return buttons

    def get_doublet(self):

        fmt = 'sc{sector}_{direction}_b{box}_q{quad}_{doublet}'
        buttons = []
        for sector in range(1,7):

            d_buttons = []
            for direction in ['f','b']:

                b_buttons = []
                for box in range(1,7):

                    q_buttons = []
                    for quad in range(1,4):

                        db_buttons = []
                        for doublet in range(1,3):

                            opts = {
                                    'sector' : sector,
                                    'direction' : direction,
                                    'box' : box,
                                    'quad' : quad,
                                    'doublet' : doublet}
                            b = getattr(self,fmt.format(**opts))
                            db_buttons += [b.isChecked()]
                        q_buttons += [db_buttons]
                    b_buttons += [q_buttons]
                d_buttons += [b_buttons]
            buttons += [d_buttons]
        return buttons




    def sendDBArray(self,*args):
        main_window = self.parent
        dcw = main_window.dcwires
        wiremaps = main_window.wiremaps

        sector_id            = self.currentIndex()
        sector_status        = self.getSec()[sector_id]
        direction_status     = self.get_direction()[sector_id]
        superlayer_status   = self.get_superlayer()[sector_id]
        box_status           = self.get_box()[sector_id]
        quad_status          = self.get_quad()[sector_id]
        doublet_status           = self.get_doublet()[sector_id]


        print('\n\ncrate id:',sector_id)
        print('supply boards:',superlayer_status)
        print('dcw.distr_box_type[0]:',dcw.distr_box_type[0,0,0,0])

        mask = np.zeros((6,6,6,112), dtype=np.bool)
        if sector_status:
            for dir_i, (dirname,dire) in enumerate(zip(['forward','backward'],direction_status)):
                if dire:
                    for slyr_id in range(6):
                        if superlayer_status[slyr_id]:
                            for qu_i,qu in enumerate(quad_status[dir_i][slyr_id]):
                                if qu:
                                    for db_i,db in enumerate(doublet_status[dir_i][slyr_id][qu_i]):
                                        if db:
                                            mask |= (dcw.sector_id==sector_id) \
                                                & (dcw.distr_box_type==dirname) \
                                                & (dcw.superlayer_id==slyr_id) \
                                                & (dcw.quad_id == qu_i) \
                                                & (dcw.doublet_id== db_i)



        wiremaps.mask = mask
        print('complete')


if __name__ == '__main__':
    import sys

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            self.db_tab = DBTab()
            self.setCentralWidget(self.db_tab)
            print(self.db_tab.get_box())
            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


