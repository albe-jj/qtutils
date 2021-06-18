# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:51:19 2021

@author: atosato
"""
import os
os.chdir(r'D:\Albo_LF')
from qcodes import Station, Monitor, Parameter
from qcodes.instrument.specialized_parameters import ElapsedTimeParameter
from qcodes import Instrument
from importlib import reload
from qtutils.measurements.stations.Leiden.device_config import DevConfig
from qtutils.measurements.measurement_sweeps import Sweep
from qtutils.measurements.param_viewer.param_viewer_GUI_main import param_viewer
from qtutils.measurements.drivers import lia_utils

from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task
from qcodes.loops import Loop
import time
from pyvisa import ResourceManager
from functools import partial
import numpy as np
# os.chdir(r'D:\Albo_LF\qtutils\measurements')

rm = ResourceManager()


# initialize the station
station_config_path = r'D:\Albo_LF\qtutils\measurements\stations\Leiden\config_station.yaml'
if Station.default is None:
    station = Station(config_file=station_config_path)
else: 
    station = Station.default
    if 'spi' in list(station.components): station.spi.spi_rack.close()
    pw.close()

station.load_ivvi()
station.load_spi()
station.load_lia1()
station.load_lia2()
station.load_lia3()
station.load_lia4()
station.load_lia5()
station.load_keithley1()
station.load_keithley2()
station.load_keithley3()
# station.load_sourcemeter()
station.load_magnet() #cryogenics MPS
# station.load_temp_control()
station.load_front_panel()
station.load_S4g(spi_rack=station.spi.spi_rack)
station.load_Paral_S4g(num_dacs=4, S4g=station.S4g)
station.load_U2(spi_rack=station.spi.spi_rack)
station.load_cryomux()
# station.magnet.unit('TESLA') #add this in yaml config file

#mps with Keithley source meter
# station.sourcemeter.smua.mode('current')
# station.sourcemeter.smua.limitv(5)
# station.sourcemeter.smua.sourcerange_i(1.5) #source_autorange_i_enabled()
# station.sourcemeter.smua.output(True)

station.U2.span1('4v bi')#?!  
station.cryomux.set_voltages_U2_minimum()

# Sweep.loc = 'D:\Albo_LF\data'
lia_int_time = .1
[station[i] for i in ['lia1', 'lia2', 'lia3'] ]

#%% Configure virtual device
# reload(dvcfg)
dev_config = DevConfig()
d = Instrument.find_instrument('d') 
zero_ivvi = station.ivvi.set_dacs_zero
station.lia1.frequency(17)
station.keithley1.integrationtime(.1)
station.keithley2.integrationtime(.2)

keithley_He = rm.open_resource('GPIB::26')
get_He_level = lambda: round(float(keithley_He.read().strip()[4:])/2*1e3-4)
# d.add_parameter('He', get_cmd=get_He_level)
# param_ls=['Vg', 'Vcg', 'V_DC_bias', 'field', 'I_DC_bias','still_current','mc_current', 'temp']
param_ls=['Vg', 'field']
pw = param_viewer(station=station, gates_object=d, param_ls=param_ls)

timee = ElapsedTimeParameter('time')
timee.reset_clock()
#%% Tasks
break_at_leakage = BreakIf(lambda: abs(d.I_leak())>2) #leakage in nA

#autorange lia
autorange_V_AC = Task(partial(lia_utils.autorange_lia, station.lia1))
autorange_I_AC = Task(partial(lia_utils.autorange_lia, station.lia2))
zero_gate_wait = Task()

def zero_Vg():
    d.Vg(0)
    time.sleep(3)
    
    

# def reduce_still_heater():
#     still = still()
#     while still>1.05e-1
#         still(still-10)
#         sleep(5)

def zero_all():
    d.Vg(0)
    d.field(0)
    d.mc_current(0)
    d.I_DC_bias(0)
    d.V_DC_bias(0)
    d.Vcg(0)

#%% quick
Vgsweep = Sweep(sweep_params=d.Vg, plot_params=[d.Rsq, d.I_AC, d.V_AC, d.I_leak])
Vg_field_sweep =  Sweep(sweep_params=[d.Vg, d.field], plot_params=[d.Rsq, d.Rxy, d.I_AC])



#%% 1D sweep

# Sweep.location = None #r'D:\LeidenMCK50_fridge\Scripts\Albo\data'
# Sweep.file_label = 'SQ21-72-1_LF1_S3_D2'

Vgsweep = Sweep(sweep_params=d.Vg, plot_params=[d.Rsq, d.I_AC, d.V_AC, d.I_leak])
Vcgsweep = Sweep(sweep_params=d.Vcg, plot_params=[d.G, d.R, d.I_AC, d.V_AC, d.I_leak])
VDCsweep = Sweep(sweep_params=d.V_DC_bias, plot_params=[d.R, d.G, d.I_AC, d.V_AC, d.I_DC])
IDCsweep = Sweep(sweep_params=d.I_DC_bias, plot_params=[d.R, d.I_AC, d.V_AC, d.V_DC])

Bsweep = Sweep(sweep_params=d.field, plot_params=[d.Rsq, d.Rxy, d.V_AC, d.Vxy_AC, d.I_DC])
# timesweep = Sweep(sweep_params=d.repetitions, plot_params=[d.Rsq, d.I_AC, d.V_AC])
timesweep = Sweep(sweep_params=d.reps, plot_params=[d.temp, d.V_AC_therm, d.I_AC_therm])

temp_sweep = Sweep(sweep_params=d.mc_current, plot_params=[d.temp, d.R, d.V_AC])

#%% 2D sweep

Vg_temp_sweep = Sweep(sweep_params=[d.Vg, d.mc_current], plot_params=[d.R, d.V_AC, d.V_DC, d.temp])
Vg_field_sweep =  Sweep(sweep_params=[d.Vg, d.field], plot_params=[d.Rsq, d.Rxy, d.I_AC])

Vcg_reps = Sweep(sweep_params=[d.Vcg, d.reps], plot_params=[d.G, d.I_AC, d.V_AC])
Vcg_field_sweep = Sweep(sweep_params=[d.Vcg, d.field], plot_params=[d.G, d.I_AC, d.V_AC])

VDC_field_sweep = Sweep(sweep_params=[d.V_DC_bias, d.field], plot_params=[d.G, d.I_AC, d.V_AC])
VDC_Vcg_sweep = Sweep(sweep_params=[d.V_DC_bias, d.Vcg], plot_params=[d.G, d.I_AC, d.V_AC])
IDC_Vg_sweep = Sweep(sweep_params=[d.I_DC_bias, d.Vg], plot_params=[d.R, d.V_AC, d.V_DC])
VDC_Vg_sweep = Sweep(sweep_params=[d.V_DC_bias, d.Vg], plot_params=[d.G, d.I_AC, d.V_DC])
VDC_reps = Sweep(sweep_params=[d.V_DC_bias, d.reps], plot_params=[d.G, d.I_AC, d.V_AC])

IDC_temp_sweep = Sweep(sweep_params=[d.I_DC_bias, d.mc_current], plot_params=[d.R, d.V_AC, d.V_DC, d.temp])
IDC_field_sweep = Sweep(sweep_params=[d.I_DC_bias, d.field], plot_params=[d.R, d.V_AC, d.V_DC])

field_temp_sweep = Sweep(sweep_params=[d.field, d.mc_current], plot_params=[d.R, d.V_AC, d.V_DC])

# V_AC2Dsweep = Sweep(sweep_params=[d.V_AC_bias, d.Vg], plot_params=[d.I_AC, d.V_AC, d.R])
# V_AC2Dsweep.run([[0,100,1],[0,5,1]], cw=1)


#%%

# B=0 at -3.35 mT
# IDC = 0 : d.I_DC_bias(-0.12) 
#%% Run sweep
d.Vg(0)
time.sleep(3)
Vgsweep.run([-2230,-2500,3], delays=[0.1], tasks=[[break_at_leakage]],cw=1) 
d.Vg(-2230)
#tasks=[[autorange_V_AC, autorange_I_AC]]

# Vcgsweep.run([d.Vcg(),-800,15], delays=[0], tasks=[[break_at_leakage]], cw=1)

# VDCsweep.run([-300,300,10], cw=1)

# IDCsweep.run([-800,800,10], delays=[0], cw=1)


# timesweep.run([0,3600*15,1], delays=[1])


# Bllim=-12
# Bulim=6
# d.field(-Blim)
# Bsweep.run([Bllim,Bulim,.09], delays=[1.5], cw=1)
# Bsweep.run([Bulim,Bllim,.09], delays=[1.5], cw=0)


Bsweep.run([-200,3000,5], delays=[.1], cw=1)
d.field(0)



# d.field(0)
# Vcgsweep.run([d.Vcg(),500,5], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-4500,15], task_list=[break_at_leakage], cw=0)

# temp_sweep.run([3820,-10,10], delays=[30], cw=True)


#%% Run 2D sweeps
# IDC_Vg_sweep.run([[-900,900,18], [-1350,-2000,10]], delays=[.1,5])
# VDC_Vg_sweep.run([], delays=[.15,10])

B_arr = np.concatenate([
    np.arange(-200,0,20),
    np.arange(0,1500,5), 
    np.arange(1500,3000,10), 
    np.arange(3000,4000,20),
    np.arange(4000,5000,40),
    np.arange(5000,9000,60)])
len(B_arr)

Vg_field_sweep.run([[-2230,-2500,7],[1600,0,7]], delays=[.1,3])
d.Vg(-2200)


# Vcg_reps.run([[-300,800,5],[0,5,1]], delays=[.2,3], cw=1)
# Vcg_field_sweep.run([[-1000,1000,5],[0,9000,150]], delays=[.2,30])

# VDC_Vcg_sweep.run([[-1200,1200,12],[-900,-1500,10]], delays=[.3,3], cw=1)
# VDC_reps.run([[-300,300,3],[0,10,1]], delays=[.2,3], cw=1)

# VDC_field_sweep.run([[-2000,2000,7], [-3.35,22,.7]], delays=[0.1,5], cw=1)
# IDC_temp_sweep.run([[-120,120,1], [3850,-80,80]], delays=[.1,15*60])

# d.field(-3.35)
# d.still_current(7750)
# IDC_temp_sweep.run([[-200,200,1], [3650,-50,50]], delays=[.1,10*60])

# IDC sweep back and forth
# Ilim = 200
# IDC_temp_sweep.run([[-Ilim,Ilim,1], [3500,-80,80]], delays=[.1,15*60], 
#                    tasks=[[],[Loop(d.I_DC_bias.sweep(Ilim,-Ilim,1)).each(*IDC_temp_sweep.save_params)]])
# IDC_field_sweep.run([[-900,900,7],[-16,10,.1]], delays=[.2,20])

# IDC_field_sweep.run([[-200,200,1],[-16,10,.1]], delays=[.2,20])

# Vg_temp_sweep.run([[-2005,-1200,5],[3820,-50,50]], delays=[.4,10*60],tasks=[[autorange_V_AC],[]])

# mc_arr = np.concatenate([np.arange(0,2000,120), 
#                 np.arange(2000,3500,60),
#                 np.arange(3500,3820,20),
#                ])
# mc_arr = np.flip(mc_arr).tolist()
# print(mc_arr, len(mc_arr) )
# field_temp_sweep.run([[-110,110.6,.7], mc_arr], delays=[.5,10*60])
# field_temp_sweep.run([[-110,110.5,.5], [3635,-50,50]], delays=[.7,10*60])

#%% Developement section


#%% Quick tests



