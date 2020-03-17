# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:41:49 2020

@author: Mike
"""

import LibWISEr.ToolLib as tl
from pathlib import Path
#================================================================
#  GetWiserPath
#================================================================
def GetWiserPath():
	'''
	Returns the parent folder containing LibWISER folder

	Architecture Notes
	----
	Architecture agnostic if using pathlib library.

	Created to handle the DATA folder containing the figure error files,
	and the cross platform path routing.

	'''
	WorkingFile = tl.__file__
	WorkingPath = Path(WorkingFile).parent.parent

	return WorkingPath

Main = GetWiserPath() # the WiserPath variable is sent to the namespace
Lib = Main / 'LibWISEr'
Metrology = Main / 'Metrology'

