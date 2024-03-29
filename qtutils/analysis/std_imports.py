import numpy as np
from scipy import constants
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm


# from qtutils.analysis import ox_data_utils
from qtutils.analysis import data_utils

from .plot_utils import * 
from .import_data_utils import *
from .mgr_utils import *
from importlib import reload

import sys
from importlib import reload

def reload_all():
	for module in [plot_utils, ox_data_utils, data_utils]:
		reload(module)

me = constants.electron_mass
ech = constants.elementary_charge
eps0 = constants.epsilon_0
hbar = constants.hbar
h = constants.h
G0 = 2*constants.e**2/constants.h
kb = constants.k


mob_label = '$\mu\ (\mathrm{cm^{2}/Vs})$'
dens_label = '$p\ \mathrm{(cm^{-2})}$'
sigma_label = '$\sigma_{xx,0}\ (\mathrm{e^2/h})$'
G_label = '$G \ (\mathrm{2e^2/h})$'
G_diff_label = '$G \ (\mathrm{2e^2/h})$'
