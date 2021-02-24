from LibWiser.EasyGo import *
import LibWiser.FermiSource 
from LibWiser.FermiSource import F2Items
Layout = F2Items

PathMetrologyFermi = lw.Paths.MetrologyFermi


#%% DEFAULT SETTINGS: You can change parameter here or in a similar <Settings> dictionary
#%=============================================================================
BeamlineName = 'LDM-FEL1'
SettingsDefault = {'Lambda' : 20e-9,
			'Waist0' : 180e-9,
			'DetectorSize' : 100e-6,
			'NSamples' : 10000,
			'UseFigureErrorOnFocusing' : True,
			'UseFigureErrorOnTransport' : False,
			'UseTransport' : True,
			'UseCustomSampling' : False,
			'FelSource' : 2,
			'UseSlits' : True,
			'OrientationToPropagate' : Enums.OPTICS_ORIENTATION.HORIZONTAL
			}
#=============================================================================


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
if S['FelSource'] == 1:
	SourceOffset = Layout.fel1_offset
elif S['FelSource'] == 2:
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

#---PMA (H)
#------------------------------------------------------------
pm2a = OpticalElement(
				Name = 'pm2a',
				CoreOpticsElement = Optics.MirrorPlane(
						L = 0.4,
						AngleGrazing = Layout.pm2a.GrazingAngle,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						ReferTo = 'source',
						PlaceWhat = 'centre',
						PlaceWhere = 'centre',
						Distance = Layout.pm2a.z + SourceOffset)
							)
_ = pm2a
_.CoreOptics.FigureErrorLoadFromFile(PathMetrologyFermi /  "PM2A" / "PM2A_I06.SLP",
									 FileType = Enums.FIGURE_ERROR_FILE_FORMAT.ELETTRA_LTP_DOS,
									 Step = 1e-3,
									 YScaleFactor = 1e-3)

#---presto (h)
#------------------------------------------------------------
presto = OpticalElement(
				Name = 'presto',
				CoreOpticsElement = Optics.MirrorPlane(
						L = 0.4,
						AngleGrazing = Layout.presto.GrazingAngle,
						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
						ReferTo = 'source',
						PlaceWhat = 'centre',
						PlaceWhere = 'centre',
						Distance = Layout.presto.z)
							)

#---kb_v
#------------------------------------------------------------
f1v = Layout.ldm_kbv.f1
f2v = Layout.ldm_kbv.f2
kb_v = OpticalElement(
				Name = 'kb_v',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.4,
													f1 = f1v,
													f2 = f2v,
													Alpha = Layout.ldm_kbv.GrazingAngle,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'upstream focus',
													PlaceWhere = 'centre',
													ReferTo = 'source'))

#---kb_h
#------------------------------------------------------------
f1h = Layout.ldm_kbh.f1
f2h = Layout.ldm_kbh.f2

kb_h = OpticalElement(
				Name = 'kb_h',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.8,
													f1 = f1h,
													f2 = f2h,
													Alpha = Layout.ldm_kbh.GrazingAngle,
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'upstream focus',
													PlaceWhere = 'centre',
													ReferTo = 'source'))
#---slits_v
#------------------------------------------------------------
slits_v = OpticalElement(
				Name = 'slits_v',
				CoreOpticsElement = Optics.Slits(
													L = 13e-3,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'centre',
													ReferTo = 'source',
													Distance = f1v - 0.5))

#---slits_h
#------------------------------------------------------------
slits_h = OpticalElement(
				Name = 'slits_h',
				CoreOpticsElement = Optics.Slits(
													L = 15e-3,
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'centre',
													ReferTo = 'source',
													Distance = f1v - 0.5))

#---Detector_h h
#------------------------------------------------------------
det_h = OpticalElement(
				Name = 'det_h',
				CoreOpticsElement = Optics.Detector(
													L = DetectorSize,
													AngleGrazing = np.deg2rad(90),
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'downstream focus',
													ReferTo = 'upstream')
							)
#---Detector
#------------------------------------------------------------
det_v= OpticalElement(
				Name = 'det_v',
				CoreOpticsElement = Optics.Detector(
													L = DetectorSize,
													AngleGrazing = np.deg2rad(90),
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'downstream focus',
													ReferTo = 'upstream',
													Distance = 0))
# Create Beamlinee beamline starting from Beamlinee Beamline Elements Objects
#------------------------------------------------------------
Beamline = None
Beamline = Foundation.BeamlineElements()
Beamline.Append(s)
Beamline.Append(pm2a)
Beamline.Append(presto)

