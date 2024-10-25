import re
import pandas as pd
from pathlib import Path
import numpy as np

import nextnanopy as nn
import xarray as xr
import pandas as pd
from pathlib import Path


# extend DataFile class with method to_xarray
from nextnanopy.outputs import DataFile

def to_xarray(self):
    coords_name = [i.name for i in self.coords]
    data_dict = {}
    coords_dict = {}
    for i in self.data:
        if hasattr(i,'dim'):
            coords_dict[i.name] = i.value
        else:
            data_dict[i.name] = (coords_name, i.value)
 
    ds = xr.Dataset(
        coords = coords_dict,
        data_vars = data_dict 
    )
    for i in self.data:
        ds[i.name].attrs['units'] = i.unit
    return ds 
DataFile.to_xarray = to_xarray


"""
valid only for version: 4.2.8.6
TODO
add units to all quantities //ds.z.assign_attrs(units='nm') 
add importing of LH quantum 
"""
class NnDataReader:

    file_ls = ['bandedges.fld', 'potential.fld', 'electric_field.fld',
           'Quantum/density_subbands_quantum_region_HH.fld', 
           'Quantum/probabilities_quantum_region_LH_.fld', 
           'Quantum/probabilities_quantum_region_HH_.fld', 
           'Quantum/amplitudes_quantum_region_HH.fld',
           'Quantum/energy_spectrum_quantum_region_HH_00000.dat',
           'Quantum/occupation_quantum_region_HH.dat']

    def __init__(self, base_path):
        '''
        base path
        '''
        self.base_path = base_path



    # Importing all files for all biases 
    def import_all_files_all_biases(self, gate_swept, file_ls=file_ls):
        '''
        base_folder: folder containing all data
        gate_swept: name of gate swept incl units e.g. "Plunger_bias[V]"
        file_ls: list of files paths to import relative to base_folder 
        '''

        base_folder = Path(self.base_path)
        
    #    get all files names based on folder at bias_00000
        if file_ls:
            files = [Path(i) for i in file_ls]
        else:
            files = [file.relative_to(base_folder/'bias_00000') for file in Path(base_folder/'bias_00000').rglob('*.fld')]
            files += [file.relative_to(base_folder/'bias_00000') for file in Path(base_folder/'bias_00000').rglob('*.dat')]

            exclude = 'shift' #as cannot be opened with nextnanopy
            files = [file for file in files if exclude not in file.name]
        #     [file.name for file in files]

        gates = pd.read_csv(base_folder / 'bias_points.log', delim_whitespace=True)
        all_gates = [i for i in gates.columns if 'bias' in i ]

        # [file.name for file in Path(base_folder+'/bias_'+bias_no).glob('*.fld')]
        data_dict = {}
        for file in files:
            ds_ls = []
            for idx, gates_i in gates.iterrows():
                bias_no = 'bias_' + str(idx).zfill(5)

                datafile = nn.DataFile(base_folder/bias_no/file, product='nextnano++')
                ds = datafile.to_xarray()
                for gate_name in all_gates:
                    ds[gate_name.replace('_bias[V]','')] = gates_i[gate_name]
                ds.coords[gate_swept.replace('_bias[V]','')] = gates_i[gate_swept]

                ds_ls.append(ds)
                dataset_name = file.name.replace('.fld','').replace('.dat', '')
            data_dict[dataset_name] = xr.concat(ds_ls, dim=gate_swept.replace('_bias[V]',''))
        return data_dict
            
            
    def import_one_file_all_biases(self, rel_path, gate_swept):
    # this is actually wrong keeps importing the same file
        base_folder = Path(self.base_path)
        rel_path = Path(rel_path)
        
        ds_ls = []
        gates = pd.read_csv(base_folder / 'bias_points.log', delim_whitespace=True)
        all_gates = [i for i in gates.columns if 'bias' in i ]
        
        for idx, gates_i in gates.iterrows():
            bias_no = 'bias_' + str(idx).zfill(5)
            datafile_2d = nn.DataFile(base_folder/bias_no/rel_path, product='nextnano++') # 2D .fld file
            ds = datafile_2d.to_xarray()
            
            for gate_name in all_gates:
                ds[gate_name.replace('_bias[V]','')] = gates_i[gate_name]
            ds.coords[gate_swept.replace('_bias[V]','')] = gates_i[gate_swept]
            ds_ls.append(ds)

        return xr.concat(ds_ls, dim=gate_swept.replace('_bias[V]',''))


    def import_data(self, no_subbands):
        """
        Import data from SP calculations done with nextnano++

        Input:
        no_subbands: no of subbands due to z confinement to import

        Output: 
        ds: dataset with 
            - wavefunction amplitude
            - Energy [eV]
            - density [cm^-2]
            - HH band edge
            - LH band edge [eV]
            - Holes fermi energy [eV]
            for the first n subbands (due to z confinement) of HH.

        dss: subset of ds for subbands with positive energies (populated with holes) only

        df_hole_dens: dataframe with integrated density of holes in regions defined in nextnano input.

        notes on imput file:
        make sure that:
            output_bandedges{ averaged = yes } 
        """
        base_path = self.base_path

        #get bias points
        df_bias_pts = pd.read_csv(base_path/'bias_points.log', delim_whitespace=True)
        #get quantum stuff
        ls = []
        df_ls = []
        for i, (idx,bias) in df_bias_pts[['GateContact_index','GateContact_bias[V]']].iterrows():
            bias_idx = str(int(idx)).zfill(5)

            # import wavefunctions amplitude data
            dfi_q = pd.read_csv(base_path / f'bias_{bias_idx}' / 'QUantum' / f'wf_amplitudes_shift_quantum_region_HH_0000.dat',delim_whitespace=True) #new data
            # dfi_q = pd.read_csv(base_path / f'bias_{bias_idx}' / 'QUantum' / f'amplitudes_shift_quantum_region_HH.dat',delim_whitespace=True) #old nn version

            dfi_q = cleanup_cols(dfi_q)
            dfi_q.set_index('x', inplace=True)

            #import bandedges data
            dfi_BE = pd.read_csv(base_path / f'bias_{bias_idx}' / f'bandedges.dat',delim_whitespace=True)
            dfi_BE = cleanup_cols(dfi_BE)
            dfi_BE.set_index('x', inplace=True)
            dfi_BE = dfi_BE.loc[dfi_q.index] #take only x subset where quantum stuff is caculated
            dfi_BE.iloc[0]=None #remove first point bc average with oxide HH band
            # import density per subband
            for sbb in range(1,no_subbands+1):
                sbb_idx = str(sbb).zfill(4)
                dfi = pd.read_csv(base_path / f'bias_{bias_idx}'  / f'density_subband_quantum_region_HH_{sbb_idx}.dat',
                                  delim_whitespace=True, header=0, names = ['x', 'dens'])
                dfi = cleanup_cols(dfi)
                dfi.set_index('x', inplace=True)
                dfi['Vg'] = bias
                dfi['sbb'] = sbb
                grid_spacing = (dfi.index.max() - dfi.index.min()) * 1e-9 * 1e2 / (len(dfi.index)-1) # cm
                dfi['dens'] = dfi.dens * 1e18 * grid_spacing  # Subband_density[1e18_cm^-3] → cm^-2
                dfi['E'] = dfi_q[f'E_{sbb}'] # [eV]   
                dfi['wf_ampl'] = dfi_q[f'Psi_{sbb}_real'] # [nm^-1/2]
                dfi['HH_edge'] = dfi_BE['HH']
                dfi['LH_edge'] = dfi_BE['LH']
                dfi['Ef_hole'] = dfi_BE['hole_Fermi_level']

                dfi.reset_index(inplace=True)
                dfi.rename(columns={'x':'z'},inplace=True)
                df_ls.append(dfi)

        df = pd.concat(df_ls)
        ds = df.set_index(['Vg', 'sbb', 'z']).to_xarray()
        ds['E'] = ds.reduce(np.mean, 'z').E # reduce the dimension for E to remove dependence on x
        ds['HH_edge'] = ds.reduce(np.mean, 'sbb')['HH_edge'] # reduce the dimension for band edges to remove dependence on sbb
        ds['LH_edge'] = ds.reduce(np.mean, 'sbb')['HH_edge']
        ds['Ef_hole'] = ds.reduce(np.mean, 'sbb')['Ef_hole']
        # select only states with positive energy
        dss = ds.where(ds.E>0)
        
        df_hole_dens = pd.read_csv(base_path/'integrated_density_hole.dat', delim_whitespace=True)
        df_hole_dens = cleanup_cols(df_hole_dens)
        df_hole_dens.rename(columns={'bias':'Vg'},inplace=True)

        return ds, dss, df_hole_dens

def cleanup_cols(df):
    "remove units from df columns"
    df.columns = [re.sub("[\(\[].*?[\)\]]", "", i) for i in df.columns]
    return df

# base_path = Path(r'\\tudelft.net\staff-homes\t\atosato\My Documents\nextnano\Output\TQW_stacked_dots')
# di = NnDataReader(base_path)
# di.import_data(no_subbands=2)