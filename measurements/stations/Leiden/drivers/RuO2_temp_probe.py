# -*- coding: utf-8 -*-
# @Author: Alberto Tosato
# @Date:   2021-05-25 14:58:12
# @Last Modified by:   TUD278249
# @Last Modified time: 2021-05-25 18:36:15
import numpy as np

def get_temp_RuO2(V_bias, I, I_gain):
    Rx = calc_R_RuO2(V_bias, I, I_gain)
    temp = RuO2_2k_R2Temp(Rx)
    return temp

def calc_Rx(V_bias, I, I_gain):
    R_Imeas = 100 + 1e-4 * I_gain # M1h for low noise setting
    Rx = V_bias / I - R_Imeas
    return Rx

def RuO2_2k_R2Temp(R):
    '''
    R: resistance in Ohms
    return: T in mK
    
    source: D:\LeidenMCK50_fridge\Scripts\Leiden Cryogenics\TC\Calibrations
    '''
    G = np.log10(R)
    I = 2740.031575332
    J = -3275.35286892
    K = 1570.730621168
    L = -376.991970858
    M = 45.248517104
    N = -2.172180622
    O=P=Q=R = 0
    
    temp = 10**(I + G*J + G**2*K + G**3*L + G**4*M + G**5*N + G**6*O + G**7*P + G**8*Q + G**9*R)
    return temp