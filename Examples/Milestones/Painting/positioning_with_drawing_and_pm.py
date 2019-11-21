# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 12:21:02 2018

@author: Mic
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:56:47 2017

@author: Mic

- Funziona
- la lascio che c'è da correggere in EllipticalMirror pTan e quindi VersosNorm
- la lascio che c'è ancora l'inifto bisticco tra XYCentre e XYCentre, XYF1 e XYF1

"""

import importlib
import numpy as np

import Rayman as rm
import Fundation
import Optics
import ToolLib as tl
import csv
import FermiSource as Fermi

importlib.reload(Fundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)
importlib.reload(Fermi)

from must import *
from Fundation import OpticalElement

print(__name__)
if __name__ == '__main__':

	tl.Debug.On = True
	
	# SOURCE
	#------------------------------------------------------------
	Lambda = 5e-9
	Waist0 =Fermi.Waist0E(Lambda)
	s_k = Optics.SourceGaussian(Lambda, Waist0)
	s_pd = Fundation.PositioningDirectives(
						ReferTo = 'absolute', 
						XYCentre = [0,0],
						Angle = np.deg2rad(45))
	s = OpticalElement(
						s_k, 
						PositioningDirectives = s_pd, 
						Name = 'source', IsSource = True)


	# PM1A (h)
	#==========================================================================
	pm1a_k = Optics.MirrorPlane(L=0.4, AngleGrazing = np.deg2rad(45) )
	pm1a_pd = Fundation.PositioningDirectives(
									ReferTo = 'upstream',
									PlaceWhat = 'centre',
									PlaceWhere = 'centre',
									Distance = 8)
	pm1a = OpticalElement(pm1a_k, 
							PositioningDirectives = pm1a_pd, 
							Name = 'pm1a')
	pm1a.ComputationSettings.Ignore = False          # Lo user decide di non simulare lo specchio ()

	
	
	# KB(h)
	#------------------------------------------------------------	
	f1 = 16
	f2 = 16
	GrazingAngle = 45
	
	kb_k = Optics.MirrorElliptic(f1 = f1, f2 = f2 , L= 1, Alpha = GrazingAngle)
	
	kb_pd = Fundation.PositioningDirectives(
						ReferTo = 'upstream',
						PlaceWhat = 'centre',
						PlaceWhere = 'centre',
						Distance = 8,
						GrazingAngle = np.deg2rad(45))
	
	kb = OpticalElement(
						kb_k, 
						PositioningDirectives = kb_pd, 
						Name = 'kb')	
	

	
	# detector (h)
	#------------------------------------------------------------
	d_k = Optics.Detector(
						L=1, 
						AngleGrazing = np.deg2rad(90) )
	d_pd = Fundation.PositioningDirectives(
						ReferTo = 'upstream',
						PlaceWhat = 'centre',
						PlaceWhere = 'downstream focus',
						Distance = 0)
	d = OpticalElement(
						d_k, 
						PositioningDirectives = d_pd, 
						Name = 'detector')

	# Assemblamento beamline
	#------------------------------------------------------------
	t = None
	t = Fundation.BeamlineElements()
	t.Append(s)
	t.Append(pm1a)
	t.Append(kb)
	t.Append(d)
	t.RefreshPositions()
	
	kb_k.PlanesInit()
	t.Paint(1)
	kb.CoreOptics.PlaneEntrance.Paint(1,Color = 'y')
	kb.CoreOptics.PlaneExit.Paint(1,Color = 'g')
	plt.axis('square')
