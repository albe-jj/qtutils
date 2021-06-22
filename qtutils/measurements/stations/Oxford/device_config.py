# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:56:23 2021

@author: atosato
"""
from device import Device
from qcodes import Instrument
import numpy as np
from scipy import constants

ech = constants.e
h = constants.h
kb = constants.k/constants.e * 1e6 #ueV/K
G0 = h/(2*ech**2)

class DevConfig:
    Imeasure_gain_AC = 1 #V/A 
    
    # Vmeasure gains: M2b * srs preamp
    Vmeasure_gain_AC = 1e3   #V/V
    
    Vsource_gain = 1e-3 #V/V
    
    dev_params =  { 
        'V_AC_bias': {'instrument': 'mock_Rmeas','parameter': 'V_AC_bias',  
                'step': 0.1, 'inter_delay': 0.01, 'scale':1/Vsource_gain*1e-6, 'unit':'uV'}, 
        
        'I_AC': {'instrument': 'lia1','parameter': 'X', 
              'unit':'A', 'scale': Imeasure_gain_AC},
        
        'V_AC': {'instrument': 'lia2','parameter': 'X', 
                 'scale': Vmeasure_gain_AC}, 
        
        'Vg': {'instrument': 'mock_dac','parameter': 'ch1', 
                 'scale': 1}, 
        }


    def __init__(self):
        if Instrument.exist('d'):
            Instrument.find_instrument('d').close()
            
        self.d = Device(name='d', parameter_map=self.dev_params)
        
        #add calculated parameters
        self.d.add_parameter('G', get_cmd=self.calc_G, unit='2e^2/h')
        self.d.add_parameter('R',get_cmd=self.calc_R, unit='Ohm')
        self.d.add_parameter('repetitions', inter_delay=0)
        
    def create_dev(self):
        '''
        None.

        '''
        
    def calc_G(self):
        try: G = self.d.I_AC()/self.d.V_AC()*G0
        except: G = np.nan
        return G
    
    def calc_R(self):
        try: R = self.d.V_AC()/self.d.I_AC()
        except: R = np.nan
        return R
    
    