# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:27:03 2019

@author: Mike
"""

#def ReadLtp2File(Path):

#%%
import scipy as sp
import importlib
import LibWISEr.Main as wr
importlib.reload(wr)
#%%

Path = 'D:\\Topics\\Metrology\\FERMI\\PM2A'
PathFolder = 'D:\\Topics\\Metrology\\FERMI\\PM2A\\'
FileNameList  = ['PM2A_I02.HGT',
				 "PM2A_C06.SLP",
				 "PM2A_C07.SLP",
				 "PM2A_C08.SLP",
				 "PM2A_I06.SLP",
				 "PM2A_I07.SLP"]

#----Load Slopes
PathFull = Path + '\\' + FileNameList[4]
x,y,FileInfo = wr.tl.Metrology.ReadLtp2File(PathFull)


#----Integrate Slopes
h = [np.trapz(y[0:i], dx = FileInfo.XStep ) for i in range(1,len(y))]
h0 = wr.tl.Metrology.SlopeIntegrate(y,dx = FileInfo.XStep)
#h1 = np.cumsum(y) *  dx
#%%
wr.plot(x*1e3,h0 * 1e9)
wr.plt.title('height: ' + FileInfo.FileName)
wr.plt.ylabel('nm')
wr.plt.xlabel('mm')
wr.plt.grid()


#%% PRESTO HE
s = wr.tl.FileIO.ReadYFile("D:\\Topics\\Metrology\\FERMI\\HE_WISE_FigureError.txt", SkipLines =1)
XStep = 1e-3
x = np.linspace(1,len(s) * XStep, len(s))
h = s * 1e-3 # [m]
#h = wr.tl.Metrology.SlopeIntegrate(s,dx = XStep)

#plot(s* 1e9)
plt.xlabel('array index')

wr.plot(x*1e3,h*1e9)
wr.plt.title('height: ')
wr.plt.ylabel('nm')
wr.plt.xlabel('mm')
wr.plt.grid()


