# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:12:18 2019

@author: Mike

Class that provide a simplified access to Eng formatting.

.
GetEngLetter(0.00015) =>'u'
GetEngArgument(1e-6) #=>1
GetEngExponent(0.00015) =>-6





GetEng

GetEngNumber(0.00015) => '150.0e-06'
GetEngNumber(0.15) => '150.0e-03'
GetEngNumber(0.15,0) => '150e-03'
GetEngLetter(0.00015) =>'u'


GetEngAxis
"""


import engineering_notation
from engineering_notation import EngNumber, EngUnit
import numpy as np
import LibWiser.Scrubs as Scrubs


from matplotlib.ticker import EngFormatter
EngFormat = EngFormatter()


PrefixLookup = {
    'y': -24,
    'z': -21,
    'a': -18,
    'f': -15,
    'p': -12,
    'n': -9,
    'u': -6,
	'μ' : -6,
    'm': -3,
    '': 0,
    'k': 3,
    'M': 6,
    'G': 9,
    'T': 12
}

# this class is kept for backcompatibility: e.g. used in  ReadLtp2File
class Units:
	SiPrefixes = PrefixLookup
	@staticmethod
	def UnitString2UnitScale(UnitString : str):
		''' Scans a unit string (e.g. mm, um, km) and returns the corresponding
			scaling value: e.g (1e-3, 1e-6, 1e3).

			Behavior:
			----
			It trims the white spaces, then takes the first character as SI
			prefix.

			Then a dictionary is used to match the prefix to the multiplier.

			By M Man
		'''
		if UnitString is not None:
			return  Units.SiPrefixes[UnitString.strip()[0]]
		else:
			return '' 
	

def SmartFormatter(x, VariableInfo = {'unit' : '', 'prefix':True,'digits':6}):
	'''
	Attempts a smart formatting of x.
	It returns
	- EngNumber(x) if x is a float, i.e. 0.00015 => 150um
	- A smart formatting if x is decorated with VariableInfo object [not deeple implemented yet]
	- str(x) in any other case
	:-)
	'''

	try:
		UsePrefix = VariableInfo['prefix']
	except:
		UsePrefix = True
		
	tp = type(x)
	if (tp is float) or (tp is int) or (tp is np.float64):
		
		if UsePrefix:
			try:
				return GetEngNumberSI(x) + VariableInfo['unit']
			except:
				raise WiserException('GetEngNumber failed, with number')
		else:
			return GetEngNumber(x, VariableInfo['digits'])
	else:
		return str(x)
	
	
	
def GetEngFormat(x):
	return str(EngFormat(x))


def GetEngLetter(x):
	'''
	GetEngLetter(0.00015) =>'u'
	GetEngLetter(1e-24) => 'y'
	
	'''

	_ = EngFormat(x).split(' ')		
	
	if len(_) == 2:
		return _[1]
	elif len(_) == 1:
		return ''
	else:
		raise Exception('Unexpected case while converting the unit. Check the code and report to the mantainer.')
		
def GetEngArgument(x):
	'''
	Return the Argument of Eng formatting.
	
	Example:
	GetEngArgument(1e-6) #=>1
	GetEngArgument(1e-24) #=>1
	GetEngArgument(1e-26) #=>0.01
	'''
	_ = EngFormat(x).split(' ')		
	return _[0]

			

			
def GetEngExponent(x):
	'''
	Return the exponent corresponding to the SI/Eng notation returned by GetEngLetter.
	
	GetEngExponent(0.00015) =>-6
	GetEngExponent(1e-24) => -24
	
	Note:
		Ideally, the function would like to return the exponent, as multiple of 1000.
		Since a lookuptable is used, this works only for values between 1e-24 and 1e12
	
	'''
	
	EngLetter = GetEngLetter(x)
	
	return PrefixLookup[EngLetter]



def GetEngInfo(x):
	'''
	Return all the info that are necessary for SI-ENG formatting.
	
	Example
	>>>GetEngInfo(23.234e-22)
	>> {'Exponent': -21,
	  'Argument': '2.3234',
	   'Prefix': 'z',
	    'Formatting': '2.3234 z'}
	
	'''
	if x is None:
		raise Warning("[GetSIInfoD] input variable x is None. Array or float expected.")
		return None
	
	if 	Scrubs.IsArrayLike(x):
		try:
			# I used to pick up the mean, but ultimately I understood
			# that probably this 
			XValue = abs(np.max(x))
		except:
			raise 
	else:
		XValue = x
		try:
			_ = XValue +1
		except:
			raise Exception ("Error: the argument x is not float-like.")
		
	
	a = GetEngExponent(XValue) # => 1e-9
	b = GetEngArgument(XValue)
	c = GetEngLetter(XValue) #=> n
	d = GetEngFormat(XValue) #=> 100e-9

	
#	Ans = {'EngExp' : a,
#		 'EngIExp' : aa, 
#		 'EngCoeff' : b, 
#		 'SIPrefix' : c , 
#		 'EngFormatting' :d,
#		 'SIFormatting' :e}
	Ans = {'Exponent' : a,
	 'Argument' : b, 
	 'Prefix' : c, 
	 'Formatting' :d}
	return Ans

def GetEngAxis(x):
	'''
	Assumed that x is either the x or y axis of an x,y plot, the function unterstand
	which SI prefix better fits the range of x, multiploes x accordingly, then return
	the scaled x and the SI prefix.
	
	e.g.
	import numpy
	x = np.arange(10e-6, 43.5e-6, 1e-7)
	(NewX, Prefix, Exponent) = GetEngAxis(x) => ([10...43.5], 'u', '-6')
	
	
	
	Return
	--------
	x*alpha : array like
	
		rescaled x
	
	SI Prefix : string
		the SI prefix
	'''
	A = GetEngInfo(x)
	
	try:
		return (x *10**(-A['Exponent']), A['Prefix'], A['Exponent'])
	except:
		raise Exception("Error in GetAxisSI")
		print(x)

GetAxisSI = GetEngAxis