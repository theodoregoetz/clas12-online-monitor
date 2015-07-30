import numpy as np
from matplotlib import pyplot, cm, colors, colorbar

from clas12monitor.util import cached_property
from clas12monitor.ui import QtGui, FigureCanvas, Figure, \
    NavigationToolbar

class DCWireStack(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        super(DCWireStack,self).__init__(parent)

        self.wiremap = DCWirePlot(self)
        self.addWidget(self.wiremap)

        self.sec_wiremaps = []
        for sec in range(6):
            self.sec_wiremaps.append(DCWireSectorPlot(sec,self))
            self.addWidget(self.sec_wiremaps[sec])

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
        else:
            sec = super(DCWireStack,self).currentIndex() - 1
            self.sec_wiremaps[sec].update()

    def setCurrentIndex(self,*args,**kwargs):
        super(DCWireStack,self).setCurrentIndex(*args,**kwargs)
        self.update_active_plot()


class DCWirePlot(QtGui.QWidget):

    def __init__(self, parent=None):
        super(DCWirePlot,self).__init__(parent)
        self.parent = parent

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self.parent)

        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.toolbar)

        self.setup_axes()

    def _transform_data(self,data):
        a = data.copy().reshape(6,6*6,112)
        a[3:,:,...] = a[3:,::-1,...]
        a.shape = (2,3,6,6,112)
        a = np.rollaxis(a,2,1)
        a = np.rollaxis(a,3,2)
        a = a.reshape(2*6*6,3*112)
        a = np.roll(a,6*6,axis=0)
        return a

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = np.zeros((2*6*6,3*112))
            return self._data

    @data.setter
    def data(self,data):
        delattr(self,'masked_data')
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
        delattr(self,'masked_data')
        self._mask = self._transform_data(mask)
        self.update()

    @cached_property
    def masked_data(self):
        return np.ma.array(self.data, mask=~self.mask)

    def update(self):
        self.im.set_data(self.masked_data)
        self.im.set_clim(vmin=np.nanmin(self.masked_data),
                         vmax=np.nanmax(self.masked_data))
        self.canvas.draw()

    def setup_axes(self):
        self.ax = self.fig.add_subplot(1,1,1)

        self.im = self.ax.imshow(np.zeros((2*6*6,3*112)),
            extent=[0,112*3,-6*6,6*6],
            vmin=0, vmax=1,
            aspect='auto', origin='lower', interpolation='nearest')
        self.ax.grid(True)

        _=self.ax.xaxis.set_ticks([0,112,112*2,112*3])
        _=self.ax.xaxis.set_ticklabels([1,112,112,112])

        yticks = np.linspace(-36,36,2*6+1,dtype=int)
        ylabels = abs(yticks)
        yl[len(yl)//2] = 1

        _=self.ax.yaxis.set_ticks(list(yticks))
        _=self.ax.yaxis.set_ticklabels([str(x) for x in ylabels])

        for sec in range(6):
            _ = self.ax.text(0.34*(sec%3) + 0.1, 1.02 if sec<3 else -0.06,
                        'Sector {}'.format(sec+1),
                        transform=self.ax.transAxes)

        self.cb = self.ax.figure.colorbar(self.im, ax=self.ax)

class DCWireSectorPlot(QtGui.QWidget):

    def __init__(self,sec,parent=None):
        super(DCWireSectorPlot,self).__init__(parent)
        self.parent = parent
        self.sec = sec

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self.parent)

        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.canvas)
        self.vbox.addWidget(self.toolbar)

        self.setup_axes()

    def _transform_data(self,data):
        return data.reshape(6*6,112)

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = np.zeros((6*6,112))
            return self._data

    @data.setter
    def data(self,data):
        delattr(self,'masked_data')
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
        delattr(self,'masked_data')
        self._mask = self._transform_data(mask)
        self.update()

    @cached_property
    def masked_data(self):
        return np.ma.array(self.data, mask=~self.mask)

    def update(self):
        self.im.set_data(self.masked_data)
        self.im.set_clim(vmin=np.nanmin(self.masked_data),
                         vmax=np.nanmax(self.masked_data))
        self.canvas.draw()

    def setup_axes(self):
        self.ax = self.fig.add_subplot(1,1,1)
        self.im = self.ax.imshow(np.zeros((6*6,112)),
            extent=[1,112,1,6*6],
            vmin=0, vmax=1,
            aspect='auto', origin='lower', interpolation='nearest')
        self.ax.grid(True)
        self.cb = self.ax.figure.colorbar(self.im, ax=self.ax)


if __name__ == '__main__':
    import sys
    from numpy import random as rand

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
            stack.data = rand.uniform(0,100,(6,6,6,112))

            vbox.addWidget(cbox)
            vbox.addWidget(stack)

            self.setCentralWidget(wid)

            cbox.valueChanged.connect(stack.setCurrentIndex)

            self.show()

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
