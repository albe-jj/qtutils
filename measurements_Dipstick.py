# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:51:19 2021

@author: atosato
"""

from qcodes import Station, Monitor
from qcodes import Instrument
from importlib import reload
from stations.Dipstick.device_config import DevConfig
from measurement_sweeps import Sweep
from sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task
import time
import os


# initialize the station
station_config_path = r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\Measurement script\stations\Dipstick\config_station.yaml'
if Station.default is None:
    station = Station(config_file=station_config_path)
else: station = Station.default

station.load_lia1()
station.load_lia2()
station.load_lia3()
station.load_ivvi()
station.load_keithley()
# station.load_magnet()
# station.magnet.unit('TESLA') #add this in yaml config file

Sweep.base_dir =  r'G:\Albo' # directory where data are saved
#%% Configure virtual device
# reload(dvcfg)
dev_config = DevConfig()
d = Instrument.find_instrument('d') # make sure you close prev instances of d
zero_ivvi = station.ivvi.set_dacs_zero
station.lia1.frequency(17)
# station.lia1.amplitude(1)
#%% 1D sweep
break_at_leakage = BreakIf(lambda: abs(d.I_leak())>2) #leakage in nA

Vgsweep = Sweep(sweep_params=d.Vg, plot_params=[d.R, d.G, d.I_AC, d.V_AC, d.I_leak])
Vcgsweep = Sweep(sweep_params=d.Vcg, plot_params=[d.G, d.R, d.I_AC, d.V_AC, d.I_leak])
# Bsweep = Sweep(sweep_params=d.field, plot_params=[d.Rsq, d.Rxy, d.I_AC, d.V_AC, d.Vxy_AC])
timesweep = Sweep(sweep_params=d.reps, plot_params=[d.G, d.R, d.I_AC, d.V_AC])

#%% 2D sweep
Vcg_reps = Sweep(sweep_params=[d.Vcg, d.reps], plot_params=[d.G, d.I_AC, d.V_AC])
# V_AC2Dsweep = Sweep(sweep_params=[d.V_AC_bias, d.Vg], plot_params=[d.I_AC, d.V_AC, d.R])
# V_AC2Dsweep.run([[0,100,1],[0,5,1]], cw=1)
# Vg_field_2Dsweep =  Sweep(sweep_params=[d.Vg, d.field], plot_params=[d.Rsq, d.Rxy, d.I_AC])

#%% Run sweep
Vgsweep.run([d.Vg(),-4000,20], task_list=[break_at_leakage], cw=1)
Vcgsweep.run([d.Vcg(),2500,5], delays=[0], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-500,5], delays=[0], task_list=[break_at_leakage], cw=0)


d.Vcg(1500)
timesweep.run([0,60*5,1], delays=[1])

# Bsweep.run([d.field(),2000,10], cw=0)

# d.field(0)
# Vcgsweep.run([d.Vcg(),500,5], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-4500,15], task_list=[break_at_leakage], cw=0)



#%% Run 2D sweeps
# Vg_field_2Dsweep.run([[-3600,-4000,5],[300,-100,100]], delays=[.3,10])
Vcg_reps.run([[0,-1300,5],[0,3,1]], delays=[.0,10], cw=1)
Vcg_reps.run([[-1300,0,5],[0,3,1]], delays=[.0,10], cw=1)



#%% Check QPCs
Vgsweep.run([d.Vg(),-3500,20], task_list=[break_at_leakage], cw=1)
# Vcg_reps.run([[1500,-1500,15],[0,4,1]], delays=[.0,30], cw=1)
Vcg_reps.run([[-1000,1500,10],[0,3,1]], delays=[.0,30], task_list=[break_at_leakage], cw=1)

Vgsweep.run([d.Vg(),-4000,20], task_list=[break_at_leakage], cw=1)
# Vcg_reps.run([[1500,-1500,15],[0,4,1]], delays=[.0,30], cw=1)
Vcg_reps.run([[-1000,1700,10],[0,3,1]], delays=[.0,30], task_list=[break_at_leakage], cw=1)

Vgsweep.run([d.Vg(),-4500,20], task_list=[break_at_leakage], cw=0)
# Vcg_reps.run([[1500,-500,7],[0,4,1]], delays=[.0,30], cw=1)
Vcg_reps.run([[-1000,1700,10],[0,3,1]], delays=[.0,30], task_list=[break_at_leakage], cw=1)

Vgsweep.run([d.Vg(),-5000,20], task_list=[break_at_leakage], cw=0)
# Vcg_reps.run([[2000,-500,7],[0,4,1]], delays=[.0,30], cw=1)
Vcg_reps.run([[-1200,1500,20],[0,3,1]], delays=[.0,30], task_list=[break_at_leakage], cw=1)

#%% test
break_at_target = BreakIf(lambda: d.Vcg()>50) #leakage in nA
Vcg_reps.run([[0,100,10],[0,3,1]], delays=[.0,0], task_list=[], cw=1)
