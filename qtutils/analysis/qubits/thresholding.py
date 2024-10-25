#%% thresholding data
#from projects.notebook_tools.notebook_tools import fit_data, ExpDec
import numpy as np
from matplotlib import pyplot as plt
# import qtt
from scipy.optimize import curve_fit
import logging
import sys
#%%
def dGauss(x, A, FWHM, x0, y0):
    w = FWHM / (2 * np.sqrt(2 * np.log(2)))
    return (x0 - x) / w**2 * A * np.exp(-(x - x0)**2 / (2 * w**2)) + y0

def fit_data(xdata, ydata, p0=None, func=dGauss,
             plot=True, return_cov=False, verbose=0,fix_params = {}, **kwargs):
    
    x_range = np.linspace(np.min(xdata), np.max(xdata), num=500)
    p0dict = {}
    if p0 is None:
        if func in [Gauss, dGauss, Lorentz]:
            
            p0dict = {
                    'A':np.max(ydata) - np.mean(ydata), 
                    'FWHM': (x_range[-1] - x_range[0]) * 0.2,
                    'x0': xdata[np.argmax(ydata)], 
                    'y0': np.mean(ydata)
                    }
            if verbose:
                logging.info('p0: ' + str(p0))
        elif func is Rabi:
            p0dict = {
                    'A':np.max(ydata) - np.mean(ydata), 
                    'f' :1/(x_range[-1] - x_range[0])*2,
                    'alpha': 0.1,
                    'y0': np.mean(ydata),
                    'phi': np.pi
                    }
            
            if verbose:
                logging.info('p0: ' + str(p0))
                
        elif func is ExpDec:
            start = np.mean(ydata[:5])
            baseline = np.mean(ydata[int(3 * len(ydata) / 4):])
            p0dict = {'A': start - baseline,
                  'm': (xdata[1] - xdata[-1]) / 2, 
                  'y0': baseline}
        elif func is DoubExpDec:
            start = np.mean(ydata[:5])
            baseline = np.mean(ydata[int(3 * len(ydata) / 4):])
            p0dict = {'A1': start - baseline,
                  'm1': (xdata[1] - xdata[0]) / 2,
                  'A2': start - baseline,
                  'm2': (xdata[1] - xdata[0]) / 4,
                  'y0': baseline}
    
    if fix_params:
        func = partial(func, **fix_params)
        
    try:
        if p0dict:
            p0 = [p0dict[arg] for arg in inspect.getfullargspec(func).args[1:]]
        
        # check p0 feasability
        if 'bounds' in kwargs.keys() and p0 is not None:
            for i,p in enumerate(p0):
                lower, upper = (kwargs['bounds'][0][i], kwargs['bounds'][1][i])
                if not lower <=p <= upper:
                    p=min([max([lower, p]),upper])
        p1, covar = curve_fit(func, xdata, ydata, p0=p0, **kwargs)
        if plot:
            plt.scatter(xdata,ydata,marker='.')
            plt.plot(x_range, func(x_range, *p1))

        if return_cov:
            return np.sqrt(np.diag(covar)), p1		
        else:
            return p1
    except RuntimeError as Err:
        logging.warning(Err)


#%%
def Gauss2(x, A, A2, FWHM, FWHM2, x0, x0_2):
    w = FWHM / (2 * np.sqrt(2 * np.log(2)))
    w2 = FWHM2 / (2 * np.sqrt(2 * np.log(2)))
    return A * np.exp(-(x - x0)**2 / (2 * w**2)) + A2 * np.exp(-(x - x0_2)**2 / (2 * w2**2)) 
def Hahn_decay(x, A, m, b, y0):
    return A * np.exp(-(x / m)**b) + y0

def _estimate_double_gaussian_parameters(x_data, y_data, split = 0.5):
    """ Estimate of double gaussian model parameters."""
    maxsignal = np.percentile(x_data, 98)
    minsignal = np.percentile(x_data, 2)

    data_left = y_data[:int((len(y_data) * split))]
    data_right = y_data[int((len(y_data) * split)):]

    amplitude_left = np.max(data_left)
    amplitude_right = np.max(data_right)
    sigma_left = (maxsignal - minsignal) * 1 / 20
    sigma_right = (maxsignal - minsignal) * 1 / 20


    x_data_left = x_data[:int((len(y_data) * split))]
    x_data_right = x_data[int((len(y_data) * split)):]
    mean_left = np.sum(x_data_left * data_left) / np.sum(data_left)
    mean_right = np.sum(x_data_right * data_right) / np.sum(data_right)
    initial_params = np.array([amplitude_left, amplitude_right, sigma_left, sigma_right, mean_left, mean_right])
    return initial_params

