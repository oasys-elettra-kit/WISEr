# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:51:20 2020

@author: Mike
"""

import LibWISEr.WiserImport as lw
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
					 ParameterRangeToScan = None, #array like
					 Detector : lw.Foundation.OpticalElement,
					 ScanType : ScanType,
					 OESubsets : list(lw.Foundation.OpticalElement),
					 OEUseFigureError : list(bool)):

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


		pass
