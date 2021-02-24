from LibWiser.EasyGo import *
import LibWiser.FermiSource 



#%% DEFAULT SETTINGS: You can change parameter here or in a similar <Settings> dictionary
#====================================================================================================================
BeamlineName = 'BLor'
SettingsDefault = {'Lambda' : 5e-9,
			'Waist0' : 50e-9,
			'DetectorSize' : 100e-6,
			'NSamples' : 8000,
			'UseFigureErrorOnFocusing' : False,
			'UseFigureErrorOnTransport' : False,
			'UseTransport' : True,
			'UseCustomSampling' : True,
			'GratingOrder' : 1,
			'UseSlits' : True,
			'OrientationToPropagate' : [Optics.OPTICS_ORIENTATION.VERTICAL],
			'ItemsToIgnore' : ['slit2_v','slit3_v','slit4_v']
			}
#====================================================================================================================


# Merge the default settings of <SettingsDefault> with the current settings of <Settings>, if
# the latter exist in the python namespace. 
try:
	SettingsDefault.update(Settings)
except:
	pass

# Creating aliases and selecting FERMI initial source offset
S = SettingsDefault
DetectorSize = S['DetectorSize']	
UseSlits = S['UseSlits']
NSamples = S['NSamples']
SourceOffset = 0 

#%% LAYOUT: creating Foundation.Optical element objects
#%=============================================================================

#---SOURCE (H,V)
#------------------------------------------------------------
DeltaSource = 0
s = OpticalElement(
			Name = 's',
			IsSource = True,
			CoreOpticsElement = Optics.SourceGaussian(
					Lambda = S['Lambda'],
					Waist0 = S['Waist0'],
					Orientation = Optics.OPTICS_ORIENTATION.ISOTROPIC),
			PositioningDirectives = Foundation.PositioningDirectives(
					ReferTo = 'absolute',
					XYCentre = [0,0],
					Angle = 0)
			)

#---slits1
#------------------------------------------------------------
slit1_v = OpticalElement(
				Name = 'slit1_v',
				CoreOpticsElement = Optics.Slits(
													L = 830e-6,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 11.517 )
				)

slit1_h = OpticalElement(
				Name = 'slit1_h',
				CoreOpticsElement = Optics.Slits(
													L = 830e-6,
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 11.517 )
				)

#---torodail mirror fm1_h (H)
#------------------------------------------------------------
fm1_h = OpticalElement(
				Name = 'fm1_h',
				CoreOpticsElement = Optics.MirrorSpheric(
						R = 117.700, 
						L = 0.5,
						AngleGrazing = np.deg2rad(90-88.25),
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 16)
							)

#---fm2_h
#------------------------------------------------------------
f1h = 13.750
f2h = 1.2
zh = 31.75
fm2_h = OpticalElement(
				Name = 'fm2_h',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.4,
													f1 = 13.750 ,
													f2 = 1.2,
													Alpha = np.deg2rad(90-88.5),
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 31.75)
				)		

#---slit2 (v)
#------------------------------------------------------------
slit2_v = OpticalElement(
				Name = 'slit2_v',
				CoreOpticsElement = Optics.Slits(
						L = 100e-3,
						Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 18)
				)

slit2_h = OpticalElement(
				Name = 'slit2_h',
				CoreOpticsElement = Optics.Slits(
						L = 100e-3,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 18)
				)

#---slit3 (v)
#------------------------------------------------------------
slit3_v = OpticalElement(
				Name = 'slit3_v',
				CoreOpticsElement = Optics.Slits(
													L = 20e-6,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 19 )
				)	

slit3_h = OpticalElement(
				Name = 'slit3_h',
				CoreOpticsElement = Optics.Slits(
													L = 100e-3,
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 19)
				)													

#---plane mirrror (v)
#------------------------------------------------------------				
pm1 = OpticalElement(
				Name = 'pm1',
				CoreOpticsElement = Optics.MirrorPlane(
						L = 0.5,
						AngleGrazing = np.deg2rad(90- 87.242500),
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 20.740 )
							)


#---grating mirror(v)
#------------------------------------------------------------	
	
