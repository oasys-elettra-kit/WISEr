# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:05:38 2017

@author: Mic

Remember:
Waist0E = Waist0I/sqrt(2) = Sigma0I/2
"""


#%%
import numpy as np
from numpy import pi, sqrt
import LibWiser.Foundation
import LibWiser.Optics

class Info:
	FermiFactor = {'fel1' : 1.25, 'fel2':1.5}
#	FermiWaist = FermiSigma * np.sqrt(2)
#	FermiDivergence = Lambda / np.pi/FermiWaist


#===========================================================================
# 	FUN: GetFermiFactorAuto
#===========================================================================
def GetFermiFactorAuto(Lambda = None, Source = ''):
	if Source == '1':
		return Info.FermiFactor['fel1']
	elif Source =='2':
		return Info.FermiFactor['fel2']
	else:
		if Lambda >= 20e-9:
			return Info.FermiFactor['fel1']
		elif Lambda < 20e-9:
			return Info.FermiFactor['fel2']

def ThetaI(Lambda, Source = ''): # rad
	FermiFactor = GetFermiFactorAuto(Lambda, Source)
	return FermiFactor * Lambda * 1e9	* 1e-6

def Sigma0I(Lambda, Source =''):
	return Lambda/2/np.pi/ThetaI(Lambda, Source)

def Waist0E(Lambda,Source =''):
#	return Waist0I(Lambda, Source)*sqrt(2)
	return 2 * Sigma0I(Lambda, Source ='')
def Waist0I(Lambda,Source =''):
#	return Lambda/np.pi/ThetaI(Lambda, Source)
	return Waist0E(Lambda,Source ='')/sqrt(2)

# Returns the Sigma of the Intensity distributon of the fermi source


def SigmaI(Lambda,z , Source =''):
	DivI = ThetaI(Lambda, Source)
	return DivI * z

def WaistI(Lambda,z, Source =''):
	return SigmaI(Lambda,z,Source) * np.sqrt(2)


class DistancesF2:
	PM2a =41.4427
	Presto = 49.8466
	DpiKbh = 98.55
	DpiKbhF2 = 1.2

#
#def Waist0I(Lambda,Source =''):
#	return Lambda/np.pi/ThetaI(Lambda, Source)
#
#def Waist0E(Lambda,Source =''):
#	return Waist0I(Lambda, Source)/sqrt(2)
#
## Returns the Sigma of the Intensity distributon of the fermi source
#def SigmaI(Lambda,z , Source =''):
#	DivI = ThetaI(Lambda, Source)
#	return DivI * z
#
#def WaistI(Lambda,z, Source =''):
#	return SigmaI(Lambda,z,Source) * np.sqrt(2)


#================================================
## CLASS: Dpi
##================================================
#class Dpi:
#	Beamline = 'dpi'
#	f1h = 98.5 # orizzontale
#	f2h = 1.180 # orizzontale
#	Mh = f1h/f2h
#	f1v = 98.5 # orizzontale
#	f2v = 1.180 # orizzontale
#	Mv = f1v/f2v

#================================================
# CLASS: Dpi
#================================================
class Dpi:
	Beamline = 'dpi'
	class Kbh:
		f1 = 98.55 #
		f2 = 1.200 # orizzontale
		M = f1/f2
		GrazingAngle = np.deg2rad(2)
		Letter ='h'

	class Kbv:
		f1 = 98.0 # orizzontale
		f2 = 1.750 # orizzontale
		M = f1/f2
		GrazingAngle = np.deg2rad(2)
		Letter = 'v'
#===========================================================================
# 	Definition of Fermi Fel1 and Fel2 as optical elements
#===========================================================================
def Fel(object):
	def __init__(Lambda):

		theta_I = TehtaI(Lambda)
		Waist0 = Waist0E(Lambda)

		source_k = Optics.SourceGaussian(Lambda, Waist0)
		source_pd = Fundation.PositioningDirectives(
						ReferTo = 'absolute',
						XYCentre = [0,0],
						Angle = 0)

		source = Fundation.OpticalElement(source_k,
									Name = 'Fel1 source',
									IsSource = True,
									PositioningDirectives = source_pd)


