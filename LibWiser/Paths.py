# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:41:49 2020

@author: Mike
"""

import LibWiser.__init__ as Init
from pathlib import Path as MakePath
#================================================================
#  GetWiserPath
#================================================================
def GetWiserPath():
	'''
	Returns the parent folder containing LibWiser folder

	'''
	WorkingFile = MakePath(Init.__file__)
	return WorkingFile.parent

#================================================================
#  GetRepositoryPath
#================================================================
def GetRepositoryPath():
	WorkingFile = MakePath(Init.__file__)
	return WorkingFile.parent.parent

def GetRepositoryParentPath():
	WorkingFile = MakePath(Init.__file__)
	return WorkingFile.parent.parent.parent


Tmp = MakePath(GetRepositoryParentPath(), 'WISEr_Tmp')
Main = GetRepositoryPath() # the WiserPath variable is sent to the namespace
LibWiser = GetWiserPath()
Metrology =  MakePath(Main, 'Metrology')
MetrologyFermi =  MakePath(Main, 'Metrology', 'FERMI')

