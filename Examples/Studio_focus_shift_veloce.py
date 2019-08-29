# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:56:47 2017

@author: Mic

A fictiously large KB system is used in order to avoid large diffraction effects
and to allow for Gaussian fitting of the intensity, instead of HEW (half-energy
width).
+
"""
import importlib
import numpy as np

import matplotlib as mp
import matplotlib.pyplot as pp
import LibWISEr.Rayman as rm
import LibWISEr.Foundation as Fundation
import LibWISEr.Optics as Optics
import LibWISEr.ToolLib as tl
import csv
import LibWISEr.FermiSource as Fermi

import cProfile as profile

import time
from LibWISEr.must import *
from LibWISEr.Foundation import OpticalElement

###############################################################################
Lambda = 2e-9
Waist0 = 180e-6
KbToUse = Fermi.Dpi.Kbh
UseFigureError = True

f1 = KbToUse.f1
f2 = KbToUse.f2
M = f1/f2
L = 0.4

NPools = 1
DetectorSize = 150e-6
DetectorRestPosition = 0

DoCaustics = True
NDeltaFocus = 10
RangeOfDeltaFocus= 10e-3# estensione del delta focus
DeltaFocusOffset = 0e-3 # dove centro il delta focus (se cambio la sorgente, dovrebbe cambiare)

DeltaSourceList = np.zeros(1) # espressa in unità di ondulatori

single_time = []

###############################################################################
# PROFILING

pr = profile.Profile()
pr.disable()

###############################################################################

print(__name__)
if __name__ == '__main__':

	tl.Debug.On = True
	
	Hew__ = [] 
	Sigma__ = [] 
	HewMinPosition_ = []
	SpotSize1_ = []
	SpotPosition1_ = []
	SpotSize2_ = []
	SpotPosition2_ = []
	SpotSize3_ = []
	SpotPosition3_ = []
	SpotSize4_ = []
	SpotPosition4_ = []
	SourceResults = []

	tic1 = time.time()
	for iSource, DeltaSource in enumerate(DeltaSourceList):
		# SOURCE
		#------------------------------------------------------------

		#DeltaFocusOffset = DeltaSource/M**2  
		AngleGrazing = np.deg2rad(2) 
		s_k = Optics.SourceGaussian(Lambda, Waist0)
		s_pd = Fundation.PositioningDirectives(
							ReferTo = 'absolute', 
							XYCentre = [0,0],
							Angle = np.pi/4-AngleGrazing)
		s = OpticalElement(
							s_k, 
							PositioningDirectives = s_pd, 
							Name = 'source', IsSource = True)
		s_k.SmallDisplacements.Long = DeltaSource 
		s_k.SmallDisplacements.Rotation = 0
		s_k.ComputationSettings.UseSmallDisplacements = True
		
		
		# KB(h)
		#------------------------------------------------------------	
		kb_k = Optics.MirrorElliptic(f1=f1, f2=f2, L=L, Alpha=AngleGrazing)
		kb_pd = Fundation.PositioningDirectives(
							ReferTo = 'source',
							PlaceWhat = 'upstream focus',
							PlaceWhere = 'centre')
		kb = OpticalElement(
							kb_k, 
							PositioningDirectives = kb_pd, 
							Name = 'kb')
		kb_k.ComputationSettings.UseFigureError = UseFigureError

		# Figure ERROR
		
		# Carico da file
		kb.CoreOptics.FigureErrorLoad(
				File = "DATA/LTP/kb" + KbToUse.Letter  + ".txt",
					  Step = 2e-3, # passo del file
					  AmplitudeScaling = -1*1e-3 # fattore di scala 
					  )
		# Aggiungo a mano ()
	
		# detector (h)
		#------------------------------------------------------------
		d_k = Optics.Detector(
							L=DetectorSize, 
							AngleGrazing = np.deg2rad(90) )
		d_pd = Fundation.PositioningDirectives(
							ReferTo = 'upstream',
							PlaceWhat = 'centre',
							PlaceWhere = 'downstream focus',
							Distance = DetectorRestPosition)
		d = OpticalElement(
							d_k, 
							PositioningDirectives = d_pd, 
							Name = 'detector')
	
	
		# Assemblamento beamline
		#------------------------------------------------------------
		t = None
		t = Fundation.BeamlineElements()
		t.Append(s)
		t.Append(kb)
		t.Append(d)
		t.RefreshPositions()  

		# Calculation of the field on the detector
		# Impose N Pools
		# ---------------------------------
		
		d.ComputationSettings.NSamples = 3000     
		d.ComputationSettings.UseCustomSampling = True  # si può mettere anche su false.
		
		kb.ComputationSettings.NSamples = 3000
		kb.ComputationSettings.UseCustomSampling = True  # può essere true o false indipendentemente da quello prima
		#------------------------------------

		tic = time.time()
		t.ComputeFields() # propagazione dei campi
		toc = time.time()

		#----- Figura: compo su detector @ focus
		plt.figure(10)    
		#Fig10
		plt.gcf().clear()   
		x = d.Results.S * 1e6
		y = abs(d.Results.Field)/max(abs(d.Results.Field))
		plt.plot(x, y)
		plt.xlabel('um')
		plt.title('Campo su Detector (DeltaF = %0.3fmm)' % (DetectorRestPosition * 1e3))

		#----- Figura: gradiente della fase sul detector
		plt.figure(100)    
		plt.gcf().clear()   
		x = d.Results.S[0:-1] * 1e6
		y = np.diff(np.angle(d.Results.Field))
		plt.plot(x, y)
		plt.xlabel('um')
		plt.title('gradiente fase su Detector (DeltaF = %0.3fmm)' % (DetectorRestPosition * 1e3))


		(a,x0,sigma) = tl.FitGaussian1d(y,x)
		sigma_um = sigma 
		exp_sigma_um = s.CoreOptics.Waist0 / sqrt(2) / kb.CoreOptics.M *1e6
		print('simulated sigma = %0.3f um' % sigma_um)
		print('expected sigma = %0.3f um' % exp_sigma_um)
		print('simulated/expected = %0.3f' % (sigma_um/exp_sigma_um))
		print('MOLTO BENE')

#%% ----- Figura: campo sui kb
		#
		plt.figure(9)     
		plt.gcf().clear()      
		x = kb.Results.S * 1e3
		y = abs(kb.Results.Field)
		y = y/max(y)
		plt.plot(x, y)
		plt.xlabel('mm')
		plt.title('@ kb')

	#%% Caustica per ogni Sorgent
		if DoCaustics  :
			# La defocus list andrebbe ricalcolata in base al delta source
			if NDeltaFocus > 1:
				DefocusList = np.linspace(DeltaFocusOffset - RangeOfDeltaFocus/2, DeltaFocusOffset+RangeOfDeltaFocus/2, NDeltaFocus )
			else:
				DefocusList = np.array([0])
				
			DefocusList_mm = DefocusList * 1e3
			tic1 = time.time()
			# pr.enable()
			ResultList, Hew_,Sigma_, More = Fundation.FocusSweep(kb, DefocusList, DetectorSize = DetectorSize, NPools = NPools)
			# pr.disable()
			toc1 = time.time()
			SourceResults.append(ResultList)
			N = len(ResultList)
			Hew__.append(Hew_)
			
			Sigma__.append(Sigma_)
			
			NumericWaist, FittedWaist = tl.FindWaist(Hew_, DefocusList_mm, Threshold = 1e-15)
			SpotPosition1_.append(NumericWaist[0])
			SpotSize1_.append(NumericWaist[1])			
			SpotPosition2_.append(FittedWaist[0]) # miglior candidato
			SpotSize2_.append(FittedWaist[1])
			
			NumericWaist, FittedWaist = tl.FindWaist(Sigma_, DefocusList_mm, Threshold = 1e-15)
			SpotPosition3_.append(NumericWaist[0])
			SpotSize3_.append(NumericWaist[1])		
			SpotPosition4_.append(FittedWaist[0])
			SpotSize4_.append(FittedWaist[1])
			
			#----- figura campo caustica
			#Plotta il campo sui detector a varie distanze durante il calcolo
			if 1==1:
				#Fig23
				plt.figure(23)
				plt.gcf().clear()
				for Res in ResultList:
					x = Res.S *1e6
					y = abs(Res.Field)
					
					plot(x,y )
					plt.title('Intensità su detector (per caustica) - DeltaSource %0.2fm' % DeltaSource)
					plt.xlabel('um')
				
			#%%----- Figura: Caustica (hew)
			
			plt.figure(33)
			plt.gcf().clear()
			#-- serie dati: hew
			plot(DefocusList_mm, Hew_,'.')
			#-- serie dati: sigma
			plot(DefocusList_mm, 2*0.68* Sigma_,'x')
			#-- serie dati: punto di minimo (1)
			plot(SpotPosition1_[iSource], SpotSize1_[iSource],'o')
			plot(SpotPosition2_[iSource], SpotSize2_[iSource],'x')
			plot(SpotPosition3_[iSource], SpotSize3_[iSource],'*') # cagare
			plot(SpotPosition4_[iSource], SpotSize4_[iSource],'.')
			
			plt.xlabel('focus shift (mm)')
			plt.ylabel('Hew')
			plt.legend(['Hew', '0.68 * 2 Sigma'])
			plt.title('Grafico Caustica')

	toc2 = time.time()
	#%%----- Figura: Spostamento Sorgente
		
	plt.figure(34)
	plt.gcf().clear()
	
	#------ Hew, raw
	y = DeltaSourceList
	x = SpotPosition1_
	plot(x, y,'x')
	#------ Hew, spline
	y = DeltaSourceList
	x = SpotPosition2_
	plot(x, y,'x')
	#------ Gaussiana, raw
	y = DeltaSourceList
	x = SpotPosition3_
	plot(x, y,'o')
	
	#------ Gaussiana, spline
	y = DeltaSourceList
	x = np.array(SpotPosition4_) 
	x = x*1e-3 
	plot(x, y,'*')
	# ------ Gaussiana, spline=> FIT
	# p = np.polyfit(x,y,1)
	# xnew = np.linspace(-5e-3,0)
	# ynew = polyval(p,xnew)
	# plot(xnew,ynew,'--')
	# #------- Teoria dell M^2
	# ynew2 = polyval([M**2,0], xnew)
	# plot(xnew, ynew2, '-')
	
	plt.xlabel('defocus (mm)')
	plt.ylabel('Sorgente (m)')
	plt.legend(['data', 'interp' , 'ds = M^2 df', 'gauss (spline)', 'interp'])
	plt.title('Spostamento sorgente')
	plt.grid()
	plt.show()

	# pr.print_stats(sort='tottime')

	print('\nnumba decorator before HuygensIntegral_1d_Kernel: @jit(nopython=False, parallel=False)')
	print('Field calculation: {:.3f} s'.format(toc - tic))
	print('Focus sweep (N = {:d}): {:.3f} s'.format(NDeltaFocus, toc1 - tic1))
	print('Total time of calculation: {:.3f} s'.format(toc2-tic))