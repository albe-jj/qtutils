# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:51:19 2021

@author: atosato
"""

from qcodes import Station, Monitor
from qcodes import Instrument
from importlib import reload
from stations.Cube.device_config import DevConfig
from measurement_sweeps import Sweep
from sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task
import time
from functools import partial


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

#%% Configure virtual device
# reload(dvcfg)
dev_config = DevConfig()
d = Instrument.find_instrument('d') 
zero_ivvi = station.ivvi.set_dacs_zero
station.lia3.frequency(17)
station.keithley1.nplc(1)
#%% 1D sweep

Sweep.base_dir = None #r'D:\LeidenMCK50_fridge\Scripts\Albo\data'
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
Vg_field_2Dsweep =  Sweep(sweep_params=[d.Vg, d.field], plot_params=[d.Rsq, d.Rxy, d.I_AC])

#%% Run sweep

Vgsweep.run([-3180,-3490,3], tasks=[[break_at_leakage]], cw=0)
d.Vg(-3180)
Vgsweep.run([-3160,-3460,3], tasks=[[break_at_leakage]], cw=0)


# Vgsweep.run([d.Vg(),-3120,.5], task_list=[break_at_leakage], cw=0)

# Vcgsweep.run([d.Vcg(),-870,3], delays=[0], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-500,5], delays=[0], task_list=[break_at_leakage], cw=0)
# VDCsweep.run([-10,20,2], cw=0)



# timesweep.run([0,300,1], delays=[1])

Bsweep.run([-.1, .1, 0.020], cw=1) #in Tesla

# d.field(0)
# d.field(0)
# Vcgsweep.run([d.Vcg(),500,5], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-4500,15], task_list=[break_at_leakage], cw=0)
# Bsweep_quick_dirty(9)
#%% Bsweep quick and dirty
def Bsweep_quick_dirty(target):
    break_at_target = BreakIf(lambda: (d.field())==target)
    station.magnet.wait_field_to_target = False
    d.field(target)
    station.magnet.wait_field_to_target = True
    reps_sweep.run([0, 3600*2, 0.1], delays=[.1], task_list=[break_at_target], cw=1) #in Tesla


#%% B vs Vcg 2D map
def set_field_to_target_no_wait(target):
    station.magnet.wait_field_to_target = False
    d.field(target)
    station.magnet.wait_field_to_target = True

def field_Vg_2Dsweep_quick(Vg_params, est_time, field_start, field_stop):
    '''[Vg_start, Vg_stop, step]'''
    
    set_field_task = Task(partial(d.field, field_start))
    set_field_to_target_no_wait_task = Task(partial(set_field_to_target_no_wait, target=field_stop))
    
    d.field(field_start)
    set_field_to_target_no_wait(field_stop)
    reps_Vg.run([[0,est_time, .1],Vg_params], 
                task_list=[set_field_task, set_field_to_target_no_wait_task], 
                delays=[0.1,0])
    
#%% Run B Vg 2D quick
# field_Vg_2Dsweep_quick(Vg_params = [-1100, -1050, 10],
#                        est_time = 10, 
#                        field_start=8.67, field_stop=8.68)
#%% Run 2D sweeps
# Vg_field_2Dsweep.run([[-2900,-3300,1.3],[9,-0.4,0.04]], delays=[.3,10], cw=1)
Vg_field_2Dsweep.run([[-3180,-3490,.7],[-0.3,9,0.020]], delays=[0.05,10], cw=1)
d.field(0)
d.Vg(-3180)
# Vcg_reps.run([[0,-1600,3],[0,5,1]], delays=[.3,3], cw=1)
# VDC_Vcg_sweep.run([[-1200,1200,12],[-900,-1500,10]], delays=[.3,3], cw=1)

# VDC_field_sweep.run([[-300,300,3],[0,615,20]], delays=[0,5], cw=1)
#%%
import time
start = time.time()
for i in range(100):
    d.field()
print(time.time()-start)