# -*- coding: utf-8 -*-
"""
Created on Mon May 11 10:20:08 2020

@author: Mike - Manfredda
"""
#%% Standard import snippet (2020)
#=======================================================================
import importlib
from LibWiser.Scrubs import DataContainer
import LibWiser.WiserImport as lw # this file and the Simulator are 'lw' compliant
from LibWiser.must import *
from LibWiser.WiserImport import * # a big mess but... preserves 'tl' in the layout file
importlib.reload(lw)
import time
import logging
import os

LogFile = lw.Paths.Tmp / 'PurosangueLog.txt'
lw.ToolLib.PathCreate(LogFile)

Tic = time.time()
LogPrint = lambda Msg : logging.warning(Msg)
try:
	os.rmdir(LogFile)
except:
	pass

# Possible settings
# Possible Autofocus Configurations:
# AutofocusForEach:
# 	for every value to be scanned, the detector is placed in the best focus (Focust is called)
#  Used in: Intensity-Scan-Mode
# AutofocusOnStart:
#	The Best focus if found just before starting the computation
#  the DefocusOffset_mm property is overwritten by the output of a FindBestFocust procedure.
#	Example: Angular jittering, HEW scan. You find the best focus

from enum import Enum
#==============================================================================
#	 ENUM : ScanTypes
#==============================================================================
class ScanTypes(Enum):

	PARAMETER_VS_DEFOCUS_VS_HEW = 0 # double scan (PARAM and DEFOCUS)
	PARAMETER_VS_DETECTOR_VS_I = 1  # single scan (PARAM)
	PARAMETER_VS_DETECTOR_VS_I_NOMINAL_FOCUS = 1  # single scan (PARAM)
	ANGLE_VS_HEW_AND_FOCALSHIFT = 4 #single scan (PARAM)
	DEFOCUS_VS_HEW = 2 # single scan (DEFOCUS)


#==============================================================================
#	 ENUM : AutofocusModes
#==============================================================================
class AutofocusModes(Enum):
	NO = 0
	ON_START = 1
	AT_FIRST_PARAMETER = 2**1 # => PARAMETER is to scan, DETECTOR is returned
	FOR_EACH_PARAMETER_VALUE = 2**2
	AT_FIRST_IN_BATCH = 2**3

#==============================================================================
#	 ENUM : ParameterToScan
#==============================================================================
class ParametersToScan(Enum):
	LAMBDA = 'lambda'
	SOURCE_SHIFT= 'shift'
	SOURCE_ANGLE = 'angle'

#==============================================================================
#	 CLASS: SourceManipulator
#==============================================================================
class SourceManipulator():
	'''
	Output format
	----
	After a long discussion, the output is "TASK-driven", and not "STRUCTURE-driven". I.e. a task produces a
	self-explainatory output.
	Each group has a description section, explaining the logic of the scan.


	ParameterScan => X,Y,Z

	Para

	'''

	class SettingsCl(DataContainer):
		def __init__(self):
			self.AutoFocus : AutofocusModes = AutofocusModes.NO
			self.DefocusOffset = 0 # Used in  PARAMETER_VS_DEFOCUS_VS_HEW
			self.DefocusRange = 10 # Used in PARAMETER_VS_DEFOCUS_VS_HEW
			self.DefocusN = 21
			self.FileOut = None
			self.NSamples = 1e4
			self.UseFocusingFigureError = False


	#==================================
	#	 FUN: __init__
	#==================================
	def __init__(self,
					Beamline : lw.Foundation.BeamlineElements = None,
					BeamlineLayout : str = '',
					BeamlineName : str = 'Beamline',
					FocusingName : str = '',
					DetectorName : str = '' ,
					ScanType : ScanTypes = ScanTypes.DEFOCUS_VS_HEW,
					Parameter : ParametersToScan = None,
					ParameterRange = [] ,
					Lambda = 20e-9, # used as default
					Waist0 = 180e-6,
					SourceAngle = 0, # used as default
					SourceShift = 0,
					DetectorSize = 100e-6,
					NSamples = 1e4,
					UseSounds = True,
					DoPlots = True): # used as default

		self.Settings = SourceManipulator.SettingsCl()
		self.Output = DataContainer(ComputationTimeMin = None)

		if Beamline is not None:
			self.Beamline = Beamline
		else:
			self.LoadBeamlineLayoutFile(BeamlineLayout, BeamlineName)
			self.Settings.LayoutFile = BeamlineLayout

		self._ScanType = ScanType

		self.Settings.DetectorName = DetectorName
		self.Settings.FocusingName = FocusingName
		self.Settings.NSamples = NSamples

		self.Lambda = Lambda
		self.SourceAngle = SourceAngle
		self.SourceShift = SourceShift

		self.DetectorSize = DetectorSize

		self._UseSounds = UseSounds

		self._FileAttributes = dict()
		self.Lambda = self.Beamline.Source.CoreOptics.Lambda

	#==================================
	#	 FUN: LoadBeamlineLayoutFile
	#==================================
	def LoadBeamlineLayoutFile(self, FilePath, BeamlineName = 'Beamline'):
		'''
		Parameters
		-------
		FilePath : str
			Path to the py file containing the beamline layout file
		BeamlineName : str

		'''


		# RUN THE BEAMLINE LAYOUT FILE #
		scriptContent = open(FilePath, 'r').read()
		exec(scriptContent)
		exec('self.Beamline =%s' % BeamlineName) #>>> example: self.Beamline = th

	#==================================
	#	 FUN: SyncSource
