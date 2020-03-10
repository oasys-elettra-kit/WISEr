# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:41:49 2020

@author: Mike
"""

import LibWISEr.ToolLib as tl
from pathlib import Path as MakePath
#================================================================
#  GetWiserPath
#================================================================
def GetWiserPath():
	'''
	Returns the parent folder containing LibWISEr folder

	'''
	WorkingFile = MakePath(tl.__file__)
	return WorkingFile.parent

#================================================================
#  GetRepositoryPath
#================================================================
def GetRepositoryPath():
	WorkingFile = MakePath(tl.__file__)
	return WorkingFile.parent.parent

Main = GetRepositoryPath() # the WiserPath variable is sent to the namespace
LibWiser = GetWiserPath()
Metrology =  tl.MakePath(Main, 'Metrology')
MetrologyFermi =  tl.MakePath(Main, 'Metrology', 'FERMI')
