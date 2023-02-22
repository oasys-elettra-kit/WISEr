from LibWiser.EasyGo import *
import LibWiser.FermiSource 
from LibWiser.FermiSource import F2Items
Layout = F2Items

PathMetrologyFermi = lw.Paths.MetrologyFermi

PathMetrology = MakePath('D:\Topics\WISER\Repository GIT\Metrology\FERMI\Best')
class FigErrorEnum:
	LDM_KBV = PathMetrology / 'ldm_kbv_(mm,nm).txt'
	LDM_KBH = PathMetrology / 'ldm_kbh_(mm,nm).txt'
	DPI_KBV = PathMetrology / 'dpi_kbv_(mm,nm).txt'
	DPI_KBH = PathMetrology / 'dpi_kbh_(mm,nm).txt'	
	
	

#%% DEFAULT SETTINGS: You can change parameter here or in a similar <Settings> dictionary
#%=============================================================================
BeamlineName = 'MAG'
SettingsDefault = {
			'--- Computation settings---' : '',
			'NSamples' : 10002,
			'OrientationToPropagate' : [Enums.OPTICS_ORIENTATION.VERTICAL],
			'ElementsToIgnore' : [],
			
			'--- Source settings---':'',
			'FelSource' : 2,
			'Waist0' : 106e-6,
			'Lambda' : 2e-9,
			
			'--- Detector settings---':'',
			'DetectorSize' : 100e-6,
			'DetectorDefocus' : 0,
			
			'---  Macro  settings---' : '',
			'UseFigureError' : False,
			'UseFigureErrorOnFocusing' : False,
			'UseFigureErrorOnTransport' : False,
			'UseTransport' : True,
			'UseCustomSampling' : True,
			'UseSlits' : True,
			'FigureErrorOnFocusingH' : FigErrorEnum.LDM_KBH,
			'FigureErrorOnFocusingV' : FigErrorEnum.LDM_KBV
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




##---PMA (H)
##------------------------------------------------------------
#pm2a = OpticalElement(
#				Name = 'pm2a',
#				CoreOpticsElement = Optics.MirrorPlane(
#						L = 0.4,
#						AngleGrazing = Layout.pm2a.GrazingAngle,
#						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
#				PositioningDirectives = Foundation.PositioningDirectives(
#						ReferTo = 'source',
#						PlaceWhat = 'centre',
#						PlaceWhere = 'centre',
#						Distance = Layout.pm2a.z + SourceOffset)
#							)
#_ = pm2a
#_.CoreOptics.FigureErrorLoadFromFile(PathMetrologyFermi /  "PM2A" / "PM2A_I06.SLP",
#									 FileType = Enums.FIGURE_ERROR_FILE_FORMAT.ELETTRA_LTP_DOS)
#
##---presto (h)
##------------------------------------------------------------
#presto = OpticalElement(
#				Name = 'presto',
#				CoreOpticsElement = Optics.MirrorPlane(
#						L = 0.4,
#						AngleGrazing = Layout.presto.GrazingAngle,
#						Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
#				PositioningDirectives = Foundation.PositioningDirectives(
#						ReferTo = 'source',
#						PlaceWhat = 'centre',
#						PlaceWhere = 'centre',
#						Distance = Layout.presto.z + + SourceOffset)
#							)
#				
#_ = presto
##-figure error
#FileName = MakePath('D:\Topics\WISEr\Examples 2020\Test grating\HE_FigureError_Step=1mm.txt')
#_.CoreOptics.FigureErrorLoadFromFile(FileName ,
#							 FileType = Enums.FIGURE_ERROR_FILE_FORMAT.HEIGHT_ONLY,
#							 Step = 1e-3,
#							 SkipLines = 1,
#							  	 YScaleFactor = -1e-3) # units of the file (minus to invert the figure error))



#--- aliases
f1v = 77.9329
f2v = 1.3

Mv = f1v / f2v

f1h = 72.4427
f2h = 6.79
Mh = f1h / f2h
GrazingAngle = np.deg2rad(2)

#---fm_h
#------------------------------------------------------------
fm_h = OpticalElement(
				Name = 'fm_h',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.4,
													f1 = f1h,
													f2 = f2h,
													Alpha = GrazingAngle,
													Orientation = Optics.OPTICS_ORIENTATION.HORIZONTAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'upstream focus',
													PlaceWhere = 'centre',
													ReferTo = 'source'))
