# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 14:24:04 2016

@author: Mic
"""

import numpy as np
from importlib import reload
from numpy import  cos, sin, tan, arctan, arctan2, pi, array, arange, size, polyval, polyfit, angle, dot, exp, arcsin, arccos, real, imag, angle, copy
from numpy.lib.scimath import sqrt
from numpy.linalg import norm
import matplotlib.pyplot as plt
import matplotlib.pyplot
plot =  matplotlib.pyplot.plot
from matplotlib.ticker import FormatStrFormatter
import time
from scipy.interpolate import interp1d

from matplotlib.ticker import MultipleLocator

from os.path import join as PathJoin




#def GridMinor()
#ax2.yaxis.set_minor_locator(minorLocator)

def execfile(filepath):
		scriptContent = open(filepath, 'r').read()
		exec(scriptContent)

def DataWrite (FileName, Data, Format = '%0.2f'):
	#here is your data, in two numpy arrays
	datafile_id = open(FileName, 'w+')
	data = np.array(Data)
	data = data.T
	#here you transpose your data, so to have it in two columns

	fmt = []
	for i in range(0,len(Data)):
		fmt.append(Format)
	np.savetxt(datafile_id, data, fmt)
	#here the ascii file is populated.
	datafile_id.close()

#========================================================
#	FUN: ReadYFile
#========================================================
def ReadYFile(Path, StepX = None , SkipLines = 2):
	'''
	Behavior:
	-----
	Reads the y data formatted as a column.

	If StepX is not None, then it creates a x vector using the command

	*x = np.linspace(1,N*StepX, N)*

	where N is len(y)



	'''
	with open(Path) as file:
		Lines = file.readlines()[SkipLines :]
	N = len(Lines)
	y = np.zeros(N)
	if StepX is not None:
		x = np.linspace(1,N*StepX, N)
	for (iLine, Line) in enumerate(Lines):
		Line = Line.strip()
		if Line != '':
			Tokens = Line.split('\t')
			y[iLine] = float(Tokens[1])

	if StepX is not None:
		return x,y
	else:
		return y
#========================================================
#	FUN: ReadXYFile
#========================================================
def ReadXYFile(Path, Delimiter = '\t', SkipLines = 2):
	'''
	Behavior:
	-----
	Reads the x,y data formatted as a column
	'''
	with open(Path) as file:
		Lines = file.readlines()[SkipLines :]
	N = len(Lines)
	x = np.zeros(N)
	y = np.zeros(N)
	for (iLine, Line) in enumerate(Lines):
		Line = Line.strip()
		if Line != '':
			Tokens = Line.split('\t')
			x[iLine] = float(Tokens[0])
			y[iLine] = float(Tokens[1])

	return x,y

