# -*- coding: utf-8 -*-
# @Author: TUD278249
# @Date:   2021-05-31 16:30:29
# @Last Modified by:   TUD278249
# @Last Modified time: 2021-05-31 17:19:37


from qcodes.instrument import Instrument
from qtutils.measurements.stations.Leiden.drivers import LCApp
from functools import partial
    
class FrontPanel(Instrument):
    def __init__(self, name):
        super().__init__(name)
        
        self.FP = LCApp.LVApp(r"DRFrontPanel.Application",r"DR FrontPanel.exe\FP.vi")
        
        self.add_parameter(name='flow', 
        				   get_cmd=self._get_Pflow)

        self.add_parameter(name='still', 
        				   get_cmd=self._get_Pstill)

        self.add_parameter(name='ivc', 
        				   get_cmd=self._get_Pivc)

        for i in range(6):
        	self.add_parameter(name=f'P{i+1}', 
        					   get_cmd=partial(self._get_P, i=i+1))
        
    def _get_P(self, i):
        return self.FP.GetData(f"P{i}")

    def _get_Pflow(self):
        return self.FP.GetData("Flow")

    
    def _get_Pstill(self):
        return self.FP.GetData('MG Data')[5]

    def _get_Pivc(self):
        return self.FP.GetData('MG Data')[4]

