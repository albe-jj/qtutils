# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 12:56:23 2021

@author: atosato
"""
from qtutils.measurements.virtual_instrument import VirtualInstrument
from qcodes import Instrument
import numpy as np
from scipy import constants
from qtutils.measurements.stations.Leiden.drivers.RuO2_temp_probe import RuO2_2k_R2Temp

ech = constants.e
h = constants.h
kb = constants.k/constants.e * 1e6 #ueV/K
G0 = h/(2*ech**2)

class DevConfig:
    Imeasure_gain_AC = 1 * 1e6 * 1#V/A 
    Imeasure_gain_DC = 1 * 1e6 * 1#V/A
    Vg_gain = 15 #V/V
    Vcg_gain = 5 #V/V

    # Vmeasure gains: M2b * srs preamp
    Vmeasure_gain_AC = 1e3 * 1  #V/V
    Vxymeasure_gain_AC = 100 #V/V
    Vmeasure_gain_DC = 1e3 * 1 #V/V

    Vsource_gain = 1e-3 #V/V
    Isource_gain = 1e-6 #A/V

    Istill_gain = 20e-3 #A/V
    Imc_gain = 20e-3 #A/V

    I_temp_gain = 100e6 #V/A
    V_temp_gain = 10e3 #V/V

    dev_params =  { 
        'Vg': {'instrument': 'ivvi','parameter': 'dac4', 
               'step': 20, 'inter_delay': .05, 'unit':'mV', 'scale': 1/Vg_gain},#1/15
        'Vcg': {'instrument': 'ivvi','parameter': 'dac9', 
               'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1/Vcg_gain},
        # 'Vcg2': {'instrument': 'ivvi','parameter': 'dac10', 
        #        'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1/Vcg_gain},

        ### Magnet power supplies

        # Cryogenics
        'field': {'instrument': 'magnet', 'parameter': 'field',
                  'scale':1e-3, 'unit':'mT'},

        #SPI S4g 
        # 'field': {'instrument':  'Paral_S4g','parameter': 'current', 
        #         'step': 0.05, 'inter_delay': 0.01, 'scale':1/(0.113375 * 1e3), 'unit':'mT'}, #0.113375 T/A # max 5.6 mT per dac (50mA) 

        #Keitheley sourcemeter 2614B
        # 'field': {'instrument':  'sourcemeter','parameter': 'smua.curr', 
        #         'step': 0.05, 'inter_delay': 0.01, 'scale':1/(0.113375 * 1e3), 'unit':'mT'}, #0.113375 T/A # max 1.5A -> 170 mT 


        'V_AC_bias': {'instrument': 'lia1','parameter': 'amplitude',  
                'step': 1, 'inter_delay': 0, 'scale':1/Vsource_gain*1e2*1e-6, 'unit':'uV'}, #1e2 -> isoiin is diveded by 100
        'V_DC_bias': {'instrument': 'ivvi','parameter': 'dac5', 
                      'step': 100, 'inter_delay': .0, 'scale': -1/Vsource_gain*1e3*1e-6, 'unit': 'uV'},#1e3 -> DAC is in mV
        'I_DC_bias': {'instrument': 'ivvi','parameter': 'dac6', 
                      'step': 100, 'inter_delay': .05, 'scale': 1/(Isource_gain*1e6)*1e3, 'unit': 'uA'},#1e3 -> DAC is in mV
        'I_AC_bias': {'instrument': 'lia1','parameter': 'amplitude', 
                      'step': .1, 'inter_delay': .05, 'scale': 1/(Isource_gain*1e9)*100, 'unit': 'nA'},
        
        'I_AC': {'instrument': 'lia2','parameter': 'X', 
              'unit':'A', 'scale': Imeasure_gain_AC},
        'I_DC': {'instrument': 'keithley2','parameter': 'amplitude', 
                  'unit':'A', 'scale': Imeasure_gain_DC},
        'V_AC': {'instrument': 'lia1','parameter': 'X', 
                 'scale': Vmeasure_gain_AC}, 
        'Vxy_AC': {'instrument': 'lia5','parameter': 'X', 
                 'scale': Vxymeasure_gain_AC}, 

        'V_DC': {'instrument': 'keithley1','parameter': 'amplitude', 
                 'unit':'V', 'scale': Vmeasure_gain_DC}, 
        # 'I_leak_cg': {'instrument': 'd4', 'parameter':  
        #            'adc1', 'scale': 1e6*1e-9, 'unit':'nA'}, #nA
        'I_leak': {'instrument': 'keithley3', 'parameter':  
                   'voltage_dc', 'scale': 1e6*1e-9, 'unit':'nA'}, #nA
        
        
        # LIA Y componenets
        'V_AC_Y': {'instrument': 'lia1','parameter': 'Y', 
                 'scale': Vmeasure_gain_AC},
        'Vxy_AC_Y': {'instrument': 'lia5','parameter': 'Y', 
                 'scale': Vxymeasure_gain_AC},
        'I_AC_Y': {'instrument': 'lia2','parameter': 'Y', 
              'unit':'A', 'scale': Imeasure_gain_AC},

        'seat': {'instrument': 'cryomux','parameter': 'sample'}, #1e3 -> DAC is in mV
        
        'mc_current': {'instrument': 'ivvi','parameter': 'dac15', 
                      'step': 100, 'inter_delay': .05, 'scale': 1/(Istill_gain*1e6)*1e3, 'unit': 'uA'}, #1e3 -> DAC is in mV
        'still_current': {'instrument': 'ivvi','parameter': 'dac16', 
                      'step': 100, 'inter_delay': .05, 'scale': 1/(Imc_gain*1e6)*1e3, 'unit': 'uA'}, #1e3 -> DAC is in mV

        # 'temp': {'instrument': 'temp_control', 'parameter': 'mc_temp'}, # picowatt temp control


        'VAC_bias_therm': {'instrument': 'lia3','parameter': 'amplitude',  
                'step': 1, 'inter_delay': 0, 'scale':1/100e-6*1e-6, 'unit':'uV'}, #1e2 -> isoiin is diveded by 100
        'I_AC_therm': {'instrument': 'lia4','parameter': 'X', 
              'unit':'A', 'scale': I_temp_gain},
        'V_AC_therm': {'instrument': 'lia3','parameter': 'X', 
              'unit':'A', 'scale': V_temp_gain},


        }


    def __init__(self):
        if Instrument.exist('d'):
            Instrument.find_instrument('d').close()
            
        self.d = VirtualInstrument(name='d', parameter_map=self.dev_params)
        
        #add calculated parameters
        self.d.add_parameter('G', get_cmd=self.calc_G, unit='2e^2/h')
        self.d.add_parameter('R',get_cmd=self.calc_R, unit='Ohm')
        self.d.add_parameter('Rsq',get_cmd=self.calc_Rsq, unit='Ohm')
        self.d.add_parameter('Rxy',get_cmd=self.calc_Rxy, unit='Ohm')
        self.d.add_parameter('temp', get_cmd=self.calc_temp, unit='mK')

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

    def calc_temp(self):
        try: temp = RuO2_2k_R2Temp(self.d.V_AC_therm()/self.d.I_AC_therm())
        except: temp = np.nan
        return temp




    