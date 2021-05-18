# -*- coding: utf-8 -*-
"""
Created on Wed May 12 12:26:47 2021

@author: atosato
"""
from qcodes import Parameter
from qcodes.loops import Loop, BreakIf, Task, ActiveLoop
from qcodes.plots.pyqtgraph import QtPlot
from sweep_seq import sweep_seq
import time

liveplot = QtPlot(theme=((60, 60, 60), 'k', ))
brk_tsk1 = BreakIf(lambda: reps1()>5)
brk_tsk2 = BreakIf(lambda: reps2()>3)

def _get_p1():
    time.sleep(.01)
    return reps1()

def _get_p2():
    time.sleep(.01)
    return reps2()

reps1 = Parameter('reps1', get_cmd=None, set_cmd=None, inter_delay=0)
reps2 = Parameter('reps2', get_cmd=None, set_cmd=None, inter_delay=0)

param1 = Parameter('param1', get_cmd=_get_p1, inter_delay=0)
param2 = Parameter('param2', get_cmd=_get_p1, inter_delay=0)


#%%
tasks = [[brk_tsk1], [brk_tsk2]]
data = sweep_seq([param1,param2], 
                  sweep_param_ranges=[(reps1,[0,11,1]), (reps2,[0,7,1])], 
                  tasks = tasks,
                  liveplotwindow=liveplot, 
                  plot_param_ls=[param1], 
                  clearwindow=1,
                  use_threading=1)

#%%