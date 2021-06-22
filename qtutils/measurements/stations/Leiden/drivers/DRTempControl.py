# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 11:52:49 2019

@author: TUD278249
"""

from qcodes.instrument.base import Instrument
try:
    from drivers import LCApp
except:
    from stations.Leiden.drivers import LCApp
    
class DRTempControl(Instrument):
    def __init__(self, name):
        super().__init__(name)
        
        self.TC = LCApp.LVApp(r"DRTempControl.Application",r"DR TempControl.exe\TC.vi")
        
        self.add_parameter(name='mc_temp', get_cmd=self._get_temperature)
        self.add_parameter(name='still_heater', get_cmd=self._get_still_heater, set_cmd=self._set_still_heater)
        self.add_parameter(name='mc_heater', get_cmd=self._get_mc_heater, set_cmd=self._set_mc_heater)
        
    def _get_temperature(self):
        return self.TC.GetData("T")[2]

    def _get_still_heater(self):
        current_string = self.TC.GetData('I2')[0]
        if current_string[-2:] == 'mA':
            return float(current_string[:-3].replace(',','.')) * 1000 #in uA
        else:
            raise ValueError
            
    def _get_mc_heater(self):
        current_string = self.TC.GetData('I3')[0]
        if current_string[-2:] == 'mA':
            return float(current_string[:-3].replace(',','.')) * 1000 #in uA
        else:
            raise ValueError
        
    def _set_mc_heater(self, current):
        on = self.TC.GetData('I3')[1]
        if(not on):
            self.TC.SetData("C_I0 4.Toggle ON/OFF",True)
        self.TC.SetData("C_I0 4.I",current)
        
    def _set_still_heater(self, current):
        on = self.TC.GetData('I2')[1]
        if(not on):
            self.TC.SetData("C_I0 3.Toggle ON/OFF",True)
        self.TC.SetData("C_I0 3.I",current)