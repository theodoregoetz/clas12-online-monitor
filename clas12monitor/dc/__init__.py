from . import tables, plots
from .components import DCComponents
from .occupancy import dc_wire_occupancy

from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg \
    as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT \
    as NavigationToolbar

from .sidebar import Sidebar
from .crate_tab import CrateTab
from .db_tab import DBTab
from .tb_tab import TBTab
from .dcrb_tab import DCRB
from .stb_tab import STBTab
from .set_run import SetRunDialogue

from .main_window import MainWindow