#	#==================================
#	def SyncSource(self):
#		self.Beamline.Source.CoreOptics.Lambda = self.Lambda
#		self.Beamline.Source.CoreOptics.Lambda.Waist0 = self.Waist0
#

	#==================================
	#	 FUN: GetDefocusList
	#==================================
	def GetDefocusList(self, Offset = None):
		# Compute the Defocus Range for Defocus Scan
		if Offset is None:
			Offset = self.Settings.DefocusOffset
		else:
			Offset = Offset
		Range = self.Settings.DefocusRange
		N = self.Setting.DefocusN

		# Compute the Defocus Range for Defocus Scan
		a = -(Range/2) + Offset
		b = (Range /2) + Offset
		DefocusList = np.linspace( a, b, N)


	#==================================
	#	 PROP: ScanType
	#==================================
	@property
	def ScanType(self):
		return self._ScanType

	@ScanType.setter
	def ScanType(self, x):
		'''
		Accordin to the ScanType, tune the different setting around the class
		'''
		self._ScanType = x
		if self._ScanType == ScanTypes.PARAMETER_VS_DEFOCUS_VS_HEW: # double scan
			self.Settings.Autofocus = AutofocusModes.NO

		elif self._ScanType ==  ScanTypes.PARAMETER_VS_DETECTOR_VS_I: # single scan
			self.Settings.Autofocus = AutofocusModes.FOR_EACH_PARAMETER_VALUE

		elif self._ScanType ==  ScanTypes.PARAMETER_VS_DETECTOR_VS_I_NOMINAL_FOCUS:
			self.Settings.Autofocus = AutofocusModes.NO

		elif self._ScanType == ScanTypes.PARAMETER_VS_HEW_AND_FOCALSHIFT: #used for new angular scab
			self.Settings.Autofocus = AutofocusModes.ON_START

		elif self._ScanType == ScanTypes.DEFOCUS_VS_HEW:
			self.Settings.Autofocus = AutofocusModes.NO


	#=======================================================================
	#	 FUN: DIGEST STUFF
	#=======================================================================
	def DigestStuff(self):

		VariableToReplace = XParameter
		XAxisLabel = VariableToReplace


		ScanDescription = {	0:'HewVsDefocusVsParameter' ,
							1:'IntensityVsDetectorVsParameter' ,
							2: 'Caustics' ,
							-1:'IntensityVsDetectorVsParameter_NominalFocus',
							-3: 'no scan'}

		YAxisLabels = { 0: 'Defocus' ,
					 1 : 'Detector' ,
					 2 : 'Defocus',
					 -1 :'Detector',
					 -3: 'Detector' }

		YAxisLabel = YAxisLabels[YTypeScan]

		# Switch Parameter-> XInfo
		if Parameter == ParametersToScan.LAMBDA:
			XInfo = DataContainer(Name = 'Lambda',
										Unit = 'm',
										Label = '$\\lambda$',
										VisualizationFactor = 1e9,
										VisualizationPrefix = 'n')

		elif  Parameter == ParametersToScan.SOURCE_ANGLE:
			XInfo = DataContainer(Name = 'Angle',
										Unit = 'rad',
										Label = '$\\vartheta$',
										VisualizationFactor  = 1e6,
										VisualizationPrefix = 'u')

		elif  Parameter == ParametersToScan.SOURCE_SHIFT:
			XInfo = DataContainer(Name = 'Source Shift',
										Unit = 'm',
										Label = '$\\Delta S$',
										VisualizationFactor  = 1,
										VisualizationPrefix = 'm')



		# Switch ScanType -> YInfo, ZInfo
		if ScanType == ScanTypes.PARAMETER_VS_DEFOCUS_VS_HEW : #returns defocus + HEW
			YInfo = DataContainer(Name = 'Defocus',
										Unit = 'm',
										Label = '$\\Delta f$',
										VisualizationFactor = 1e3,
										VisualizationPrefix = 'm')

			ZInfo = DataContainer(Name = 'HEW',
										Unit = 'm',
										Label = 'Spot Size (HEW)',
										VisualizationFactor = 1e6,
										VisualizationPrefix = 'u')
			ZAxisLabel = 'HEW'


		elif ScanType == ScanTypes.PARAMETER_VS_DETECTOR_VS_I  or ScanType == ScanTypes.PARAMETER_VS_DETECTOR_VS_I_NOMINAL_FOCUS:
			YInfo = DataContainer(Name = 'Detector',
										Unit = 'm',
										Label = '$s$',
										VisualizationFactor = 1e3,
										VisualizationPrefix = 'm')

			ZInfo = DataContainer(Name = 'Intensity',
										Unit = 'a.u.',
										Label = 'I',
										VisualizationFactor = 1,
										VisualizationPrefix = '')

			ZAxisLabel = 'Intensity'
			DefocusOffset_mm = np.NAN
			DefocusRange_mm = np.NAN

		else: # dummy. Introduced only to not perform any scan (debug purposes)
			YInfo = DataContainer(Name = 'dummy',
										Unit = '',
										Label = '',
										VisualizationFactor = 1,
										VisualizationPrefix = '')

			ZInfo = DataContainer(Name = 'dummy',
										Unit = '',
										Label = '',
										VisualizationFactor = 1,
										VisualizationPrefix = '')
			ZAxisLabel = ''
			DefocusOffset_mm = np.NAN
			DefocusRange_mm = np.NAN

		# Set HewInfo, FocalShiftInfo
		HewInfo = DataContainer(Name = 'HEW',
									Unit = 'm',
									Label = 'Spot Size (HEW)',
									VisualizationFactor = 1e6,
									VisualizationPrefix = 'u')

		FocalShiftInfo = DataContainer(Name = 'Focal shift',
									Unit = 'm',
									Label = '$\\Delta f$',
									VisualizationFactor = 1e3,
									VisualizationPrefix = 'm')

		# Initialize H5 Attributes

		FileAttributes = dict()

		# about the source
		self._FileAttributes['Waist0'] = Waist0
		self._FileAttributes['SourceAngle'] = SourceAngle
		self._FileAttributes['Lambda'] = Lambda
		self._FileAttributes['SourceShift'] = SourceShift
		self._FileAttributes['NSamples'] = NSamples

		# about the Scan
		self._FileAttributes['YTypeScan'] = ScanType
		self._FileAttributes['YScanDescription'] = YScanDescription [ScanType]
		self._FileAttributes['ScanType'] = ScanType
		self._FileAttributes['ScanDescription'] = ScanDescription[ScanType]

		# about the detector and optics
		self._FileAttributes['UseFigureError'] = UseFigureError
		self._FileAttributes['DetectorSize'] = DetectorSize
		#--- Defocus scan only
		self._FileAttributes['DefocusRange_mm'] = self.Settings.DefocusRange * 1e3
		self._FileAttributes['DefocusOffset_mm'] = self.Settings.DefocusOffset * 1e3

		#--- ParameterScan
		self._FileAttributes['XParameter'] = XAxisLabel
		self._FileAttributes['Parameter'] = XAxisLabel

		self._FileAttributes['whos'] = 'X is %s, Y is %s, Z is %s' % (XAxisLabel, YAxisLabel, ZAxisLabel)
		self._FileAttributes['whos_X'] = XAxisLabel
		self._FileAttributes['whos_Y'] = YAxisLabel
		self._FileAttributes['whos_Z'] = ZAxisLabel


		#----- Default naming list, if not existing in the namespace
		try:
			NamingList
		except:
			NamingList = ['Parameter','UseFigureError']
		#----- Define the name of the output file
		KernelTag = 'byDamascus'
		__ = os.path.splitext(FileBeamlineLayout)[0] # get the file name without extension
		__ = __.replace('beamline_layout_','').upper() # remove 'beamline_layout' in the file name

		if (FileNameBase =='auto' ) :
			FileNameBase = __
		else :
				FileNameBase = FileNameBase + '_' + __




		NamingValues = ','.join([ Key + '=' + lw.Units.SmartFormatter(FileAttributes[Key]) for Key in NamingList])
		FileName = FileNameBase + '_' + YScanDescription [YTypeScan] + '_' + NamingValues + '_' + KernelTag + '.h5'




		self.Settings.FileOut = PathJoin(OutFolder,FileName)


	#%% DATA SAVE/SAVEING
	#----- Helper code: Choosing the proper XAxis YAxis
	try:
		if SaveData == True:
			XAxis = XTypeScanList

			if YTypeScan == 0:
				YAxis = DefocusList
			elif YTypeScan == 1:
				YAxis = DetectorToUse.ComputationData.S
			elif YTypeScan == -1:
				YAxis = DetectorToUse.ComputationData.S
	except:
		pass


	#======================================================
	#	 FUN: Compute
	#======================================================
	def Compute(self):

		HewCollection = []
		SigmaCollection = []
		ECollection= []
		ZCollection = [] # it's a 2D matrix, appended column by column
		BestFocalShiftList = [] # 1d, used in YType=1, for storing the best defocys
		BestHewList = [] # as before

		if ScanType != -2:

			# Link to ParameterToScan
			#=============================
			if self.Parameter == ParametersToScan.LAMBDA:
				ParameterToScan = Beamline.Source.CoreOptics.Lambda

			elif self.Parameter == ParametersToScan.SOURCE_ANGLE:
				ParameterToScan = Beamline.Source.CoreOptics.SmallDisplacements.Rotation

			elif self.Parameter == ParametersToScan.SOURCE_SHIFT:
				ParameterToScan = Beamline.Source.CoreOptics.SmallDisplacements.Long

			# Link to Detector
			#===================================================
			Detector = Beamline[self.DetectorName]

			# Link to Focusing
			#===================================================
			Focusing = Beamline[self.FocusingName]

			# Applying Initial conditions to the source
			#===================================================
			Source.CoreOptics.Lambda = self.Lambda
			Source.CoreOptics.CoreOptics.SmallDisplacements.Rotation = self.SourceRotation
			Source.CoreOptics.CoreOptics.SmallDisplacements.Long = self.SourceShift

			# AUTOFOCUS ON START
			#==========================================================================
			'''
			Before the XParameter scan, I find the best focus using the nominal condition.
			Used for: PARAMETER_VS_HEW_AND_FOCALSHIFT
			'''
			if self.Settings.AutofocusMode == AutofocusModes.ON_START:
				AutofocusOnStartResults = Foundation.FocusFind(FocussingElement,
									  DetectorSize = DetectorSize,
												MaxIter = 31)

				Detector.PositioningDirectives.Distance += AutofocusOnStartResults.BestDefocus
				Beamline.RefreshPositions()


			#===================================================================
			#Start the X-Parameter Scan
			#===================================================================
			for iScanValue, ScanValue in enumerate(ParameterRange):
				# Timing
				SubTic = time.time()
				if UseSounds:
					Beep(644,50)
					Beep(744,50)
				Msg= ('Scan %d/%d, %s=%0.1e' %(iScanValue+1, NScans, XParameter, ScanValue))
				LogPrint(Msg)
				ParameterToScan = ScanValue


				# COMPUTE FIELD (up to the nominal position)
				Beamline.ComputeFields()
				DeltaS = np.mean(np.diff(Detector.Results.S))  # Sample spacing on the detector


				# PARAMETER SCAN
				#=========================================================================
				if self.ScanType == ScanTypes.PARAMETER_VS_DETECTOR_VS_I:
					'''
					Parameter: Any
					Autofocus: FOR_EACH or NONE

					Single scan along PARAMETER
					Autofocus For Each X, if required, then the intensity is returned

					Used for: Lambda scans
					'''
					# Optimize the focus for each value of the Parameter
					#-------------------------------------------------------------------
					if self.Settings.Autofocus or AutofocusModes.FOR_EACH_PARAMETER_VALUE:
						Results = Foundation.FocusFind(FocussingElement,
														  DetectorSize = DetectorSize,
																		MaxIter = 21)
						I = np.abs(Results.BestField)**2
						BestFocalShiftList.append(Results.BestDefocus) # a scalar
						BestHewList.append(Results.BestHew) #tbc
					else:
						I = np.abs(Detector.ComputationResults.Field)

					ZCollection.append(I) # existing

				# PARAMETER AND DEFOCUS SCAN
				#=========================================================================
				elif self.ScanType == ScanTypes.PARAMETER_VS_DEFOCUS_VS_HEW:
					'''
					Double scan along PARAMETER and DEFOCUS

					'''
					DefocusList_mm = DefocusList * 1e3

					# Optimize the focus BEFORE performing the scan
					#-------------------------------------------------------------------
					if self.Settings.Autofocus or AutofocusModes.ON_START:
						Results = Foundation.FocusFind(FocussingElement,
														  DetectorSize = DetectorSize,
																		MaxIter = 21)

					DefocusList = GetDefocusList(Offset = Results.BestDefocus )

					HewList = wr.Foundation.FocusSweep2(FocussingElement,
																		   DefocusList,
																			DetectorSize = DetectorSize)
					SigmaList = [None] * len(HewList)
					HewCollection.append(HewList)
					SigmaCollection.append(SigmaList)
					ZCollection.append(HewList)

				# ANGULAR SCAN (SPECIALIZED)
				#=========================================================================
				elif self.ScanType == ScanTypes.PARAMETER_VS_HEW_AND_FOCALSHIFT:
					'''
					Like parameter scan, but specialized for the angle, and with AUTOFOCUS_ON_START
					Parameter = Angle
					Autofocus = ON_START (is expected to be like that)

					'''
					# The field is already computed
					I = np.abs(Detector.ComputationData.Field)**2
					(Hew, Centre) = lw.Rayman.HalfEnergyWidth_1d(I, Step=DeltaS, UseCentreOfMass = False)
					HewList.append(Hew) # HEW

				elif self.ScanType == ScanTypes.DEFOCUS_VS_HEW:
					pass

				# Next iteration
				SubToc = time.time()
				Msg= ('\t Delta t %0.1f min' %( (SubToc-SubTic)/60))
				LogPrint(Msg)

			# End of Loop
			Toc = time.time()
			ComputationTimeMin = (Toc-Tic)/60
