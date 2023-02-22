# -*- coding: utf-8 -*-
"""
Created on Sat May  7 02:18:23 2022

@author: Mike
"""
#%%
import numpy as np
import matplotlib.pyplot as plt

L = 1
N = int(1e3)

period = 15
hi_size= 10


y = np.zeros((N))
hi_y = np.zeros(high_size)+1
N_i = int(np.floor(N/period))

for i in range(0,N_i):
	y[i*period:(i+1) * hi_size] = hi_y[:]	
plt.plot(y)
