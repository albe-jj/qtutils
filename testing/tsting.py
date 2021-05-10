# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 17:47:26 2021

@author: atosato
"""
from qcodes import Station, Monitor
from qcodes import Instrument
from dummy_dev_config import DevConfig
from measurement_sweeps import Sweep
from sweep_seq import sweep_seq
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.actions import BreakIf, Task


# Instrument.close_all()

# initialize the station
station_config_path = r'V:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\Measurement script\stations\dummy\config_dummy_station.yaml'
if Station.default is None:
    station = Station(config_file=station_config_path)
else: station = Station.default

station.load_mock_dac()
station.load_mock_Rmeas()
# station.load_instrument('mock_Rmeas') #this 

dev_config = DevConfig()
d = Instrument.find_instrument('d')
# pw = QtPlot()

def run_test():
    break_at_leakage = BreakIf(lambda: d.I_AC()>1)
    VACsweep = Sweep(sweep_params=d.V_AC_bias, plot_params=[d.I_AC, d.V_AC, d.R])
    # d.V_AC_bias(0)
    VACsweep.run([0,10,1], task_list=[break_at_leakage], cw=0)

