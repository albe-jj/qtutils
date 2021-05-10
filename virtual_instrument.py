# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 15:08:51 2020

@author: Albo
"""

from qcodes import Instrument
from qcodes.utils.validators import Numbers

class VirtualInstrument(Instrument):
    """
    Implements a device as a virtual instrument for QCoDeS
    """

    def __init__(self, name, parameter_map):
        """Create a virtual instrument to represent the device params

        Args:
            name (str): name of the virtual instrument
            parameter_map (dict): dictionary mapping the hallbars measurable parameters to their
                                  measurement instruments
        """
        super().__init__(name=name)
        self._map_parameters(parameter_map)


    def _map_parameters(self, parameter_map):
        """Add all parameters that need to be mapped to the cryomux"""
        for parameter_name in parameter_map:
            info = parameter_map[parameter_name].copy()

            external_instrument = Instrument.find_instrument(info.pop('instrument'))
            external_parameter = external_instrument[info.pop('parameter')]
            unit = info.pop('unit', external_parameter.unit)
            
            if external_parameter.gettable:
                get_cmd = external_parameter.get  
            else: get_cmd = False
            if external_parameter.settable:
                set_cmd = external_parameter.set  
            else: set_cmd = False

            self.add_parameter(name=parameter_name,
                               get_cmd=get_cmd,
                               set_cmd=set_cmd, #external_parameter.__call__,
                               unit=unit,
                               vals=Numbers(),
                               **info)

    def ask_raw(self, cmd: str) -> None:
        """Dummy method to satisfy base class overrides"""
        raise NotImplementedError(
            f'Instrument {type(self).__name__} is virtual and requires no ask_raw method'
        )

    def write_raw(self, cmd: str) -> None:
        """Dummy method to satisfy base class overrides"""
        raise NotImplementedError(
            f'Instrument {type(self).__name__} is virtual and requires no write_raw method'
        )
        
    def close(self):
        super().close()
