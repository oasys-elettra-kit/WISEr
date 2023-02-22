# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 12:11:14 2022

@author: Mike
"""

#%%
from LibWiser.EasyGo import MakePath as _MakePath
from enum import Enum as _Enum

PathMetrology = _MakePath('D:\Topics\WISER\Repository GIT\Metrology\FERMI\Best')
PathLayout = _MakePath('D:\Topics\WISEr\Repository GIT\Examples Layout Files')

class Enums(_Enum):
	LDM = 'ldm'
	MAG = 'mag'
	
LDM = Enums.LDM
MAG = Enums.MAG	


class EnumLayout(_Enum):
	LDM = PathLayout / 'layout_ldm_vh_GOOD.py'
	MAG = PathLayout / 'layout_mag_vh.py'

class EnumFigErrors(_Enum):
	LDM_KBV = PathMetrology / 'ldm_kbv_(mm,nm).txt'
	LDM_KBH = PathMetrology / 'ldm_kbh_(mm,nm).txt'
	DPI_KBV = PathMetrology / 'dpi_kbv_(mm,nm).txt'
	DPI_KBH = PathMetrology / 'dpi_kbh_(mm,nm).txt'	
	
def GetLayoutFile(MyEnum : Enums):
	return	MakePath(MyEnum.value)




