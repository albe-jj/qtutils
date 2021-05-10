# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 12:51:39 2020

@author: TUD278427
"""

import pyqtgraph as pg
import qcodes
from qcodes.loops import Loop
from qcodes.loops import Task
from qcodes.measure import Measure
from qcodes import Parameter
import numpy as np
import time
from functools import partial
from time import sleep
from window_mngr import bring_up_window, position_window, resize_window
import os
#%%
def set_station_dev(st,dv):
    global station
    global dev
    station = st
    dev = dv

def check_station():
    return station

def parse_param(gate):
    if isinstance(gate, Parameter):
        return gate
    elif isinstance(gate, str):
        return getattr(station.gates, gate)
    else:
        raise Exception(
            'parameter has to be either string or qcodes parameter')

def parse_range(r, param, randomize = False):
    if isinstance(r, list) and len(r) == 3:
        sw = param[r[0]:r[1]:r[2]]
    else:
        sw = param[r]
    if randomize:
        np.random.shuffle(sw._values)        
    return sw

def upload_play(seq):
    seq.upload(seq.sweep_index[::-1])
    seq.play(seq.sweep_index[::-1])
    seq.uploader.wait_until_AWG_idle()

def play(seq):
    seq.play(seq.sweep_index[::-1], release = False)
    seq.uploader.wait_until_AWG_idle()

def get_y_plot(data):
    VarPlt = []
    vv = [k for (k, v) in data.arrays.items() if not v.is_setpoint]
    if (len(vv) > 0):
        for element in vv:
            VarPlt.append([data.arrays[element], data.arrays[vv[0]].name])

    return VarPlt

def ramp_param(values, index=0, settle_time=1, verbose = False):
    
    param = values.parameter
    val = values[index]
    if verbose > 0:
        print('ramping gate:'+param.name+' to value '+str(val))

    if hasattr(param, 'get'):
        v = param.get()
        if v is not None:
            try:
                if val != np.round(v):
                    param(val)
                    sleep(settle_time)
            except:
                pass
    else:
        param(val)

def add_liveplot(liveplotwindow, y_plt, maxplots, clw, plot_idx_ls):
    if liveplotwindow is None:
        liveplotwindow = liveplot
    if liveplotwindow is not None:
        # liveplotwindow.win.show()
        liveplotwindow.win.show()
        if clw:
            liveplotwindow.clear()
            
        liveplotwindow.win.activateWindow()
        j = 0
        # for i in range(0, min(maxplots, len(y_plt))):
        for i in plot_idx_ls:
            data_dim = len(np.shape(y_plt[i][0])) if np.shape(y_plt[i][0])[0] > 1 else 0 #Detect dimension of plot, discriminate between (n,) and (1,)
            if data_dim < 3 and data_dim > 0:
                liveplotwindow.add(y_plt[i][0], subplot=j + 1)
                j = j + 1
        return Task(liveplotwindow.update)

def autorange_li():
    # time.sleep(3)
    station.lia1.auto_gain()
    time.sleep(3)
    
def kick_gate():
    hallbar.Vg(1000)
    print('gate set to +2000 mV')
    hallbar.Vg(-1400)
    print('gate set to -1400 mV')
    time.sleep(10)
    
def measure_Rn():
    hallbar.DC_offset(0)
    magnet_ramp_up(field=.12) # set B > Bc
    save_Rn_tofile(file_path)
    magnet_ramp_down(field=0)
    station.magnet.field(0)
    time.sleep(1)
    
    
    
   
def create_Rn_file():
    start_time = int(time.time())
    start_date = date.today()
    folder_path = Path(r'D:\LeidenMCK50_fridge\Scripts\Albo\data\Rn_steps\{}'.format(start_date))
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / Path('{}steps.txt'.format(start_time))
    with open(file_path, 'w') as f:
        f.write("{}\t{}\t{}\t{}\t{}\n".format("Vxx", 'Vxx_DC', "Isd",'B','seat'))
        f.write("{}\t{}\t{}\t{}\t{}\n".format("V", "V", "A", 'T',''))
    return file_path
        
def save_Rn_tofile(file_path):
    sample=cryomux.sample()
    Vxx = hallbar.Vxx()
    Isd = hallbar.Isd()
    B = station.magnet.field()
    Vxx_DC = hallbar.Vxx_DC()
    with open(file_path, 'a') as f:   
            f.write(f"\t{Vxx}\t{Vxx_DC}\t{Isd}\t{B}\t{sample}\n")
            
def autorange_lia(srs, max_changes=5):
    def autorange_once():
        r = srs.R.get()
        sens = srs.sensitivity.get()
        if r > 0.9 * sens:
            return srs.increment_sensitivity()
        elif r < 0.1 * sens:
            return srs.decrement_sensitivity()
        return False

    sets = 0
    while autorange_once() and sets < max_changes:
        sets += 1
        time.sleep(srs.time_constant.get())
            
def autorange_lia1_special():
    time.sleep(1)
    lia1 = station.lia1
    autorange_lia(lia1, max_changes=30)  
    lia1.increment_sensitivity()
    # lia1.increment_sensitivity()

def autorange_lia2_special():
    time.sleep(1)
    lia2 = station.lia2
    autorange_lia(lia2, max_changes=30)  
    lia2.increment_sensitivity()
    # lia1.increment_sensitivity()
            
    
def set_VAC():
    while dev.V_AC()>1e-6 and dev.V_AC_bias()>1:
        new_bias = dev.V_AC_bias()-.1
        dev.V_AC_bias(new_bias)
        time.sleep(.5)

def nothing():
    return None

# def check_leakage():
#     condition = (dev.I_leak()>0.2 or dev.I_leak()<-0.2)
#     return condition
#%%Function to make a 2D sweep(sweep and step two parameters)
def sweep_seq(outputs, sequence=None, sweep_param_ranges=[], plot_param_ls=[],
              location=None, delays= None, file_label='', 
              liveplotting = True, liveplotwindow=None, settle_time=0, 
              maxplots=6, randomize = None, verbose = 1, update_dim = None, clearwindow = True,
              meas_Rn=False, ar_lia2=False, VAC_range=False, task_list=None,
              use_threads=False, base_dir=None,
              **kwargs):
    """
    Args:
        outputs: arrays of measurement functions
        sequence: a pulselib sequence with optional internal sweeps
        sweep_param_ranges: list(tuple(Parameter,list(start, end, step))) extra
            parameters to be swept.
        delays - a number of seconds to wait after setting a value before
            continuing. 0 (default) means no waiting and no warnings. > 0
            means to wait, potentially filling the delay time with monitoring,
            and give an error if you wait longer than expected.
        file_label: string to add to folder name
    """
    
    # global station
    #creates file to measure Rn
    if meas_Rn:
        global file_name
        file_path = create_Rn_file()
    
    # Being flexible on the inputs, bit ugly
    if isinstance(sequence, list):
        if verbose > 0:
            print('Sequence was set to list, assuming no sequence...')
        sweep_param_ranges = sequence
        sequence = None
    
    # Determining dimensions of sequence and sweep_params
    dim_seq_sweep = len(sequence.labels) if sequence else 0
    dim_param_sweep = len(sweep_param_ranges)
    dim_total = dim_seq_sweep + dim_param_sweep
    
    # Sanity checking inputs
    if not delays:
        delays = [0]*dim_total
    elif len(delays) is not dim_total:
        raise Exception('Delays array has incorrect length')
    if not randomize:
        randomize = [False]*dim_total
    elif len(randomize) is not dim_total:
        raise Exception('Randomize array has incorrect length')
    
    if verbose > 0:
        print('%iD sweep detected' %dim_total)    
    
    if not update_dim:
        update_dim = dim_total
    
    ## Constructing the loops
    i = 0
    loop = None
    
    # Define some stuff dependent on existence of sequence
    if sequence:
        upload_play_task = Task(partial(upload_play,sequence))
        label = "vs".join([sp.name for sp in sequence.params] + [sp[0].name for sp in sweep_param_ranges])
    else:
        label = "vs".join([sp[0].name for sp in sweep_param_ranges])

    if verbose > 1:
        print('Measuring' + label)
        
    # Looping through sequence parameters    
    for i in range(dim_seq_sweep):
        sweepvalues = parse_range(sequence.setpoints[i], sequence.params[i], randomize[i])
        if loop:
            loop = Loop(sweepvalues, delay=delays[i]).each(loop)
        else:
            if verbose > 1:
                print('first loop is sequence')
            loop = Loop(sweepvalues, delay=delays[i]).each(upload_play_task, *outputs)
    
    # Looping through sweep parameters
    for (j, param_range) in enumerate(sweep_param_ranges):
        param = parse_param(param_range[0])
        sweepvalues = parse_range(param_range[1], param, randomize[i+j])
        ramp_param(sweepvalues, settle_time=settle_time, verbose = verbose)
        
        # Check if there is already an existing loop to build on top
        if loop:
            loop = Loop(sweepvalues, delay=delays[j]).each(loop)
            print(sweepvalues)
        # If not, define first loop with measurables
        else:
            if verbose > 1:
                print('first loop is non-sequence')
            # If a sequence (without sweeps) exists, add a waveform play task
            if sequence:
                play_task = Task(partial(play,sequence))
                sequence.upload(sequence.sweep_index)
                loop = Loop(sweepvalues, delay=delays[i]).each(play_task, *outputs)
            # Else, regular measurement loop
            else:
                loop = Loop(sweepvalues, delay=delays[i]).each(*outputs)
    

    if base_dir:
        os.chdir(base_dir)
        print(os.getcwd())
    # If no loop was generated, measurement needs to be taken (using dummy loop)    
    if not loop:
        measure = Measure(*outputs)      
        data = measure.get_data_set(
        location=location,
        loc_record={
            'name': 'sweep0D',
            'label': '0D_measurement' + file_label})
        if sequence:
            upload_play(sequence)
        data = measure.run(use_threads)    
        if liveplotting:
                y_plt = get_y_plot(data)
                add_liveplot(liveplotwindow, y_plt, maxplots, clearwindow)
    # 
    else:
        data = loop.get_data_set(
            location=location,
            loc_record={
                'name': 'sweep%iD' % dim_total,
                'label': label + file_label})
    
        if liveplotting:
            y_plt = get_y_plot(data)  
            plot_idx_ls = [outputs.index(param) for param in plot_param_ls if param in outputs]
            plotupdate = add_liveplot(liveplotwindow, y_plt, maxplots, clearwindow, plot_idx_ls)
            gui_update = Task(pg.mkQApp().processEvents)
            
    
        ar_lia2_task = Task(autorange_lia2_special) if ar_lia2 else Task(nothing)
        set_VAC_task = Task(set_VAC) if VAC_range else Task(nothing)
        kick_gate_task = Task(kick_gate)
        meas_Rn_task = Task(measure_Rn) if meas_Rn else Task(nothing)
        # check_leak_task = Task(check_leakage)
        
        # qttBreak = qcodes.actions.BreakIf(check_leak_task)
        
        update_loop = loop
        for k in range(dim_total-update_dim):
            update_loop = update_loop.actions[0]
        update_loop.actions.extend([plotupdate, gui_update] + task_list)#ar_task, kick_gate_task # update_loop.actions.extend([plotupdate, gui_update, qttBreak])#ar_task, kick_gate_task
        update_loop.progress_interval = 5
        
        data = loop.run()
        
    # data.add_metadata({'gates': station.gates.allvalues()})
    if sequence:
        try:
            data.add_metadata(sequence.metadata)
        except:
            print("failed to add metadata")
    try:
        data.save_metadata()
    except BaseException:
        pass
        
    data.finalize()

    return data