_ = fm_h
# figure error
FileFigureErrorKbh = S['FigureErrorOnFocusingH']
_.CoreOptics.FigureErrorLoadFromFile(PathFile = FileFigureErrorKbh,
									  FileType = Enums.FIGURE_ERROR_FILE_FORMAT.POSITION_AND_HEIGHT,
									  XScaleFactor = 1e-3,
									  YScaleFactor = 1e-9,
									  YSign = +1)

#---fm_v
fm_v= OpticalElement(
				Name = 'fm_v',
				CoreOpticsElement = Optics.MirrorElliptic(
													L = 0.4,
													f1 = f1v,
													f2 = f2v,
													Alpha = GrazingAngle,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'upstream focus',
													PlaceWhere = 'centre',
													ReferTo = 'source'))
_ = fm_v
# figure error

#FileFigureErrorKbv =  PathMetrologyFermi /"LDM KAOS2019 KBH" / "Scan_Motor5_56_res.dat"
FileFigureErrorKbv = S['FigureErrorOnFocusingV']
_.CoreOptics.FigureErrorLoadFromFile(PathFile = FileFigureErrorKbv,
									  FileType = Enums.FIGURE_ERROR_FILE_FORMAT.POSITION_AND_HEIGHT,
									  XScaleFactor = 1e-3,
									  YScaleFactor = 1e-9,
									  YSign = +1)




#---slits_v
#------------------------------------------------------------
alpha = np.pi/4

slits_v = OpticalElement(
				Name = 'slits_v',
				CoreOpticsElement = Optics.Slits(
													L = 13e-3,
													Orientation = Optics.OPTICS_ORIENTATION.VERTICAL),
				PositioningDirectives = Foundation.PositioningDirectives(
													PlaceWhat = 'centre',
													PlaceWhere = 'centre',
													ReferTo = 'source',
													Distance = f1v - 0.5 ) )

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
													Distance = f1v - 0.5 ))

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
													ReferTo = 'upstream',
													Distance = 0 + S['DetectorDefocus'])
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
													Distance = 0 + S['DetectorDefocus']))
# Create Beamlinee beamline starting from Beamlinee Beamline Elements Objects
#------------------------------------------------------------------------------------------------
Beamline = None
Beamline = Foundation.BeamlineElements()

Beamline.Append(s)

#if S['UseSlits']:
#	Beamline.Append(slits_v)
#	Beamline.Append(slits_h)
#	pass
Beamline.Append(fm_h)
Beamline.Append(fm_v)
Beamline.Append(det_h)
Beamline.Append(det_v)
Beamline.RefreshPositions()
Beamline.Name = BeamlineName

#%% LAYOUT MACROS, modifing the behavior of the beamline
#===============================================================================================

# Direction to propagate 
#-----------------------------------------------------------------------------------------------
Beamline.ComputationSettings.OrientationToCompute = S['OrientationToPropagate']
print(Beamline) #



# Use Figure error?
#-----------------------------------------------------------------------------------------------
for Item in [fm_v, fm_h]:
	Item.CoreOptics.ComputationSettings.UseFigureError = S['UseFigureErrorOnFocusing']
	
#--- Set the Sampling
for Item in Beamline.ItemList:
	Item.ComputationSettings.UseCustomSampling = S['UseCustomSampling']
	Item.ComputationSettings.NSamples = NSamples

#-- Ignore?
for ItemName in SettingsDefault['ElementsToIgnore']:
	try:
		Item = Beamline[ItemName]
		Item.ComputationSettings.Ignore = True
	except:
		pass
#%% Settings: UseFigureError
#==========================================================
try:
	print(Beamline)
	if 1==0:
		Beamline.ComputeFields()
		det_v.PlotIntensity()
		fm_v.PlotIntensity()
#		slits_v.PlotIntensity()
except:
	raise Exception("You got erros in the last lines of Kernel Investigator function. Remember to comment them!")

fm_h.CoreOptics.ComputationSettings.UseFigureError
