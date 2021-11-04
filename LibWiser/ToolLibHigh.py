# -*- coding: utf-8 -*-
"""
Hi-level Tool Library.

It uses the type and functions created elsewhere in LibWiser and has not a clear 
distinction of types.


Created on Tue Oct 19 11:53:02 2021

@author: Mike
"""

from LibWiser.EasyGo import *
from LibWiser.Optics import OpticsNumerical
#from LibWiser.Foundation import OpticalElement
#%% Enums

class SamplingMethods:
	MAXIMUM_GRAZING_RAY = 1
	MAXIMUM_SCATTERING = 2

#%% Angle Handling Functions




#==========================================
# FUN: GetCentredViewAngle 
#==========================================
def GetCentredViewAngle (Optics0 : OpticsNumerical, Optics1 : OpticsNumerical) -> float:
	'''
	It returns the angle subtended by the Optics1 from the central point of Optics0.
	
	'''
	X1, Y1 = Optics0.GetXY(3)
	X2, Y2 = Optics1.GetXY(2)
	
	C0 = [X1[1], Y1[1]]
	
	A1 = [X2[0], Y2[0]]
	B1 = [X2[1], Y2[1]]

	Angle = ToolLib.AngleBetweenPoints(C0, A1, B1 )
	
	return Angle
	


#==========================================
# FUN: GetMaximumViewAngle 
#==========================================
def GetMaximumViewAngle12(Optics1 : OpticsNumerical, Optics2 : OpticsNumerical) -> float:
	'''
	Two-Body function.
	It extracts the Maximum View Angle at which oe0 "sees" oe1.
	MaximumViewAngle = <maximum angle subtended by oe1 from oe0> - <angle of RealRayOut>
	
	It works only the the included CoreOptics element are of type: OpticsNumerical.
	
	'''
	try:
		X1, Y1 = Optics1.GetXY(3)
		X2, Y2 = Optics2.GetXY(2)
	except:
		raise WiserException ("Error in Getting the View Angle. Maybe the optical element is not numerical and does not have a defined transverse extension.")
	
	A = [X2[0], Y2[0]]
	B = [X2[1], Y2[1]]

	AngleList = [ToolLib.AngleBetweenPoints([X1[i], Y1[i]], A, B ) for i in [0,1,2]]
	Angle = max(AngleList)
	
	return Angle
	

def GetABC(OpticalElement : OpticalElement):
	
	if type(OpticalElement) == LibWiser.Foundation.OpticalElement:
		Optics1 = OpticalElement.CoreOptics
	else:
		Optics1  = OpticalElement
		
	X, Y = Optics1.GetXY(3)
	
	A = [X[0], Y[0] ]
	B = [X[2], Y[2] ]
	C = [X[1], Y[1] ]
	A = np.array(A)
	B = np.array(B)
	C = np.array(C)
	return A,B,C

#==========================================
# FUN: GetMaximumViewAngle
#==========================================
def GetMaximumGrazingRayCentred(Optics1 : OpticsNumerical, Optics2 : OpticsNumerical) -> float:
	'''
	Two-Body function.
	
	Given two optical elements, with central point C1 ant terminal points A2,B2
	- computes the possible combination of rays: C1-A2, C1-B2 and return the one which is
	most tilted w.r.t the surface
		
	 
	Parameters
	----
	Optics1 : NumericalOptics
		First Optical element

	Optics1 : NumericalOptics
		Second Optical element
	
	Return
	---------------------------
	V1 : Ray
		The k-vector which is mostly grazing w.r.t. the normal of the surface of Optics1
		
	V2 : Ray
		The same as V1, but for Optics2
	
	'''
	
	
	try:
		X1, Y1 = Optics1.GetXY(3)
		X2, Y2 = Optics2.GetXY(3)
	except:
		raise WiserException ("Error in Getting the View Angle. Maybe the optical element is not numerical and does not have a defined transverse extension.")
	
	_,_,C1 = GetABC(Optics1)
	A2,B2,_ = GetABC(Optics2)
		
	Va = ToolLib.UnitVector(A = C1, B = A2)
	Vb = ToolLib.UnitVector(A = C1, B= B2)
	
	N2 = Optics2.VersorNorm
	
	VList = [Va,Vb]
	AngleList = [N2.Dot(_) for _ in VList]
	IndexMax = np.argmax(AngleList)
		
	return VList[IndexMax]


