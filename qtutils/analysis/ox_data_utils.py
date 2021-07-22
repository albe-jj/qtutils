# -*- coding: utf-8 -*-
# @Author: atosato
# @Date:   2021-03-17 11:36:11
# @Last Modified by:   Alberto Tosato
# @Last Modified time: 2021-07-16 18:50:46
import pandas as pd
import xarray as xr
from pathlib import Path
import yaml
import matplotlib.pyplot as plt
from matplotlib import colors
from scipy import constants

from tabulate import tabulate
from datetime import datetime

from .path_utils import get_root, upload_to_Mdrive


G0 = 2*constants.e**2/constants.h


root = Path(r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto')

class DataImporter:
    def __init__(self, base_folder, network_data_folder=None, root=root):
        root = get_root(root) 
        base_folder = root/Path(base_folder)
        if not base_folder.is_dir():
            print('could not find:\n', base_folder)
        else:
            self.base_folder = base_folder

        if network_data_folder:
            network_data_folder = Path(network_data_folder)
            if not network_data_folder.is_dir():
                print('could not find:', network_data_folder)
        self.network_data_folder = network_data_folder


    def import_data(self, name, I_gain=1e6, V_gain=1e3, refresh=False, debug=False):
        data_path = self.base_folder/Path(name)
        if self.network_data_folder and (not data_path.is_file() or refresh):
            upload_to_Mdrive(data_path, self.network_data_folder)
        cols = self.get_cols(name)
        df = pd.read_csv(data_path, sep='\t', comment='#', header=None)
        df_cols = pd.DataFrame.from_dict(cols).T.reset_index()

        df.drop([8,9], axis=1, inplace=True)
        df.columns = df_cols.drop([8,9]).name.values

        set_params = []
        units = []

        if 'triton (magnitude (Tesla))' in df.columns:
            df['B'] = df['triton (magnitude (Tesla))']
            set_params += ['B']
            units += ['T']
        if 'dac4 (CG1 (5V/V))' in df.columns:
            df['Vcg'] = df['dac4 (CG1 (5V/V))']*5 #mV
            set_params += ['Vcg']
            units += ['mV']
        if 'dac1 (Vbias (10mV/V))' in df.columns:
            df['V_DC_bias'] = df['dac1 (Vbias (10mV/V))']*1e3 #V
            set_params += ['V_DC_bias']
            units += ['V']
        if 'dac1 (Vbias (1mV/V))' in df.columns:
            df['V_DC_bias'] = df['dac1 (Vbias (1mV/V))']*1e2 #V??
            set_params += ['V_DC_bias']
            units += ['V']
        if 'dac1 (Ibias (1uA/V))' in df.columns:
            df['I_DC_bias'] = df['dac1 (Ibias (1uA/V))']*1 #nA
            set_params += ['I_DC_bias']
            units += ['nA']
            print('Ibias')
        if 'temperature (temperature)' in df.columns:
            df['Temp'] = df['temperature (temperature)'] #V
            set_params += ['Temp']
            units += ['K']
        if 'dac8 (Dummy)' in df.columns:
            df['reps'] = df['dac8 (Dummy)']
            set_params += ['reps']

        # if 'triton' in cols['Column 2']['name']:
        #     df['B'] = df[1]
        #     set_params += ['B']
        #     units += ['T']
        # elif 'dac4' in cols['Column 2']['name']:
        #     df['Vcg'] = df[1]*5 #mV
        #     set_params += ['Vcg']
        #     units += ['mV']
        # if 'Vbias' in cols['Column 1']['name']:
        #     df['V_DC_bias'] = df[0]*1e3 #V
        #     set_params += ['V_DC_bias']
        #     units += ['V']
        # if 'Ibias' in cols['Column 1']['name']:
        #     df['I_DC_bias'] = df[0]*1e3* 1e-3 #mA
        #     set_params += ['I_DC_bias']
        #     units += ['mA']
        #     print('Ibias')
        # if 'temperature' in cols['Column 2']['name']:
        #     df['Temp'] = df[1] #V
        #     set_params += ['Temp']
        #     units += ['K']



        df = df.set_index(set_params)
    #     df.index.set_names(['V_DC_bias', 'Vcg'], inplace=1)
        df['G'] = df['Lockin 2']/G0
        df['V_DC'] = df['Keithley 2']
        df['I_DC'] = df['Keithley 1']
        df['V_AC'] = df['Lockin2_X']/V_gain
        df['I_AC'] = df['Lockin1_X']/I_gain
        df['R'] = df.V_AC/df.I_AC
        # df['Temp_meas'] = df['T_mc']

        df.columns = df.columns.astype(str)
        if debug:
            return df

        if df.index.duplicated().any():
            print('WARNING: removing duplicated indexes')
            df = df[~df.index.duplicated(keep='first')]

        ds = df.to_xarray()

        # ds = ds.set_coords('V_DC')
        if 'Vbias' in cols['Column 1']['name']:
            ds = ds.assign_coords(VDC=ds.V_DC*1e6)
            ds.VDC.attrs['units']='uV'
        if 'triton' in cols['Column 2']['name']:
            ds.B.attrs['units']='T'
        # if 'Temp' in set_params:
        #     ds = ds.assign_coords(T_meas = ds.Temp_meas)
        #     ds.T_meas.attrs['units'] = 'K'
        ds.G.attrs['units']='2$e^2$/h'
        print('max V_AC : {:.1f} uV'.format(ds.V_AC.max().values*1e6))
        
        for set_param, unit in zip(set_params,units):
            ds[set_param].attrs['units'] = unit

        return ds


    def get_cols(self, name):
        txt = ''
        with open(self.base_folder/Path(name)) as f:
            for line in f:
                if line.startswith('#'):
        #             print(line.strip('#'))
                    line = line.replace('# ','')
                    line = line.replace('\t','   ')
                    txt+=line.strip('#')

        cols_dict = yaml.safe_load(txt).copy()
        cols_dict.pop('Filename')
        cols_dict.pop('Timestamp')
        cols_dict
        cols = [item['name'] for item in cols_dict.values()]
        index = [item['name'] for item in cols_dict.values() if item['type']=='coordinate']
        return cols_dict


    def get_settings(self, name, refresh=False):
        file_path = self.base_folder/ name
        if self.network_data_folder and (not file_path.is_file() or refresh):
            upload_to_Mdrive(file_path, self.network_data_folder)
        with open(file_path,'r') as file:
            txt = ''
            for i in range(2):
                _ = file.readline()
            for line in file: 
                if 'Instrument' in line:
                    line = line.replace('Instrument: ','')[:-2]
                    line += ':\n'
                txt +=line.replace('\t','  ')
        return yaml.safe_load(txt)


    def get_last_measurements(self, no=5):

        list_meas = self.network_data_folder.glob('*.dat')
        latest_meas = sorted(list_meas, key=lambda p: p.lstat().st_mtime)
        output = [[ i.name,
                    round( i.stat().st_size * 1e-6, 2), 
                    datetime.fromtimestamp(i.stat().st_mtime).strftime("%m-%d %H:%M "),#.ToString("MM/dd/yyyy hh:mm tt"), 
                    datetime.fromtimestamp(i.stat().st_ctime).strftime("%m-%d %H:%M "),
                    ] for i in latest_meas[-no:]]
        output.reverse()
        print(tabulate(output, ['', 'Mb', 'mtime', 'ctime' ]))
        # return output

    def get_Vg(self, name):
        return self.get_settings(name+'.set')['IVV']['dac3']*15