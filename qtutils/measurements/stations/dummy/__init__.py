# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 16:40:41 2021

@author: atosato
"""
from dummy_instrument import Dummy_R_measure
from qcodes import Station, Monitor
from qcodes import Instrument
from qcodes.tests.instrument_mocks import DummyInstrument
from qcodes.instrument.parameter import DelegateParameter, combine, CombinedParameter
from qcodes.tests.instrument_mocks import MockParabola

#%%
Instrument.close_all()

# def connect_to_instruments():

# dummy_Rmeas = Dummy_R_measure('dummy_Rmeas')
station = Station(config_file=r'V:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto\Scripts\Measurement script\stations\dummy\config_dummy_station.yaml')

# station.add_component()

# B = DelegateParameter('B', source=dummy_Rmeas.V_AC_bias, unit='T')
station.load_mock_dac
station.load_instrument('mock_parabola')
station.load_instrument('mock_Rmeas')


#%% monitor

# monitor = Monitor(dummy_Rmeas.V_AC, dummy_Rmeas.V_AC_bias, dummy_Rmeas.I_AC)