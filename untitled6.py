# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:27:03 2019

@author: Mike
"""

#def ReadLtp2File(Path):

#%%
import importlib
import LibWISEr.Main as wr
importlib.reload(wr)

Path = 'D:\\Topics\\Metrology\\FERMI\\PM2A\\PM2A_C08.SLP'

x,y,FileInfo = wr.tl.Metrology.ReadLtp2File(Path)
#%%
#=============================================================#
# FUN ReadLtp2File
#=============================================================#
def ReadLtp2File(Path : str):
	'''
	Read an (old) Ltp2 file and returns
	- x,y data array in S.I units
	- a data structure containing various info on the file.

	Return
	=====
	x : x data. Position along the mirror.

	y : y data. Either height or slopes. See FileInfo.YUnit

	FileInfo: data structure, containing
		FileName XUnit YUnit XScale YScale XStep
	'''
	FileInfo = namedtuple('FileInfo', 'FileName XUnit YUnit XScale YScale XStep')
	with open(Path, 'r') as f:
	    Lines = f.readlines()


	I_FILENAME = 6
	I_STEP_SIZE = 10
	I_X_UNIT = 11
	I_Y_UNIT = 12
	I_DATA_START = 40

	# Get File Name
	FileInfo.FileName = Lines[I_STEP_SIZE].strip()



	#Get X,Y Unit
	FileInfo.XUnit = (Lines[I_X_UNIT].strip()).split(':')[1]
	FileInfo.YUnit = (Lines[I_Y_UNIT].strip()).split(':')[1]

	#Get X,Y Scale
	FileInfo.XScale = Units.UnitString2UnitScale(FileInfo.XUnit)
	FileInfo.YScale = Units.UnitString2UnitScale(FileInfo.YUnit)

	# Get XStep
	FileInfo.XStep = (Lines[I_X_UNIT].strip()).split(':')[1] * FileInfo.XScale

	#Get X,Y Arrays
	N = len(Lines) -  I_DATA_START
	x = np.zeros([N])
	y = np.zeros([N])
	for (iLine, Line) in enumerate(Lines, I_DATA_START):
		Tokens = Line.split('\t')
		x[iLine] = float(Tokens[0])
		y[iLine] = float(Tokens[1])

	x = x * FileInfo.XScale
	y = y * FileInfo.YScale

	return (x,y, FileInfo)