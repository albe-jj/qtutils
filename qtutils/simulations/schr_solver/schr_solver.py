import numpy as np
import scipy
from scipy import linalg
from functools import partial
from scipy import constants
import matplotlib.pyplot as plt
from plot_utils import * 
import xarray as xr
from collections import deque
from scipy import signal
from qtutils.analysis.plot_utils import two_axis

# hbar = constants.hbar
# m0 = constants.m_e
# mstar = 1 * m0

ech = scipy.constants.e
h = scipy.constants.h

length = scipy.constants.physical_constants['atomic unit of length'][0] *1e9 # nm 
energy = scipy.constants.physical_constants['Hartree energy in eV'][0] *1e3 # meV


def calc_eps_r_SiGe(x):
    '''
    x: Ge fraction'
    permittivity of SiGe (F/m) (Schaffler F. et al. (2001) @ 300 K)
    '''
    return (11.7+4.5*x)



def make_potential_function(x, heterostructure):
    '''
    get the heterostructure parameters as a function of spatial coordinate
    input:
    x: array of spatial points to simulate heterostructure
    heterostructure: tuple of lists ([length_1, height_1, eps_1], [length_2, height_2, eps_2] ) 

    !! note: all units are in Hartree units
        '''
    z_points = np.array(heterostructure).T[0].cumsum()
    z_points = np.insert(z_points,0,0)
    h_points = np.array(heterostructure).T[1]
    eps_points = np.array(heterostructure).T[2]
    condlist = []
    funclist_V = []
    funclist_eps = []
    
    for idx,z in enumerate(z_points[:-1]):
        condlist += [(x>=z) & (x<z_points[idx+1])]  # the last point is not included [z, z+1)
        funclist_V += [h_points[idx]]
        funclist_eps += [ eps_points[idx]]
    Vz = np.piecewise(x, condlist=condlist, funclist=funclist_V)
    eps_z = np.piecewise(x, condlist=condlist, funclist=funclist_eps)
    return Vz, eps_z



#Poisson part
def calc_Efield(heterostructure, Vg, sigma_hetero_arr, steps):
    '''
    Solves Poisson equation for the given heterostructure at given gate voltage.

    Parameters:
    heterostructure: tuple of lists (see above)
    Vg: gate voltage
    sigma_arr: array of charge in heterostructure
    sigma_arr: charge in the system len: steps-1
    '''

    ech = 1
    q = -1
    
    z_points = np.array(heterostructure).T[0].cumsum()
    l = z_points[-1]
    dz = l/steps
    Z = np.linspace(0, l ,steps+1)[:-1]
    Vz,eps_z = make_potential_function(Z, heterostructure)
    n = steps
    
    # build matrix A of linear eq from Gauss law
    eps_arr = np.array(heterostructure).T[2]
    a11 = np.diag(eps_z,0) + np.diag(-eps_z[:-1],-1)

    a12 = np.eye(n+1)
    a12 = a12[:-1,:]

    a21 = np.zeros([n,n])
    a21 = np.append(a21, np.ones([1,n])*dz, axis=0)

    a22 = np.diag(np.ones(n), k=1)
    a22[-2,:] = 1
    
    A  = np.block([[a11, a12],
          [a21, a22]
         ])
    b = np.concatenate([np.zeros(n), sigma_hetero_arr, [0,-Vg]])
    
    # calcualte solutions
    sol = np.linalg.solve(A,b)
    E_field = sol[:n]
#     sigma_arr = sol[n:]
    sigma_gate = sol[n]
    sigma_bottom = sol[-1]
    V_field = q * E_field.cumsum() * dz
    
    U_band = Vz + V_field - Vg
#     print('sigma gate: \t{:.3}'.format(sigma_gate))
#     print('sigma bottom: \t{:.3}'.format(sigma_bottom))
    
    return Z, E_field, U_band, sigma_gate, sigma_bottom



# Shcrodinger part
def calculate_psi_from_potential(Z, Vz, mstar, steps):
    '''
    Matrix solutions of the discretised Schrodinger equation (Paul Harrison pag. 94)
    parameters:
        Z: array of spatial points points
        Vz: Electrical potential (band of the heterostructure) 
        mstar: effective mass in z-direction
        steps: no of z points #TODO it's redundant
    '''

    hbar=1
    
    
    assert all(np.isclose(np.diff(Z), np.diff(Z).mean())) #check that Z are equally spaced
    dz = np.diff(Z).mean() 

    a = c = -hbar**2 / (2 * mstar * dz**2)
    b = hbar**2 / (mstar * dz**2) 

    H = np.diag(b * np.ones(steps), 0) + np.diag(Vz, 0) +\
        np.diag(c * np.ones(steps-1), 1) + \
        np.diag(a * np.ones(steps-1), -1) 

    E_self, psi_matr = linalg.eigh(H)
    psi = psi_matr.T
    psi_sq = psi**2
    return E_self, psi, psi_sq



