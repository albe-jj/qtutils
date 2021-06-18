# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 16:27:26 2020

@author: TUD278249
"""


import sys
import time
from qcodes_contrib_drivers.drivers.QuTech.IVVI import IVVI
from qcodes import Instrument
# from device import Device
import logging
from qtutils.measurements.stations.Leiden.drivers import LCApp

sys.path.append(r'D:\LeidenMCK50_fridge\Scripts\Albo')
from drivers.LCApp import LVApp
# from drivers.DRTempControl import DRTempControl
from pyvisa import ResourceManager

#%% gains current sources
Istill_gain = 20e-3 #A/V
Imc_gain = 20e-3 #A/V

#%% connect to instruments
lcapp_temp = LVApp(r"DRTempControl.Application",r"DR TempControl.exe\TC.vi")
T_mc = lambda: lcapp_temp.GetData('T')[2]
T_still = lambda: lcapp_temp.GetData('T')[1]

lcapp_panel = LVApp(r"DRFrontPanel.Application",r"DR FrontPanel.exe\FP.vi")
P_still = lambda: lcapp_panel.GetData('MG Data')[-1]

# if Instrument.exist('heaters'):
#     Instrument.find_instrument('heaters').close()
#     Instrument.find_instrument('ivvi').close()

# ivvi = IVVI(name='ivvi', address='ASRL1',
#                       dac_step=15, dac_delay=0.01,  polarity=['BIP', 'BIP', 'BIP', 'BIP'], 
#                       numdacs=16, use_locks=True)

# heaters_param_map = {
#     'mc': {'instrument': 'ivvi','parameter': 'dac15', 
#                   'step': .1, 'inter_delay': .05, 'scale': 1/(Istill_gain*1e3)*1e3, 'unit': 'mA'}, #1e3 -> DAC is in mV
#     'still': {'instrument': 'ivvi','parameter': 'dac16', 
#                   'step': .1, 'inter_delay': .05, 'scale': 1/(Imc_gain*1e3)*1e3, 'unit': 'mA'}, #1e3 -> DAC is in mV
#     }

# heaters = Device(name='heaters',parameter_map = heaters_param_map)

logging.getLogger().setLevel(logging.INFO)
#%% functions 

current_step = 50

def reduce_heaters(still, mc):
    new_still = still()-current_step
    still(new_still)
    new_mc = mc()-current_step
    mc(new_mc)
    logging.warning(f'decreased still heater to {round(new_still,2)}')
    logging.warning(f'decreased mc heater to {round(new_mc,2)}')
    
def increase_heaters(still, mc):
    if T_still()<2e3: #mK
        new_still = still() + current_step
        still(new_still)
        logging.info(f'increased still heater to {round(new_still,2)}')
    if T_mc()<2e3: #mK
        new_mc = mc() + current_step
        mc(new_mc)
        logging.info(f'increased mc heater to {round(new_mc,2)}')
        
def ramp_to_max(still, mc, Imax=20):
    print('did you turn off the turbo and are you pumping the 1k pot?')
    mc_done, still_done = False,False
    while not (mc_done and still_done):

        if still()<Imax:
            new_still = still() + current_step
            still(new_still)
            logging.info(f'increased still heater to {round(new_still,2)}')
        else: still_done=True
            
        if mc()<Imax:
            new_mc = mc() + current_step
            mc(new_mc)
            logging.info(f'increased mc heater to {round(new_mc,2)}')
        else: mc_done=True
        for _ in range(2): time.sleep(1)
#%% main loop
still = d.still_current
mc = d.mc_current

counts = 0
while True:
    if P_still()>1.1e-1 and counts>3:
        reduce_heaters(still,mc)
    elif P_still()<9.9e-2 and counts>5: #every 3 cycles and if P_still<9.5
        increase_heaters(still, mc)
        counts = 0
    for _ in range(3): time.sleep(1)
    counts+=1
    
        
        