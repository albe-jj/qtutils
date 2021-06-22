# -*- coding: utf-8 -*-
# @Author: TUD278249
# @Date:   2021-05-28 17:37:04
# @Last Modified by:   TUD278249
# @Last Modified time: 2021-06-02 08:58:52


from qcodes.utils.validators import Numbers
from qcodes import Instrument
import numpy as np

class Paral_S4g(Instrument):
    def __init__(self, name, S4g, num_dacs=1, **kwargs):
        '''
        Parallelize the current source of the S4g for magnet power supply.
        Ramps one dac at the time.
        Args:
            name (str): 
            S4g (qcodes.Instrument): the instance of the S4g
            num_dacs (int): number of dacs connected in parallel.
                            Default is 1

        '''
        self.S4g = S4g
        self.num_dacs = num_dacs
        self.max_val = .04999 #A 
        self.max_field = self.max_val * self.num_dacs * 0.113375 #T
        
        super().__init__(name)
        validator = Numbers(-self.max_val*num_dacs, self.max_val*num_dacs)
        
        for i in range(num_dacs):
            S4g[f'span{i+1}']('range_max_bi')
            
        self.dac_ls = [S4g[f'dac{i+1}'] for i in range(num_dacs)] 
        
        self.add_parameter('current',
                           label='current',
                           get_cmd=self._get_current,
                           set_cmd=self._set_current,
                           vals=validator)
        
        
    
    def _get_current(self):
        return sum([p() for p in self.dac_ls])
        
    def _set_current(self, value):
        max_val = self.max_val
        sgn = np.sign(value)
        for idx,p in enumerate(self.dac_ls):
            if abs(value) > (max_val * (idx+1)):
                p(sgn*max_val)
                # print(f'set dac{idx+1} to {p()}')
            elif (max_val * (idx)) <= abs(value) <= (max_val * (idx+1)):
                p(value - sgn*max_val*idx)
                # print(f'set dac{idx+1} to {p()}')
            elif abs(value) <= (max_val * (idx+1)):
                p(0)
                # print(f'set param{idx+1} to {p()}')
                return
