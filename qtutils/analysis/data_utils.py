import pandas as pd
import xarray as xr


from qcodes.data.data_set import load_data
from qcodes.dataset.plotting import plot_dataset
from qcodes.data.data_array import DataArray

from pathlib import Path
import yaml

import matplotlib.pyplot as plt
from matplotlib import colors
from scipy import constants

import os
import glob


from qtutils.analysis.path_utils import get_root, upload_to_Mdrive




G0 = constants.e**2/constants.h
unit_factor = {
                'n':1e-9,
                'u':1e-6,
                'm':1e-3}

root = Path(r'M:\tnw\ns\qt\ScappucciLab\0_Group members\Alberto')

class DataImporter:
    def __init__(self, base_folder, root=root, network_data_folder=None):
        root = get_root(root) 
        base_folder = root/Path(base_folder)
        if not base_folder.is_dir():
            print('could not find:\n', base_folder)
        else:
            self.base_folder = base_folder

        if network_data_folder:
            network_data_folder = Path(network_data_folder)
            try:
                if network_data_folder.is_dir():
                    self.network_data_folder = Path(network_data_folder)
                else:
                    print('could not connect: ', network_data_folder)
                    self.network_data_folder = None
            except WindowsError as e:
                print(e)
                self.network_data_folder=None
                pass
        else: 
            self.network_data_folder = None
            
        



    def import_data(self, location, names_dict={},refresh=False, 
        with_metadata=False, G_units='e^2/h'):
        file_location = self.base_folder/location
        if self.network_data_folder and (not file_location.is_dir() or refresh):
            network_data_folder=self.network_data_folder/'data'/file_location.parent.name
            upload_to_Mdrive(file_location, network_data_folder)
        file_path_ls = list(file_location.glob('*.dat'))

        ds_ls = []
        for file_path in file_path_ls:
            dataset = load_data(str(file_path))
            dataset.location = str(Path(dataset.location).parent) #to load metadaata need parent folder
            dataset.formatter.read_metadata(dataset)
            ds = dataset.to_xarray()
            _add_param_spec_to_xarray_data_vars(dataset, ds)
            _add_param_spec_to_xarray_coords(dataset, ds)
            ds = _update_param_names(dataset, ds)
            if not with_metadata:
                _drop_metadata(ds)
                
            # rename labels (optional)
            ds = ds.rename(name_dict=names_dict)
            
            # add VDC as a coordinate if exist
            if 'V_DC' in ds:
                print('V_AC max: {:.1f} uV'.format(ds.V_AC.max().values*1e6))
                ds = ds.assign_coords(VDC=ds.V_DC*1e6)
                ds.VDC.attrs['units'] = 'uV'
            
            # add calculateed data vars
            if G_units == '2e^2/h':
                Gzero = 2*G0

            if 'field' in ds.coords._names:
                if ds.field.attrs['units']=='T':
                    ds['invB'] = 1 / ds.field 
                elif ds.field.attrs['units']=='mT':
                    ds['invB'] = 1e3 / ds.field 
                else:
                    print('could not calculate invB. Units of B are wierd')
                ds.invB.attrs['units'] = '1/T'
            
            # add columns
        #     ds['R'] = ds.V_AC/ds.I_AC
        #     ds['G'] = ds.I_AC/ds.V_AC*h/(2*ech**2)
            # if not 'sigma_xx' in ds:
            #     dsr['sigma_xx'] = dsr.Rsq/(dsr.Rsq**2+dsr.Rxy**2)/(G0/2)
            #     dsr.sigma_xx.attrs['units']='e$^2$/h'

            # if not 'sigma_xy' in ds:
            #     ds['sigma_xy'] = ds.Rxy/(ds.Rsq**2+ds.Rxy**2)/(G0/2)
            #     ds.sigma_xy.attrs['units']='e$^2$/h'

            ds_ls.append(ds)
        if len(ds_ls)>1:
            return ds_ls
        else:
            return ds_ls[0]


    def plot_VDC_map(self, location, stepped_var, offset=0, names_dict={}, roll_window=1):
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


    def get_last_measurements(self, no=5, days=5):

        data_path = self.network_data_folder/Path('data')
        list_of_day_folders = data_path.glob('*')
        latest_day_folder = sorted(list_of_day_folders, key=lambda p: p.lstat().st_mtime)[-days:]
        latest_meas = []
        for i in latest_day_folder:
            list_meas = i.glob('*')
            latest_meas += sorted(list_meas, key=lambda p: p.lstat().st_mtime)
        output = ['/'.join(i.parts[-3:]) for i in latest_meas[-no:]]
        output.reverse()
        for i in output:
            print('location = "{}"'.format(i))
        # return output



def convert_units(ds, dim, conversion: tuple):
    ds[dim] = ds.dim / convert_units[conversion]

def _add_param_spec_to_xarray_data_vars(dataset, xrdataset) -> None:
    for data_var in xrdataset.data_vars:
        paramspec_dict = _paramspec_dict_with_extras(dataset, str(data_var))
        xrdataset.data_vars[str(data_var)].attrs.update(paramspec_dict.items())
        
def _add_param_spec_to_xarray_coords(dataset, xrdataset) -> None:
    for coord in xrdataset.coords:
        if coord != "index":
            paramspec_dict = _paramspec_dict_with_extras(dataset, str(coord))
            xrdataset.coords[str(coord)].attrs.update(paramspec_dict.items())

def _paramspec_dict_with_extras(dataset, dim_name: str):
    paramspec_dict = dict(dataset.metadata['arrays'][str(dim_name)])
    # units and long_name have special meaning in xarray that closely
    # matches how qcodes uses unit and label so we copy these attributes
    # https://xarray.pydata.org/en/stable/getting-started-guide/quick-overview.html#attributes
    paramspec_dict["units"] = paramspec_dict.get("unit", "")
    paramspec_dict["long_name"] = paramspec_dict.get("label", "")
    return paramspec_dict



def _update_param_names(dataset, xrdataset):
    for coord in xrdataset.coords:
        xrdataset = xrdataset.rename({coord:xrdataset[coord].long_name})

    for data_var in xrdataset.data_vars:
        long_name = xrdataset[data_var].long_name
        if long_name in xrdataset.coords:
            long_name+= '_meas'
        xrdataset = xrdataset.rename({data_var:long_name})
    return xrdataset

def _drop_metadata(ds):
    if ds. attrs['metadata']:
        del ds.attrs['metadata']