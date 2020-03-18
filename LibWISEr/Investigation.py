# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:51:20 2020

@author: Mike
"""
from pathlib import Path
import numpy as np

import LibWiser.WiserImport as lw
import enum

class ObsUnit():
	def __init__(self, Symbol : str , Unit : str, Name: str = None, SIPrefix = None ):
		self.Symbol = Symbol
		self.Name = Name
		self.Unit = Unit
		self.SIPrefix = SIPrefix

class SourceParameter(enum.Enum):
	LAMBDA = ObsUnit('\lambda','m', 'Wavelength','n')
	SOURCE_ANGLE= ObsUnit('\Theta' ,'rad', 'Source angle')
	SOURCE_SHIFT= ObsUnit('\Delta S' ,'m', 'Source shift')
	WAIST = ObsUnit('w_0' ,'m', 'Source waist', 'u')

class ScanType(enum.Enum):
	GET_SPOT_INTENSITY= 0
	DEFOCUS_SCAN_TO_GET_HEW= 1

# First version: a unique Parameter can be scanned
class SourceManipulator():
	def __init__(self, Beamline : lw.Foundation.BeamlineElements,
					 ParameterToScan : SourceParameter,
					 ParameterRange = None, #array like
					 Detector : lw.Foundation.OpticalElement,
					 ScanType : ScanType, # GET_SPOT_INTENSITY or  DEFOCUS_SCAN_TO_GET_HEW
					 NSampling = None, # if None uses auto
					 OESubsets : list(lw.Foundation.OpticalElement),
					 OEUseFigureError : list(bool),
					 SaveData = False,
					 WorkingFolder = Path(''),  # Required if SavaData = True
					 OutputFolder : str =  None,# Optional, used if SaveData = True
					 FileNameBase = Path('SourceManipulation_'), # Optional, used if SaveData = True
					 DefocusOE = None,		# Required if ScanType = DEFOCUS_SCAN_TO_GET_HEW. Else, it attempts to find automatically
					 DefocusN = 21,# Required if ScanType = DEFOCUS_SCAN_TO_GET_HEW
					 DefocusRange = 10e-3,# Required if ScanType = DEFOCUS_SCAN_TO_GET_HEW
					 DefocusOffset = 0, 	# Required if ScanType = DEFOCUS_SCAN_TO_GET_HEW
					 ):
		'''
		Simple manipulator class used for investigating the behaviour of the spot under
		the variation of the source.

		It allows to change the following source paramenters:
			wavelength, source angle, source shift, waist.

		The results are observed on the "Detector" element.

		The Manipulator can perform two scans:
			-compute the field(intensity) on the detector at a fixed defocus distance
			for any Parameter value (N parameter values) => Field Size x N Param Values

			-perform the defocs scan (K step), compute the HEW => K HEW values x N Param Values

		The manipulator is also capable to basically interact with the optics of the
		beamline. It can
		- (De)activate the FigureError
		- (De)activate the Roughness (*not working yet, 12-01-2020)
		- Switch the .Ignore attribute (*to do)
		All the other settings must be properly done elsewhere.
		'''

		self.ParameterToScan = ParameterToScan
		self.ParameterRange = ParameterRange
		self.Detector = Detector
		self.ScanType = ScanType
		self.NSampling = NSampling
		self.OESubsets = OESubsets
		self.OEUseFigureError = OEUseFigureError
		self.SaveData = SaveData
		self.WorkingFolder = WorkingFolder
		self.OutputFolder = OutputFolder
		self.FileNameBase=FileNameBase
		self.DefocusOE  = DefocusOE
		self.DefocusN = DefocusN
		self.DefocusRange = DefocusRange
		self.DefocusOffset = DefocusOffset

		#------------------------------------
		# PATHS                             |
		#------------------------------------
		self.OutFolder = WorkingFolder / 'Output1 (WISEr)' if OutFolder is None else OutFolder
	return

	def _InitDefocusScan(self):

		# Y-Type Variables:
		#  - HEW =>  set Defocus SCAN
		#	- Intensity => Nothing More to set
		#===========================================================================

		#------------------------------------
		# DEFOCUS SCAN                      |
		#------------------------------------
		self.DefocusOffset_mm = DefocusOffset * 1e-3
		self.DefocusRange_mm = DefocusRange * 1e-3
		DetectorSize = 50e-6 ;
		#	FocussingElementToUse = 'dpi_kbh'

	#====================================================
	# _InitTypicalPresets
	#====================================================
	def _InitTypicalPresets(self):
		'''
		To be called every time that ParameterToScan is changed
		'''
	# Typical presets:
	if ParameterRange is None:
		if ParameterToScan == SourceParameter.LAMBDA:
			ParameterRange = np.arange(1,21,0.5) * 1e-9

		elif ParameterToScan == SourceParameter.SOURCE_ANGLE:
			ParameterRange = np.linspace(-10,10,5) * 1e-6

		elif ParameterToScan == SourceParameter.SOURCE_SHIFT:
			ParameterRange = np.array([0, -0.5, -1,5]) * 3.75 # 3.75 ius the separation b\w undulators at FERMI-FEL

		elif ParameterToScan == SourceParameter.WAIST:
			ParameterRange = np.array([180, 200]) * 1e-6

	#------------------------------------
	# SELECT THE TYPE OF SCAN              |
	#------------------------------------
	# X-TYPE

	VariableToReplace = 'Lambda' 		 #'can be Angle', 'Lambda' ,'DeltaSource'
	# Y-Type:
	YTypeScanDicts = {'defocus scan to get HEW' : 0, 'no scan to get intensity' : 1}
	YTypeScan = 1


	def _DigestParameters(self):
		# digest parameters -------------------------------

		a = -(DefocusRange_mm/2) + DefocusOffset_mm
		b = (DefocusRange_mm/2) + DefocusOffset_mm
		DefocusList = np.linspace( a*1e-3, b* 1e-3, Defocus_N)


		NamingFigErr = {True: 'WithFigErr', False: 'NoFigErr'}
		NamingSource = 'DeltaSource=%0d' % SourceDelta
		NamingN = 'NSamples=%d' % N
		NamingDefocus = 'Range%0.1f,Delta%0.1f,N%0i' %(DefocusRange_mm, DefocusOffset_mm, Defocus_N)

		if YTypeScan==0:
			NamingList = [FileNameBase, NamingSource, NamingFigErr[UseFigureError], NamingN, NamingDefocus]
		elif  YTypeScan==1:
			NamingList = [FileNameBase, NamingN, NamingFigErr[UseFigureError], NamingSource]

		FileName = '_'.join(NamingList) +'.txt'
		FileOut = PathJoin(OutFolder,FileName)

		if VariableToReplace == 'Angle':
			XTypeScanList = AngleList
		elif VariableToReplace == 'Lambda':
			XTypeScanList = LambdaList
		elif VariableToReplace == 'DeltaSource':
			XTypeScanList = DeltaSourceList

#%% SCAN
	HewCollection = []
	SigmaCollection = []
	ECollection= []

	ZCollection = [] # it's a 2D matrix, appended column by column
	#===========================================================================
	for ScanValue in XTypeScanList:
		winsound.Beep(644,50)
		winsound.Beep(744,50)

		# LIVE SECTION #
		#.............................................
		''' || ============================================||'''
		CommandStr = '%s=ScanValue' % VariableToReplace
		exec(CommandStr)
		#     example: Angle = ScanValue
		''' || ============================================||'''

		#=============================================================================================================
		#=============================================================================================================
		#=============================================================================================================


		#=============================================================================================================
		#=============================================================================================================
		#=============================================================================================================
#		runfile('D:\\Topics\\Simulazioni FERMI2\\Theta Scan\\beamline_layout_dpi_h.py')
#		execfile('D:\\Topics\\Simulazioni FERMI2\\Theta Scan\\beamline_layout_dpi_h.py')
#		scriptContent = open('D:\\Topics\\Simulazioni FERMI2\\Theta Scan\\beamline_layout_dpi_h.py', 'r').read()

		scriptContent = open('beamline_layout_dpi_h.py', 'r').read()
		exec(scriptContent)

		exec('DetectorToUse =%s' % DetectorToUseName) #>>> example: DetectorToUse  = dpi_dh

		# Perturbazioni Sorgente
		#==========================================================================
		Beamline.Source.CoreOptics.SmallDisplacements.Rotation = SourceAngle
		Beamline.ComputeFields()

		# DEFOCUS SCAN, TO GET HEW VS DEFOCUS LIST
		#==========================================================================
		if YTypeScan == 0:

			DefocusList_mm = DefocusList * 1e3
			ResultList, HewList, SigmaList, More = wr.Foundation.FocusSweep(dpi_kbh, DefocusList,
																	DetectorSize = DetectorSize)
			# STORE DATA
			HewCollection.append(HewList)
			SigmaCollection.append(SigmaList)
			ZCollection.append(HewList)

		elif YTypeScan == 1: # NO SCAN, TO GET INTENSITY VS DETECTOR POSITION
			I = np.abs(DetectorToUse.ComputationData.Field)**2
			ZCollection.append(I)
			plot(I)

	#%% DATA SAVE/SAVEING
	#----- Helper code: Choosing the proper XAxis YAxis

	if SaveData == True:
		XAxis = XTypeScanList

		if YTypeScan == 0:
			YAxis = DefocusList
		elif YTypeScan == 1:
			YAxis = DetectorToUse.ComputationData.S

		print(FileOut)
		tl.SaveMatrix(FileOut, ZCollection,  YAxis, XAxis)
		t1 = time.localtime()

	#%% Plot della HEW
	if YTypeScan == 0:
		plt.figure(32)
		for i, HewList in enumerate(HewCollection):
			plot(DefocusList_mm, HewList *1e6,'.')
			plot(DefocusList_mm, 2*0.68* SigmaList * 1e6 * (1+i*1e-1),'x')
			plt.title('HEWs')
			plt.xlabel('defocus (mm)')
			plt.ylabel('Hew')
			plt.legend(['Hew', '0.68 * 2 Sigma'])
	#%% Plot of the Computed Field
	if 1==1:
		plt.figure(33)
		for Result in ResultList:
			plot(Result.S * 1e6, abs(Result.Field)**2)
			plt.title('Computed Fields @ detector')
			plt.xlabel('detector (um)')
			plt.ylabel('I (a.u.)')





		pass
