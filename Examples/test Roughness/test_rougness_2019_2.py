# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:07:13 2019

@author: Mike
"""
#%%
import LibWISEr.WiserImport as wr
import LibWISEr.Noise as Noise
import numpy as np
from LibWISEr.must import*
import LibWISEr.ToolLib as tl
from LibWISEr.must import *

#%% power law
a = 11.2
b = -1.482

if 1==1:
	N = 1000
	L = 1

	PsdArgs = [a,b]
	PsdFun = wr.Noise.PsdFuns.PowerLaw

	s, PS = wr.Noise.PsdAnalytic2Noise(L , N = N,
								PsdFun = wr.Noise.PsdFuns.PowerLaw,
								   PsdArgs = PsdArgs)

	PSOut = tl.PowerSpectrum(s)
	PSOutHB = abs(PSOut[0:N//2])
	#----
	plt.figure(2)
	#---- PLOT Numeric PS
	plot(PSOutHB) # positive bandwidth
	#---- PLOT Analytic PS
	plot(PS)
	plt.legend(['Numeric PS', 'Analytic PS'])
	plt.loglog()

#%% TEST HEW SCATTERING

def HewScatteringContribution (Lambda, GrazingAngle, Kn,n):
	return (Kn/(n-1)) **(1/(n-1)) * (np.sin(GrazingAngle)/Lambda) **(3-n)/(n-1)

Kn = 0.233 # m^3
n = 2.122 #
Lambda_nm = np.linspace(0.5,20,1000)
Lambda = Lambda_nm * 1e-9

GrazingAngle = np.deg2rad(2.5)
Hew = HewScatteringContribution(Lambda, GrazingAngle, Kn,n)
Hew_um = Hew * 1e6
plt.plot(Lambda_nm, Hew_um)
plt.xlabel('lambda nm')
plt.ylabel('um')


