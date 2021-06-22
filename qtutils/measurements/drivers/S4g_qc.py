# -*- coding: utf-8 -*-
# @Author: atosato
# @Date:   2021-05-10 17:53:42
# @Last Modified by:   TUD278249
# @Last Modified time: 2021-05-10 20:14:17

from qcodes.instrument.base import Instrument
from qcodes.utils.validators import Enum, Numbers
import numpy as np
from functools import partial

try:
    from spirack import S4g_module
except ImportError:
    raise ImportError(('The S4g_module class could not be found. '
                       'Try installing it using pip install spirack'))


class S4g(Instrument):
    """
    Qcodes driver for the S4g DAC SPI-rack module.

    functions:
    -   set_dacs_zero   set all DACs to zero current

    parameters:
    -   dacN:       get and set DAC current
    -   stepsizeN   get the minimum step size corresponding to the span
    -   spanN       get and set the DAC span:
    				 -	  0 to 50 mA: 'range_max_uni'
    				 -	-50 to 50 mA: 'range_max_bi'
					 -	-25 to 25 mA: 'range_min_bi'

    where N is the DAC number from 1 up to 4

    """

    def __init__(self, name, spi_rack, module, inter_delay=0.01, dac_step=50e-6,
                 reset_currents=False, mA=False, number_dacs=4, **kwargs):
        """ Create instrument for the S4g module.

        The S4g module works with Amps as units. For backward compatibility
        there is the option to allow mA for the dacX parameters.

        The output span of the DAC module can be changed with the spanX
        command. Be carefull when executing this command with a sample
        connected as voltage jumps can occur.

        Args:
            name (str): name of the instrument.

            spi_rack (SPI_rack): instance of the SPI_rack class as defined in
                the spirack package. This class manages communication with the
                individual modules.

            module (int): module number as set on the hardware.
            inter_delay (float): time in seconds, passed to dac parameters of the object
            dac_step (float): max step size (A or mA), passed to dac parameters of the object
            reset_currents (bool): passed to S4g_module constructor
            mA (bool): if True, then use mA as units in the dac parameters
            number_dacs (int): number of DACs available. This is 8 for the D5mux
        """
        super().__init__(name, **kwargs)

        self.s4g = S4g_module(spi_rack, module, reset_currents=reset_currents)
        self._number_dacs = number_dacs

        self._span_set_map = {
            'range_max_uni': S4g_module.range_max_uni,
            'range_max_bi': S4g_module.range_max_bi,
            'range_min_bi': S4g_module.range_min_bi,
        }

        self._span_get_map = {v: k for k, v in self._span_set_map.items()}

        self.add_function('set_dacs_zero', call_cmd=self._set_dacs_zero,
                          docstring='Reset all dacs to zero mA. Ramping is performed.') 

        if mA:
            self._gain = 1e3
            unit = 'mA'
        else:
            self._gain = 1
            unit = 'A'

        # make a cache, to get a numerically not rounded value.
        self.current_cache = np.zeros([number_dacs])
        for i in range(number_dacs):
            self.current_cache[i] = self.__get_dac(i)

        for i in range(self._number_dacs):
            validator = self._get_validator(i)

            self.add_parameter('dac{}'.format(i + 1),
                               label='DAC {}'.format(i + 1),
                               get_cmd=partial(self._get_dac, i),
                               set_cmd=partial(self._set_dac, i),
                               unit=unit,
                               vals=validator,
                               step=dac_step,
                               inter_delay=inter_delay)

            self.add_parameter('stepsize{}'.format(i + 1),
                               get_cmd=partial(self.s4g.get_stepsize, i),
                               unit='A',
                               docstring='Returns the smallest voltage step of the DAC.')

            self.add_parameter('span{}'.format(i + 1),
                               get_cmd=partial(self._get_span, i),
                               set_cmd=partial(self._set_span, i),
                               vals=Enum(*self._span_set_map.keys()),
                               docstring='Change the output span of the DAC. This command also updates the validator.')

    def set_dac_unit(self, unit: str) -> None:
        """Set the unit of dac parameters"""
        allowed_values = Enum('mA', 'A')
        allowed_values.validate(unit)
        self._gain = {'A': 1, 'mA': 1e3}[unit]
        for i in range(1, self._number_dacs + 1):
            setattr(self.parameters[f'dac{i}'], 'unit', unit)
            setattr(self.parameters[f'dac{i}'], 'vals', self._get_validator(i - 1))

    def _set_dacs_zero(self):
        for i in range(self._number_dacs):
            # self._set_dac(i, 0.0)
            self[f'dac{i+1}'](0)

    def _set_dac(self, dac, value):
        self.current_cache[dac] = value
        return self.s4g.set_current(dac, value / self._gain)

    def _get_dac(self, dac):
        return self.current_cache[dac]
    
    def __get_dac(self, dac):
        return self._gain * self.s4g.currents[dac]

    def _get_span(self, dac):
        return self._span_get_map[self.s4g.span[dac]]

    def _set_span(self, dac, span_str):
        self.s4g.change_span_update(dac, self._span_set_map[span_str])
        self.parameters['dac{}'.format(
            dac + 1)].vals = self._get_validator(dac)

    def _get_validator(self, dac):
        span = self.s4g.span[dac]

        if span == S4g_module.range_max_uni:
            validator = Numbers(0 * self._gain, 50e-3 * self._gain)
        elif span == S4g_module.range_max_bi:
            validator = Numbers(-50e-3 * self._gain, 50e-3 * self._gain)
        elif span == S4g_module.range_min_bi:
            validator = Numbers(-25e-3, 25e-3 * self._gain)
        else:
            msg = 'The found DAC span of {} does not correspond to a known one'
            raise Exception(msg.format(span))

        return validator
