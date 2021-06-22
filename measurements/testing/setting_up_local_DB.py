# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 14:30:11 2021

@author: atosato
"""

from core_tools.data.SQL.connect import set_up_local_storage
set_up_local_storage("albo", "123", "test",
	"project_name", "set_up_name", "sample_name")


#%%

from core_tools.drivers.hardware.hardware import hardware
from core_tools.drivers.virtual_dac import virtual_dac
from core_tools.drivers.gates import gates

import qcodes as qc

# generate the dacs
my_dac_1 = virtual_dac("dac_a", "virtual")
my_dac_2 = virtual_dac("dac_b", "virtual")

# add the hardware
hw =  hardware()
hw.dac_gate_map = {
    'B0': (0, 1), 'P1': (0, 2), 
    'B1': (0, 3), 'P2': (0, 4),
    'B2': (0, 5), 'P3': (0, 6), 
    'B3': (0, 7), 'P4': (0, 8), 
    'B4': (0, 9), 'P5': (0, 10),
    'B5': (0, 11),'P6': (0, 12),
    'B6': (0, 13), 'S6' : (0,14,),
    'SD1_P': (1, 1), 'SD2_P': (1, 2), 
    'SD1_B1': (1, 3), 'SD2_B1': (1, 4),
    'SD1_B2': (1, 5), 'SD2_B2': (1, 6),}
hw.boundaries = {'B0' : (0, 2000), 'B1' : (0, 2500)}
hw.virtual_gates.add('test', ['B0', 'P1', 'B1', 'P2', 'B2', 'P3', 'B3', 'P4', 'B4', 'P5', 'B5', 'P6', 'B6', 'S6', 'SD1_P', 'SD2_P'])
hw.awg2dac_ratios.add(hw.virtual_gates.test.gates)
    
my_gates = gates(name="gates", 
                 hardware=hw, #qc.Instrument instance that contains the dac_gate_map
                 dac_sources=[my_dac_1, my_dac_2] # instances of the d5b or ivvi rack
                 )

station=qc.Station(my_dac_1, my_dac_2, my_gates, hw)


#%%

from core_tools.GUI.parameter_viewer_qml.param_viewer import param_viewer

# if gates are not names gates, it needs to be provided as an argument.
ui = param_viewer(my_gates)