# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:30:09 2016

@author: Mic
#todo: this example shall be rewritten

Paint an ellipse alone. Does not use the BeamlineElements class
"""


#%%
import importlib
import Rayman as rm
import Optics
import numpy as np
import ToolLib as tl
import importlib
importlib.reload(tl)
importlib.reload(rm)
importlib.reload(Optics)
import matplotlib.pyplot as plt
import matplotlib as mp
from matplotlib.pyplot import plot
from numpy import *
from EasyStart import *



from time import time


#% prova ellisse
N0 = 1e4
N1 = N0
L =1
GrazingAngle = np.rad2deg(3)

# Costruisco ellisse e definisco arco dello specchio
Ell = Optics.MirrorElliptic(a = 1, b=0.5 , L= 1, Alpha = GrazingAngle)

#_p1Lab = rm.RotPoly(Ell._p1Prop, Ell.XYOrigin, Ell.RotationAngle)
#

#% Costruisco un ellisse che dovrebbe essere equivalente
Ell2 = Optics.MirrorElliptic(f1 = 16, f2 = 8, Alpha = GrazingAngle, L = L)
print (Ell)
print (Ell2)


# Disegno Proper Frame reference
#------------------------------------------------------------------------------------------------
if 1==1 :
	EllUse = Ell2


	plt.figure(1)
	#plt.axis([-1, 1, -1, 1])
	plt.grid(True)

	# specchio
#	Mir_x = linspace(EllUse._XYProp_Start[0], EllUse._XYProp_End[0], 1e2)
#	Mir_y = EllUse._EvalMirrorYProp(Mir_xProp)
	
	Mir_x, Mir_y = EllUse.GetXY_IdealMirror(200)
	
	Mir_x_all, Mir_y_all =  EllUse.GetXY_CompleteEllipse(200,'lab')
	plot(Mir_x_all, Mir_y_all,'r-.', linewidth= 0.5)
	plot(Mir_x, Mir_y,'r', linewidth= 2)
	#Mir_xy = np.column_stack((Mir_x, Mir_y))
	

	# fuochi
	plot(EllUse.XYF1[0], EllUse.XYF1[1],'ro')
	plot(EllUse.XYF2[0], EllUse.XYF2[1],'ro')
	# centro specchio
	plot(EllUse.XYCentre[0],EllUse.XYCentre[1],'bo')
	
	# braccio f1
	xx = linspace(EllUse.XYF1[0], EllUse.XYCentre[0],100)
	yy = polyval(EllUse.p1, xx)
	plot(xx,yy,'-r')
	# braccio f2
	xx = linspace(EllUse.XYCentre[0],EllUse._XYProp_F2[0],100)
	yy = polyval(EllUse.p2, xx)
	plot(xx,yy,'-g')
	# tangente
	#xx = arange(-0.5,1.5,0.01)
	#yy = polyval(EllUse.pTan,xx)
	#plot(xx,yy,'-y')

#if 1==1 :
#	EllUse = Ell
#
#
#	plt.figure(1)
#	plt.axis([-1, 1, -1, 1])
#	plt.grid(True)
#
#	# specchio
#	Mir_x__ , Mir_y__ = EllUse.GetXY_CompleteEllipse(1e3, ReferenceFrame = 'lab')
#	NewOrigin = [1,0]
#	Angle = pi/5
#
#
#	#Mir_x, Mir_y = rm.CartChange(Mir_x__, Mir_y__, NewOrigin, Angle)
##	EllUse._Transformation_Add(pi/4, - EllUse._XYProp_F1, EllUse._XYProp_F1, ClearAll = True)
#
#
#	#Mir_x, Mir_y = EllUse._Transformation_XYPropToXYLab(Mir_x__, Mir_y__)
#	EllUse.SetXYAngle_MirrorCentre([0,0],0)
#	Mir_x, Mir_y = EllUse.GetXY_CompleteEllipse(1000)
#	#Mir_xy = np.column_stack((Mir_x, Mir_y))
#	plot(Mir_x__,Mir_y__,'-r', linewidth= 1)
#	plot(Mir_x,Mir_y,'-g', linewidth= 1)
#	# Centro specchio
#	plt.axis('square')
#	plt.xlim([-1.5,1.5])
#	plt.ylim([-1.5,1.5])