g1 = OpticalElement(
				Name = 'g1',
				CoreOpticsElement = Optics.GratingMono(
						L = 0.5,
						AngleGrazing = np.deg2rad(90-87.980900 ),
						Lambda = S['Lambda'],
						Order = S['GratingOrder'],
						LinesPerMillimiter =  400, #3750,
						GrooveLength = None, # if None, then set = L
						GrooveHeight = 31.5e-9, # if None, the figure error can not be computed
						GrooveDutyCycle = 0.5,
						GrooveType = Optics.GROOVE_TYPE.SQUARE,
						Orientation = VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 21.0)
							)
			

#---slit4
#------------------------------------------------------------
slit4_v = OpticalElement(
				Name = 'slit4_v',
				CoreOpticsElement = Optics.Slits(
						L = 20e-3,
						Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 23 )
				)	

slit4_h = OpticalElement(
				Name = 'slit4_v',
				CoreOpticsElement = Optics.Slits(
						L = 10e-6,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						Distance = 23 )
				)	

#---fm2_v
#------------------------------------------------------------
f1v = 83
f2v = 1.650
zv = 31.3
fm2_v = OpticalElement(
				Name = 'fm2_v',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.4,
													f1 = 83,
													f2 = 1.650,
													Alpha = np.deg2rad(90-88.5),
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 31.300)
				)
				
#---fm2_h
#------------------------------------------------------------
f1h = 13.750
f2h = 1.2
zh = 31.75
fm2_h = OpticalElement(
				Name = 'fm2_h',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.4,
													f1 = 13.750 ,
													f2 = 1.2,
													Alpha = np.deg2rad(90-88.5),
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													Distance = 31.75)
				)
							
#---Detector
#------------------------------------------------------------
det_v= OpticalElement(
				Name = 'det_v',
				CoreOpticsElement = Optics.Detector(
													L = DetectorSize,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'downstream focus',
													ReferTo = 'upstream',
													Distance = 0))

#---Detector
#------------------------------------------------------------
det_h = OpticalElement(
				Name = 'det_h',
				CoreOpticsElement = Optics.Detector(
													L = DetectorSize,
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'downstream focus',
													ReferTo = 'upstream',
													Distance = 0))		
				
# Create Beamlinee beamline starting from Beamlinee Beamline Elements Objects
#------------------------------------------------------------
Beamline = None
Beamline = Foundation.BeamlineElements()

Beamline.Append([s, 
				 slit1_v, slit1_h,
				 fm1_v, fm1_h,
				 slit2_v, slit2_h,
				 slit3_v, slit3_h,
				 pm1,
				 g1,
				 slit4_v, slit4_h,
				 fm2_v,
				 fm2_h,
				 det_v, det_h])
	

Beamline.RefreshPositions()
Beamline.Name = BeamlineName
print(Beamline)
Bh = Beamline.GetSubBeamlineCopy(HORIZONTAL)
Bv = Beamline.GetSubBeamlineCopy(VERTICAL)
print(Bh)
print(Bv)
#%%

#%%
Beamline.ComputationSettings.OrientationToCompute = S['OrientationToPropagate']
print(Beamline) #

#%% Sampling

for Item in Beamline.ItemList:
	Item.ComputationSettings.UseCustomSampling = S['UseCustomSampling']
	Item.ComputationSettings.NSamples = NSamples


#%% LAYOUT MACROS, modifing the behavior of the beamline
#===============================================================================================

# Direction to propagate 
#-----------------------------------------------------------------------------------------------
Beamline.ComputationSettings.OrientationToCompute = S['OrientationToPropagate']
print(Beamline) #



# Use Figure error?
#-----------------------------------------------------------------------------------------------
#for Item in [pm2a,presto]:
#	Item.CoreOptics.ComputationSettings.UseFigureError = S['UseFigureErrorOnTransport']
#for Item in [fm_v, fm_h]:
#	Item.CoreOptics.ComputationSettings.UseFigureError = S['UseFigureErrorOnFocusing']
	
#--- Set the Sampling
for Item in Beamline.ItemList:
	Item.ComputationSettings.UseCustomSampling = S['UseCustomSampling']
	Item.ComputationSettings.NSamples = NSamples

#-- Ignore?
for _ in S['ItemsToIgnore']:
		Item = Beamline[_]
		Item.ComputationSettings.Ignore = True
