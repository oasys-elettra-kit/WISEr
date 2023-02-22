# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 15:39:06 2022

@author: Mike
"""

#%%
from LibWiser.EasyGo import *
import h5py
from pathlib import Path
PathMain = Path(u'D:\Topics\Simulazioni WISER\All Beamlines\Output1 (WISEr)')
Names = ['SourceScan_LAYOUT_LDM_VH_GOOD_01__OrientationLetter=H.h5']


#for i, File in enumerate(FileList):
#	h5 = h5py.File(File)
	

f = h5py.File(PathMain / Names[0])
Lambda = f.attrs['Lambda']
Lambda_nm = Lambda*1e9
GroupName = 'TaskSourcePositionScan'
DeltaSource = f[GroupName]['SourceShift'].value
Hew = f[GroupName]['AsIsHew'].value

plot(DeltaSource, Hew*1e6,'o', label = '%0.1f nm' % Lambda_nm)
plt.xlabel('Source shift (m)')
plt.ylabel('Spot size - HEW (um)')

plt.grid()
plt.legend()
