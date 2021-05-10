# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 15:18:53 2020

@author: TUD278249
"""


from stations import LeidenMCK50
from cryomux.cryomux import CryogenicMultiplexer, FOUR_VOLTS_UNI, FOUR_VOLTS_BI
from measurement.sweep_seq import sweep_seq, set_station_dev, check_station, autorange_lia2_special,autorange_lia1_special
from qcodes.plots.pyqtgraph import QtPlot
from qcodes.instrument.parameter import Parameter
from qcodes.instrument import Instrument
import numpy as np
from measurement.sweep_seq import set_station_dev
from measurement.param_viewer.param_viewer_GUI_main import param_viewer
from spirack import SPI_rack, B2b_module, D5a_module, D4b_module
from qcodes_contrib_drivers.drivers.QuTech.D4 import D4
from measurement.window_mngr import bring_up_window, position_window, resize_window
import time

ech = 1.60217662e-19 #coulombs
h = 6.62607004e-34 #m2 kg / s
kB = 86 #ueV/K

#%% Initialiaze (re-initialize) instrument connections
global station
station = LeidenMCK50.initialize(reinit=True, exclude=[])#'temp_control',
#%%

    
# station.ivvi.set_dacs_zero()



try: 
    gate_liveplot
    [liveplot.win.show(), gate_liveplot.win.show(),cg1_liveplot.win.show(),
      cg2_liveplot.win.show(),time_plot.win.show(), Vbias_liveplot.win.show()] #pv.show(),
except: 
    liveplot = QtPlot()   
    gate_liveplot = QtPlot() 
    cg1_liveplot = QtPlot() 
    cg2_liveplot = QtPlot()
    Vbias_liveplot = QtPlot()
    time_plot = QtPlot()
    # pv = param_viewer(station,dev)
    plt_windows = [liveplot,gate_liveplot,cg1_liveplot,cg2_liveplot,time_plot, Vbias_liveplot]
    for i in plt_windows:
        resize_window(i, geom=[1000,400])


station.keithley1.integrationtime(0.4) #V_DC
station.keithley2.integrationtime(0.4) #I_DC
station.keithley3.nplc(2)

station.keithley1.range(10)
station.keithley2.range(10)
# station.keithley3.nplc(5) # nplc/50=integration_time in s
# station.keithley3.range(10)

set_station_dev(station, dev)

# save_param_ls = [dev.Vg, dev.Vcg1, dev.Vcg2, dev.I_leak_g, 
#                  dev.V_AC_bias, dev.V_DC_bias,
#                  R, G, dev.V_AC, dev.V_DC, dev.I_AC, ]
exlude_from_saving = ['IDN', 'repetitions']
save_param_ls = [dev[param] for param in dev.parameters if param not in exlude_from_saving]
save_param_ls.extend([R,G])

#%%
class combi_par(Parameter):
    def __init__(self, name, param, label):
        """
        Make a combined parameter:
        Args:
            name (str): name of the combi_par
            param (list) : list of parameters
            label (list) : list of labels

        """
        super().__init__(name, label = label, unit= "mV" )
        self.param = param

    def set_raw(self, value):
        for param in self.param:
            param(value)

def make_combiparameter(*args, **kwargs):
    """
    Make a combined qcodes parameter. 
    Args: 
        *args : list of gates or parameters
        (e.g. make_combiparameter("A1", "A3", station.gates.B1 ))
    """
    station = qcodes.station.Station.default
    parameters = []
    for i in args:
        if type(i) == str:
            parameters.append(getattr(hallbar, i))
        else:
            parameters.append(i)

    label = ""
    for i in parameters:
        label += i.label + " "
    name = 'combi_par'
    if 'name' in kwargs:
        name = kwargs['name']
        
    return combi_par(name, parameters, label)

combi_cg = combi_par('combi_cg', [dev.Vcg1, dev.Vcg2],'combi_cg')

#%% Gates

def gate_sweep(target, step, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.Vg, [dev.Vg(), target, step])], 
        plot_param_ls = [R, G, dev.I_leak_g, dev.I_AC],
        clearwindow = cw, liveplotwindow = gate_liveplot,
        )

def cg1_sweep(target, step, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.Vcg1, [dev.Vcg1(), target, step])],       
        plot_param_ls = [R, G, dev.I_AC,dev.I_leak_g],
        clearwindow = cw, liveplotwindow = cg1_liveplot,
        )

def cg2_sweep(target, step, cw, delay=0):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.Vcg2, [dev.Vcg2(), target, step])],       
        plot_param_ls = [R, G, dev.I_AC,dev.I_leak_g],
        clearwindow = cw, liveplotwindow = cg2_liveplot,
        delay=delay
        )
    
def combi_cg_sweep(target, step, cw, delay=0):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(combi_cg, [combi_cg(), target, step])],       
        plot_param_ls = [R, G, dev.I_AC,dev.I_DC, dev.I_leak_g],
        clearwindow = cw, liveplotwindow = cg2_liveplot,
        delay=delay
        )

def combi_cg_field_2Dsweep(combi_cg_sets, B_sets, delays, cw):
        sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (combi_cg, combi_cg_sets),
            (dev.field, B_sets)], 
        plot_param_ls = [R, G, dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot
        )
#%% Other
def field_sweep(field_sets, cw):   
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.field, [field_sets[0], field_sets[1], field_sets[2]])], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = [30], liveplotwindow = liveplot
        )
    
def time_sweep(delay=0, cw=True): 
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(repetitions, [0, 3600*10, 1])], 
        plot_param_ls = [R, G, dev.I_leak_g, dev.I_AC],
        maxplots=4, clearwindow = cw, delays = [delay], liveplotwindow = time_plot
        )

def find_leaking_sample(samples=range(1,14)):
    for i in samples:
        cryomux.sample(i)
        time.sleep(3)
        print([i,round(dev.I_leak_g(),3)])
#%% Current biassweeps
def I_bias_sweep(I_sets, delay, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.I_DC_bias, I_sets)], 
        plot_param_ls = [R, G, dev.V_DC],
        clearwindow = cw, delays = [delay], liveplotwindow = Vbias_liveplot,
        use_threads=True
        )
    
def I_bias_gate_2Dsweep(Vg_sets, I_sets, delays, cw):
        sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.I_DC_bias, I_sets),
            (dev.Vg, Vg_sets)], 
        plot_param_ls = [R, G, dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot
        )

def I_bias_combi_cg_2Dsweep(I_sets, cg_sets, delays, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.I_DC_bias, I_sets),
            (combi_cg, cg_sets)], 
        plot_param_ls = [R, G, dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        )
        
def I_bias_field_2Dsweep(I_sets, B_sets, delays, cw):
        sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.I_DC_bias, I_sets),
            (dev.field, B_sets)], 
        plot_param_ls = [R, G, dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot
        )
        
def field_I_bias_2Dsweep(I_sets, B_sets, delays, cw):
        sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.field, B_sets), 
            (dev.I_DC_bias, I_sets)],
        plot_param_ls = [R, G, dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot
        )

def estimate_2Dsw_time(Vg_lims, Vg_step, I_lims, I_step, delays):
    I_time = (I_lims[1]-I_lims[0])/I_step*delays[0]
    tot_time = I_time* (Vg_lims[1]-Vg_lims[0])/Vg_step
    print(f'I sweep {I_time/60} mins \ntot_time {tot_time/3600} hrs')
    print(f'I-points {(I_lims[1]-I_lims[0])/I_step}, Vg-points {(Vg_lims[1]-Vg_lims[0])/Vg_step}')
        
#%% Voltage bias sweeps
def V_bias_sweep(V_sets, delay, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [(dev.V_DC_bias, V_sets)], 
        plot_param_ls = [R, G, dev.I_DC,dev.V_DC],
        clearwindow = cw, delays = [delay], liveplotwindow = Vbias_liveplot,
        ar_lia=False, VAC_range=False, use_threads=True,
        )
def V_bias_gate_2Dsweep(Vg_sets, V_sets, delays, cw, **kwargs):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.V_DC_bias, V_sets),
            (dev.Vg, Vg_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        # **dict(station=station)
        )

def V_bias_cg2_2Dsweep(cg2_sets, V_sets, delays, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.V_DC_bias, V_sets),
            (dev.Vcg2, cg2_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        # **dict(station=station)
        )

def V_bias_cg1_2Dsweep(cg1_sets, V_sets, delays, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.V_DC_bias, V_sets),
            (dev.Vcg1, cg1_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        # **dict(station=station)
        )

def V_bias_combi_cg_2Dsweep(V_sets, delays, cg_sets, cw, ar_lia2=False):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.V_DC_bias, V_sets),
            (combi_cg, cg_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        # **dict(station=station)
        ar_lia2=ar_lia2
        )
    

def V_bias_field_2Dsweep(V_sets, B_sets, delays, cw):
        sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.V_DC_bias, V_sets),
            (dev.field, B_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        station=station, use_threads=True,
        )
        
def V_bias_temp_2Dsweep(V_sets, mc_heater_sets, delays, cw):
        sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.V_DC_bias, V_sets),
            (station.temp_control.mc_heater, mc_heater_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        station=station
        )

#%% gate to gate

def Vcg_Vg_2Dsweep(Vcg_sets, Vg_sets, delays, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.Vcg, Vcg_sets),
            (dev.Vg, Vg_sets)], 
        plot_param_ls = [R, G, dev.V_AC,dev.V_DC],
        clearwindow = cw, delays = delays, liveplotwindow = liveplot,
        # **dict(station=station)
        )
    


def cg1_cg2_2Dsweep(cg1_sets, cg2_sets, cw):
    sweep_seq(
        outputs = save_param_ls,
        sweep_param_ranges = [
            (dev.Vcg1, cg1_sets),
            (dev.Vcg2, cg2_sets)],       
        plot_param_ls = [R,G, dev.V_AC,],
        clearwindow = cw, liveplotwindow = liveplot,
        )


#%%
# D_sweep_I_bias_gate(Vg_lims=[-3133,-4000], Vg_step=10, I_lims, I_step, delays, cw)
# dev.Vg.

# estimate_2Dsw_time(
#     Vg_lims=[-3133,-4000], Vg_step=11, 
#     I_lims=[0,2700], I_step=5, 
#     delays=[.5,1]
#     )
# #%%
# I_bias_gate_2Dsweep(
#     Vg_sets=[-3133,-4010,11],
#     I_sets=[0,2700,5],
#     delays=[.5,30],
#     cw=True
#     )