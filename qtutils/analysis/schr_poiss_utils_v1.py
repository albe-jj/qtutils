import numpy as np
import scipy
from scipy import linalg
from functools import partial
from scipy import constants
import matplotlib.pyplot as plt
from plot_utils import * 

# hbar = constants.hbar
# m0 = constants.m_e
# mstar = 1 * m0

def calc_eps_r_SiGe(x):
    '''
    x: Ge fraction'
    permittivity of SiGe (F/m) (Schaffler F. et al. (2001) @ 300 K)
    '''
    return (11.7+4.5*x)



def get_fz(x, heterostructure):
    '''get the heterostructure parameters as a function of spatial coordinate'''
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

# Shcrodinger part

def calculate_psi_from_potential(Z, Vz, mstar, steps):
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
 

def plot_psi(Z, Vz, E, psi, psi_sq, no_states=5, psi_ampl=2):
    psi = psi * Vz.max() * psi_ampl
    psi_sq = psi_sq * Vz.max() * psi_ampl**2 
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=[13,4])
    
    for i in range(no_states):
        ax1.plot(Z,psi[i]+E[i])
        ax2.plot(Z,psi_sq[i] +E[i])
        


    ax1.plot(Z, Vz, c='k', linewidth=1)
    ax2.plot(Z, Vz, c='k', linewidth=1)
    ax1.set_ylabel('$\Psi$')
    ax2.set_ylabel('$|\Psi|^2$')
    plt.tight_layout()
    

def calc_occupied_states(E_self, psi, psi_sq, Ef, mstar):
    hbar = 1
    ech = 1
    q = -1
    Ef_E_self_diff = np.max(
        [np.zeros(len(E_self)), -q * (Ef-E_self)],
        axis=0
        ) # is zero for states below fermi energy
    occupation_per_state = np.reshape((Ef_E_self_diff),[-1,1]) * mstar / (np.pi * hbar**2) * psi_sq  # spin degeneracy is accounted in this formula
    if len(occupation_per_state)>0:
        sigma_z = sum(occupation_per_state) * ech * q
    else: sigma_z = np.zeros(np.shape(psi)[0])
    tot_charge = sum(sigma_z)
        
#     print('total charge = \t{:.3}'.format(tot_charge))
    return occupation_per_state, sigma_z


def plot_states_occ(Z, occupation_per_state, sigma_z, fig=None):
    
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=[13,4])
    
    for i in occupation_per_state:
        ax1.plot(Z,i)
    ax2.plot(Z, sigma_z)
    ax1.set_ylabel('$\sigma_z$ per state')
    ax2.set_ylabel('$\sigma_z$ tot')
    plt.tight_layout()



#Poisson part

def calc_Efield(heterostructure, Vg, sigma_hetero_arr, steps):
    '''
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
    Vz,eps_z = get_fz(Z, heterostructure)
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

def plot_field(Z, E_field, Vz_field):
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=[13,4])
    ax1.plot(Z, E_field)
    ax1.set_ylabel('E_field')

    ax2.plot(Z, Vz_field)
    plt.ylabel('V')
    plt.tight_layout()
    