# Solver
def solve_sys(Vg_arr, heterostructure, mstar=1, steps=300):
    '''
    Given ann array of gate voltages and the specs of the heterostructure,
    solves the Schrodinger equation for each gate voltage using following method: 
    Matrix solutions of the discretised Schrodinger equation (Paul harrison chapter 3.9 pag. 94)
    to implement effective mass dependence on z m*(z) check pag 104
    
    
    '''
    if np.size(Vg_arr)==1:
        Vg_arr = [Vg_arr]

    Z_ls = []
    psi_ls = []
    psi_sq_ls = []
    E_self_ls = []
    U_band_ls = []
    sigma_gate_ls = []
    E_field_ls = []
    E_level_ls = []

    for Vg in Vg_arr:
        # Solve poisson for heterostructure with charge sigma_hetero_arr=0
        sigma_hetero_arr = np.zeros(steps-1)
        Z, E_field, U_band, sigma_gate, sigma_bottom = calc_Efield(heterostructure, Vg, sigma_hetero_arr, steps)

        # solve Schrodinger 
        E_self, psi, psi_sq = calculate_psi_from_potential(Z, U_band, mstar=mstar, steps=steps )

        E_level = range(len(E_self))

        Z_ls.append(Z)
        psi_ls.append(psi)
        psi_sq_ls.append(psi_sq)
        E_self_ls.append(E_self)
        U_band_ls.append(U_band)
        sigma_gate_ls.append(sigma_gate)
        E_field_ls.append(E_field)
        E_level_ls.append(E_level)



    ds = xr.Dataset(
        data_vars = dict(
            psi = (['Vg', 'E_level', 'Z'], psi_ls),
            psi_sq = (['Vg', 'E_level', 'Z'], psi_sq_ls),
            E_self = (['Vg','E_level'], E_self_ls),
            U_band = (['Vg','Z'], U_band_ls),
#             sigma_z = (['Vg','Z'], [sigma_z]),
            # sigma_hetero = (['Vg','Z'], [sigma_hetero_arr]),
            sigma_gate = (['Vg'], sigma_gate_ls),
            # sigma_bottom = (['Vg'], [sigma_bottom]),
#             occupation_per_state = (['Vg','E_level', 'Z'], [occupation_per_state]),
            E_field = (['Vg','Z'], E_field_ls)
        ),

        coords = dict(
            Z=Z,
            E_level = E_level,
            Vg = Vg_arr
        )
    )


    return ds


def get_coupling(Vg_bounds, heterostructure, mstar, steps):
    '''
    Finds the minimum delta_E of the first two energy states (assumed to be in the DQW system)
    then zoom into the gate voltage aroound the enrgy miniumum (~delta_sas) until the
    delta_sas converges to a actual number 

    Vg_bounds: gate bounds in mV to begin with
    '''
    Vg_bounds = np.array(Vg_bounds)/energy
    Vg_steps=20
    Vg_arr_i = np.linspace(Vg_bounds[0], Vg_bounds[1], Vg_steps)
    dq = deque(maxlen=2)
    dq.append(0)
    precision = 0
    
    i=0

    while precision<0.99:

        ds = solve_sys(Vg_arr_i, heterostructure, mstar, steps)

        delta_e1_e2 = ds.sel(E_level=1).E_self - ds.sel(E_level=0).E_self # meV
        

        # select the first local minima, 
        # the second minima should be the due to states at the oxide interface at high bias
        idx_mins = signal.argrelextrema(delta_e1_e2.values, np.less)
        idx_min = idx_mins[0][0]
        Vg_min = delta_e1_e2.Vg[idx_min].values
        delta_sas = delta_e1_e2[idx_min].values
        dq.append(delta_sas)
        precision = 1 - abs(np.diff(dq)/delta_sas)[0]
        # print(delta_sas)
        # print(precision)
        # print()


        shift = abs(Vg_bounds[1] - Vg_bounds[0]) / 10
        Vg_bounds = [Vg_min-shift, Vg_min+shift]
        Vg_arr_i = np.linspace(Vg_bounds[0], Vg_bounds[1], Vg_steps)
        # break

        i+=1
        if i>15:
            break
            print('max iterations reached')

    print('converged in {:0.0f} iterations with precision {:0.2f}'.format(i,precision))

    # transform in normal units
    ds['Z'] = ds.Z*length
    ds['Vg'] = ds.Vg*energy
    ds['E_self'] = ds.E_self * energy
    ds['U_band'] = ds.U_band * energy
    ds['psi'] = ds.psi*100

    delta_e1_e2 = ds.sel(E_level=1).E_self - ds.sel(E_level=0).E_self # meV
    delta_sas = delta_e1_e2.min().values
    tc = delta_sas/2 # meV
    f = (tc * ech/1000)/ h # Hz

    ax1, ax2 = two_axis()
    delta_e1_e2.plot(ax=ax1)
    ax1.set_ylabel('$E_1-E_0$ (meV)')

    dss = ds.sel(Vg=115, method='nearest').sel(E_level=slice(0,4))

    dss.U_band.plot(ax=ax2)
    (dss.psi+dss.E_self).plot(hue='E_level', add_legend=0)
    plt.title('with Vg at resonance')
    plt.tight_layout()

    print('Vg min = {:0.2e} mV'.format(delta_e1_e2.idxmin().values))
    print('delta_sas = {:.2e} meV'.format(delta_sas))
    print('tc = {:.2e} meV'.format(tc))
    print('f = {:.2e} Hz'.format(f))
    to_clipboard()

    return ds