#%%
def thresholded_data(im, xaxis, split = 0.5, max_diff = 5, plot = True, sensor = None):
        
    if sensor == None:
        sensor = 'sensor1'
    t_wait = xaxis

    xdata = np.arange(0,len(im[0]))
    
    try:
        threshold_prev = threshold
    except:
        threshold_prev = split
    
    thrs = []
    for i in np.arange(0,len(t_wait)):
        i_min = i - 2
        if i_min < 0:
            i_min = 0
            
        i_max = i + 2
        if i_max > max(np.arange(0,len(t_wait))):
            i_max = max(np.arange(0,len(t_wait)))
        
        ydata_guess = np.mean(im[i_min:i_max], axis = 0)
        ydata = im[i]
    
        
        guess = _estimate_double_gaussian_parameters(xdata,ydata_guess, split = split)
        p1_guess = fit_data(xdata, ydata_guess, func = Gauss2, p0=guess, plot=False)

        try:
            p1 = fit_data(xdata, ydata, func = Gauss2, p0=p1_guess, plot=False)
            threshold = (p1[4]+p1[5])/2
            threshold_guess = (p1_guess[4]+p1_guess[5])/2
            if abs(threshold - threshold_guess)<max_diff:
                thrs.append(threshold)
                threshold_prev = threshold
            else:
                thrs.append(threshold_guess)
                threshold_prev = threshold_guess
        
        except:
            threshold = threshold_prev
            thrs.append(threshold)
            print("thresholding failed")

    z = im
        
    if plot: 
        #plotting the threshold
        plt.figure()
        plt.pcolor(z)
        plt.plot(thrs, np.array(range(len(thrs)))+0.5,'r')
    
    
    #calculation fraction blocked
    sup = []
    for i in np.arange(0,len(thrs)):
        thrs_i = thrs[i]
        try:
            thrs_i = int(thrs_i)
        except:
            thrs_i = split
        j = sum(z[i][:thrs_i])
        sup.append(j)
    
    nsub = np.array(sup)
    # if sensor == 'sensor1':
    #         nsub = 1-nsub
            
    return nsub, thrs  
#%%

def thresholded_2d_data(im2d, xaxis, yaxis, split = 0.5, max_diff = 5, plot = True, sensor = None):
    
    """
    xaxis should be a 1d array, for example use data.xaxis[0]
    """
        
    # if sensor == None:
    #     sensor = 'sensor1'
    t_wait = xaxis
    
    array_2d = []

    xdata = np.arange(0,len(xaxis))
   
    
    for j in np.arange(0,len(yaxis)):
    
        thrs = []
        for i in np.arange(0,len(t_wait)):
            i_min = i - 2
            if i_min < 0:
                i_min = 0
                
            i_max = i + 2
            if i_max > max(np.arange(0,len(t_wait))):
                i_max = max(np.arange(0,len(t_wait)))
            
            
            ydata_guess = np.mean(im2d[j][i_min:i_max], axis = 0)
            ydata = im2d.ndarray[j][i]

            guess = _estimate_double_gaussian_parameters(xdata,ydata_guess, split = split)
            p1_guess = fit_data(xdata, ydata_guess, func = Gauss2, p0=guess, plot=False)
#            guess = [9.40000000e-02, 4.90000000e-02, 4.75200000e+00, 4.75200000e+00,48, 76]


            try:
                p1 = fit_data(xdata, ydata, func = Gauss2, p0=p1_guess, plot=False)
                threshold = (p1[4]+p1[5])/2
                threshold_guess = (p1_guess[4]+p1_guess[5])/2
                if abs(threshold - threshold_guess)<max_diff:
                    thrs.append(threshold)
                else:
                    thrs.append(threshold_guess)
            
            except:
                print("thresholding failed")
        

        z = im2d[j] 
        
        if plot: 
            #plotting the threshold
            plt.figure()
            plt.pcolor(z)
            plt.plot(thrs, np.array(range(len(thrs)))+0.5,'r')
        
        
        #calculation fraction blocked
        sup = []
        for i in np.arange(0,len(thrs)):
            thrs_i = thrs[i]
            thrs_i = int(thrs_i)
            j = sum(z[i][:thrs_i])
            sup.append(j)
        
        nsub = np.array(sup)
        # if sensor == 'sensor1':
        #         nsub = 1-nsub
                
        array_2d.append(nsub)
            
    return array_2d
            