# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 11:32:53 2021

@author: atosato
"""

from device import Device
from qcodes.instrument.parameter import Parameter
from qcodes.instrument import Instrument
from qcodes.instrument import base
from dummy_instrument import Dummy_R_measure

import numpy as np
import deck_config

#%%

def create_virtual_device():
    
    # close virtual instruments if exist   
    for i in ['d', 'cryomux']:
        if Instrument.exist(i):
            Instrument.find_instrument(i).close()
    # Instrument.close_all()
    
    # create instance of virtual instruments
    d = Device(name='d', parameter_map=virtual_instr_params)
    
        
    
    #  calculated params functions
    def calc_G():
        try: G = d.I_AC()/d.V_AC()*h/(2*ech**2)
        except: G = np.nan
        return G
    
    def calc_R():
        try: R = d.V_AC()/d.I_AC()
        except: R = np.nan
        return R
    
    #add calculated 
    d.add_parameter('G', get_cmd=calc_G, unit='2e^2/h')
    
    d.add_parameter('R',get_cmd=calc_R, unit='Ohm')
    
    d.add_parameter('repetitions', inter_delay=0)
    
    return d
    


