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
    
    Vsource_gain = 1e-3 #V/V
    # Isource_gain = 1e-3 #A/V
    Vg_gain = 15
    Vcg_gain = 5

    Vmeasure_gain = 100 #V/V
    Imeasure_gain = 1e6 #V/A

    dev_params =  { 
        # Settable
        'Vg': {'instrument': 'ivvi','parameter': 'dac3', 
           'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1/Vg_gain},

        'Vcg': {'instrument': 'ivvi','parameter': 'dac1', 
              'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1/Vcg_gain},
        # 'field': {'instrument': 'magnet', 'parameter': 'field',
        #           'scale':1e-3, 'unit':'mT'},
        
        'V_AC_bias': {'instrument': 'lia1','parameter': 'amplitude',  
                'step': 1, 'inter_delay': 1e-4, 'scale':1/Vsource_gain*1e-6, 'unit':'uV'}, #-1e2 if isoiin is diveded by 100

        # 'I_AC_bias': {'instrument': 'lia1','parameter': 'amplitude', 
        #               'step': .1, 'inter_delay': .05, 'scale': -1/(Isource_gain*1e9)*100, 'unit': 'nA'},
        
        'I_AC': {'instrument': 'lia3','parameter': 'X', 
              'unit':'A', 'scale': Imeasure_gain},
    #    'I_DC': {'instrument': 'keithley2','parameter': 'amplitude', 
    #             'unit':'A', 'scale': Imeasure_gain},
        'V_AC': {'instrument': 'lia1','parameter': 'X', 
                'scale': Vmeasure_gain}, #*1e2
        # 'V_AC_xy': {'instrument': 'lia2','parameter': 'X', 
        #         'scale': 1e3},
    #    'V_DC': {'instrument': 'keithley1','parameter': 'amplitude', 
    #             'unit':'V', 'scale': 100},
        'I_leak': {'instrument': 'keithley', 'parameter':  
                  'amplitude', 'scale': 1e6*1e-9, 'unit':'nA'}, #nA
    }


    def __init__(self):
        if Instrument.exist('d'):
            Instrument.find_instrument('d').close()
            
        self.d = Device(name='d', parameter_map=self.dev_params)
        
        #add calculated parameters
        self.d.add_parameter('G', get_cmd=self.calc_G, unit='2e^2/h')
        self.d.add_parameter('R',get_cmd=self.calc_R, unit='Ohm')
        # self.d.add_parameter('Rsq',get_cmd=self.calc_Rsq, unit='Ohm')
        # self.d.add_parameter('Rxy',get_cmd=self.calc_Rxy, unit='Ohm')
        self.d.add_parameter('reps', inter_delay=0, set_cmd=None)
        
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
    
    def calc_Rsq(self):
        aspect_ratio = 5
        try: Rsq = self.d.V_AC()/self.d.I_AC()/aspect_ratio
        except: Rsq = np.nan
        return Rsq

    def calc_Rxy(self):
        try: Rxy = self.d.Vxy_AC()/self.d.I_AC()
        except: Rxy = np.nan
        return Rxy