# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:12:18 2019

@author: Mike
"""
#import enum
#from enum import Enum, Flag




#class UnitType(
#					 UnitType
#					 UnitStr : str,
#					 UnitMath : str = None,
#					 SiPrefixPreferred  : str = None  )

import engineering_notation
from engineering_notation import EngNumber, EngUnit
import numpy as np

def SmartFormatter(x):
	'''
	Attempts a smart formatting of x.
	It returns
	- EngNumber(x) if x is a float
	- A smart formatting if x is decorated with UnitInfo object
	- str(x) in any other case
	'''

	if x is float:
		return EngNumber(x)
	else:
		return str(x)


def GetSiUnitScale(x):
	'''
	Get the most convenient SI unit for representing x.
	e.g.
		x=1e-7 => n
		x=1e-6 => u
		x=1e-5 => u
		x=1e-4 => u

   if x is an array, it uses the mean value
	'''

	if type(x) is np.ndarray:
		x = np.mean(x)

	if (type(x) is float) or (type(x) is np.float64):
		StrUnit = EngUnit(x).eng_num.to_pn()
		tok = StrUnit[-1]
		NewStrUnit = ''
		try:
			a = int(tok)
			NewStrUnit = ''
		except:
			NewStrUnit = tok
		return NewStrUnit
	else:
		return ''

class Units:
	SiPrefixes = { 'a':1e-18, 'f':1e-15, 'p':1e-12, 'n' : 1e-9 , 'u' : 1e-6, 'm' : 1e-3, '' : 1e0, 'k' : 1e3, 'M' :1e6, 'G' : 1e9 }
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

		return Units.SiPrefixes[UnitString.strip()[0]]

#class (Unit ='',  # e.g. 'm'
#	   Name = '',   # e.g. 'FocalShift' if empty set equal to label.
#	   Label = '',  # e.g. '\Delta f' if empty set equal to Name
#	   Multiplier = 1, # 1 if data are in SI. 1e-3 if data are in mm.
#	    PlotMultiplier = 1): # 1e-3 if data shall be plot in mm
#

# Code below copied from
#https://stackoverflow.com/questions/10969759/python-library-to-convert-between-si-unit-prefixes
# credit if used
#	def __init__(self):
#	    global si;
#	    si = {
#	          -18 : {'multiplier' : 10 ** 18, 'prefix' : 'a'},
#	          -17 : {'multiplier' : 10 ** 18, 'prefix' : 'a'},
#	          -16 : {'multiplier' : 10 ** 18, 'prefix' : 'a'},
#	          -15 : {'multiplier' : 10 ** 15, 'prefix' : 'f'},
#	          -14 : {'multiplier' : 10 ** 15, 'prefix' : 'f'},
#	          -13 : {'multiplier' : 10 ** 15, 'prefix' : 'f'},
#	          -12 : {'multiplier' : 10 ** 12, 'prefix' : 'p'},
#	          -11 : {'multiplier' : 10 ** 12, 'prefix' : 'p'},
#	          -10 : {'multiplier' : 10 ** 12, 'prefix' : 'p'},
#	          -9 : {'multiplier' : 10 ** 9, 'prefix' : 'n'},
#	          -8 : {'multiplier' : 10 ** 9, 'prefix' : 'n'},
#	          -7 : {'multiplier' : 10 ** 9, 'prefix' : 'n'},
#	          -6 : {'multiplier' : 10 ** 6, 'prefix' : 'u'},
#	          -5 : {'multiplier' : 10 ** 6, 'prefix' : 'u'},
#	          -4 : {'multiplier' : 10 ** 6, 'prefix' : 'u'},
#	          -3 : {'multiplier' : 10 ** 3, 'prefix' : 'm'},
#	          -2 : {'multiplier' : 10 ** 2, 'prefix' : 'c'},
#	          -1 : {'multiplier' : 10 ** 1, 'prefix' : 'd'},
#	           0 : {'multiplier' : 1, 'prefix' : ''},
#	           1 : {'multiplier' : 10 ** 1, 'prefix' : 'da'},
#	           2 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
#	           3 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
#	           4 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
#	           5 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
#	           6 : {'multiplier' : 10 ** 6, 'prefix' : 'M'},
#	           7 : {'multiplier' : 10 ** 6, 'prefix' : 'M'},
#	           8 : {'multiplier' : 10 ** 6, 'prefix' : 'M'},
#	           9 : {'multiplier' : 10 ** 9, 'prefix' : 'G'},
#	          10 : {'multiplier' : 10 ** 9, 'prefix' : 'G'},
#	          11 : {'multiplier' : 10 ** 9, 'prefix' : 'G'},
#	          12 : {'multiplier' : 10 ** 12, 'prefix' : 'T'},
#	          13 : {'multiplier' : 10 ** 12, 'prefix' : 'T'},
#	          14 : {'multiplier' : 10 ** 12, 'prefix' : 'T'},
#	          15 : {'multiplier' : 10 ** 15, 'prefix' : 'P'},
#	          16 : {'multiplier' : 10 ** 15, 'prefix' : 'P'},
#	          17 : {'multiplier' : 10 ** 15, 'prefix' : 'P'},
#	          18 : {'multiplier' : 10 ** 18, 'prefix' : 'E'},
#	          }
#
#	def convert(self, number):
#	    # Checking if its negative or positive
#	    if number < 0:
#	        negative = True;
#	    else:
#	        negative = False;
#
#	    # if its negative converting to positive (math.log()....)
#	    if negative:
#	        number = number - (number*2);
#
#	    # Taking the exponent
#	    exponent = int(math.log10(number));
#
#	    # Checking if it was negative converting it back to negative
#	    if negative:
#	        number = number - (number*2);
#
#	    # If the exponent is smaler than 0 dividing the exponent with -1
#	    if exponent < 0:
#	        exponent = exponent-1;
#	        return [number * si[exponent]['multiplier'], si[exponent]['prefix']];
#	    # If the exponent bigger than 0 just return it
#	    elif exponent > 0:
#	        return [number / si[exponent]['multiplier'], si[exponent]['prefix']];
#	    # If the exponent is 0 than return only the value
#	    elif exponent == 0:
#	        return [number, ''];