#==========================================
# FUN: GetMaximumViewAngle
#==========================================
def GetMaximumGrazingRay(Optics1 : OpticsNumerical, Optics2 : OpticsNumerical) -> float:
	'''
	Two-Body function.
	
	Given two optical elements, with terminal points A1 B1 A2 B2 it
	- computes the possible combination of rays: A1-A2, A1-B2, B1-A2, B1-B2,
		
	- for each one of the surfaces, returns the ray which is most grazing to the
	surface
	 
	Parameters
	----
	Optics1 : NumericalOptics
		First Optical element

	Optics1 : NumericalOptics
		Second Optical element
	
	Return
	---------------------------
	V1 : Ray
		The k-vector which is mostly grazing w.r.t. the normal of the surface of Optics1
		
	V2 : Ray
		The same as V1, but for Optics2
	
	'''
	
	
	try:
		X1, Y1 = Optics1.GetXY(2)
		X2, Y2 = Optics2.GetXY(2)
	except:
		raise WiserException ("Error in Getting the View Angle. Maybe the optical element is not numerical and does not have a defined transverse extension.")
	
	A1 = [X1[0], Y1[0]]
	B1 = [X1[1], Y1[1]]

	A2 = [X2[0], Y2[0]]
	B2 = [X2[1], Y2[1]]
		
	Va = ToolLib.UnitVector(A = A1, B= A2)
	Vb = ToolLib.UnitVector(A = A1, B= B2)
	Vc = ToolLib.UnitVector(A = B1, B= A2)
	Vd = ToolLib.UnitVector(A = B1, B= B2)
	
	N1 = Optics1.VersorNorm
	N2 = Optics2.VersorNorm
	
	NList = [N1,N2]
	VList = [Va,Vb,Vc,Vd]
	
#	for _ in VList:
#		print(_)
#		print('\n')
	
	VMaxList= []
	for N in NList :
		AngleList = [N1.Dot(_) for _ in VList]
		IndexMax = np.argmax(AngleList)
		VMaxList.append(VList[IndexMax])
		
	return(VMaxList[0], VMaxList[1])
#	print(VMaxList[0])
#	print(VMaxList[1])
	

#%% Sampling Functions

#==========================================
# FUN: GetNSamples12_MaximumGrazing
#==========================================
def GetNSamples12_VerySimple(Lambda: float, 
					   Oe0 : OpticalElement, 
					   Oe1: OpticalElement) -> int:
	'''
	
	Description of the approach
	-----
	Oe0 and Oe1 are treated alternatively as "point sources".
	
	Step0 is computed as 
	
	One of the base function for computing the sampling.
	
	The step
	
	
	Returns
	---------------------------
	Ans : dict
		Dictionary with fields
		- N0, N1: the Number of samples
		- Step0, Step1: the step sizes
	'''
	 
	z = np.linalg.norm(Oe1.CoreOptics.XYCentre - Oe0.CoreOptics.XYCentre)
	L0 = Oe0.CoreOptics.L
	L1 = Oe1.CoreOptics.L
	Opt0 = Oe0.CoreOptics
	Opt1 = Oe1.CoreOptics
	Theta0 = Oe0.CoreOptics.VersorNorm.Angle
	Theta1 = Oe1.CoreOptics.VersorNorm.Angle
	a = Oe1.ComputationSettings.OversamplingFactor
	
	V0,V1 = Optics.GetMaximumGrazingRay(Opt0, Opt1)
	
	Alpha0 = abs(V0.Dot(Opt0.VersorNorm))
	Alpha1 = abs(V1.Dot(Opt1.VersorNorm))
	
	Step0 = Lambda/2/Alpha0 
	Step1 = Lambda/2/Alpha1	
	N0 = int(np.round(L0/Step0))
	N1 = int(np.round(L1/Step1))
	
	Ans = {'N0' : N0, 'N1' : N1, 'Step0' : Step0, 'Step1' : Step1,
		'Alpha0' : Alpha0, 'Alpha0Deg' : np.rad2deg(Alpha0),
		'Alpha1' : Alpha0, 'Alpha1Deg' : np.rad2deg(Alpha1),
		'z' : z}
	
	return Ans

