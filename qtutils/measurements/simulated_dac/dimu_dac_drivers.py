# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 13:37:14 2021

@author: atosato
"""
# https://qcodes.github.io/Qcodes/examples/writing_drivers/Creating-Simulated-PyVISA-Instruments.html

from qcodes.instrument.visa import VisaInstrument
import qcodes.utils.validators as vals
import numpy as np


class Simul_dac(VisaInstrument):
    """
    QCoDeS driver for the stepped attenuator
    Weinschel is formerly known as Aeroflex/Weinschel
    """

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r', **kwargs)

        self.add_parameter('attenuation', unit='dB',
                           set_cmd='ATTN ALL {:02.0f}',
                           get_cmd='ATTN? 1',
                           vals=vals.Enum(*np.arange(0, 60.1, 2).tolist()),
                           get_parser=float)

        self.connect_message()