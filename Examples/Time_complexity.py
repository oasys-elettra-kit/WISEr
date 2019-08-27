# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27

@author: Aljosa

Time the code and plot n, t(n) graph to display time complexity.

First a simple beamline: source -> plane mirror -> detector (Studio_focus_shift_veloce.py)
is created and then the sampling is changed in increments of 10x.

"""
import numpy as np

import matplotlib.pyplot as plt
import LibWISEr.Rayman as rm
import LibWISEr.Foundation as Fundation
import LibWISEr.Optics as Optics
import LibWISEr.ToolLib as tl
import LibWISEr.FermiSource as Fermi

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

DetectorSize = 150e-6
DetectorRestPosition = 0

DoCaustics = True
NDeltaFocus = 5
RangeOfDeltaFocus= 10e-3# estensione del delta focus
DeltaFocusOffset = 0e-3 # dove centro il delta focus (se cambio la sorgente, dovrebbe cambiare)

DeltaSourceList = np.zeros(1) # espressa in unità di ondulatori

single_time = []

###############################################################################

print(__name__)
if __name__ == '__main__':

	# Debugging
	tl.Debug.On = False
	
	hew__ = []
	sigma__ = []
	hewMinPosition_ = []
	spotSize1_ = []
	spotPosition1_ = []
	spotSize2_ = []
	spotPosition2_ = []
	spotSize3_ = []
	spotPosition3_ = []
	spotSize4_ = []
	spotPosition4_ = []
	sourceResults = []

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
		sampling = np.array([5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]) # number of points
		timing = np.zeros(len(sampling))

		for i, no_pts in enumerate(sampling):

			d.ComputationSettings.NSamples = no_pts
			d.ComputationSettings.UseCustomSampling = True  # si può mettere anche su false.

			kb.ComputationSettings.NSamples = no_pts
			kb.ComputationSettings.UseCustomSampling = True  # può essere true o false indipendentemente da quello prima

			time.sleep(1) # Wait for a second before calculation

			tic = time.time()
			t.ComputeFields() # Field propagation
			toc = time.time()

			DefocusList = np.linspace(DeltaFocusOffset - RangeOfDeltaFocus/2, DeltaFocusOffset+RangeOfDeltaFocus/2, NDeltaFocus )

			print('Calculating: {}'.format(no_pts))

			time.sleep(1) # Wait for a second before calculation

			tic1 = time.time()
			ResultList, Hew_,Sigma_, More = Fundation.FocusSweep(kb, DefocusList, DetectorSize = DetectorSize, NPools = 1)
			toc1 = time.time()
			timing[i] = (toc1 - tic1) / NDeltaFocus

	print('\n DONE!')



	plt.plot(sampling, timing, linestyle='None', marker='o')
	plt.xscale('log')
	plt.yscale('log')

	plt.title('Time complexity of WISEr')
	plt.xlabel('N points')
	plt.ylabel('t [seconds]')
	plt.show()