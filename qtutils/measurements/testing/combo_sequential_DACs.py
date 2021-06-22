# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 11:41:30 2020

@author: atosato
"""

from measurement.sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.instrument.parameter import Parameter
import numpy as np
import qcodes

ech = 1.60217662e-19 #coulombs
h = 6.62607004e-34 #m2 kg / s
kB = 86 #ueV/K

def gt():
    return np.random.randint(100)


reps1 = qcodes.Parameter('reps1', set_cmd=None, inter_delay=.1)
reps2 = qcodes.Parameter('reps2', set_cmd=None, inter_delay=.1)
param3 = qcodes.Parameter('reps1', set_cmd=None, get_cmd=gt, inter_delay=1)


    
#%%
def set_cmd(value):
        if abs(param_ls[0]())<10:
            param_ls[0](value)
        if abs(param_ls[0]())>=10:
            param_ls[1](value-param_ls[0]())
        return sum([p() for p in param_ls])
    
def get_cmd():
    return sum([p() for p in param_ls])
reps1(0)
reps2(0)
param_ls = [reps1, reps2]

#combo_reps = qcodes.Parameter('reps1', 
#                              set_cmd=set_cmd, inter_delay=.5)
#combo_reps.step = 1
combo_reps = Parameter('c', set_cmd=set_cmd, get_cmd=get_cmd, inter_delay=.1, step=1)
combo_reps(0)

liveplot= QtPlot()
sweep_seq([combo_reps,reps1,reps2],[(combo_reps,[0,20,1])], liveplotwindow=liveplot)

#%%
class Paral_DACs(Parameter):
    def __init__(self, param_ls, max_val):
        self.param_ls = param_ls
        self.max_val = max_val
        super().__init__('paral_dacs')
    
    def get_raw(self):
        return sum([p() for p in self.param_ls])
    
    def set_raw(self, value):
        max_val = self.max_val
        sgn = np.sign(value)
        for idx,p in enumerate(self.param_ls):
            if abs(value) > (max_val * (idx+1)):
                p(sgn*max_val)
                print(f'set param{idx+1} to {p()}')
            elif (max_val * (idx)) <= abs(value) <= (max_val * (idx+1)):
                p(value - sgn*max_val*idx)
                print(f'set param{idx+1} to {p()}')
            elif abs(value) <= (max_val * (idx+1)):
                p(0)
                print(f'set param{idx+1} to {p}')
                return

#%%
cmb = Paral_DACs([reps1,reps2], max_val=10)
cmb(-15)

#%%
from qcodes.utils.validators import Numbers
class Mps_spi(Instrument):
    def __init__(self, name, S4g, num_dacs=1, **kwargs):
        self.S4g = S4g
        self.num_dacs = num_dacs
        self.max_val = .05
        
        super().__init__(name)
        validator = Numbers(-self.max_val*num_dacs, self.max_val*num_dacs)
        
        for i in range(num_dacs):
            S4g[f'span{i+1}']('range_max_bi')
            
        self.dac_ls = [S4g[f'dac{i+1}'] for i in range(num_dacs)] 
        
        self.add_parameter('current',
                           label='current',
                           get_cmd=self._get_current,
                           set_cmd=self._set_current,
                           vals=validator)
        
        
    
    def _get_current(self):
        return sum([p() for p in self.dac_ls])
        
    def _set_current(self, value):
        max_val = self.max_val
        sgn = np.sign(value)
        for idx,p in enumerate(self.dac_ls):
            if abs(value) > (max_val * (idx+1)):
                p(sgn*max_val)
                print(f'set dac{idx+1} to {p()}')
            elif (max_val * (idx)) <= abs(value) <= (max_val * (idx+1)):
                p(value - sgn*max_val*idx)
                print(f'set dac{idx+1} to {p()}')
            elif abs(value) <= (max_val * (idx+1)):
                p(0)
                print(f'set param{idx+1} to {p()}')
                return


        
#%%
Instrument.find_instrument('t1').close()
mps = Mps_spi('t1', station.S4g, num_dacs=2)
        
        
        