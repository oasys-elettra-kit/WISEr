# -*- coding: utf-8 -*-
"""

This examples implements the following layout:

Gaussian Source --> Slit ---> Observation screen.

The slit can be tilted.
There is no focusing optics.

"""
#%% Standard import snippet (20190826)
#=======================================================================
import importlib
from LibWiser.WiserImport import *

plt.close('all') # close all the open figures
#%% =======================================================================


print(__name__)
if __name__ == '__main__' or __name__ == '__lvmain__':
	

#%% MAKE OPTICAL ELEMENTS
	#---- PARAMETERS	
	
	#---source parameters
	Lambda = 50e-9 	 		 # wavelength( nm)
	Waist0 = 100e-6  	 	 # (127um is FERMI-FEL1)
	DeltaSource = 0  	 	 # (Variation w.r.t. the nominal source position)
	#---slit parameters
	SlitSize =  0.5 * 500e-6 	 	 # width of the slit
	SlitZ = 10  	 	 	 # (m) distance from the source
	#---detector parameters
	DetectorSize = 10e-3 	 # size of the detector
	DetectorZ = SlitZ + 10	 # distance of detector from the source

	#---- SOURCE (H)
	#------------------------------------------------------------
	s = OpticalElement(
				Name = 'FEL2',
				IsSource = True, # tells that this optical element is the source
				CoreOpticsElement = Optics.SourceGaussian(
						Lambda = Lambda,
						Waist0 = Waist0,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL), # **kwargs
				PositioningDirectives = Foundation.PositioningDirectives(
						ReferTo = 'absolute',
						XYCentre = [0,0],
						Angle = 0)
				)

	#---- SLIT
	#------------------------------------------------------------
	slit = OpticalElement(
					Name = 'slit',
					CoreOpticsElement = Optics.Slits(
							L = SlitSize, # This is the slit size
							Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Foundation.PositioningDirectives(
							ReferTo = 'source', 
							Distance = SlitZ)
								)


	# detector_h
	#------------------------------------------------------------
	det = OpticalElement(
					Name = 'det',
					CoreOpticsElement = Optics.Detector(
							L = DetectorSize,
							AngleGrazing = np.deg2rad(90),
							Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					PositioningDirectives = Foundation.PositioningDirectives(
							ReferTo = 'source',
							Distance = DetectorZ )
								)

#%% Making up the beamline
	'''
	After creating the optical elements, here we  are creating the beamline.
	This involves
	1) initializing a BeamlineElements() object 
	2) appending the optial elements to it
	3) Make the code compute and update the position of the elements, via the RefreshPositions() method
	

	'''
	# Create Beamlinee beamline starting from Beamlinee Beamline Elements Objects
	#------------------------------------------------------------
	Beamline = None
	Beamline = Foundation.BeamlineElements()
	Beamline.Append(s)
	Beamline.Append(slit)
	Beamline.Append(det)
	Beamline.RefreshPositions()
	#%%
	'''	Note
	Use print(Beamline) or Beamline.Print() to check that WISER put the elements in the correct way.
	Use Beamline.Paint() to have a very coarse grain painting of the beamline. Notice: the painting is
	not optimized yet, so sometimes you may get visually uncomfortable output.
	'''
	
	print(Beamline) #
	#%%
	Beamline.Paint()

#%% SETUP: SAMPLING
	'''
	Here I set the sampling for the optical elements.
	In principle, automatic sampling is available.
	Here, I am manually setting the samples for the optical elements.
	'''
		
	# The same result could be obtained by means of
	Beamline.SetAllNSamples(5000)
	Beamline.SetAllUseCustomSampling(True)	

	# Alternative way, element by element
# 	slit.ComputationSettings.UseCustomSampling = True
# 	slit.ComputationSettings.NSamples = 5e3
# 	det.ComputationSettings.UseCustomSampling  = True
# 	det.ComputationSettings.NSamples = 5e3




	Beamline.GetSamplingList()
#%% SETUP: SAMPLING
	'''
	The .Ignore attribute is a way to temporarily exclude an optical element
	from the optics train. It still appears in the optical layout, but it is
	not considered during the propagation.
	
	It is useful to temporaly exclude optical elements from the total simulation.

	Just (un)comment the following line to see the differences
	'''
	pass
# 	slit.ComputationSettings.Ignore = False
# #%% SETUP:: Figure ERROR
# 	#==========================================================
# 	pm.CoreOptics.ComputationSettings.UseFigureError = False
# 	el1.CoreOptics.ComputationSettings.UseFigureError = False

#%% PROPAGATION

	Beamline.ComputeFields() # Integrated field propagation
	
#%% AUTOMATIC PLOTS
 
	# plot: intensity over slit
	tl.CommonPlots.IntensityAtOpticalElement(slit, FigureIndex = 10)
	# plot: intensity over slit det
	tl.CommonPlots.IntensityAtOpticalElement(det, XUnitPrefix = 'm',Normalize = False, FigureIndex = 20)

DeltaZ = (DetectorZ - SlitZ)
XMinimum = Lambda *  DeltaZ / SlitSize
FresnelN = SlitSize**2/Lambda/DeltaZ
print('Fresnel Number D^2/Lambda/z = %0.2f ' % FresnelN)
print('Analitically, the position of the first minimum is at %0.2e m ' % XMinimum)



#%% MANUAL PLOT
'''
Example:
This code shows how to manually extract from WISER the computed field and the coordinates of the
target element 
'''
import matplotlib.ticker as ticker

S = slit.ComputationData.S # points of the optical element
I = slit.ComputationData.Intensity

fig, ax = plt.subplots()

ax.plot(S,I)

ax = plt.gca()
ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))


