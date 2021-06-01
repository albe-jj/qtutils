# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:51:19 2021

@author: atosato
"""

from qcodes import Station, Monitor
from qcodes import Instrument
from dummy_dev_config import DevConfig
from qtutils.measurements.measurement_sweeps import Sweep
from qtutils.measurements.sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task
from qcodes.instrument.parameter import CombinedParameter
from qcodes.loops import Loop

# Instrument.close_all()

# initialize the station
station_config_path = r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\qtutils\measurements\stations\dummy\config_dummy_station.yaml'
if Station.default is None:
    station = Station(config_file=station_config_path)
else: station = Station.default

station.load_mock_dac()
station.load_mock_Rmeas()
# station.load_instrument('mock_Rmeas') #this 

dev_config = DevConfig()
d = Instrument.find_instrument('d')

 
# pw = QtPlot()

#%% Combined params
import qcodes as qc
cp = qc.combine(station.mock_dac.ch1, station.mock_dac.ch2, name='tst')

#%% my sweeep function
from qcodes.loops import Loop
import pyqtgraph as pg

pltw = pg.plot()
pltitem = pltw.plot() #Create new plotitem or trace

def update_plot():
      pltitem.setData(x=data.arrays['d_V_AC_bias_set'],y=data.arrays['d_I_AC'], clear=False)
     # print(data.arrays['d_I_AC'])
plt_update_tsk = Task(update_plot)

loop = Loop(d.V_AC_bias.sweep(1,10,num=10), delay=0).each(plt_update_tsk, d.I_AC)

# loop = Loop(d.V_AC_bias.sweep(1,10,num=10), delay=0)
# loop = loop.loop(d.Vg.sweep(0,1,num=10), delay=0).each(plt_update_tsk, d.I_AC)
data = loop.run()
# plt.plot(x=data.arrays['d_V_AC_bias_set'],y=data.arrays['d_I_AC'], clear=False)

#%% 1D sweep
break_at_leakage = BreakIf(lambda: d.I_AC()>1)
Sweep.base_dir=None
VACsweep = Sweep(sweep_params=d.V_AC_bias, plot_params=[d.I_AC, d.V_AC, d.R])
# d.V_AC_bias(0)
VACsweep.run([0,10,1], cw=0)


#%%
# Vg_sweep = Sweep(sweep_params=d.Vg, plot_params=[d.I_AC, d.V_AC, d.R])
# Vg_sweep.run([0,10,1])

#%% 2D sweep
# V_AC2Dsweep = Sweep(sweep_params=[d.V_AC_bias, d.Vg], plot_params=[d.I_AC, d.V_AC, d.R])
# d.V_AC_bias(0)
# V_AC2Dsweep.run([[0,100,1],[0,5,1]], cw=1)
VAC_Vg_2Dsweep_return = Sweep(sweep_params=[d.V_AC_bias, d.Vg], plot_params=[d.I_AC, d.V_AC, d.R])

VAC_vals = [0,10,1]
VAC_Vg_2Dsweep_return.run([VAC_vals, [0,100,10]], tasks=[[],[Loop(d.Vg.sweep(0,10,num=10)).each(d.R)]])
#%%
# sweep_seq(
#             outputs = [d.I_AC],
#             sweep_param_ranges = [(d.V_AC_bias, [0, 100,1])],       
#             plot_param_ls = [d.I_AC],
#             clearwindow = 1, liveplotwindow = pw,
#             delay=0
#         )
# QtPlot(figsize=[1000,400])


#%% Developement
loop1 = Loop(d.V_AC_bias.sweep(1,100,num=10), delay=0).each(d.R)
loop2 = Loop(d.V_AC_bias.sweep(1,100,num=10), delay=0).each(d.R)
loop = Loop(d.Vg.sweep(1,10,num=10), delay=0).each(loop1,loop2)
loop.run()
#%%
loop = Loop(d.Vg.sweep(1,100,num=10)).each(Loop(d.Vg.sweep(0,10,num=10)).each(d.R), d.I_AC)
loop.run()