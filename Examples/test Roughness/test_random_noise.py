# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 11:55:48 2016

@author: Mic
"""


import numpy as np
from must import *
rand = np.random.rand
fft = np.fft.fft
fftshift = np.fft.fftshift

N = 1000 ;
sigma_N = 30
x = np.linspace(-N/2, N/2,N) ;
y = np.exp(-0.5 * x**2/sigma_N**2) ;

r = np.exp(1j*2*pi * rand(N)) ;

f = fft((fftshift(y)*r)) ;
rf = real(f) ;
af = abs(f) ;


#%%
plot(rf,'r') ;
plot(af,'b');


plt.figure(2)
ac_rf = np.correlate(rf,rf,'same') ;
plot(ac_rf) ;