if S['UseSlits']:
	Beamline.Append(slits_v)
	Beamline.Append(slits_h)
	
Beamline.Append(kb_v)
Beamline.Append(kb_h)

Beamline.Append(det_h)
Beamline.Append(det_v)

Beamline.RefreshPositions()
Beamline.Name = BeamlineName

Beamline.ComputationSettings.OrientationToCompute = S['OrientationToPropagate']
print(Beamline) #


for Item in [pm2a,presto]:
	Item.ComputationSettings.UseFigureError = S['UseFigureErrorOnTransport']

#%% Settings Sampling

for Item in Beamline.ItemList:
	Item.ComputationSettings.UseCustomSampling = S['UseCustomSampling']
	Item.ComputationSettings.NSamples = NSamples

#NSamplesGrating = int(2e4)
#presto.ComputationSettings.NSamples= NSamples
#kb_h.ComputationSettings.NSamples = NSamples
#Detector_h.ComputationSettings.NSamples = NSamples
#%% Settings Surface Profile
#==========================================================



#---FigError presto
#------------------------------------------------------------------
h = tl.FileIO.ReadYFile(PathMetrologyFermi / "PRESTO\HE_FigureError_Step=1mm.txt",
					 SkipLines=1)
h = h*1e-3 # mm => m
if UseGrating:
	LinesPerMillimiter = 3759
	L1 = 60e-3
	L0 = 250e-3
	GrooveHeight = 9.5e-9
	hGrating, GratingStep =lw.tl.Metrology.RectangularGrating(
			L0 = L0,
			L1 = L1,
			N = int(NSamplesGrating),                     # SAMPLING OFTHE GRATING HARDCODED HERE
			LinesPerMillimiter =LinesPerMillimiter, #3759
			GrooveHeight = GrooveHeight,   #9.5e-9
			HighDuty = 0.65,      #0.65
			ReturnStep = True)
	NGrating = len(hGrating)
	hNew = rm.FastResample1d(h,NGrating) # now h has the same sampling as hGrating

	hTot = 0* hNew + hGrating
	XStep = GratingStep

else:
	hTot = h
	XStep = 1e-3

presto.CoreOptics.FigureErrorLoad(
			hTot,
			Step  = XStep,
			AmplitudeScaling = 1,
			Append = False)

#---FigError kbV (replica of kbh)
#------------------------------------------------------------------
x,h, ComputedStep = tl.Metrology.ReadLtpLtpJavaFileA(PathMetrologyFermi /"LDM KAOS2019 KBH" / "Scan_Motor5_56_res.dat",
									   Decimation = 2,
										ReturnStep = True,
										XScaling = 1e-3, # input is in mm
										YScaling = 1e-3)    # input isk in mm
kb_v.CoreOptics.FigureErrorLoad(
						h = h,
						Step = ComputedStep, # step
						AmplitudeScaling = -1 ,
						Append = False)


#---FigError kb_h
#------------------------------------------------------------------
x,h, ComputedStep = tl.Metrology.ReadLtpLtpJavaFileA(PathMetrologyFermi /"LDM KAOS2019 KBH" / "Scan_Motor5_50_res.dat",
									   Decimation = 2,
										ReturnStep = True,
										XScaling = 1e-3, # input is in mm
										YScaling = 1e-3)    # input isk in mm
kb_h.CoreOptics.FigureErrorLoad(
						h = h,
						Step = ComputedStep, # step
						AmplitudeScaling = -1 ,
						Append = False)
#%% Settings Ignore
#==========================================================
# Ignore List
pm2a.ComputationSettings.Ignore = False
presto.ComputationSettings.Ignore = False

slits_v.ComputationSettings.Ignore = False
slits_h.ComputationSettings.Ignore = True
kb_v.ComputationSettings.Ignore = False
kb_h.ComputationSettings.Ignore = False
Detector_v.ComputationSettings.Ignore = False
Detector_h.ComputationSettings.Ignore = False
#%% Settings: UseFigureError
#==========================================================
pm2a.CoreOptics.ComputationSettings.UseFigureError = UseFigureError
presto.CoreOptics.ComputationSettings.UseFigureError = UseFigureError
kb_v.CoreOptics.ComputationSettings.UseFigureError = UseFigureError
kb_h.CoreOptics.ComputationSettings.UseFigureError = UseFigureError

tl.CommonPlots.FigureError(presto)
