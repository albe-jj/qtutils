# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 13:12:24 2020

@author: atosato
"""

from PyQt5.QtCore import Qt
from qcodes.plots.pyqtgraph import QtPlot

from io import BytesIO
import win32clipboard
from PIL import Image

# window.win.setWindowState(Qt.WindowMinimized)
# window.win.setWindowState(Qt.WindowNoState)
# window.win.activateWindow()
# window.set_relative_window_position(1.25,0.15)

def bring_up_window(window):
    window.win.setWindowState(Qt.WindowMinimized)
    window.win.setWindowState(Qt.WindowNoState)
    window.win.show()
    
def position_window(window, position=[1.25, 0.15]):
    """
    Parameters
    ----------
    window : qcodes.plots.pyqtgraph.QtPlot
        Plot window.
    position : list, optional
        list [x,y]. The default is [1.25, 0.15].
    """
    window.set_relative_window_position(*position)
    
def resize_window(window, geom=[1000,500]):
    window.win.resize(*geom)
    # window.setGeometry(300,300,1000,600)
    
    
 # self.win.setWindowTitle(self.get_default_title())
 
 
# def send_to_clipboard(clip_type, data):
#     win32clipboard.OpenClipboard()
#     win32clipboard.EmptyClipboard()
#     win32clipboard.SetClipboardData(clip_type, data)
#     win32clipboard.CloseClipboard()
    
# img.save('tst',"PNG", 0)
