from __future__ import print_function, division

import os

from clas12monitor.ui import QtGui, uic

class DBTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(QtGui.QTabWidget, self).__init__(parent)
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

            def _check_sector(_,target=sector,parents=directions):
                is_checked = any([p.isChecked() for p in parents])
                target.setChecked(is_checked)

            for direction_id, direction in enumerate(directions):
                sector.clicked.connect(direction.setChecked)
                sector.clicked.connect(self.stateChanged)
                direction.clicked.connect(_check_sector)

                boxes = self.boxes[sector_id][direction_id]
                def _check_direction(_,target=direction,parents=boxes):
                    is_checked = any([p.isChecked() for p in parents])
                    target.setChecked(is_checked)

                for box_id,box in enumerate(boxes):
                    direction.clicked.connect(box.setChecked)
                    sector.clicked.connect(box.setChecked)
                    sector.clicked.connect(self.stateChanged)
                    direction.clicked.connect(self.stateChanged)
                    box.clicked.connect(_check_direction)
                    box.clicked.connect(_check_sector)

                    quads = self.quads[sector_id][direction_id][box_id]
                    def _check_box(_,target=box,parents=quads):
                        is_checked = any([p.isChecked() for p in parents])
                        target.setChecked(is_checked)

                    for quad_id,quad in enumerate(quads):
                        box.clicked.connect(quad.setChecked)
                        direction.clicked.connect(quad.setChecked)
                        sector.clicked.connect(quad.setChecked)
                        box.clicked.connect(self.stateChanged)
                        direction.clicked.connect(self.stateChanged)
                        sector.clicked.connect(self.stateChanged)
                        quad.clicked.connect(_check_box)
                        quad.clicked.connect(_check_direction)
                        quad.clicked.connect(_check_sector)

                        doublets = self.doublets[sector_id][direction_id][box_id][quad_id]
                        def _check_quad(_, target=quad,parents=doublets):
                            is_checked = any([p.isChecked() for p in parents])
                            target.setChecked(is_checked)

                        for doublet in doublets:
                            quad.clicked.connect(doublet.setChecked)
                            box.clicked.connect(doublet.setChecked)
                            direction.clicked.connect(doublet.setChecked)
                            sector.clicked.connect(doublet.setChecked)
                            
                            quad.clicked.connect(self.stateChanged)
                            box.clicked.connect(self.stateChanged)
                            direction.clicked.connect(self.stateChanged)
                            sector.clicked.connect(self.stateChanged)
                            
                            doublet.clicked.connect(_check_quad)
                            doublet.clicked.connect(_check_box)
                            doublet.clicked.connect(_check_direction)
                            doublet.clicked.connect(_check_sector)

            for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                sector.clicked.connect(superlayer.setChecked)

                boxes = [x[superlayer_id] for x in self.boxes[sector_id]]
                def _check_superlayer(_,target=superlayer,parents=boxes):
                    is_checked = any([p.isChecked() for p in parents])
                    target.setChecked(is_checked)

                for direction_id, direction in enumerate(directions):
                    direction.clicked.connect(_check_superlayer)

                    boxes = self.boxes[sector_id][direction_id]

                    for box_id,box in enumerate(boxes):
                        if box_id == superlayer_id:
                            superlayer.clicked.connect(box.setChecked)
                            superlayer.clicked.connect(self.stateChanged)
                            box.clicked.connect(_check_superlayer)
                            
                            quads = self.quads[sector_id][direction_id][box_id]

                            for quad_id,quad in enumerate(quads):
                                superlayer.clicked.connect(quad.setChecked)
                                superlayer.clicked.connect(self.stateChanged)
                                quad.clicked.connect(_check_superlayer)

                                doublets = self.doublets[sector_id][direction_id][box_id][quad_id]

                                for doublet in doublets:
                                    superlayer.clicked.connect(doublet.setChecked)
                                    superlayer.clicked.connect(self.stateChanged)
                                    doublet.clicked.connect(_check_superlayer)

            for direction_id, direction in enumerate(directions):
                boxes = self.boxes[sector_id][direction_id]
                def _check_direction(_,target=direction,parents=boxes):
                    is_checked = any([p.isChecked() for p in parents])
                    target.setChecked(is_checked)
                for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                    superlayer.clicked.connect(_check_direction)

            for superlayer_id,superlayer in enumerate(self.superlayers[sector_id]):
                superlayer.clicked.connect(_check_sector)
                
                
                
                
    def get_sector(self):

        fmt = 'sc{sector}'

        buttons = []
        for sector in range(1,7):                        
            opts = {    'sector' : sector
                    }
            b = getattr(self,fmt.format(**opts))             
            buttons += [b.isChecked()]
        return buttons            
        
    def get_super_layer(self):

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
            for super_layer in range(1,7):

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

    """
    def status_changed(self):

        buttons = self.get_buttons()
        print(buttons)
        
    @staticmethod
    def getSec(parent = None):
        temp = DBTab(parent)
        answer = temp.currentIndex()        
        print(answer)
        #return answer
   """
    def getSec(self):
        return self.currentIndex() + 1
        

   
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


