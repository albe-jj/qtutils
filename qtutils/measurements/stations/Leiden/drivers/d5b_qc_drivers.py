# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 17:06:58 2020

@author: Alberto Tosato
"""

from qcodes.instrument.base import Instrument
from qcodes.utils.validators import Enum, Numbers

try:
    from spirack import D5b_module
except ImportError:
    raise ImportError(('The D5b_module class could not be found. '
                       'Try installing it using pip install spirack'))

from functools import partial


class D5b(Instrument):
    """
    Qcodes driver for the D5b DAC SPI-rack module.
    functions:
    -   set_dacs_zero   set all DACs to zero voltage
    parameters:
    -   dacN:       get and set DAC voltage
    -   stepsizeN   get the minimum step size corresponding to the span
    -   spanN       get and set the DAC span: '4v uni', '4v bi', or '2.5v bi'
    where N is the DAC number from 1 up to 16
    """

    def __init__(self, name, spi_rack, module, inter_delay=0.1, dac_step=10e-3,
                 reset_voltages=False, mV=False, number_dacs=8, **kwargs):
        """ Create instrument for the D5b module.
        The D5b module works with volts as units. For backward compatibility
        there is the option to allow mV for the dacX parameters.
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
            dac_step (float): max step size (V or mV), passed to dac parameters of the object
            reset_voltages (bool): passed to D5b_module constructor
            mV (bool): if True, then use mV as units in the dac parameters
            number_dacs (int): number of DACs available. This is 8 for the D5mux
        """
        super().__init__(name, **kwargs)

        self.d5b = D5b_module(spi_rack, module, reset_voltages=reset_voltages)
        self._number_dacs = number_dacs

        self._span_set_map = {
            '4V_uni':0, 
            '8V_uni':1, 
            '4V_bi':2, 
            '8V_bi':3, 
            '2V_bi':4
            }

        self._span_get_map = {v: k for k, v in self._span_set_map.items()}

        self.add_function('set_dacs_zero', call_cmd=self._set_dacs_zero,
                          docstring='Reset all dacs to zero voltage. No ramping is performed.')

        if mV:
            self._gain = 1e3
            unit = 'mV'
        else:
            self._gain = 1
            unit = 'V'

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
                               get_cmd=partial(self.d5b.get_stepsize, i),
                               unit='V',
                               docstring='Returns the smallest voltage step of the DAC.')

            self.add_parameter('span{}'.format(i + 1),
                               get_cmd=partial(self._get_span, i),
                               set_cmd=partial(self._set_span, i),
                               vals=Enum(*self._span_set_map.keys()),
                               docstring='Change the output span of the DAC. This command also updates the validator.')

    def set_dac_unit(self, unit: str) -> None:
        """Set the unit of dac parameters"""
        allowed_values = Enum('mV', 'V')
        allowed_values.validate(unit)
        self._gain = {'V': 1, 'mV': 1e3}[unit]
        for i in range(1, self._number_dacs + 1):
            setattr(self.parameters[f'dac{i}'], 'unit', unit)
            setattr(self.parameters[f'dac{i}'], 'vals', self._get_validator(i - 1))

    def _set_dacs_zero(self):
        for i in range(self._number_dacs):
            self._set_dac(i, 0.0)

    def _set_dac(self, dac, value):
        return self.d5b.set_voltage(dac, value / self._gain)

    def _get_dac(self, dac):
        return self._gain * self.d5b.voltages[dac]

    def _get_span(self, dac):
        return self._span_get_map[self.d5b.get_DAC_span(dac)]

    def _set_span(self, dac, span_str):
        self.d5b.set_DAC_span(dac, self._span_set_map[span_str])
        self.parameters['dac{}'.format(
            dac + 1)].vals = self._get_validator(dac)

    def _get_validator(self, dac):
        span = self.d5b.get_DAC_span(dac)
        if span == D5b_module.range_2V_bi:
            validator = Numbers(-2 * self._gain, 2 * self._gain)
        elif span == D5b_module.range_4V_bi:
            validator = Numbers(-4 * self._gain, 4 * self._gain)
        elif span == D5b_module.range_4V_uni:
            validator = Numbers(0, 4 * self._gain)
        else:
            msg = 'The found DAC span of {} does not correspond to a known one'
            raise Exception(msg.format(span))

        return validator