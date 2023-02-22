# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:27:03 2019

@author: Mike
"""

#def ReadLtp2File(Path):

#%%
import scipy as sp
import importlib
import LibWiser.Main as wr
from LibWiser.must import *
import LibWiser.WiserImport as lw
from pathlib import Path
import scipy
importlib.reload(wr)


PathMetrology = MakePath('D:\Topics\WISER\Repository GIT\Metrology\FERMI\Best')
from enum import Enum
class FigErrorEnum(Enum):
	LDM_KBV = PathMetrology / 'ldm_kbv_(mm,nm).txt'
	LDM_KBH = PathMetrology / 'ldm_kbh_(mm,nm).txt'
	DPI_KBV = PathMetrology / 'dpi_kbv_(mm,nm).txt'
	DPI_KBH = PathMetrology / 'dpi_kbh_(mm,nm).txt'	


#%% KAOS2 LDM KBH

#reload(lw)
SelectedTag  = FigErrorEnum.LDM_KBH

PathFull = SelectedTag.value  

xb, h0b  = lw.tl.FileIO.ReadXYFile(PathFull, SkipLines  = 0 )
xb_UnitFactor = 1 # mm
h0b_UnitFactor = 1 # nm

# Plot (mm,nm)
plt.plot(xb,
		 (h0b - min(h0b)),
		 '-', 
		 label = SelectedTag.name)
plt.ylabel('Height (nm)')
plt.xlabel('mm')
plt.grid('on')
plt.legend()
plt.title('figure error')
#plt.legend(loc ='lower left')


