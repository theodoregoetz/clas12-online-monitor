import os
import numpy as np
from matplotlib import pyplot, cm, colors, colorbar

from clas12monitor.util import cached_property, flame
from clas12monitor.ui import QtCore, QtGui, FigureCanvas, Figure, \
    NavigationToolbar

class DCWireStack(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        super(DCWireStack,self).__init__(parent)
        self.components = None

        self.wiremap = DCWirePlot(self)
        self.addWidget(self.wiremap)

        self.sec_wiremaps = []
        for sec in range(6):
            self.sec_wiremaps.append(DCWireSectorPlot(sec,self))
            self.addWidget(self.sec_wiremaps[sec])

    def setCurrentIndex(self,sec):
        super(DCWireStack,self).setCurrentIndex(sec)
        self.update_active_plot()

    @property
    def data(self):
        return self.wiremap.data

    @data.setter
    def data(self,d):
        self.wiremap.data = d
        for sec in range(6):
            self.sec_wiremaps[sec].data = d[sec]
        self.update_active_plot()

    @property
    def mask(self):
        return self.wiremap.mask

    @mask.setter
    def mask(self,m):
        self.wiremap.mask = m
        for sec in range(6):
            self.sec_wiremaps[sec].mask = m[sec]
        self.update_active_plot()

    def update_active_plot(self):
        if super(DCWireStack,self).currentIndex() == 0:
            self.wiremap.update()
            self.wiremap.canvas.setFocus()
        else:
            sec = super(DCWireStack,self).currentIndex() - 1
            print('updating sector plot',sec)
            self.sec_wiremaps[sec].update()
            self.sec_wiremaps[sec].canvas.setFocus()

class DCWirePlot(QtGui.QWidget):

    def __init__(self, parent=None):
        super(DCWirePlot,self).__init__(parent)
        self.parent = parent

        self.fig = Figure((5.0, 4.0), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.toolbar = NavigationToolbar(self.canvas, self.parent)

        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.toolbar)

        self.setup_axes()
        self.setup_textbox()

        self.canvas.mpl_connect('motion_notify_event', self.mouse_move)

    def _transform_data(self,data):
        a = data.copy().reshape(6,6*6,112)
        a[3:,:,...] = a[3:,::-1,...]
        a.shape = (2,3,6,6,112)
        a = np.rollaxis(a,2,1)
        a = np.rollaxis(a,3,2)
        a = a.reshape(2*6*6,3*112)
        a = np.roll(a,6*6,axis=0)
        return a

    def clear(self):
        try:
            del self.masked_data
        except AttributeError:
            pass

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = np.zeros((2*6*6,3*112))
            return self._data

    @data.setter
    def data(self,data):
        self.clear()
        self._data = self._transform_data(data)
        self.update()

    @property
    def mask(self):
        try:
            return self._mask
        except AttributeError:
            self._mask = np.ones((2*6*6,3*112),dtype=np.bool)
            return self._mask

    @mask.setter
    def mask(self,mask):
        self.clear()
        self._mask = self._transform_data(mask)
        self.update()

    @cached_property
    def masked_data(self):
        return np.ma.array(self.data, mask=~self.mask)

    def update(self):
        self.im.set_data(self.masked_data)
        self.im.set_clim(vmin=min(0,np.nanmin(self.masked_data)),
                         vmax=max(1,np.nanmax(self.masked_data)))
        self.canvas.draw()

    def setup_axes(self):
        self.ax = self.fig.add_subplot(1,1,1)

        self.im = self.ax.imshow(np.zeros((2*6*6,3*112)),
            extent=[0,112*3,-6*6,6*6],
            vmin=0, vmax=1,
            cmap=flame,
            aspect='auto', origin='lower', interpolation='nearest')
        self.ax.grid(True)

        _=self.ax.xaxis.set_ticks([0,112,112*2,112*3])
        _=self.ax.xaxis.set_ticklabels([1,112,112,112])

        yticks = np.linspace(-36,36,2*6+1,dtype=int)
        ylabels = abs(yticks)
        ylabels[len(ylabels)//2] = 1

        _=self.ax.yaxis.set_ticks(list(yticks))
        _=self.ax.yaxis.set_ticklabels([str(x) for x in ylabels])

        for sec in range(6):
            _ = self.ax.text(0.34*(sec%3) + 0.1, 1.02 if sec<3 else -0.06,
                        'Sector {}'.format(sec+1),
                        transform=self.ax.transAxes)

        self.cb = self.ax.figure.colorbar(self.im, ax=self.ax)

    def setup_textbox(self):
        # text location in fig coords
        self.txt = self.fig.text( 0.98, 0.98, '',
            ha = 'right',
            va = 'top',
            bbox = dict(alpha=0.5, color='white'),
            transform=self.fig.transFigure,
            family='monospace',
            zorder=100)
        self.msg = '''\
Sec: {sec: >1}, Slyr: {slyr: >1}, Lyr: {lyr: >1}, Wire: {wire: >3}
Crate: {crate: >1}, Slot: {slot: >2}, Subslot: {subslot: >1}, Channel: {ch: >2}
Distr Board: {dboard: <8}, Quad: {quad: >1}, Doublet: {doublet: >1}
Trans Board: {tboard: >1}, Trans Board Half: {tboard_half: >1}'''

    def mouse_move(self, event):
        if not event.inaxes: return
        if self.parent.components is None: return

        x, y = int(event.xdata),abs(int(event.ydata))

        if (x < 0) or (112*3 <= x) or (y < 0) or (6*6 <= y):
            return

        comp = self.parent.components

        wire = x%112
        lyr = y%6
        slyr = y//6
        sec = (x//112) + (3 if event.ydata<0 else 0)

        point = (sec,slyr,lyr,wire)

        msgopts = dict(
            sec=sec+1,slyr=slyr+1,lyr=lyr+1,wire=wire+1,
            crate       = comp.crate_id[point]+1,
            slot        = comp.slot_id[point]+1,
            subslot     = comp.subslot_id[point]+1,
            ch          = comp.subslot_channel_id[point]+1,
            dboard      = comp.distr_box_type[point],
            quad        = comp.quad_id[point]+1,
            doublet     = comp.doublet_id[point]+1,
            tboard      = comp.trans_board_id[point]+1,
            tboard_half = comp.trans_board_slot_id[point]+1,
        )
        self.txt.set_text(self.msg.format(**msgopts))
        self.canvas.draw()

class DCWireSectorPlot(QtGui.QWidget):

    def __init__(self,sec,parent=None):
        super(DCWireSectorPlot,self).__init__(parent)
        self.parent = parent
        self.sec = sec

        self.fig = Figure((5.0, 4.0), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.toolbar = NavigationToolbar(self.canvas, self.parent)

        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.toolbar)

        self.setup_axes()
        self.setup_textbox()

        self.canvas.mpl_connect('motion_notify_event', self.mouse_move)

    def _transform_data(self,data):
        return data.reshape(6*6,112)

    def clear(self):
        try:
            del self.masked_data
        except AttributeError:
            pass

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = np.zeros((6*6,112))
            return self._data

    @data.setter
    def data(self,data):
        self.clear()
        self._data = self._transform_data(data)
        self.update()

    @property
    def mask(self):
        try:
            return self._mask
        except AttributeError:
            self._mask = np.ones((6*6,112),dtype=np.bool)
            return self._mask

    @mask.setter
    def mask(self,mask):
        self.clear()
        self._mask = self._transform_data(mask)
        self.update()

    @cached_property
    def masked_data(self):
        return np.ma.array(self.data, mask=~self.mask)

    def update(self):
        print('updating sector wiremap',self.sec)
        print('    non-mask elements:',np.count_nonzero(self.mask))
        print('    mask:',self.mask.shape,self.mask)
        print('    data:',self.data.shape,self.data)
        self.im.set_data(self.masked_data)
        self.im.set_clim(vmin=min(0,np.nanmin(self.masked_data)),
                         vmax=max(1,np.nanmax(self.masked_data)))
        self.canvas.draw()

    def setup_axes(self):
        self.ax = self.fig.add_subplot(1,1,1)
        self.im = self.ax.imshow(np.zeros((6*6,112)),
            extent=[0,112,0,6*6],
            cmap=flame,
            vmin=0, vmax=1,
            aspect='auto', origin='lower', interpolation='nearest')
        self.ax.grid(True)

        xticks = list(np.linspace(0,112,112//16+1,dtype=int))
        xlabels = [str(x) for x in xticks]
        xlabels[0] = '1'

        yticks = list(np.linspace(0,36,36//6+1,dtype=int))
        ylabels = [str(x) for x in yticks]
        ylabels[0] = '1'

        self.ax.xaxis.set_ticks(xticks)
        self.ax.xaxis.set_ticklabels(xlabels)
        self.ax.yaxis.set_ticks(yticks)
        self.ax.yaxis.set_ticklabels(ylabels)

        self.ax.set_title('Sector '+str(self.sec+1))

        self.cb = self.ax.figure.colorbar(self.im, ax=self.ax)

    def setup_textbox(self):
        # text location in fig coords
        self.txt = self.fig.text( 0.98, 0.98, '',
            ha = 'right',
            va = 'top',
            bbox = dict(alpha=0.6, color='white'),
            transform=self.fig.transFigure,
            family='monospace',
            zorder=100)
        self.msg = '''\
Sec: {sec: >1}, Slyr: {slyr: >1}, Lyr: {lyr: >1}, Wire: {wire: >3}
Crate: {crate: >1}, Slot: {slot: >2}, Subslot: {subslot: >1}, Channel: {ch: >2}
Distr Board: {dboard: <8}, Quad: {quad: >1}, Doublet: {doublet: >1}
Trans Board: {tboard: >1}, Trans Board Half: {tboard_half: >1}'''

    def mouse_move(self, event):
        if not event.inaxes:
            return
        if self.parent.components is None:
            return

        x, y = int(event.xdata),abs(int(event.ydata))

        if (x < 0) or (112 <= x) or (y < 0) or (6*6 <= y):
            return

        comp = self.parent.components

        wire = x%112
        lyr = y%6
        slyr = y//6
        sec = self.sec

        point = (sec,slyr,lyr,wire)

        msgopts = dict(
            sec=sec+1,slyr=slyr+1,lyr=lyr+1,wire=wire+1,
            crate       = comp.crate_id[point]+1,
            slot        = comp.slot_id[point]+1,
            subslot     = comp.subslot_id[point]+1,
            ch          = comp.subslot_channel_id[point]+1,
            dboard      = comp.distr_box_type[point],
            quad        = comp.quad_id[point]+1,
            doublet     = comp.doublet_id[point]+1,
            tboard      = comp.trans_board_id[point]+1,
            tboard_half = comp.trans_board_slot_id[point]+1,
        )
        self.txt.set_text(self.msg.format(**msgopts))
        self.canvas.draw()


if __name__ == '__main__':
    '''
    to run this, issue the following command:

        python3 -m clas12monitor.dc.plots
    '''

    import sys
    from numpy import random as rand
    from clas12monitor.dc import dc_wire_occupancy, DCComponents

    class MainWindow(QtGui.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()

            wid = QtGui.QWidget()
            vbox = QtGui.QVBoxLayout()
            wid.setLayout(vbox)

            cbox = QtGui.QSpinBox()
            cbox.setMinimum(0)
            cbox.setMaximum(6)
            cbox.setSpecialValueText('-')
            stack = DCWireStack()

            infile = QtGui.QFileDialog.getOpenFileName(self,'open file',os.getcwd())

            stack.data = dc_wire_occupancy(infile)
            stack.components = DCComponents()
            stack.components.run = 1
            stack.components.fetch_data()

            vbox.addWidget(cbox)
            vbox.addWidget(stack)

            self.setCentralWidget(wid)

            cbox.valueChanged.connect(stack.setCurrentIndex)

            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
