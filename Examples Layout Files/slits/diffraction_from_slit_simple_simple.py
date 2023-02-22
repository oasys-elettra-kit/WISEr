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
if __name__ == '__main__' or __name__ == '__lvmain__':
	

#%% 1) MAKE THE OPTICAL ELEMENTS
	#---- PARAMETERS	
	NSamples = 5000
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
	#--------------------------------------------------------------------------
	mysource = OpticalElement(
				Name = 'FEL2',
				IsSource = True, # tells that this optical element is the source
				CoreOpticsElement = Optics.SourceGaussian(
						Lambda = Lambda,
						Waist0 = Waist0,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL), # **kwargs
				DistanceFromSource = 0 
				)

	# The following code set up some advanced parameters of the optical element
	# A more involved understanding of WISER design in required.
	__ = mysource
	__.CoreOptics.SmallDisplacements.Long = DeltaSource
	__.CoreOptics.SmallDisplacements.Rotation = 0
	__.CoreOptics.ComputationSettings.UseSmallDisplacements = True


	#---- SLIT
	#--------------------------------------------------------------------------
	slit = OpticalElement(
					Name = 'slit',
					CoreOpticsElement = Optics.Slits(
							L = SlitSize, # This is the slit size
							Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					DistanceFromSource = SlitZ
						)


	# detector_h
	#--------------------------------------------------------------------------
	det = OpticalElement(
					Name = 'det',
					CoreOpticsElement = Optics.Detector(
							L = DetectorSize,
							AngleGrazing = np.deg2rad(90),
							Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
					DistanceFromSource =  DetectorZ 
								)

#%% 2) ASSEMBLING THE BEAMLINE 
	'''
	After creating the optical elements, here we  are creating the beamline.
	This involves
	1) initializing a BeamlineElements() object 
	2) appending the optial elements to it
	3) Make the code compute and update the position of the elements, via the RefreshPositions() method
	

	'''
	# Create Beamlinee beamline starting from Beamlinee Beamline Elements Objects
	#------------------------------------------------------------
	Beamline = Foundation.BeamlineElements()
	Beamline.Append(mysource)
	Beamline.Append(slit)
	Beamline.Append(det)
	Beamline.RefreshPositions()
	#%% print
	'''	Note
	Use print(Beamline) or Beamline.Print() to check that WISER put the elements in the correct way.
	Use Beamline.Paint() to have a very coarse grain painting of the beamline. Notice: the painting is
	not optimized yet, so sometimes you may get visually uncomfortable output.
	'''
	
	print(Beamline) #
	#%% paint
	Beamline.Paint()

#%% 3) SETUP the SAMPLING
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
#%% 3b) SETUP the Ignore parameter (optional)
	'''
	The .Ignore attribute is a way to temporarily exclude an optical element
	from the optics train. It still appears in the optical layout, but it is
	not considered during the propagation.
	
	It is useful to temporaly exclude optical elements from the total simulation.

	Just (un)comment the following line to see the differences
	'''
	pass
# 	slit.ComputationSettings.Ignore = False

#%% 3c) SETUP  Figure ERROR (optional)
# 	#==========================================================
	# add code here, when mirror are used (not here)
#%% 4) PROPAGATION

	Beamline.ComputeFields() # Integrated field propagation
	
#%% 4b) AUTOMATIC PLOTS
 
	# plot: intensity over slit
	tl.CommonPlots.IntensityAtOpticalElement(slit, FigureIndex = 10)
	# plot: intensity over slit det
	tl.CommonPlots.IntensityAtOpticalElement(det, XUnitPrefix = 'm',Normalize = False, FigureIndex = 20)

DeltaZ = (DetectorZ - SlitZ)
XMinimum = Lambda *  DeltaZ / SlitSize
FresnelN = SlitSize**2/Lambda/DeltaZ
print('Fresnel Number D^2/Lambda/z = %0.2f ' % FresnelN)
print('Analitically, the position of the first minimum is at %0.2e m ' % XMinimum)


#%% Tg

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

#%% 
'''
Bon, qui l'esempio è finito. Si può andare un po' avanti per capire come funzionano un po' meglio  
le cose "under the hood". In particolare: come avviene la propagazione?

C'è una grossa parte del codice che si occupa del compito (apparentemente banale) di gestire il posizionamento
degli elementi ottici nello spazio. Questo è fatto dal comando
Beamline.RefreshPositions()
che in realtà è un mondo a sé stante, ancorché poco interessante e stimolante.

Una volta che gli oggetti sono ben posizionati, ognuno di essi è rappresentato da coordinate
X,Y, accessibili, per esempio, mediante:
	
'''
N = NSamples
slit_x, slit_y = slit.GetXY(N)
det_x, det_y = det.GetXY(N)

''' a questo punto del codice (che è già stato eseguito una volta), sulle slit esiste già
un campo elettromagnetico, cui si può accedere come segue. Ricordare che il campo e' 1d e non 2d'
'''
slit_E = slit.ComputationData.Field
print(slit_E)
print("size of E: %d" %  slit_E.shape)


'''
poiché il campo esiste gia', si puo' riprodurre manualmente gli stessi comandi che WISER esegue
per la propagazione numerica.

'''
from LibWiser.Rayman import HuygensIntegral_1d_Kernel
# HuygensIntegral_1d_Kernel(wl, Ea, xa, ya, xb, yb):

det_E_manual = HuygensIntegral_1d_Kernel(Lambda, slit_E, slit_x, slit_y, det_x, det_y)	
'''
e vediamo che det_E_manual è uguale al campo calcolato da WISER nel suo processo automatico
'''
residual = np.sum(det_E_manual  - det.ComputationData.Field)
print("Residuo totale: %0.1f" % residual)

'''
Qualunque nuovo propagatore si sviluppi, deve inserirsi in questo punto.
'''