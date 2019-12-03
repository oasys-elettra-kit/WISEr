# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 13:59:42 2019

@author: Mike
"""

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
