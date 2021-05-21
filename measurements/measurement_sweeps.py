# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 16:42:16 2021

@author: atosato
"""
from qcodes.plots.pyqtgraph import QtPlot
from qtutils.measurements.sweep_seq import sweep_seq
import weakref
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import os


class Sweep:
    _pltwindows = {}
    # base_dir = None
    file_label = None
    def __init__(self, sweep_params, plot_params, location=None):
        if Sweep.base_dir:
            os.chdir(Sweep.base_dir) #directory where data are saved
            # print('base_dir ', Sweep.base_dir)
        if not isinstance(sweep_params, list):
            sweep_params = [sweep_params]
        self.d = sweep_params[0].root_instrument
        self.save_params = self.get_device_params()
        self.sweep_params = sweep_params
        self.plot_params = plot_params
        self.settable_params = self.settable_params()
        # self.location = Sweep.location

    def run(self, sweep_ranges, cw=True, delays=0, tasks=None):
        if not isinstance(sweep_ranges[0], list):
            sweep_ranges = [sweep_ranges]
        figsize = [350*len(self.plot_params), 250]
        param_names = [i.name for i in self.sweep_params]
        self.plot_window = self.find_create_pltwindow(param_names, figsize)
        self.plot_window.win.setWindowState(Qt.WindowNoState)
        sweep_param_ranges = list(zip(self.sweep_params,sweep_ranges))
        # if len(self.save_params)>1:
        #     self.add_linecut_viewer()
        # loc, lbl  = self.get_loc_label()
        sweep_seq(
            # base_dir = Sweep.location,
            # file_label = lbl,
            outputs = self.save_params,
            sweep_param_ranges = sweep_param_ranges,       
            plot_param_ls = self.plot_params,
            clearwindow = cw, liveplotwindow = self.plot_window,
            delays=delays,  tasks=tasks
        )
        
        
    def get_device_params(self)->list:
        params = self.d.parameters.copy()
        params.pop('IDN')
        # params.pop('repetitions')
        return list(params.values())
    
    
    def settable_params(self)->dict:
        settable_params = {}
        for name,param in self.d.parameters.items():
            if param.settable:
                settable_params['name'] = param
        return settable_params
    
    
    @classmethod
    def find_create_pltwindow(cls, param_names, figsize):
        pltw_ref = '-'.join(param_names)
        if pltw_ref in cls._pltwindows.keys():
            pltw = cls._pltwindows[pltw_ref]()
        else:
            pltw = QtPlot(theme=((60, 60, 60), 'k', ),
                          figsize=figsize,show_window=True, 
                          window_title=pltw_ref+' sweeps', remote=True,
                          )
            wr = weakref.ref(pltw)
            cls._pltwindows[pltw_ref] = wr
        return pltw

    @classmethod
    def get_loc_label(cls):
        return[cls.location, cls.file_label]

    
    
    def add_linecut_viewer(self):
        pltw = self.plot_window
        infline = pg.InfiniteLine(movable=True, hoverPen=dict(width=5))
        pltw.subplots[0].addItem(infline)
        
        def update(): 
            if not pltw.linecut_view:
                pltw.win.setFixedHeight(pltw.win.geometry().height()+100)
                pltw.win.addPlot(row=1,col=0,rowspan=2, colspan=3)
                pltw.win.getItem(1,0).setFixedHeight(200)
                pltw.linecut_view = True
            # get the roi selected data from image view 1 
            x_line = infline.getPos()[0]*len(x)/abs(x[-1]-x[0])
            z_cut = pg.affineSlice(z, shape=(len(y),), origin=(x_line,0), vectors=((0,1),), axes=(0,1))
            # update the image view 2 data 
            pltw.win.getItem(1,0).plot(y,z_cut, clear=True) #is clear=True the most efficient way to do this?
            # plotWidget.show()   
            # print([x_line, z_cut[0]])
    
        infline.sigDragged.connect(update)
    
    