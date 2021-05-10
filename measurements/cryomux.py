# -*- coding: utf-8 -*-
"""
Offer Cryomux driver as class

@author: layeoh, HvdD, mwilmer
"""

import qcodes

from qcodes.utils.validators import Numbers, Ints
from time import sleep
from spirack import SPI_rack, U2_module
from spirack.chip_mode import CRYOMUX_MODE, CRYOMUX_SPEED

FOUR_VOLTS_UNI = '4v uni'
FOUR_VOLTS_BI = '4v bi'


#TODO: self.voltage_spans

class CryogenicMultiplexer(qcodes.Instrument):
    """Software representation and driver for the cryogenic multiplexer

    """

    _supply_voltages = {
        'positive_mux_voltage', 'negative_mux_voltage',
        'positive_shiftregister_voltage', 'negative_shiftregister_voltage',
    }
    """The supply voltages for the shift register and multiplexer chips"""

    _logic_voltages = {
        'logic_high', 'logic_low'
    }
    """The logic voltages for signaling with the multiplexer"""

    _voltages = {
        *_supply_voltages,
        *_logic_voltages
    }
    """All voltages that can be configured"""

    _voltage_spans = {
        'positive_mux_voltage_span', 'negative_mux_voltage_span',
        'positive_shiftregister_voltage_span', 'negative_shiftregister_voltage_span',
        'logic_high_span', 'logic_low_span'
        }
    """All voltage spans that can be configured"""

    _mapped_parameters = {
        *_supply_voltages,
        *_voltage_spans,
#        'B_real'#,'sample_resistance'
    }
    """All measurement/control parameters that need to be mapped"""

    def __init__(self, name, parameter_map,
                 sample_range=range(1, 9), # default support of 8 samples
                 voltage_settings=None,
                 voltage_spans=None, 
                 num_shift_registers=2,
                 **kwargs):
        """
        Virtual instrument to connect with the Cryogenic Multiplexer

        Maps the cryomux's settings to the underlying measurement and control hardware
        and facilitates its configuration.

        Args:
            name (str): Instrument name
            parameter_map (dict): Dictionary with a mapping to the measurement instruments
            sample_range (iterable): Iterable that marks the samples that are selectable
            voltage_settings (dict, optional): When given, the cryogenic multiplexer is
                initialized to use these voltages
            voltage_spans (dict, optional): When given, the cryogenic multiplexer is
                initialized to use these voltage spans


        """
        super().__init__(name=name, **kwargs)

        self._sample = None # "Undefined initial value"
        self._sample_range = sample_range
        self._num_shift_registers = num_shift_registers
        """Range of samples to be operated by the current multiplexer"""

        self._map_parameters(parameter_map)
        self._add_internal_parameters()

        if voltage_settings is not None:
            self.set_voltages(voltage_settings)

        if voltage_spans is not None:
            self.set_voltage_spans(voltage_spans)
            
        '''
        This is my own HACK!!!!! Remove when confirmed
        '''
        self.testd5a = self.find_instrument('spi1')
        self.Clk   = 4         #D5a channel for 74HC4094D shift register"""
        self.Data  = 5         #D5a channel for 74HC4094D shift register
        self.Str   = 6
        self.D5a_U_Source = 7  #D5a channel for measuring Source
        self.D5a_V1_pos = 0    #D5a channel for V1 pos power supply
        self.D5a_V1_neg = 1    #D5a channel for V1 neg power supply
        self.D5a_V2_pos = 2    #D5a channel for V1 pos power supply
        self.D5a_V2_neg = 3    #D5a channel for V1 neg power supply

    def _add_internal_parameters(self):
        self.add_parameter(name='logic_high',
                           get_cmd=None,
                           set_cmd=None,
                           unit='V')

        self.add_parameter(name='logic_low',
                           get_cmd=None,
                           set_cmd=None,
                           unit='V')

        self.add_parameter(name='sample',
                           get_cmd=lambda: self._sample,
                           set_cmd=self._set_sample,
                           vals=Ints())
        self.add_parameter(name='multi_sample',
                           get_cmd=self._multi_sample,
                           set_cmd=self._set_multi_sample)

    def _map_parameters(self, parameter_map):
        """Add all parameters that need to be mapped to the cryomux"""
        for parameter_name in self._mapped_parameters:
            info = parameter_map[parameter_name].copy()
            instrument = info.pop('instrument')
            parameter = info.pop('parameter')

            external_instrument = qcodes.Instrument.find_instrument(instrument)
            external_parameter = external_instrument[parameter]
            unit = info.pop('unit', external_parameter.unit),
            self.add_parameter(name=parameter_name,
                               get_cmd=external_parameter.__call__,
                               set_cmd=external_parameter.__call__,
                               unit=unit,
                               **info)
    '''
    ORIGINAL set_sample (FIXME)
    def _set_sample(self, value):
        """Switch the selected sample on the cryogenic multiplexer"""
        if value not in self._sample_range:
            raise ValueError('Selected sample not in valid sample range')

        max_sample_number = max(self._sample_range)
        
        print(range(1,max_sample_number + 1))
        for k in range(1,max_sample_number + 1):
            if k == (max_sample_number - value + 1):
                print(k)
                self._send_bit(1)                            
            else:
                print(k)
                self._send_bit(0)

        self._send_strobe()

        self._sample = value
    '''
    """ old _set_sample, before using U2 module
    def _set_sample(self, value):
        if value not in self._sample_range:
            raise ValueError('Selected sample not in valid sample range')

        max_sample_number = max(self._sample_range)
        

        for k in range(1,max_sample_number + 1):
            if k == (max_sample_number - value + 1):
                self.SendBitK(1)                            
            else:
                self.SendBitK(0)
                
        self.SendStrobeK()

        self._sample = value
    """
    
    def _set_sample(self, value):
        self.testd5a.d5a.select_mux(value)
        self._sample = value
        #to guarantee proper switching
