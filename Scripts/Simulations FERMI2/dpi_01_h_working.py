# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:56:47 2017

@author: ManMk

Base on dpi_01_h_debug

"""
#%% Standard import snippet (20190826)
#=======================================================================
import importlib
import numpy as np
import winsound
import matplotlib as mp
import matplotlib.pyplot as pp
import LibWISEr.Rayman as rm
import LibWISEr.Foundation as Fundation
import LibWISEr.Optics as Optics
import LibWISEr.ToolLib as tl
from LibWISEr.must import *
from LibWISEr.Foundation import OpticalElement
import LibWISEr.FermiSource as  FermiSource
from numpy import array
import csv
#import LibWISEr.FermiSource as Fermi

importlib.reload(Fundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)
importlib.reload(FermiSource)
Distances = FermiSource.DistancesF2
#%% =======================================================================

PathMetrologyFermi = "D:\\Topics\\Metrology\\FERMI"
PathMetrologyFermi = "..\\..\\Metrology\\FERMI"

print(__name__)
x = np.arange(1,100)
x = x**2
if __name__ == '__main__' or __name__ == '__lvmain__':
	a = np.array([0])

	tl.Debug.On = True

	DetectorSize = 150e-6

	# SOURCE (H,V)
	#------------------------------------------------------------
	Lambda = 2e-9
	Waist0 = 180e-6
	DeltaSource = 0
	AngleGrazing = np.deg2rad(2)

	s = OpticalElement(
				Name = 'FEL2',
				IsSource = True,
				CoreOpticsElement = Optics.SourceGaussian(
						Lambda = Lambda,
						Waist0 = Waist0,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL), # **kwargs
				PositioningDirectives = Fundation.PositioningDirectives(
						ReferTo = 'absolute',
						XYCentre = [0,0],
						Angle = 0)
				)
	__ = s
	__.CoreOptics.SmallDisplacements.Long = DeltaSource
	__.CoreOptics.SmallDisplacements.Rotation = 0
	__.CoreOptics.ComputationSettings.UseSmallDisplacements = True

	# PM2A (H)
	#------------------------------------------------------------
	pm2a = OpticalElement(
					Name = 'PM2a',
					CoreOpticsElement = Optics.MirrorPlane(
							L = 0.4,
							AngleGrazing = np.deg2rad(2.5),
							Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Fundation.PositioningDirectives(
							ReferTo = 'source',
							PlaceWhat = 'centre',
							PlaceWhere = 'centre',
							Distance = 41.4427)
								)
	__ = pm2a
	__.ComputationSettings.Ignore = True

	# presto (h)
	#------------------------------------------------------------
	presto = OpticalElement(
					Name = 'presto',
					CoreOpticsElement = Optics.MirrorPlane(
							L = 0.4,
							AngleGrazing = np.deg2rad(2.5),
							Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Fundation.PositioningDirectives(
							ReferTo = 'upstream',
							PlaceWhat = 'centre',
							PlaceWhere = 'centre',
							Distance = 8.4039)
								)
	__ = presto
	__.ComputationSettings.Ignore = True


	# diagnostic detector
	#------------------------------------------------------------
	dd = OpticalElement(
					Name = 'dd',
					CoreOpticsElement = Optics.Detector(
														L = 0.4,
														AngleGrazing = np.deg2rad(90),
														Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Fundation.PositioningDirectives(
														PlaceWhat = 'centre',
														PlaceWhere = 'centre',
														ReferTo = 'upstream',
														Distance = 50 )
								)

	# dpi_kbh
	#------------------------------------------------------------
	dpi_kbh = OpticalElement(
					Name = 'dpi_kbh',
					CoreOpticsElement = Optics.MirrorElliptic(
														L = 0.4,
														f1 = 98.55,
														f2 = 1.2,
														Alpha = np.deg2rad(2.5),
														Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Fundation.PositioningDirectives(
														PlaceWhat = 'centre',
														PlaceWhere = 'centre',
														ReferTo = 'upstream',
														Distance = Distances.DpiKbh - Distances.PM2a)
								)
	__ = dpi_kbh




	# detector_h
	#------------------------------------------------------------
	dpi_dh = OpticalElement(
					Name = 'dh',
					CoreOpticsElement = Optics.Detector(
														L = DetectorSize,
														AngleGrazing = np.deg2rad(90),
														Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Fundation.PositioningDirectives(
														PlaceWhat = 'centre',
														PlaceWhere = 'centre',
														ReferTo = 'upstream',
														Distance = Distances.DpiKbhF2 )
								)
	__ = dpi_dh



	# Create the beamline starting from the Beamline Elements Objects
	#------------------------------------------------------------
	th = None
	th = Fundation.BeamlineElements()
	th.Append(s)
	th.Append(pm2a)
#	th.Append(dd)
	th.Append(presto)
	th.Append(dpi_kbh)
	th.Append(dpi_dh)
	th.RefreshPositions()

	print(th) #
	th.Paint()


#%% Settings Sampling
	pm2a.ComputationSettings.UseCustomSampling = True
	pm2a.ComputationSettings.NSamples = 1e4

	dd.ComputationSettings.UseCustomSampling = True
	dd.ComputationSettings.NSamples = 1e4

	presto.ComputationSettings.UseCustomSampling = True
	presto.ComputationSettings.NSamples = 5e3

	dpi_kbh.ComputationSettings.UseCustomSampling  = True
	dpi_kbh.ComputationSettings.NSamples = 5e3

	dpi_dh.ComputationSettings.UseCustomSampling  = True
	dpi_dh.ComputationSettings.NSamples = 5e3

	th.GetSamplingList()
#%% Settings Metrology
	#==========================================================

	#--- pm2a
	x,y,FileInfo  = tl.Metrology.ReadLtp2File(PathMetrologyFermi + '\\' +  "PM2A\\PM2A_I06.SLP") # read slopes
	h = tl.Metrology.SlopeIntegrate(y,dx = FileInfo.XStep) # integrate slopes
	pm2a.CoreOptics.FigureErrorLoad(
				h,
				Step  = FileInfo.XStep,
				AmplitudeScaling = 1, # UNDERSTAND IF -1 or +1
				Append = False				)

	pm2a.CoreOptics.ComputationSettings.UseFigureError = True

	#--- presto
	h = tl.FileIO.ReadYFile(PathMetrologyFermi + "\\HE_WISE_FigureError.txt",
						 SkipLines=1)
	XStep = 1e-3
	presto.CoreOptics.FigureErrorLoad(
				h,
				Step  = XStep,
				AmplitudeScaling = 1e-3,
				Append = False	)


	#---kbh
	dpi_kbh.CoreOptics.ComputationSettings.UseFigureError = True      # use figure error?
	dpi_kbh.CoreOptics.FigureErrorLoad(
							File = PathMetrologyFermi + "\\dpi_kbh.txt",
							Step = 2e-3, # passo del file
							AmplitudeScaling = 1*(-1*1e-3),  # fattore di scala
							Append = False
							 )
#%% Settings Ignore
	#==========================================================
	# Ignore List
	pm2a.ComputationSettings.Ignore = False
	presto.ComputationSettings.Ignore = False
	dpi_kbh.ComputationSettings.Ignore = False
	dpi_dh.ComputationSettings.Ignore = False
#%% Settings: UseFigureError
	#==========================================================
	pm2a.CoreOptics.ComputationSettings.UseFigureError = True
	presto.CoreOptics.ComputationSettings.UseFigureError = True
	dpi_kbh.CoreOptics.ComputationSettings.UseFigureError = True

#%% Settings Pitch
	#==========================================================
#	pm2a.CoreOptics.SmallDisplacements.Rotation = np.deg2rad(1)
	# it is not useful :()

	#%%	  Propagation: Source => (beamline) => Detector
	if 1==1:
		#------------------------------------
		th.ComputeFields() # Integrated field propagation
		#%% --- Intensity on pm2a
		if 1==1:
			tl.CommonPlots.IntensityAtOpticalElement(pm2a, XUnitPrefix = 'm', FigureIndex = 11)
		#%% --- Intensity on dd
		if 1==0:
			tl.CommonPlots.IntensityAtOpticalElement(dd, XUnitPrefix = 'm', FigureIndex = 13)
		#%% --- Intensity on presto
		if 1==1:
			tl.CommonPlots.IntensityAtOpticalElement(presto, XUnitPrefix = 'm',Normalize = False, FigureIndex = 12, clear=True)

		#%% --- Intensity on KB
		if 1==1:
			tl.CommonPlots.IntensityAtOpticalElement(dpi_kbh, XUnitPrefix = 'm',Normalize = False, FigureIndex = 14, clear=True)

		#%% --- Intensity on detector
		if 1==1:
			tl.CommonPlots.IntensityAtOpticalElement(dpi_dh, XUnitPrefix = 'm',Normalize = False, FigureIndex = 15,
											clear=False)

#%%
		if 1==1:
			tl.Metrology.PlotFigureError(pm2a,Index = 0, FigureIndex=1000, clear = True)
			tl.Metrology.PlotFigureError(presto, Index = 0, FigureIndex = 1000)
			tl.Metrology.PlotFigureError(dpi_kbh,Index = 0, FigureIndex=1000)

			tl.Metrology.PlotFigureError(pm2a,LastUsed=True, FigureIndex=1001, clear = True)
			tl.Metrology.PlotFigureError(presto, LastUsed=True, FigureIndex = 1001)
			tl.Metrology.PlotFigureError(dpi_kbh,LastUsed=True, FigureIndex=1001)




