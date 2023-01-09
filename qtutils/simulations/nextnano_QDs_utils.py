import re
import pandas as pd
from pathlib import Path
import numpy as np

"""
valid only for version: 4.2.8.6
TODO
"""
class NnDataReader:
    def __init__(self, base_path):
        self.base_path = base_path

        base_folder = Path('C:\Users\atosato\nextnano\output') / base_path

        cols = ['x', 'z', 'Gamma[eV]', 'X_1[eV]', 'X_2[eV]', 'X_3[eV]', 'HH[eV]',
               'LH[eV]', 'SO[eV]', 'electron_Fermi_level[eV]', 'hole_Fermi_level[eV]']
        df = pd.read_csv(base_folder/'bias_00000/bandedges.dat', delim_whitespace=True, names=cols)
        df = df.set_index(['z', 'x'])
        dsb = df.to_xarray()