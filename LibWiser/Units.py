# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:12:18 2019

@author: Mike

Class that provide a simplified access to Eng and SI formatting.

With Eng formatting we denote the fact that the numbers are expressed as multiple of 1000

1, 1e3, 0.1e3, 1e6, etc.

With SI formatting we denote the use of SI prefixes
1, 1 k , 0.1k, 1M, etc.


The logic is contained in GetEngInfo
The interface function (To oasys-wiser) is GetAxisSI

"""


import engineering_notation
from engineering_notation import EngNumber, EngUnit
import numpy as np
import LibWiser.Scrubs as Scrubs
from LibWiser.Scrubs import WiserException


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

PrefixLookupI = {
	-24: "y",
	-21: "z",
	-18: "a",
	-15: "f",
	-12: "p",
	-9: "n",
	-6: "u",
	-3: "m",
	 0: "",
	3: "k",
	6: "M",
	9: "G",
	12: "T",
	15: "P",
	18: "E",
	21: "Z",
	24: "Y"
	}



def _PickMeaningfulValue(x):
	'''
	Helper function to call in GetEngInfo.
	If x is an array, it selects the most meaningful value (which
	is determined as the absolute maximum of the array).
		
	'''
	
	if x is None:
		raise Warning("[_PickMeaningfulValue] input variable x is None. Array or float expected.")
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
	return XValue
	
def GetEngInfo(x, places = None):
	"""
	Formats a number in engineering notation, appending a letter
	representing the power of 1000 of the original number.
	Some examples:

	>>> format_eng(0)	   # for self.places = 0
	'0'

	>>> format_eng(1000000) # for self.places = 1
	'1.0 M'

	>>> format_eng("-1e-6") # for self.places = 2
	u'-1.00 \N{GREEK SMALL LETTER MU}'

	`num` may be a numeric value or a string that can be converted
	to a numeric value with ``float(num)``.
	"""
	MAX_ENG_PREFIX = 12
	MIN_ENG_PREFIX = -24
	import math, six
	num = _PickMeaningfulValue(x) 
	if isinstance(num, six.string_types):
		warnings.warn(
			"Passing a string as *num* argument is deprecated since"
			"Matplotlib 2.1, and is expected to be removed in 2.3.",
			mplDeprecation)

	dnum = float(num)
	sign = 1
	fmt = "g" if places is None else ".{:d}f".format(places)

	if dnum < 0:
		sign = -1
		dnum = -dnum

	if dnum != 0:
		pow10 = int(math.floor(math.log10(dnum) / 3) * 3)
	else:
		pow10 = 0
		# Force dnum to zero, to avoid inconsistencies like
		# format_eng(-0) = "0" and format_eng(0.0) = "0"
		# but format_eng(-0.0) = "-0.0"
		dnum = 0.0

	pow10_all = pow10
	pow10 = np.clip(pow10, MIN_ENG_PREFIX, MAX_ENG_PREFIX)
	mant = sign * dnum / (10.0 ** pow10)
	mant_all = sign * dnum / (10.0 ** pow10_all)
	
	
	# Taking care of the cases like 999.9..., which
	# may be rounded to 1000 instead of 1 k.  Beware
	# of the corner case of values that are beyond
	# the range of SI prefixes (i.e. > 'Y').
	_fmant = float("{mant:{fmt}}".format(mant=mant, fmt=fmt))
	if _fmant >= 1000 and pow10 != max(self.ENG_PREFIXES):
		mant /= 1000
		pow10 += 3
		
	_fmant = float("{mant:{fmt}}".format(mant=mant_all, fmt=fmt))
	if _fmant >= 1000:
		mant_all /= 1000
		pow10_all += 3

	prefix = PrefixLookupI[int(pow10)]

#	formatted = "{mant:{fmt}}{sep}{prefix}".format(
#		mant=mant, sep=self.sep, prefix=prefix, fmt=fmt)

	Output = dict()
	Output['SIMant'] = mant
	Output['SIPow10'] = int(pow10)
	Output['SIPrefix'] = prefix
	Output['EngMant'] = mant_all
	Output['EngPow10'] = int(pow10_all)	  

	return Output

def GetFormattedSI(x, places = None):
	'''
	Returns a number formatted in ENG notation With SI prefixes
	0.0000001=> "1 u"
	'''
	fmt = "g" if places is None else ".{:d}f".format(places)
	EngInfo = GetEngInfo(x)
	mant = EngInfo['SIMant']
	prefix = EngInfo['SIPrefix']
	sep = ' '
	
	formatted = "{mant:{fmt}}{sep}{prefix}".format(
		mant=mant, sep=sep, prefix=prefix, fmt=fmt)
	return formatted

def GetFormattedEng(x, places = None):
	'''
	Returns a number formatted in ENG notation With SI prefixes
	0.0000001=> "1e-6"
	
	
	'''
	fmt = "g" if places is None else ".{:d}f".format(places)
	EngInfo = GetEngInfo(x)
	mant = EngInfo['EngMant']
	pow10  = EngInfo['EngPow10']
	sep = 'e'
	
	formatted = "{mant:{fmt}}{sep}{pow10}".format(
		mant=mant, sep=sep, pow10=pow10, fmt=fmt)
	return formatted



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
				return GetFormattedSI(x) + VariableInfo['unit']
			except:
				raise WiserException('GetEngNumber failed, with number')
		else:
			return GetFormattedEng(x, VariableInfo['digits'])
	else:
		return str(x)
	

def GetAxisSI(x):
	'''
	This function provides a rescaled axis + a SI unit to use in plot.
	
	This is the ONLY access point to Units.py from within OASYS.
	
	Do not change the output format (Axis, Prefix)
	'''
	# attempt to force a list to a numpy array
	if type(x) is list:
		try:
			x  =np.array(x)
		except:
			raise WiserException('Failed when converting X to array', 
						By = "GetEngAxis")
			
	A = GetEngInfo(x)
	Axis = x *10**(-A['SIPow10'])
	Prefix =A['SIPrefix']
	Pow10 = A['SIPow10']
	
	return (Axis, Prefix)


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
	
