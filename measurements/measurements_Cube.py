# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:51:19 2021

@author: atosato
"""
import os
os.chdir(r'F:\Albo_Cube\qtutils\measurements')
from qcodes import Station, Monitor
from qcodes import Instrument
from importlib import reload
from qtutils.measurements.stations.Cube.device_config import DevConfig
from qtutils.measurements.measurement_sweeps import Sweep
from qtutils.measurements.sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task
import time
from functools import partial
import logging


# initialize the station
station_config_path = r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\Measurement script\stations\Cube\config_station.yaml'
if Station.default is None:
    station = Station(config_file=station_config_path)
else: 
    station = Station.default

station.load_ivvi()
station.load_lia1()
station.load_lia2()
station.load_lia3()
station.load_keithley1()
station.load_magnet()

# station.magnet.log.setLevel(level=logging.DEBUG)
#%% Configure virtual device
# reload(dvcfg)
dev_config = DevConfig()
d = Instrument.find_instrument('d') 
zero_ivvi = station.ivvi.set_dacs_zero
station.lia3.frequency(17)
#%% 1D sweep

Sweep.base_dir = r'F:\Albo_Cube'
# Sweep.file_label = 'SQ21-72-1_LF1_S3_D2'/

break_at_leakage = BreakIf(lambda: abs(d.I_leak())>10) #leakage in nA

Vgsweep = Sweep(sweep_params=d.Vg, plot_params=[d.Rsq, d.I_AC, d.V_AC, d.I_leak])
# Vcgsweep = Sweep(sweep_params=d.Vcg, plot_params=[d.G, d.R, d.I_AC, d.V_AC, d.I_leak])
# VDCsweep = Sweep(sweep_params=d.V_DC_bias, plot_params=[d.G, d.I_AC, d.V_AC, d.V_DC, d.I_DC])

Bsweep = Sweep(sweep_params=d.field, plot_params=[d.Rsq, d.Rxy, d.I_AC, d.V_AC, d.Vxy_AC, d.B_meas])
reps_sweep = Sweep(sweep_params=d.reps, plot_params=[d.field, d.Rsq, d.Rxy, d.I_AC, d.V_AC, d.Vxy_AC])
# timesweep = Sweep(sweep_params=d.repetitions, plot_params=[d.Rsq, d.I_AC, d.V_AC])

#%% 2D sweep
Vg_reps = Sweep(sweep_params=[d.Vg, d.reps], plot_params=[d.Rsq, d.Rxy, d.I_AC])
reps_Vg = Sweep(sweep_params=[d.reps, d.Vg], plot_params=[d.Rsq, d.Rxy, d.I_AC])
# VDC_field_sweep = Sweep(sweep_params=[d.V_DC_bias, d.field], plot_params=[d.R, d.V_DC, d.I_DC])
# VDC_Vcg_sweep = Sweep(sweep_params=[d.V_DC_bias, d.Vcg], plot_params=[d.G, d.I_AC, d.V_AC])


# V_AC2Dsweep = Sweep(sweep_params=[d.V_AC_bias, d.Vg], plot_params=[d.I_AC, d.V_AC, d.R])
# V_AC2Dsweep.run([[0,100,1],[0,5,1]], cw=1)
Vg_field_2Dsweep =  Sweep(sweep_params=[d.Vg, d.field], plot_params=[d.Rsq, d.Rxy, d.I_AC, d.field])

#%% Run sweep

Vgsweep.run([-3000,-3300,3], tasks=[[break_at_leakage]], cw=0)
d.Vg(-3000)
Vgsweep.run([-1000,-700,3], tasks=[[break_at_leakage]], cw=0)
d.Vg(-700)

# Vgsweep.run([d.Vg(),-3120,.5], task_list=[break_at_leakage], cw=0)

# Vcgsweep.run([d.Vcg(),-870,3], delays=[0], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-500,5], delays=[0], task_list=[break_at_leakage], cw=0)
# VDCsweep.run([-10,20,2], cw=0)



# timesweep.run([0,300,1], delays=[1])

Bsweep.run([-0.1,0.1,0.050], cw=1) #in Tesla

# d.field(0)
# d.field(0)
# Vcgsweep.run([d.Vcg(),500,5], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-4500,15], task_list=[break_at_leakage], cw=0)
# Bsweep_quick_dirty(9)


#%% Run 2D sweeps
# Vg_field_2Dsweep.run([[-2900,-3300,1.3],[9,-0.4,0.04]], delays=[.3,10], cw=1)
Vg_field_2Dsweep.run([[-3000,-3301.5,1.5],[-0.2,9,0.050]], delays=[0.05,10], cw=1)
d.field(0)
d.Vg(-1000)
# Vcg_reps.run([[0,-1600,3],[0,5,1]], delays=[.3,3], cw=1)
# VDC_Vcg_sweep.run([[-1200,1200,12],[-900,-1500,10]], delays=[.3,3], cw=1)

# VDC_field_sweep.run([[-300,300,3],[0,615,20]], delays=[0,5], cw=1)

#%% Bsweep quick and dirty
def Bsweep_quick_dirty(B_start, B_stop, mins=10):
    break_at_target = BreakIf(lambda: (d.field())==B_stop)
    B_to_start_and_sweep_to_stop(B_start, B_stop)
    reps_sweep.run([0, mins*60, 0.1], delays=[.1], tasks=[[break_at_target]], cw=1) #in Tesla

def Bsweep_quick_dirty_2D(B_start, B_stop, Vg_params, mins=15):
    break_at_target = BreakIf(lambda: (d.field())==B_stop)
    B_task = Task(partial(B_to_start_and_sweep_to_stop,B_start, B_stop))
    B_to_start_and_sweep_to_stop(B_start, B_stop)
    reps_Vg.run([[0, mins*60, 0.1],Vg_params ], delays=[.1,0], tasks=[[break_at_target],[B_task]], cw=1) #in Tesla

def B_to_start_and_sweep_to_stop(B_start, B_stop):
    station.magnet.wait_field_to_target = True
    d.field(B_start)
    station.magnet._go_to_target(B_stop, wait_field_to_target=False, atol=0.0001)
    
#%% Run quick B sweeps

Bsweep_quick_dirty_2D(B_start=-0.3, B_stop=0.3, Vg_params=[-3180,-3490,5], mins=5)
d.field(0)

Bsweep_quick_dirty(B_start=-0.3, B_stop=0.3, mins=5)
d.field(0)
