from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers, Ints, OnOff
import re
import numpy as np
from collections import deque
import time
import logging

'''
TODO
- empty buffer at some point 
'''

log = logging.getLogger(__name__)


class APS100(VisaInstrument):
    '''
    Drivers for magnet power supply 
    '''
    _re_flt = '([-+]?\d+\.\d*?)'
    # shall the ramp limits be added here?
    # also current limit to add here

    def __init__(self, name, address, wait_field_to_target=True,
        atol=0, **kwargs):
        '''
        wait_field_to_target: wait for the field to reach target before return [Ture,False]
        atol: tolerance for target field accuracy (in Tesla) 0.1e-3 T is an acceptable tolerance  

        '''

        super().__init__(name, address, terminator='\r', **kwargs)

        self.visa_handle.baud_rate = 19200
        self._ramp_limit0 = 0.0350 #[0,30] Amps
        self._ramp_limit1 = 0.0175 #[30,45]Amps
        # 0.0100 #[45-60]Amps
        # 0.0100 #[60-?]Amps
        # 0.0100 #[?-??]Amps

        self._sweep_lim_limit = 9 #T
        self._field_atol = atol #0.1e-3 #T



        # ???
        # self.visa_handle.parity = visa.constants.Parity.none
  #       self.visa_handle.stop_bits = visa.constants.StopBits.one
  #       self.visa_handle.data_bits = 8
  #       self.visa_handle.flow_control = 0
  #       self.visa_handle.flush(vi_const.VI_READ_BUF_DISCARD |
  #                              vi_const.VI_WRITE_BUF_DISCARD)  # kee
        self.wait_field_to_target = wait_field_to_target


        self.add_parameter(
            name='field',
            unit='T',
            set_cmd=self._set_field,
            get_cmd=self._get_field,
            )

        self.add_parameter(
            name='rampRate0',
            get_cmd=self._get_rampRate0,
            set_cmd=self._set_rampRate0,
            vals=Numbers(0, self._ramp_limit0)
            )

        self.add_parameter(
            name='rampRate1',
            get_cmd=self._get_rampRate1,
            set_cmd=self._set_rampRate1,
            vals=Numbers(0, self._ramp_limit1)
            )

        self.add_parameter(
            name='ulim',
            get_cmd=self._get_ulim,
            set_cmd=self._set_ulim,
            vals=Numbers(-self._sweep_lim_limit, self._sweep_lim_limit)
            )

        self.add_parameter(
            name='llim',
            get_cmd=self._get_llim,
            set_cmd=self._set_llim,
            vals=Numbers(-self._sweep_lim_limit, self._sweep_lim_limit)
            )

        self.add_parameter(
            name='sweep',
            get_cmd=self._get_sweep,
            set_cmd= self._set_sweep,
            # vals=Numbers() #TODO
            )

        self.add_parameter(
            name='units',
            get_cmd=self._get_units,
            set_cmd=self._set_units,
            # vals=Numbers() #TODO
            )

        self.add_parameter(
            name='heater',
            get_cmd=self._get_heater,
            set_cmd=self._set_heater,
            vals=OnOff()
            )

        self.add_parameter(
            name='connection',
            get_cmd=False, #TODO
            set_cmd=self._set_connection,
            # vals=Numbers() #TODO
            )

        # self.add_parameter(
        #     name='',
        #     get_cmd=self._get_,
        #     set_cmd=self._set_,
        #     vals=Numbers()
        #     )

        # self.add_parameter(
        #     name='',
        #     get_cmd=self._get_,
        #     set_cmd=self._set_,
        #     vals=Numbers()
        #     )

        # self.add_parameter(
        #     name='',
        #     get_cmd=self._get_,
        #     set_cmd=self._set_,
        #     vals=Numbers()
        #     )

        self.units('kG')
        self.connection('remote')

    def get_idn(self):
        """
        Overwrites the get_idn function using constants as the hardware
        does not have a proper \*IDN function.
        """
        idparts = ['Cryomagnetics', 'Magnet PS APS100', 'None', '?']

        return dict(zip(('vendor', 'model', 'serial', 'firmware'), idparts))
    
    def query(self, cmd):
        self.ask_raw(cmd)
        res = self.visa_handle.read()
        return res.strip()

    def _set_connection(self, connection):
        '''local or remote'''
        self.ask(connection)


    def _get_field(self):     
            Imag = self.query('imag?')
            m = re.match(f'{APS100._re_flt}(kG)',Imag)
            field_T = round(float(m[1])/10,5)
            return field_T #in Tesla

    def _set_field(self, field):
        '''if wait_field_to_target is True pauses sweep after reaching target
        with absoulute tolerance atol'''
        self._go_to_target(field, wait_field_to_target=self.wait_field_to_target, atol=self._field_atol)

    def _get_rampRate0(self):
        rate = self.query('rate? 0')
        return float(rate[1:7])

    def _get_rampRate1(self):
        rate = self.query('rate? 1')
        return float(rate[1:7])

    def _set_rampRate0(self, Amp_s):
        self.ask('rate 0 {:.4f}'.format(Amp_s))

    def _set_rampRate1(self, Amp_s):
        self.ask('rate 1 {:.4f}'.format(Amp_s))

    def _get_llim(self):
        r = self.query('llim?')
        m = re.match(f'{APS100._re_flt}(kG)',r)
        llim = round(float(m[1])/10,5) # in Tesla
        return llim

    def _set_llim(self, llim):
        '''llim: sweep lower limit in Tesla'''
        self.ask('llim {:.4f}'.format(llim*10))
        log.debug(f'llim set to {llim}')

    def _get_ulim(self):
        r = self.query('ulim?')
        m = re.match(f'{APS100._re_flt}(kG)',r)
        ulim = round(float(m[1])/10,5) # in Tesla
        return ulim

    def _set_ulim(self, ulim):
        '''ulim: sweep upper limit in Tesla'''
        self.ask('ulim {:.4f}'.format(ulim*10))
        log.debug(f'ulim set to {ulim}')

    def _get_sweep(self):
        r = self.query('sweep?')
        return r.strip()

    def _set_sweep(self, sweep):
        '''UP, DOWN, PAUSE, or ZERO'''
        self.ask('sweep {}'.format(sweep))
        log.debug(f'sweep set to {sweep}')

    def _get_units(self):
        r = self.query('units?')
        return r

    def _set_units(self,units):
        self.ask_raw('units {}'.format(units))

    def _get_heater(self):
        r = int(self.query('pshtr?'))
        if r==1:
            heater = 'on'
        elif r==0:
            heater = 'off'
        return heater

    def _set_heater(self, heater):
        r = self.ask_raw('pshtr {}'.format(heater))

    def _go_to_target(self, target, wait_field_to_target=True, atol=0):
        '''
        atol: ablsolute tolerence (Tesla) to pause ramp
            default is 0.1 mT

        TODO: 
        - set sweep to zero command when target is 0?
        - take a number of averages for determining if field is at target
        - after pausing the sweep the field still changes   
        '''
        if self.sweep()!='Pause':
            self.sweep('pause')

        #TODO validate targert

        field = self.field()
        if target>field:
            self.ulim(target)
            sweep_dir = 'up'
        elif target<field:
            self.llim(target)
            sweep_dir = 'down'
        else:
            return

        if self._can_start_ramping():
            

            self.sweep(sweep_dir)

            if wait_field_to_target:
                at_target = False

                if atol==0: d = deque(maxlen=20)
                else: d = deque(maxlen=1)
                d.append(self.field())

                while not at_target:
                    d.append(self.field())
                    at_target = np.isclose(np.mean(d),target, atol=atol) 
                    time.sleep(.1)
                self.sweep('pause')
        return

    def _can_start_ramping(self):
        '''chek if all is ok before starting to ramp'''
        self._set_connection('remote')
        cond = []
        units = self.units()
        heater = self.heater()
        r = self.query('*STB?')
        bts = bin(int(r))
        sweep = self.sweep()
        llim = self.llim()
        ulim = self.ulim()

        if units == 'kG':
            cond.append('True')
        else: 
            cond.append('False')
            log.error('magnet units are set to {}. Pls set them to "kG"'.format(self.units()))

        if heater=='on':
            cond.append(True)
        else:
            log.error('persistent heater is off. Pls turn it on')

        if int(bts[-3])==0:
            cond.append(True)
        else:
            log.error('quench detected')

        if sweep != 'Pause':
            log.warning('Sweep is in state: {}'.format(sweep))

        if abs(ulim)<=9 and abs(llim)<=9:
            cond.append(True)
        else:
            log.error(f'limits are beyond specs. llim={llim}, ulim={ulim}')

        can_start = all(cond)

        return can_start



