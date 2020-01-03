# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:41:49 2020

@author: Mike
"""

import LibWISEr.ToolLib as tl
#================================================================
#  GetWiserPath
#================================================================
def GetWiserPath():
	'''
	Returns the parent folder containing LibWISER fodler

	Architecture Notes
	----
	To be tested on unix.
	Check if better solutions are possible.
	Created to handle the DATA folder containing the figure error files,
	and the cross platform path routing.

	'''
	WorkingFile = tl.__file__
	WorkingFileItems  = tl.PathSplit(WorkingFile)
#	 Workaround, for handling Windows Units Letters
#	if WorkingFileItems[0][1] == ':':
#		WorkingFileItems[0] = WorkingFileItems[0] + os.path.sep

	WorkingPath =  tl.PathJoin(*WorkingFileItems[0:-2])
	return WorkingPath

Main = GetWiserPath() # the WiserPath variable is sent to the namespace
Lib = tl.os.path.join(Main, 'LibWISEr')
Metrology =  tl.os.path.join(Main, 'Metrology')
