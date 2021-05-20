# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:51:19 2021

@author: atosato
"""

from qcodes import Station, Monitor, Parameter
from qcodes import Instrument
from importlib import reload
from stations.Leiden.device_config import DevConfig
from measurement_sweeps import Sweep
from sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task
import time
from pyvisa import ResourceManager
import os
os.chdir(r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\Measurement script')

rm = ResourceManager()


# initialize the station
station_config_path = r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\Measurement script\stations\Leiden\config_station.yaml'
if Station.default is None:
    station = Station(config_file=station_config_path)
else: 
    station = Station.default
    station.spi.spi_rack.close()

station.load_ivvi()
station.load_spi()
station.load_lia1()
station.load_lia2()
station.load_lia3()
station.load_keithley1()
station.load_keithley2()
station.load_keithley3()
# station.load_magnet()
station.load_temp_control()
station.load_S4g(spi_rack=station.spi.spi_rack)
station.load_U2(spi_rack=station.spi.spi_rack)
station.load_cryomux()
# station.magnet.unit('TESLA') #add this in yaml config file

station.U2.span1('4v bi')#?!  
station.cryomux.set_voltages_U2_minimum()

Sweep.base_dir = r'D:\Albo_LF'



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
#%% 1D sweep

# Sweep.location = None #r'D:\LeidenMCK50_fridge\Scripts\Albo\data'
# Sweep.file_label = 'SQ21-72-1_LF1_S3_D2'

break_at_leakage = BreakIf(lambda: abs(d.I_leak())>2) #leakage in nA

Vgsweep = Sweep(sweep_params=d.Vg, plot_params=[d.R, d.I_AC, d.V_AC, d.I_leak])
Vcgsweep = Sweep(sweep_params=d.Vcg, plot_params=[d.G, d.R, d.I_AC, d.V_AC, d.I_leak])
VDCsweep = Sweep(sweep_params=d.V_DC_bias, plot_params=[d.G, d.I_AC, d.V_AC, d.V_DC, d.I_DC])
IDCsweep = Sweep(sweep_params=d.I_DC_bias, plot_params=[d.R, d.I_AC, d.V_AC, d.V_DC])

Bsweep = Sweep(sweep_params=d.field, plot_params=[d.R, d.I_AC, d.V_AC])
# timesweep = Sweep(sweep_params=d.repetitions, plot_params=[d.Rsq, d.I_AC, d.V_AC])
# timesweep = Sweep(sweep_params=d.reps, plot_params=[d.He])

#%% 2D sweep
Vcg_reps = Sweep(sweep_params=[d.Vcg, d.reps], plot_params=[d.G, d.I_AC, d.V_AC])
# VDC_field_sweep = Sweep(sweep_params=[d.V_DC_bias, d.field], plot_params=[d.R, d.V_DC, d.I_DC])
VDC_Vcg_sweep = Sweep(sweep_params=[d.V_DC_bias, d.Vcg], plot_params=[d.G, d.I_AC, d.V_AC])
IDC_Vg_sweep = Sweep(sweep_params=[d.I_DC_bias, d.Vg], plot_params=[d.R, d.V_AC, d.V_DC])
VDC_Vg_sweep = Sweep(sweep_params=[d.V_DC_bias, d.Vg], plot_params=[d.G, d.I_AC, d.V_DC])



# V_AC2Dsweep = Sweep(sweep_params=[d.V_AC_bias, d.Vg], plot_params=[d.I_AC, d.V_AC, d.R])
# V_AC2Dsweep.run([[0,100,1],[0,5,1]], cw=1)
# Vg_field_2Dsweep =  Sweep(sweep_params=[d.Vg, d.field], plot_params=[d.Rsq, d.Rxy, d.I_AC])

#%% Run sweep
Vgsweep.run([d.Vg(),-3500,10], task_list=[break_at_leakage], cw=0)
# Vcgsweep.run([d.Vcg(),-870,3], delays=[0], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-500,5], delays=[0], task_list=[break_at_leakage], cw=0)
VDCsweep.run([-200,200,1], cw=5)
# IDCsweep.run([-150,150, .5], cw=1)


# timesweep.run([0,3600*15,1], delays=[10])

Bsweep.run([5.66,-5.66,.1], cw=0)

# d.field(0)
# Vcgsweep.run([d.Vcg(),500,5], task_list=[break_at_leakage], cw=1)
# Vcgsweep.run([d.Vcg(),-4500,15], task_list=[break_at_leakage], cw=0)



#%% Run 2D sweeps
# IDC_Vg_sweep.run([[-150,150,1], [-3500,-2000,10]], delays=[.3,5])
VDC_Vg_sweep.run([[-100,120,3], [-2135,-2220,5]], delays=[.1,3])
# Vg_field_2Dsweep.run([[-3600,-4000,5],[300,-100,100]], delays=[.3,10])
# Vcg_reps.run([[0,-1600,3],[0,5,1]], delays=[.3,3], cw=1)
# VDC_Vcg_sweep.run([[-1200,1200,12],[-900,-1500,10]], delays=[.3,3], cw=1)

# VDC_field_sweep.run([[-300,300,3],[0,615,20]], delays=[0,5], cw=1)

#%%
