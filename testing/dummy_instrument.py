# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 14:20:30 2021

@author: atosato
"""

from qcodes import Parameter
from qcodes import Instrument
from qcodes.utils.validators import Numbers

class Dummy_R_measure(Instrument):

    def __init__(self, name, Res=10, **kwargs):

        super().__init__(name, **kwargs)
        
        self.Res = Res

        self.add_parameter('V_AC_bias',
                           initial_value=0,
                           unit='V',
                           label='V_AC_biast',
                           vals=Numbers(-2,2),
                           get_cmd=None,
                           set_cmd=None)
        
        self.add_parameter('V_AC',
                            # initial_value=1,
                           unit='V',
                           label='V_AC',
                           vals=Numbers(-2,2),
                           get_cmd= lambda: self.V_AC_bias(),
                           set_cmd=False)

        self.add_parameter('I_AC',
                            # initial_value=1,
                           unit='A',
                           label='I_AC',
                           vals=Numbers(-2,2),
                           get_cmd= lambda: self.V_AC_bias()/self.Res,
                           set_cmd=False)
        