#==========================================
# FUN: GetNSamples12_MaximumGrazing
#==========================================
def GetNSamples12_MaximumGrazing(Lambda: float, 
					   Oe0 : OpticalElement, 
					   Oe1: OpticalElement) -> int:
	'''
	One of the base function for computing the sampling.
	
	The step
	
	
	Returns
	---------------------------
	Ans : dict
		Dictionary with fields
		- N0, N1: the Number of samples
		- Step0, Step1: the step sizes
	'''
	 
	z = np.linalg.norm(Oe1.CoreOptics.XYCentre - Oe0.CoreOptics.XYCentre)
	L0 = Oe0.CoreOptics.L
	L1 = Oe1.CoreOptics.L
	Opt0 = Oe0.CoreOptics
	Opt1 = Oe1.CoreOptics
	Theta0 = Oe0.CoreOptics.VersorNorm.Angle
	Theta1 = Oe1.CoreOptics.VersorNorm.Angle
	a = Oe1.ComputationSettings.OversamplingFactor
	
	V0,V1 = Optics.GetMaximumGrazingRay(Opt0, Opt1)
	
	Alpha0 = abs(V0.Dot(Opt0.VersorNorm))
	Alpha1 = abs(V1.Dot(Opt1.VersorNorm))
	
	Step0 = Lambda/2/Alpha0 
	Step1 = Lambda/2/Alpha1	
	N0 = int(np.round(L0/Step0))
	N1 = int(np.round(L1/Step1))
	
	Ans = {'N0' : N0, 'N1' : N1, 'Step0' : Step0, 'Step1' : Step1,
		'Alpha0' : Alpha0, 'Alpha0Deg' : np.rad2deg(Alpha0),
		'Alpha1' : Alpha0, 'Alpha1Deg' : np.rad2deg(Alpha1),
		'z' : z}
	
	return Ans


#==========================================
# FUN: GetNSamples12_MaximumGrazing
#==========================================
def GetNSamples12_MaximumScattering(Lambda: float, 
					   Oe0 : OpticalElement, 
					   Oe1: OpticalElement) -> int:
	'''
	One of the base function for computing the sampling.
	
	The step
	
	
	Returns
	---------------------------
	Ans : dict
		Dictionary with fields
		- N0, N1: the Number of samples
		- Step0, Step1: the step sizes
	'''
	 
	z = np.linalg.norm(Oe1.CoreOptics.XYCentre - Oe0.CoreOptics.XYCentre)
	L0 = Oe0.CoreOptics.L
	L1 = Oe1.CoreOptics.L
	Opt0 = Oe0.CoreOptics
	Opt1 = Oe1.CoreOptics
	Theta0 = Oe0.CoreOptics.VersorNorm.Angle
	Theta1 = Oe1.CoreOptics.VersorNorm.Angle
	a = Oe1.ComputationSettings.OversamplingFactor
	V0,V1 = Optics.GetMaximumGrazingRay(Opt0, Opt1)
	
	#--- Sampling for 0
	ThetaMax = Opt0.RayOutNominal.Angle + GetCentredViewAngle(Opt0, Opt1)/2 
	
	Theta0 = Opt0.RayOutReflected.Angle
	Alpha0 = np.abs(ThetaMax - Theta0) # angle between the 0-order angle and the maximum scattered angle
	Step0 = Lambda/2/Alpha0 
	N0 = int(np.round(L0/Step0))
	
	#--- Sampling for 1
	_, V1 = GetMaximumGrazingRay(Opt0, Opt1)
	Alpha1 = np.inner(V1.v, Opt1.VersorTan.v)
	Step1 = Lambda/2/Alpha1	
	N1 = int(np.round(L1/Step1))
	
	Ans = {'N0' : N0, 'N1' : N1, 'Step0' : Step0, 'Step1' : Step1,
		'Alpha0' : Alpha0, 'Alpha0Deg' : np.rad2deg(Alpha0),
		'Alpha1' : Alpha0, 'Alpha1Deg' : np.rad2deg(Alpha1),
		'z' : z}
	
	
	return Ans
	

#==========================================
# FUN: GetNSamples1To2()
#==========================================
def GetNSamples01(Lambda: float, 
					   Oe0 : OpticalElement, 
					   Oe1: OpticalElement,
					   Method : SamplingMethods = SamplingMethods.MAXIMUM_SCATTERING) -> int:
	'''
	Parameters
	----
	Oe0 : OpticalElement OR Optics
	Oe1 : OpticalElemtn OR Optics
	
	'''

	
	if Method == SamplingMethods.MAXIMUM_GRAZING_RAY:
		Ans = GetNSamples12_MaximumGrazing(Lambda, Oe0, Oe1)
	elif Method == SamplingMethods.MAXIMUM_SCATTERING:
		Ans = GetNSamples12_MaximumScattering(Lambda, Oe0, Oe1)

	return Ans