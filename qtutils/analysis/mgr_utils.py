# -*- coding: utf-8 -*-
# @Author: atosat
# @Date:   2021-06-17 14:05:44
# @Last Modified by:   Alberto Tosato
# @Last Modified time: 2023-01-12 11:59:37

from scipy import constants
from qtutils.analysis.plot_utils import * 
from scipy.fft import fft
import xrft
from scipy.signal import hilbert, find_peaks
from scipy.optimize import curve_fit


me = constants.electron_mass
ech = constants.elementary_charge
eps0 = constants.epsilon_0
hbar = constants.hbar
h = constants.h
G0 = constants.e**2/constants.h
mu_B = constants.physical_constants['Bohr magneton'][0]

mob_label = '$\mu\ (\mathrm{cm^{2}/Vs})$'
dens_label = '$p\ \mathrm{(cm^{-2})}$'
sigma_label = '$\sigma_{xx,0}\ (\mathrm{e^2/h})$'

def calc_mob_dens(ds, B_slice=slice(None), Vg_slice=slice(None), std_xy_tol=1e6, std_xx_tol=1e6, with_plts=True):
    dsr = ds.sel(field=B_slice, Vg=Vg_slice)
    dsr = dsr.where((dsr.Rxy.std('field')<std_xy_tol) & (dsr.Rsq.std('field')<std_xx_tol))
    dsr = dsr.dropna(dim='Vg', subset=['Rxy'])

    if dsr.field.attrs['units']=='mT':
        field_scaling = 1e3
    elif dsr.field.attrs['units']=='T':
        field_scaling = 1
    else:
        print('assuming field in Tesla')
        field_scaling = 1

    zero_field = 0
    closest_field_to_zero = dsr.sel(field=0, method='nearest').field.values
    if closest_field_to_zero!=0:
        print(f'No data for field=0, assuming zero field at B={closest_field_to_zero} {dsr.field.attrs["units"]}')
        zero_field = closest_field_to_zero
    # if not sigma_xx in ds:
    #     dsr['sigma_xx'] = dsr.Rsq/(dsr.Rsq**2+dsr.Rxy**2)/(G0/2)
    #     dsr.sigma_xx.attrs['units']='e$^2$/h'

    # if not sigma_xx_0 in ds:
    #     dsr['sigma_xx_0'] = 1/dsr.Rsq.sel(field=0, method='nearest') 
    #     dsr.sigma_xx_0.attrs['units'] = '$\Omega$'

    coef = dsr.Rxy.polyfit(dim='field',deg=1).polyfit_coefficients

    dsr['dens'] = (coef[0]*field_scaling*ech*1e4)**-1
    dsr.dens.attrs['units'] = 'cm$^{-2}$'
    dsr['mob'] = (dsr.dens*ech*dsr.Rsq.sel(field=zero_field))**-1
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

    # calculate capacitance 
    coef = dsr.dens.polyfit(dim='Vg',deg=1).polyfit_coefficients
    capacitance = coef[0] * -ech * 1e3 #1e3 factor to convert mV in V
    print('capacitance = {:.2f} nF/cm2'.format(capacitance.values*1e9))
    dsr['capacitance'] = capacitance

    # mean free path at peak mobility
    vg = float(dsr.mob.idxmax('Vg').values)
    mob = dsr.sel(Vg=vg).mob.values * 1e-4
    dens = dsr.sel(Vg=vg).dens.values * 1e4
    lmfp = mob * hbar * (2 * np.pi * dens)**0.5 / ech
    print('mean free path at peak mob = {:0.3f} um'.format(lmfp*1e6))


    return dsr


def calc_sdh_dens(da, interp_arr, m, p_trash=2):
    '''
    !!! GIVES WRONG RESULTS !!!
    Calculate SdH density given a datarray.
    da:
    interp_arr: array used for interpolating 1/B
    m: molteplicity (2 if Zeeman not resolved)
    p_trashold: peak finder hight trahold
    '''
    das = da.swap_dims({'field':'invB'})
    das = das.interp(invB=interp_arr)
    
    ax1,ax2 = two_axis()
    das.plot(marker='.',ax=ax1)


    # das.sel(invB=slice(None)).G.plot()
    das = (das-das.mean('invB'))/das.max()
    da_dft = xrft.fft(das)
    da_dft['ampl'] = abs(da_dft.sel(freq_invB=slice(0,None)).real)
    da_dft['dens'] = m * 2.415 * 1e10 * 1/da_dft.freq_invB
    da_dft.ampl.plot(x='dens', xlim=(0,2e10))

    idx,_ = find_peaks(da_dft.ampl, height=p_trash) 
    p_dens = da_dft.isel(freq_invB=idx).dens.values
    plt.scatter(da_dft.isel(freq_invB=idx).dens, da_dft.isel(freq_invB=idx).ampl, marker='x', c='r')
    for i in p_dens:
        print('density: {:.2e} cm^-2'.format(i))
    return da_dft

