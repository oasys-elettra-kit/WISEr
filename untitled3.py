# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 15:40:44 2020

@author: Mike - Manfredda
"""
import numpy as np
from numpy import pi

pi/1.50e3/2


#%% Calcolo formula "1.25 lambda" alla dimensione della sorgente
#
# Noi usiamo
# Theta_nm = 1.25 * Lambda_nm
#o equivalentemente, con tutte le unità in S.I.
# Theta = 1.25e3 * Lambda
#
#Poiché Theta = Lambda/pi/w0
#si ha che 1.25e3 = 1/pi/w0
print('Quantità calolate a partire dalla "formula della divergenza"')
print('Theta[urad] = 1.25 * Lambda [nm]')

w0 = 1/pi/1.25e3
w0_um = w0*1e6
print('w0=%0.1f um' % w0_um)

SigmaI_um = w0_um / 2
print('SigmaI=%0.1f um' % SigmaI_um)

# Fisso una lambda e calcolo la divergenza
Lambda = 40e-9
Theta = 1.25e3 * Lambda
Theta_um = Theta*1e6
print('Theta=%0.1f um  @ Lambda = %0.0f nm' % (Theta_um, Lambda * 1e9))

#%% Dato il waist, calcolo gli altri parametri
Waist0 = 124e-6

Lambda = 40e-9
ThetaI = Lambda / np.pi / Waist0 # divergenza


ThetaI_urad = ThetaI * 1e6
Waist0_mm = Waist0*1e3
