from schr_poiss_utils_v1 import * 
from functools import partial
from multiprocessing import Pool
import multiprocessing
import pandas as pd
import xarray as xr


#initialize array for mixing
def calculate_Schr_poiss_single_Vg(Vg, heterostructure, Ef, mstar=1, steps = 300, add_charge_iter = 30, self_iter = 100):
    sigma_hetero_arr = np.zeros(steps-1)


    I = np.linspace(0,1,add_charge_iter)
    I = np.insert(I,-1,np.ones(self_iter))

    sigma_hetero_arr_ls = [sigma_hetero_arr]
    sigma_gate_ls = []
    sigma_bottom_ls = []
    tot_ch_ls = []
    E0_ls = []
    sigma_z_ls = []

    for idx, k in enumerate(I):

        if idx>add_charge_iter:
            lbda = .999
        else:
            lbda = 0.995

        # Solve poisson for heterostructure with charge sigma_hetero_arr
        Z, E_field, U_band, sigma_gate, sigma_bottom = calc_Efield(heterostructure, Vg, sigma_hetero_arr, steps)

        # solve Schrodinger 
        E_self, psi, psi_sq = calculate_psi_from_potential(Z, U_band, mstar=mstar, steps=steps )

        # Calculate occupaied states -> charge
        occupation_per_state, sigma_z = calc_occupied_states(E_self, psi, psi_sq, Ef, mstar)
        sigma_hetero_arr = ((1-lbda) * sigma_z[1:] + lbda * sigma_hetero_arr_ls[idx]) * k # ?is it correct to exclude last one?
        sigma_gate_ls.append(sigma_gate)
        sigma_bottom_ls.append(sigma_bottom)
    #     tot_ch = sum(sigma_z[:-1])
        tot_ch = sum(sigma_hetero_arr)

        tot_ch_ls.append(tot_ch)
        sigma_hetero_arr_ls.append(sigma_hetero_arr)
        sigma_z_ls.append(sigma_z)
        E0_ls.append(E_self[0])
    #     print(E_self[0])

    convergence_df = pd.DataFrame(dict(
        sigma_gate_ls=sigma_gate_ls,
        sigma_bottom_ls=sigma_bottom_ls,
        tot_ch=tot_ch,
        # sigma_hetero_arr=sigma_hetero_arr,
        sigma_z_ls=sigma_z_ls,
        ))

    E_levels = range(len(E_self))

    ds = xr.Dataset(
        data_vars = dict(
            psi = (['Vg', 'E_level', 'Z'], [psi]),
            psi_sq = (['Vg', 'E_level', 'Z'], [psi_sq]),
            E_self = (['Vg','E_level'], [E_self]),
            U_band = (['Vg','Z'], [U_band]),
            sigma_z = (['Vg','Z'], [sigma_z]),
            # sigma_hetero = (['Vg','Z'], [sigma_hetero_arr]),
            sigma_gate = (['Vg'], [sigma_gate]),
            sigma_bottom = (['Vg'], [sigma_bottom]),
            occupation_per_state = (['Vg','E_level', 'Z'], [occupation_per_state]),
            E_field = (['Vg','Z'], [sigma_z])
        ),

        coords = dict(
            Z=Z,
            E_level = E_levels,
            Vg = [Vg]
        )
    )
    return ds


def calculate_Schr_poiss(Vg_arr, heterostructure, Ef, steps = 300, add_charge_iter = 30, self_iter = 100, mstar=1):
    f = partial(calculate_Schr_poiss_single_Vg, heterostructure=heterostructure, Ef=Ef, mstar=mstar,
        steps = steps, add_charge_iter = add_charge_iter, self_iter = self_iter)
    ds_ls = run_with_multiprocessing(Vg_arr, f)
    # ds_ls = f(Vg_arr[0])
    ds = xr.concat(ds_ls,dim='Vg')
    return ds



def run_with_multiprocessing(array, f):
    with Pool(multiprocessing.cpu_count()) as p:
        out = p.map(f, array)
    return out