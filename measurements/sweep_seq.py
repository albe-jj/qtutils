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
from qcodes.plots.pyqtgraph import QtPlot
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
        liveplotwindow = QtPlot()
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


#%%Function to make a 2D sweep(sweep and step two parameters)
def sweep_seq(outputs, sequence=None, sweep_param_ranges=[], plot_param_ls=[],
              location=None, delays= None, file_label='', 
              liveplotting = True, liveplotwindow=None, settle_time=0, 
              maxplots=6, randomize = None, verbose = 1, plt_update_dim = None, clearwindow = True,
              meas_Rn=False, ar_lia2=False, VAC_range=False, tasks=None,
              use_threads=False, base_dir=None,
              **kwargs):
    """
    Args:
        outputs: arrays of measurement functions
        sequence: a pulselib sequence with optional internal sweeps
        sweep_param_ranges: list(tuple(Parameter,list(start, end, step))) extra
            parameters to be swept. [(*inner_sweep_params), ..., (*outer_sweep_params)]
        delays - a number of seconds to wait after setting a value before
            continuing. 0 (default) means no waiting and no warnings. > 0
            means to wait, potentially filling the delay time with monitoring,
            and give an error if you wait longer than expected.
        file_label: string to add to folder name
        tasks: arrays of tasks [[*inner_loop_tasks], ..., [*outer_loop_tasks]]

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
    
    if not plt_update_dim:
        plt_update_dim = dim_total
    
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
            

        
        update_loop = loop
        for k in range(dim_total-plt_update_dim):
            update_loop = update_loop.actions[0]
        update_loop.actions.extend([plotupdate, gui_update])
        update_loop.progress_interval = 5
        
        
        #loop from outer to inner loop to add tasks
        if tasks is None:
            tasks = [[]] * dim_param_sweep
        loopi = loop
        for i in range(dim_param_sweep): 
            dim_i = dim_param_sweep -1 - i
            loopi.actions.extend(tasks[dim_i])
            loopi = loopi.actions[0]

        data = loop.run(use_threads)
        
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