#				FileAt



	#		print(FileOut)
	#		lw.tl.SaveMatrix(FileOut, ZCollection,  YAxis, XAxis)

#		#%% Best Focus: Plot of the Best Field
#	if 1==0:
#		plt.figure(34)
#		for I in ZCollection:
#			plot(I)
#			plt.title('best spot')
#			plt.xlabel('detector (um)')
#			plt.ylabel('I (a.u.)')
#
#	#%% Best Focus: Plot of the Focal Shift
#	if 1==0:
#		plt.figure(35)
#		plot(XTypeScanList *1e9, BestFocalShiftList,'o-')
#		plt.title('Focal Shift')
#		plt.xlabel(XParameter)
#		plt.ylabel('Focal shift')
#
#	#%% Best Focus: Plot of the HEW caustics
#	if 1==0:
#			plt.figure(36)
#			plot(XTypeScanList *1e9, BestHewList,'o-')
#			plt.title('HEW')
#	#			plt.xlabel('detector (um)')
#			plt.ylabel('HEW')
#
#
#		#%% Plot della HEW (da 2)
#	if 1==0:
#		if YTypeScan == 2:
#			plt.figure(321)
#			plot(DefocusList_mm, HewList *1e6,'b.')
#			plt.title('HEWs')
#			plt.xlabel('defocus (mm)')
#			plt.ylabel('Hew')
#			plt.legend(['Hew'])
#
#	#%% Plot della HEW caustic
#		if YTypeScan == 0:
#			plt.figure(32)
#			for i, HewList in enumerate(HewCollection):
#				StrLabel = '%0.1f' % DefocusList_mm[i]
#				plot(DefocusList_mm, HewList *1e6,'b.', label = 'HEW')
##				plot(DefocusList_mm, 2*0.68* SigmaList * 1e6 * (1+i*1e-1),'x')
#				plt.title('HEWs')
#				plt.xlabel('defocus (mm)')
#				plt.ylabel('Hew')
##				plt.legend(['Hew', '0.68 * 2 Sigma'])
#				plt.legend()
#
#				lw.ToolLib.Debug.PutData('hew1',HewList *1e6,'tmp10')
#	#%% Plot of the Computed Field
#	if YTypeScan == 0:
#		plt.figure(33)
#		for i, Result in enumerate(ResultList):
#			StrLabel = '%0.1f mm' % DefocusList_mm[i]
#			plot(Result.S * 1e6, abs(Result.Field), label = StrLabel)
#
#		plt.title('Computed Fields @ detector')
#		plt.xlabel('detector (um)')
#		plt.ylabel('W (a.u.)')
#		plt.legend()
#	#%% CHECK1 Plot of the First Computed Field on the detector
#	if 1==1:
#		plt.figure(48)
#		lw.ToolLib.CommonPlots.IntensityAtOpticalElement(Detector, FigureIndex = 48, color = 'b')
#		lw.ToolLib.Debug.PathTemporaryH5File
#		lw.ToolLib.Debug.PutData('s1', Detector.ComputationData.S,'tmp_total')
#		lw.ToolLib.Debug.PutData('i1', Detector.ComputationData.Intensity,'tmp1tmp_total00')
#
#	#%% CHECK2 figure error
#	if 1==0:
#		lw.ToolLib.CommonPlots.FigureError(kb, FigureIndex = 49)
##%% 	CHECK 3 campo sui kb
#	if 1==1:
#		try:
#			tl.Debug.PutData('ks1', kb.ComputationData.S,'tmp100')
#			tl.Debug.PutData('ki1', kb.ComputationData.Intensity,'tmp100')
#		except:
#			pass
##%% PLT "D
#	if 1==1:
#		try:
#			fig = plt.figure(666)
#			ax = fig.gca(projection='3d')
#			X, Y = np.meshgrid(XAxis*1e6, YAxis*1e3)
#			Z = np.array(ZCollection).transpose()
#			surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='hot', edgecolor = 'none',antialiased=True)
#			plt.xlabel(XInfo.Name)
#			plt.ylabel(YInfo.Name)
#			plt.title('lambda = %0.1f nm'% (Lambda*1e9))
#			plt.show()
#		except:
#			pass
#	#%% test save to h5
#	if YTypeScan != -2:
#		lw.tl.FileIO.SaveToH5(FileOut,
#						[
#					  ('ParameterScan/X',XAxis, XInfo),
#					  ('ParameterScan/Y',YAxis, YInfo),
#					  ('ParameterScan/Z',ZCollection, ZInfo),
#					  ('BestFocus/Hew',BestHewList, HewInfo),
#					  ('BestFocus/FocalShift',BestFocalShiftList,FocalShiftInfo),
#					  ('BestFocus/X', XAxis, XInfo)],
#					  FileAttributes,
#					  Mode = 'w')
#
#	PathFileOut = MakePath(os.getcwd()) / FileOut
#	PathWithFileName = MakePath(os.getcwd()).parent / 'functions'/'last_output.txt'
#	f = open(PathWithFileName,'w')
#	f.write(str(PathFileOut))
#	f.close()
#	Beep(744,50)
#	Beep(744,50)
#	Beep(744,50)
#
#	print(os.getcwd())
#	print(FileOut)
#	import playsound
#	Str = str(Paths.Main / 'doc' / 'cow.wav')
#	for i in range(1,2):
#		playsound.playsound(Str)
#	#%%
#	'''
#	Prototyping
#
#	ExtensiveDefocusScan
#		-Offset
#		-Range
#
#
#	'''

