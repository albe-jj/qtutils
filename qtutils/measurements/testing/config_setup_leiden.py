
class VirtualConfig:
    Imeasure_gain_AC = 1 * 10e6 * 1#V/A 
    Imeasure_gain_DC = 1 * 10e6 * 10#V/A
    
    # Vmeasure gains: M2b * srs preamp
    Vmeasure_gain_AC = 1e3 * 1  #V/V
    Vmeasure_gain_DC = 1e3 * 10 #V/V
    
    Vsource_gain = 1e-3 #V/V
    Isource_gain = 1e-6 #A/V
    
    Istill_gain = 10e-3 #A/V
    Imc_gain = 10e-3 #A/V
    
    dev_params =  { 
        'Vg': {'instrument': 'ivvi','parameter': 'dac4', 
               'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1/15},#1/15
        'Vcg1': {'instrument': 'ivvi','parameter': 'dac9', 
               'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1},
        'Vcg2': {'instrument': 'ivvi','parameter': 'dac10', 
               'step': 20, 'inter_delay': .1, 'unit':'mV', 'scale': 1},
        'field': {'instrument': 'magnet', 'parameter': 'field',
                  'scale':1e-3, 'unit':'mT'},
        # 'field': {'instrument':  'ivvi','parameter': 'dac8', 
        #         'step': 0.05, 'inter_delay': 0.01, 'scale':1/(20*1e-3*0.113375), 'unit':'mT'}, 
        'V_AC_bias': {'instrument': 'lia1','parameter': 'amplitude',  
                'step': 0.1, 'inter_delay': 0.01, 'scale':1/Vsource_gain*1e2*1e-6, 'unit':'uV'}, #1e3 -> isoiin is diveded by 100
        'V_DC_bias': {'instrument': 'ivvi','parameter': 'dac5', 
                      'step': 100, 'inter_delay': .0, 'scale': -1/Vsource_gain*1e3*1e-6, 'unit': 'uV'},#1e3 -> DAC is in mV
        'I_DC_bias': {'instrument': 'ivvi','parameter': 'dac6', 
                      'step': 100, 'inter_delay': .05, 'scale': 1/(Isource_gain*1e9)*1e3, 'unit': 'nA'},#1e3 -> DAC is in mV
        'I_AC_bias': {'instrument': 'lia1','parameter': 'amplitude', 
                      'step': .1, 'inter_delay': .05, 'scale': 1/(Isource_gain*1e9)*100, 'unit': 'nA'},
        
        'I_AC': {'instrument': 'lia2','parameter': 'X', 
              'unit':'A', 'scale': Imeasure_gain_AC},
        'I_DC': {'instrument': 'keithley2','parameter': 'amplitude', 
                  'unit':'A', 'scale': Imeasure_gain_DC},
        'V_AC': {'instrument': 'lia1','parameter': 'X', 
                 'scale': Vmeasure_gain_AC}, 
        'V_DC': {'instrument': 'keithley1','parameter': 'amplitude', 
                 'unit':'V', 'scale': Vmeasure_gain_DC}, 
        # 'I_leak_cg': {'instrument': 'd4', 'parameter':  
        #            'adc1', 'scale': 1e6*1e-9, 'unit':'nA'}, #nA
        'I_leak_g': {'instrument': 'keithley3', 'parameter':  
                   'amplitude', 'scale': 1e6*1e-9, 'unit':'nA'}, #nA
        'temp': {'instrument': 'temp_control', 'parameter': 'mc_temp'}, 
        
        
        # LIA Y componenets
        'V_AC_Y': {'instrument': 'lia1','parameter': 'Y', 
                 'scale': Vmeasure_gain_AC},
        'I_AC_Y': {'instrument': 'lia2','parameter': 'Y', 
              'unit':'A', 'scale': Imeasure_gain_AC},
        
        'I_DC_mc': {'instrument': 'ivvi','parameter': 'dac15', 
                      'step': 100, 'inter_delay': .05, 'scale': 1/(Istill_gain*1e6)*1e3, 'unit': 'uA'}, #1e3 -> DAC is in mV
        'I_DC_still': {'instrument': 'ivvi','parameter': 'dac16', 
                      'step': 100, 'inter_delay': .05, 'scale': 1/(Imc_gain*1e6)*1e3, 'unit': 'uA'}, #1e3 -> DAC is in mV
        }