#        sleep(3)
#        if(value == 10):
#            sleep(0.3) 
#        else:
#            sleep(0.2)
        
    def _set_multi_sample(self, mux):
        self.testd5a.d5a.select_multiple_mux(mux, self._num_shift_registers)
        #sleep(0)
        
    def _multi_sample(self):
        return self.testd5a.d5a.get_active_mux()
        
    def set_voltages(self, voltage_settings):
        """Set voltages for the cryogenic multiplexer from a dictionary"""
        for voltage_name in self._voltages:
            value = voltage_settings[voltage_name]
            # Set parameter
            self[voltage_name](value)
            
    def set_voltages_U2(self, voltage_settings):
        self.testd5a.d5a.set_register_supply([voltage_settings['positive_shiftregister_voltage']
                                            , voltage_settings['negative_shiftregister_voltage']])
        self.testd5a.d5a.set_switch_supply([voltage_settings['positive_mux_voltage']
                                          , voltage_settings['negative_mux_voltage']])
        self.testd5a.d5a.set_data_levels([voltage_settings['logic_low']
                                        , voltage_settings['logic_high']])
    
    def get_voltages_U2(self):
        voltage_settings = {}
        register_supply = self.testd5a.d5a.get_register_supply()
        switch_supply = self.testd5a.d5a.get_switch_supply()
        data_levels = self.testd5a.d5a.get_data_levels()
        
        voltage_settings['positive_shiftregister_voltage'] = register_supply[0]
        voltage_settings['negative_shiftregister_voltage'] = register_supply[1]
        
        voltage_settings['positive_mux_voltage'] = switch_supply[0]
        voltage_settings['negative_mux_voltage'] = switch_supply[1]
        
        voltage_settings['logic_low'] = data_levels[0]
        voltage_settings['logic_high'] = data_levels[1]
        
        return voltage_settings

    def set_voltage_spans(self, voltage_spans):
        """Set SPI rack voltage ranges for Cryomux operation

        Values are normally kept and need not be changed again. Only necessary
        when configuring from scratch."""

        for span in self._voltage_spans:
            self[span](voltage_spans[span])

    def get_voltages(self):
        """Return all the voltage settings used"""
        voltages = {name: self[name] for name in self._voltages}
        return voltages

    def get_sample_information(self):
        """Return information on selected sample"""
        # TODO: link to sample number and resistance
        pass

    # TODO: If works in station configuration, can be removed
    def setup_resistance_measurement(self):
        """Set the digital multimeter to work in resistance mode"""
        pass # this is moved to the station

    # TODO: snapshot
    def get_status(self):
        """Return a status summary of the device"""
        status = {
            'voltages': self.get_voltages(),
            'voltage_spans': self.get_voltages(),
            'sample': self.get_sample_information(),
        }
        return status

    def _send_bit(self, bit):
        """Send bit to shift register

        Args:
            bit (bool/int: 0-1): bit of data for shift register
        """
        print(type(self['mux_data_signal']))
        if bit == 1:
            self['mux_data_signal'](self.logic_high())
            print(bit)
        elif bit == 0:
            self['mux_data_signal'](self.logic_low())
            print(bit)
            
        self['mux_clock_signal'](self.logic_high())
        self['mux_clock_signal'](self.logic_low())
        print("clock")
        
    ''' 
    HACK!!!! FIXME!!!!
    '''
    def SendBitK(self,bit):
        if bit == 1:
            self.testd5a.d5a.set_voltage (self.Data, self.logic_high())
            sleep (0.0001)
            self.testd5a.d5a.set_voltage (self.Clk, self.logic_high())
            sleep (0.0001)
            self.testd5a.d5a.set_voltage (self.Clk, self.logic_low())
            sleep (0.0001)
        elif bit == 0:
            self.testd5a.d5a.set_voltage (self.Data, self.logic_low())
            sleep (0.0001)
            self.testd5a.d5a.set_voltage (self.Clk, self.logic_high())
            sleep (0.0001)
            self.testd5a.d5a.set_voltage (self.Clk, self.logic_low())
            sleep (0.0001)

    def SendStrobeK(self):
        """Send bit to shiftregister"""
        self.testd5a.d5a.set_voltage (self.Str, self.logic_high())
        sleep (0.0001)
        self.testd5a.d5a.set_voltage (self.Str, self.logic_low())


    def _send_strobe(self):
        """Send bit to shift register"""
        self['mux_strobe_signal'](self.logic_high())
        self['mux_strobe_signal'](self.logic_low())
        print("strobe")

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