def calc_dens_mob_Hall_effect(ds):
    dsr = ds.drop_duplicates('field').dropna('field')
    coef = dsr.Rxy.polyfit(dim='field',deg=1).polyfit_coefficients

    dsr['dens'] = (coef[0]*ech*1e4)**-1
    dsr.dens.attrs['units'] = 'cm$^{-2}$'
    R_sq_zero_field = dsr.Rsq.sel(field=0, method='nearest').mean()
    dsr['mob'] = (dsr.dens*ech*R_sq_zero_field)**-1
    dsr.mob.attrs['units'] = 'cm$^2$/Vs'

    dsr = dsr.drop('degree')
    print('dens = {:.2e}, mob = {:.2e}'.format(dsr.dens.values, dsr.mob.values))
    return dsr.dens.values, dsr.mob.values


def add_calc_params(ds, aspect_ratio):
    ds['Rsq'] = ds.Vxx/ds.Iac/aspect_ratio
    ds['Rxy'] = ds.Vxy/ds.Iac

    ds['sigma_xx'] = ds.Rsq/(ds.Rsq**2+ds.Rxy**2)/(G0)
    ds.sigma_xx.attrs['units']='e$^2$/h'
    ds['sigma_xx_0'] = 1/ds.Rsq.sel(field=0, method='nearest')/(G0) # it's less noisy than the one calculated with equation above
    ds.sigma_xx_0.attrs['units'] = 'x $e^2/h$'
    ds['sigma_xy'] = ds.Rxy/(ds.Rsq**2+ds.Rxy**2)/(G0)

    ds.sigma_xy.attrs['units']='e$^2$/h'
    ds['invB'] = 1/ds.field
    return ds


def inv_field(ds):
    dss = ds.copy()
    dss = dss.swap_dims({'field':'invB'})
    dss = dss.sortby('invB').sel(invB=slice(0,100))
    return dss


### PERCOLATION DENSITY
def f_sigma(n,a,np):
    return a*(n-np)**(1.31) #return sigma


def fit_percolation_density(ds_res, dens_cutoff=5.5e10, dens_min=0):

    dss = ds_res.where((ds_res.dens<dens_cutoff) & (ds_res.dens>dens_min)).dropna('Vg')
    dens = dss.dens.values
    sigma = dss.sigma_xx_0.values

    pop, pcov = curve_fit(f_sigma, dens, sigma, p0=[1,1e10])
    
    percolation = pop[1]
    print('percolation dens = {:.2e}'.format(percolation))

    ax1, ax2 = two_axis()

    ax1.scatter(dens,sigma)
    ax1.set_xlabel('$\sigma_{xx,0}\ (\mathrm{e^2/h})$')
    ax1.set_ylabel('$p\ \mathrm{(cm^{-2})}$')
    ax1.set_yscale('log')

    dens_arr = np.linspace(dens.min(), dens.max(),100)
    ax1.plot(dens_arr,f_sigma(dens_arr, *pop), c='r')


    ax2.scatter(ds_res.dens,ds_res.sigma_xx_0)
    ax2.plot(dens_arr,f_sigma(dens_arr, *pop), c='r')
    ax2.plot(ds_res.dens,f_sigma(ds_res.dens, *pop), c='r', ls='--', alpha=0.8)
    ax2.set_xlabel('$\sigma_{xx,0}\ (\mathrm{e^2/h})$')
    ax2.set_ylabel('$p\ \mathrm{(cm^{-2})}$')
    ax2.set_yscale('log')
    ds_res['percolation_dens'] = percolation
    ds_res['perc_fit'] = f_sigma(dens_arr, *pop)
    ds_res['perc_fit_full'] = f_sigma(ds_res.dens, *pop)

    print('pop', pop)
    print('pcov', pcov)
    print('percolation dens = {:.2e}'.format(percolation))



    return percolation