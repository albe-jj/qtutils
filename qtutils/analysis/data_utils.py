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




G0 = 2*constants.e**2/constants.h


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
					print('could not find:\n', network_data_folder)
					self.network_data_folder = None
			except WindowsError as e:
				print(e)
				self.network_data_folder=None
				pass
			
		



	def import_data(self, location, names_dict={},refresh=False):
		file_location = self.base_folder/location
		if self.network_data_folder and (not file_location.is_dir() or refresh):
			network_data_folder=self.network_data_folder/'data'/file_location.parent.name
			upload_to_Mdrive(file_location, network_data_folder)
		file_path_ls = list(file_location.glob('*.dat'))

		ds_ls = []
		for file_path in file_path_ls:

			# import as qcodes dataset
			dataset = load_data(str(file_location))
			
			# parse column names
			with open(file_path, 'r') as f:
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

			# remove rows with nans in set_params
			df.dropna(axis=0, subset=name_set_vals, inplace=True)

			#set index
			df.set_index(name_set_vals, inplace=True)

			#remove parameters that are both set and saved, to avoid duplicate errors
			duplicates = list(set(name_set_vals) & set(df.columns))
			df.drop(columns=duplicates, inplace=True)




			
			# create DataSet and add metadata
			ds = df.to_xarray()
			for idx, key in enumerate(usecol_names):
				ds[key].attrs = dataset.metadata['arrays'][usecol_long_names[idx]]
				ds[key].attrs['units'] = dataset.metadata['arrays'][usecol_long_names[idx]]['unit']
				
			# rename labels (optional)
			ds = ds.rename(name_dict=names_dict)
			
			# add VDC as a coordinate if exist
			if 'V_DC' in ds:
				print('V_AC max: {:.1f} uV'.format(ds.V_AC.max().values*1e6))
				ds = ds.assign_coords(VDC=ds.V_DC*1e6)
				ds.VDC.attrs['units'] = 'uV'

			if 'G' in ds:
				ds.G.attrs['units'] = '2$e^2$/h'
			
			# add coords
			# for coord in coords:
			
			# add columns
		#     ds['R'] = ds.V_AC/ds.I_AC
		#     ds['G'] = ds.I_AC/ds.V_AC*h/(2*ech**2)
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