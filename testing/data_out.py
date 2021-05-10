# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 12:14:30 2020

@author: TUD278249
"""


from qcodes.data.data_set import load_data
from qcodes.dataset.plotting import plot_dataset
from qcodes.data.data_array import DataArray
from pathlib import Path

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.pyplot import pcolormesh


import numpy as np
import qcodes

from pandas import DataFrame
import pandas as pd
import os
import glob

ech = 1.60217662e-19 #coulombs
h = 6.62607004e-34 #m2 kg / s
kB = 86 #ueV/K
base_folder = Path(r'D:\LeidenMCK50_fridge\Scripts\Albo')

def get_data(location, names_dict={}, base_folder=base_folder):
    
    file_location = Path(location)
    os.chdir(base_folder/file_location)
    file_path = base_folder/file_location/Path(glob.glob('*.dat')[0])

    # import as qcodes dataset
    dataset = load_data(str(base_folder/location))
    
    # parse column names
    f = open(file_path, 'r')
    line = [f.readline().replace('#', '').replace('"', '') for i in range(3)]
    col_names = line[1].split()
    col_long_names = line[0].split()
    nr_set_vars = len(line[2].split())
    name_set_vals = col_names[:nr_set_vars]

    # remove cols that you both set and measure from measured values
    usecol_idx = list(range(nr_set_vars)) + [idx for idx,name in enumerate(col_names) if name not in name_set_vals]
    usecol_names = [col_names[i] for i in usecol_idx]
    usecol_long_names = [col_long_names[i] for i in usecol_idx]
    
    
    # create dataframe
    df = pd.read_csv(file_path, sep='\t', skiprows=[0,1,2], usecols=usecol_idx, names=usecol_names)
    df.set_index(name_set_vals, inplace=True)
    
    # create DataSet and add metadata
    ds = df.to_xarray()
    for idx, key in enumerate(usecol_names):
        ds[key].attrs = dataset.metadata['arrays'][usecol_long_names[idx]]
        ds[key].attrs['units'] = dataset.metadata['arrays'][usecol_long_names[idx]]['unit']
        
    # rename labels (optional)
    ds = ds.rename(name_dict=names_dict)
    
    # add coords
    # for coord in coords:
    
    # add columns
#     ds['R'] = ds.V_AC/ds.I_AC
#     ds['G'] = ds.I_AC/ds.V_AC*h/(2*ech**2)
    return(ds, df)

def get_data_VDC(location, roll_window=1,  offset=0):
    ds, df = get_data(location)
#     ds.G.plot(cmap='hot', vmin=0, vmax=3)
    vdc = ds.V_DC.rolling(V_DC_bias=roll_window).mean()
    dst = ds.assign_coords(VDC=vdc)
    dst = dst.assign_coords(Vgss=ds.Vg)
    fixed_offset = dst.VDC.mean('V_DC_bias')+offset
    dst['VDC'] = dst.VDC-fixed_offset

    return dst

def plot_VDC_map(location, stepped_var, offset=0, names_dict={}, roll_window=1):
    ds, df = get_data(location)
#     ds.G.plot(cmap='hot', vmin=0, vmax=3)
    vdc = ds.V_DC.rolling(V_DC_bias=roll_window).mean()
    dst = ds.assign_coords(VDC=vdc)
    dst = dst.assign_coords(Vgss=ds.Vg)
    # fixed_offset = (dst.VDC.max('V_DC_bias').mean()+dst.VDC.min('V_DC_bias').mean())/2+3.3e-5 + offset
    fixed_offset = dst.VDC.mean('V_DC_bias')+offset
    dst['VDC'] = dst.VDC-fixed_offset

    dst.G.plot(x='VDC', hue=stepped_var, figsize=(10,7),marker='.')
    plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
    return dst

