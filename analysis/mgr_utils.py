# -*- coding: utf-8 -*-
# @Author: atosat
# @Date:   2021-06-17 14:05:44
# @Last Modified by:   TUD278249
# @Last Modified time: 2021-06-17 16:40:28

from scipy import constants
from qtutils.analysis.plot_utils import * 

me = constants.electron_mass
ech = constants.elementary_charge
eps0 = constants.epsilon_0
hbar = constants.hbar
h = constants.h
G0 = 2*constants.e**2/constants.h

def calc_mob_dens(ds, B_slice, Vg_slice, std_xy_tol, std_xx_tol, with_plts=True):
    dsr = ds.sel(field=B_slice, Vg=Vg_slice)
    dsr = dsr.where((dsr.Rxy.std('field')<std_xy_tol) & (dsr.Rsq.std('field')<std_xx_tol))
    dsr = dsr.dropna(dim='Vg', subset=['Rxy'])

    if dsr.field.attrs['units']=='mT':
        field_scaling = 1e3
    elif dsr.field.attrs['units']=='mT':
        field_scaling = 1
    else:
        print('assuming field in Tesla')
        field_scaling = 1

    coef = dsr.Rxy.polyfit(dim='field',deg=1).polyfit_coefficients

    dsr['dens'] = (coef[0]*field_scaling*ech*1e4)**-1
    dsr.dens.attrs['units'] = 'cm$^{-2}$'
    dsr['mob'] = (dsr.dens*ech*dsr.Rsq.sel(field=0, method='nearest'))**-1
    dsr.mob.attrs['units'] = 'cm$^2$/Vs'

    dsr = dsr.drop('degree')
        # plt.ylim(0,.5e6)

    if with_plts:
        ax1,ax2 = two_axis(figsize=[10,3])
        dsr.Rxy.plot(hue='Vg', ax=ax1, add_legend=False )
        dsr.Rsq.plot(hue='field', ax=ax2, add_legend=False)
        plt.show()

        ax1,ax2 = two_axis(figsize=[10,3])
        dsr.plot.scatter(x='Vg', y='dens',ax=ax1)
        dsr.plot.scatter(x='Vg', y='mob', ax=ax2)
        plt.show()

        dsr.plot.scatter(x='dens', y='mob')
        plt.show()
    print("max dens = {:.2e}".format(dsr.dens.max().values))
    print("max mob = {:.2e}".format(dsr.mob.max().values))


    return dsr