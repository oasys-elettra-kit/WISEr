# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 14:24:04 2016

@author: Mic
"""
from sys import platform
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
from pathlib import Path as MakePath
from LibWiser.Scrubs import DataContainer, ListAttr, ListAttrRecursive


from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm




#ax2.yaxis.set_minor_locator(minorLocator)

#çTODO To improve (it is stupid to re-define the function each time
# accordingly to the os. Use conditional definition of the function instead)
def Beep(a,b):
	if platform =='linux' or platform == 'linux2':
		pass
	elif platform == 'win32':
		from winsound import Beep as WinBeep
		WinBeep(a,b)
	elif platform == 'darwin':
		pass
	return None

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

#========================================================
#	FUN: frozen
#========================================================
def frozen(set):
    "Raise an error when trying to set an undeclared name."
    def set_attr(self,name,value):
        if hasattr(self,name):
            set(self,name,value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr
#========================================================
#	class: Frozen
#========================================================
class Frozen(object):
    """Subclasses of Frozen are frozen, i.e. it is impossibile to add
     new attributes to them and their instances."""
    __setattr__=frozen(object.__setattr__)
    class __metaclass__(type):
        __setattr__=frozen(type.__setattr__)

