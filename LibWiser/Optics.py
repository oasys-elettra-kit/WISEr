# -*- coding: utf-8 -*-
"""
Created on Mon Aug 08 16:10:57 2016

@author: Mic
:math:`y = m x + q`
"""
import LibWiser.ToolLib as tl
import LibWiser.Noise as Noise
import LibWiser.Rayman as rm

import matplotlib.pyplot as plt
import numpy as np

from abc import abstractmethod
from enum import Enum

'''

Conventions:
----------------

RF : stands for "reference frame"
XYSelf : couple of (x,y) coordinates expressed in the RF of the optical element.

XYKLab : couple of (x,y) coordinates expressed in the RF of the laboratory

AngleGrazing : is the "grazing angle" (see wikipedia), and it is typically taken from the central point of an optical element.
	In this sense it is independent on the laboratory RF.

AngleIn : "In" stands for Input, and designate the angle of the input beam (in the laboratory RF)

AngleOut : The same as AngleIn, but for the Output beam



'''


#UnitVector = geom.tl.UnitVector
#Ray = geom.Ray
#Line = geom.Line
#Segment = geom.Segment
#from Optics import EvalField_XYOb


#===============================
#	 Enum: OPTICS_BEHAVIOUR
#===============================
class OPTICS_BEHAVIOUR:
	Source = 'source'
	Mirror = 'mirror'
	Focus = 'focus'
	Split = 'split'
	Slits = 'slits'

class FIGURE_ERROR_FILE_FORMAT(Enum):
	HEIGHT_ONLY = 0 	#  label: "Height (Y)"
	POSITION_AND_HEIGHT = 2**1 #  label: "Position, Height (X,Y)"
	SLOPE_ONLY = 2**2 #  label: "Slope (dY)"
	ELETTRA_LTP_JAVA1 = 2**3 # label: "ELETTRA LTP-JAVA1"
	ELETTRA_LTP_DOS = 2**4 # label: "ELETTRA LTP"

def DiffractionMinimum(Lambda, D, z, Alpha = 0):
	x0 = Lambda * z / D / np.sin(Alpha)
	return x0

#===============================
#	 TypeOfAngle
#===============================
class TypeOfAngle:
	GrazingNominal = 'grazing'
	InputNominal = 'input'
	OutputNominal = 'output'
	SelfFrameOfReference = 'aixs' # e.g. the x axis of the ellipse.
	NormalAbsolute = 'default'
	TangentAbsolute = 'tangent'
	Surface = 'default'
	AxisOrigin = 'axis'
#===============================
#	 TypeOfXY
#===============================
class TypeOfXY:
	MirrorCentre = 'centre'
	AxisCentre = 'axis'
	MirrorStart = 'start'

#==============================================================================
#	 Definition: Ray
#==============================================================================
# Ray is an array.
# Ray[0] : propagation angle (in lab reference frame)
# Ray[1]	:



#===============================
#	 CLASS: OPTICS_INFO
#===============================
class OPTICS_INFO(Enum):
	__TypeStr = 'ts'
	__TypeDescr = "Type Description"
	__Behaviour = OPTICS_BEHAVIOUR.Mirror
	__IsAnalytic = False
	__PropList = ['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
					  'XYStart', 'XYCentre', 'XYEnd']



#=============================
#     ENUM: OPTICS_ORIENTATION
#=============================
class OPTICS_ORIENTATION(Enum):
	ISOTROPIC = 0
	VERTICAL = 2
	HORIZONTAL = 2**2
	ANY = 2**3

#==============================================================================
#	 CLASS: Optics
#==============================================================================
class Optics(object):

	#================================================================
	#CLASS (INTERNAL):  _ClassSmallDisplacements
	#================================================================
	class _SmallDisplacements:
		'''
		Contains the info about displacements in X,Y and Angle which are applied when
		calling the GetXY function (if the option "UseSmallDisplacements" is selected).

		The displacements are intendet to be applied after the "nominal construction" of the
		beamline, and affects the result of GetXY function only.

		The displacements are defined along the direction of RayInNominal and can be

		- Rotation (radians)
		- Longitudinal
		- Transverse

		The element is first rotated (around the nominal XYCentre), then shifted
		'''
		def __init__(self):
			self.Rotation = 0.0
			self.Long= 0.0
			self.Trans= 0.0


	#=================================================
	#CLASS (INTERNAL):  _ComputationSettings [Optics]
	#=================================================
	class _ComputationSettings:
		#===============================
		#	 CLASS: __init__[ComputationSettings]
		#===============================
		def __init__(self, Ignore = False):
			self.UseSmallDisplacements = True

		#===============================
		#	 CLASS: __str__
		#===============================
		def __str__(self):
			prop_list = dir(self)
			str_buf = ''
			for prop in prop_list:
				if prop[0]!='_':
					str_buf += '%s\t%s\n' % (prop, str(prop))

			return str_buf

		def __descr__(self):
			return self.__str__()

	#===============================
	#	 CLASS: __init__ [Optics]
	#===============================
	def __init__(self, XPosition=0 , YPosition=0, Orientation=OPTICS_ORIENTATION.ANY, UseAsReference=True):
		self.XY = np.array([XPosition, YPosition])
		self.SmallDisplacements = Optics._SmallDisplacements()
		self.ComputationSettings = Optics._ComputationSettings()
		self.Orientation = Orientation
		self.UseAsReference = UseAsReference
	#================================
	# PROP: Orientation
	#================================
	@property
	def Orientation(self) -> OPTICS_ORIENTATION:
		'''
		Created for: handling the succession of Vertical and Horizontal items in a beamline,
		and in the the pertinent field propagation.

		This property is queried by the 1d propagation system in order to know which o.e. couple
		together.

		'''
		return self._Orientation
	@Orientation.setter
	def Orientation(self, Value):
		self._Orientation = Value

	# ================================
	# PROP: UseAsReference
	# ================================
	@property
	def UseAsReference(self):
		'''
		Created for: use current optical element as a reference element in positioning directives.

		If True, then the element can be referred to, otherwise it will be transparent.
		'''
		return self._UseAsReference

	@UseAsReference.setter
	def UseAsReference(self, Value):
		self._UseAsReference = Value
	#================================================
	#	 FUN: PaintMiniature
	#================================================
	def PaintMiniature(self, FigureHandle= None, N = 100, Length = 1, ArrowWidth = None, Color = 'm', Title = ''):
		'''
		Produces a figures that contains the present Optics only.
		Uses the .Paint method which is defined in the more specific subclass
		'''
		self.Paint(self, FigureHandle= None, N = 100, Length = 1, ArrowWidth = None, Color = 'm')
		plt.tile(Title)

		pass

#==============================================================================
#	 CLASS ABSTRACT: Analytical Optics
#==============================================================================
class OpticsAnalytical(Optics):
	''' Implements optics which can be (totally, unically or mostly) described
	analytically (e.g. gaussian sources, theoretical diffraction grating, etc).
	'''
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	#================================================
	#	 EvalField_XYSelf
	#================================================
	def EvalField_XYSelf(self,z=np.array(None), y=np.array(None)):
		''' Evaluates the Field in the reference frame of the object
		'''
		pass

	#================================================
	#	 EvalField_XYLab
	#================================================
	def EvalField_XYLab(self, x=np.array(None), y=np.array(None)):
		''' Evaluates the Field in the laboratory raference frame
		'''
		pass

#==============================================================================
#	 CLASS ABSTRACT: OpticsNumerical
#==============================================================================
class OpticsNumerical(Optics):
	''' Implements optics for which the explicit field computation is required, within
	field propagation
	'''

	#================================================================
	#CLASS (INTERNAL):  _ComputationSettings
	#================================================================
	class _ComputationSettings(Optics._ComputationSettings):

		def __init__(self, Ignore=False, **kwargs):
			super().__init__(**kwargs)
			self.UseSmallDisplacements = True
			self.UseRoughness = False
			self.UseFigureError = False

			# attributi ereditati dal ComputationSettings di OpticalElement
#			self.Ignore = Ignore
#			self.NSamples = 2002
#			self.NPools = 4
#			self.OversamplingFactor = 1

		@property
		def UseIdeal(self):
			return not(self.UseRoughness) and not(self.UseFigureError)

		@UseIdeal.setter
		def UseIdeal(self, boolean):
			if boolean == True:
				self.UseRoughness = False
				self.UseFigureError = False

		def __str__(self):
			prop_list = dir(self)
			str_buf = ''
			for prop in prop_list:
				if prop[0]!='_':
					str_buf += '%s\t%s\n' % (prop, str(prop))

			return str_buf

		def __descr__(self):
			return self.__str__()

	#================================
	#FUN:  __init__[OpticsNumerical]
	#================================
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._Transformation_List = [ [], [], [] ]
		self.AngleLab = 0
		self._XYLab_Centre = np.array([0,0])

		self.ComputationSettings = OpticsNumerical._ComputationSettings()

	#================================
	# EvalField(N)
	#================================
	def EvalField(self, x1, y1, Lambda, E0, NPools=1,  Options=['HF']):
		'''
		Helper function (forwards)
		Propagates the field E0 from this optical element (x0,y0) onto the plane
		x1, y1.
		x0 and y0 are are automatically computed.

		>>> x0, y0 = self.GetXY(len(x0), Options)

		Options can be (they are case insensitive):
		- Any of the values of GetXY. Such Options are tunneled to self.GetXY, which is used to get the x0,y0 for the propagations
		'''
		N = len(x1)
		x0, y0 = self.GetXY(N)
		tl.Debug.Print('Evaluating Field: N  = %d (EvalField)' % N, NIndent =3 )
		tl.Debug.pr('\t\t\tLambda')

		#ad hoc correction: multiply by transmission function before propagation
		E0 = E0 * self.TransmissionFunction(x0,y0)

		# print('--------------------------------')
		# print('Lambda', type(Lambda), np.shape(Lambda))
		# print('Ea', type(E0), np.shape(E0))
		# print(E0)
		# print('xa', type(x0), np.shape(x0))
		# print(x0)
		# print('ya', type(y0), np.shape(y0))
		# print(y0)
		# print('xb', type(x0), np.shape(x0))
		# print(x1)
		# print('yb', type(y0), np.shape(y0))
		# print(y1)

		E1 = rm.HuygensIntegral_1d_Kernel(Lambda, E0, x0, y0, x1, y1)

		return E1

	@abstractmethod
	def GetXY(self):
		"""
        Abstract method to write a message.
        Raises: NotImplementedError
        """
		raise NotImplementedError("You should implement GetXY.")

	'''
	The two master variables are XYOrigin as AngleLab
	'''
	#================================
	# PROP: XYCentre
	#================================
	@property
	def XYCentre(self) -> float:
		return self._XYLab_Centre
	@XYCentre.setter
	def XYCentre(self, Value):
		self._XYLab_Centre = Value

	#================================
	# PROP: AngleLab
	#================================
	@property
	def AngleLab(self) -> float:
		"""
		AngleLab is the orientation angle of
			-the normal of the mirror
			- in the lab ref frame
	   """
		return self._AngleLab
	@AngleLab.setter
	def AngleLab(self, Value):
		self._AngleLab = Value
#		self._VersorLab = UnitVector(Angle = self._AngleLab, XYOrigin = self.XYOrigin)




	#================================
	# PROP: VersorLab
	#================================
	@property
	def VersorLab(self) ->tl.UnitVector:
		"""
		VersorLab is the versor specifying the orientation of the mirror in the Lab ref. frame.
		   DIRECTION is
		   - NORMAL to the mirror surface
		   - centred in the mirror centre
		   - oriented on the same half-plane containing the reflectiong surface.

		"""
		return tl.UnitVector(Angle = self.AngleLab, XYOrigin = self.XYCentre)
	@VersorLab.setter
	def VersorLab(self, Value):
		if type(Value) == np.ndarray:
			 V = tl.UnitVector(Value)
		elif type(Value) == tl.UnitVector:
			V = Value
		else:
			print('Error in Optics.OpticsNumerical.VersorTan setter')

		self.XYOrigin = V.XYOrigin
		self._AngleLab = V.Angle

	#================================
	# PROP: AngleTanLab
	#================================
	@property
	def AngleTanLab(self) -> float:
		return self.VersorLab.Angle - np.pi/2
	@AngleTanLab.setter
	def AngleTanLab(self, Value):
		self._AngleLab = Value + np.pi/2

	#================================
	# PROP: VersorTan
	#================================
	@property
	def VersorTan(self) -> tl.UnitVector:
		return tl.UnitVector(Angle = self.AngleTanLab, XYOrigin = self.XYCentre)

	#================================
	# PROP: VersorNorm
	#================================
	@property
	def VersorNorm(self) -> tl.UnitVector:
		return self.VersorLab

	#================================
	# FieldForwards(N)
	#================================
	def FieldForwards(self, x1, y1, Lambda, E0, NPools=1,  Options=['HF']):
		'''
		Helper function (forwards)
		Propagates the field E0 from this optical element (x0,y0) onto the plane
		x1, y1.
		x0 and y0 are are automatically computed.

		>>> x0, y0 = self.GetXY(len(x0), Options)

		Options can be (they are case insensitive):
		- Any of the values of GetXY. Such Options are tunneled to self.GetXY, which is used to get the x0,y0 for the propagations
		'''
		N = len(x1)
		x0, y0 = self.GetXY(N)
		tl.Debug.Print('Calcolo Campi: N  = %d' % N)
		tl.Debug.pr('Lambda')
		E1 = rm.HuygensIntegral_1d_Kernel(Lambda, E0, x0, y0, x1, y1)

		return E1

	def TransmissionFunction(self,x,y):
		'''
		Transmission function of the optics.
		When EvalField is called, the field on the object is multiplied by the
		TransmissionFunction. Then, the propagation is computed.


		'''

		return 1



	#================================================
	#	 _Transformation_Clear
	#================================================
	def _Transformation_Clear(self):
		self._Transformation_List = [ [], [], [] ]

	#================================================
	#	 _Transformation_Add
	#================================================
	def _Transformation_Add(self, Rotation = 0, XYTranslation = [0,0], RotationCentre = [0,0], ClearAll = False):
		'''
			The operation list will be: Translation1, Rotation1, Translation2, Rotation2.

			If you want to start with a pure rotation, set Translation1 = [0,0]
		'''
		if ClearAll:
			self._Transformation_Clear()
		self._Transformation_List[0].append(XYTranslation)
		self._Transformation_List[1].append(Rotation)
		self._Transformation_List[2].append(RotationCentre)

	#================================================
	#	 _Transformation_XYPropToXYLab
	#================================================
	def _Transformation_XYPropToXYLab(self, XProp, YProp):
		'''
		Apply the sequence of Transformations contained in ._Transformation_List
		in order to map XProp, YProp into XLab, YLab.

		Parameters
		-------------------
		XProp, YProp : 1d-array like
			x nd y coordinates
		'''
		x = XProp
		y = YProp
		N = len(self._Transformation_List[0])

		#Process the transformation in _Transformation_List
		for i in range(0,N):
			XYTranslation = self._Transformation_List[0][i]
			Rotation = self._Transformation_List[1][i]
			RotationCentre = self._Transformation_List[2][i]
			x,y = tl.RotXY(x,y,Rotation, RotationCentre)
			x = x + XYTranslation[0]
			y = y + XYTranslation[1]

		return x, y

	def Transformation_XYSelfToXYLab(self, XSelf, YSelf):
		return self._Transformation_XYPropToXYLab(self, XSelf, YSelf)

	#================================================
	#	 _Transformation_XYPropToXYLab
	#================================================
	def _Transformation_XYLabToXYProp(self, XLab, YLab):
		'''
		Reversed version of _Transformation_XYPropToXYLab.
		Will it wordk?

		Parameters
		-------------------
		XProp, YProp : 1d-array like
			x nd y coordinates
		'''
		x = XLab
		y = YLab
		N = len(self._Transformation_List[0])

		#Get the reversed Transformation List
		_Transformation_List = self._Transformation_List[::-1]

		#Process the transformation in _Transformation_List
		# and apply -1 multiplication to translations and rotations
		for i in range(0,N):
			XYTranslation = -1 * np.array(self._Transformation_List[0][i])
			Rotation = -1 * np.array(self._Transformation_List[1][i])
			RotationCentre = self._Transformation_List[2][i]
			x = x + XYTranslation[0]
			y = y + XYTranslation[1]
			x,y = tl.RotXY(x,y,Rotation, RotationCentre)

		return x, y

	def Transformation_XYLabToXYSelf(self, XLab, YLab):
		return self._Transformation_XYLabToXYProp(self, XLab, YLab)

	#================================================
	#	 _Transformation_PolyPropToPolyLab
	#================================================
	def _Transformation_PolyPropToPolyLab(self, P):
		'''
		I hate this function. Should have written a better doc.
		It converts a polynomial P(X) in the X reference frame of the object(self) into
		the laboratory reference frame.

		How is it done?
		In an ugly way...
		1 compute the polynomials px, py
		2 Apply the transformation to px=> px_new, py => py_new
		3 Perform a polinomial fit onto px_new py_new
		'''
		Oversampling = 10 # Originally conceived to be =1
		P = np.array(P)
		NP =   Oversampling * len(P)-1 # degree of the polynomial
		if NP <1:
			print('Errror: Polynomial order too low (<1), finding coefficient is useles...')
			return None

		N = len(self._Transformation_List[0])
		if N >0:
			px = np.linspace(0,NP, NP+1)
			py = np.polyval(P,px)
			for i in range(0,N):
				XYTranslation = self._Transformation_List[0][i]
				Rotation = self._Transformation_List[1][i]
				RotationCentre = self._Transformation_List[2][i]

				px = px + XYTranslation[0]
				py = py + XYTranslation[1]
				px_new, py_new = tl.RotXY(px,py, Rotation, RotationCentre)

			# Polynomial fit
			P_new = np.polyfit(px_new, py_new, NP)
			P_new2 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
			return P_new2
		else:
			return P

#.......................

	#================================================
	#	 _Transformation_XYPropToXYLab_Point
	#================================================
	def _Transformation_XYPropToXYLab_Point(self, XYPropPoint):
		'''
		The same as _Transformation_XYPropToXYLab, except that takes as input
		a unique [x0,y0] point rather than two x,y arrays.

		Parameters
		-----------------
		XYPropPoint : point-like
			[x,y]

		Returns
		-----------------
		XYLabPoint : point-like
			[x,y]

		'''
		x0 = XYPropPoint[0]
		y0 = XYPropPoint[1]
		x , y = self._Transformation_XYPropToXYLab([x0],[y0])
		return np.array([x[0],y[0]])

	#================================================
	#	 _ApplySmallDisplacements [OpticsNumerical]
	#================================================
	def _ApplySmallDisplacements(self, xLab,yLab):
		'''
		xLab, yLab : the (x,y) points of the optical element in the lab reference.

		Notice: SmallDisplacements affect the GetXY function
		'''
		tl.Debug.Print('Applying small displacements', 3, False)
#		XYTranslation = self._Transformation_List[0][i]
#		Rotation = self._Transformation_List[1][i]
#		RotationCentre = self._Tranisformation_List[2][i]

		# SmallDisplacements is defined as function of RayInNominal
		# I express it as function of the laboratory reference frame.
		#  DeltaAngle is used to compute the projection of Long and Trans Displacement

		DeltaX = self.SmallDisplacements.Long * np.cos(np.pi - self.RayInNominal.Angle + self.SmallDisplacements.Rotation)
		DeltaY = self.SmallDisplacements.Long * np.sin(np.pi - self.RayInNominal.Angle + self.SmallDisplacements.Rotation)

		xNew,yNew = tl.RotXY(xLab, yLab, self.SmallDisplacements.Rotation, self.XYCentre)
		xNew = xLab + DeltaX
		yNew = yLab + DeltaY

		tl.Debug.Print('\t\t\tDeltaX = %0.2f' % DeltaX)
		tl.Debug.Print('\t\t\tDeltaY = %0.2f' % DeltaY)
		tl.Debug.Print('\t\t\tRotation =%0.1e' % self.SmallDisplacements.Rotation)

		return(xNew, yNew)

#	#================================================
#	#	 _Transformation_XYProp_To_XYLab
#	#================================================
#	def _Transformation_Update_XYPropToXYLab_Point(self, XYPropPoint):
#		''' The same as _Transformation_XYPropToXYLab_Point, except that the usage
#		of this one is shorter for updating the class members.
#
#			>>> a  =_Transformation_XYPropToXYLab_Point(a)
#
#			>>> _Transformation_Update_XYPropToXYLab_Point(a)
#		'''
#
 	#================================
	# GetXY
	#================================
	def GetXY(self, N, Options =[], **kwargs ):
		'''
		ABSTRACT
		'''
		pass
 	#================================
	# RayInNominal
	#================================
	@property
	def RayInNominal(self)-> tl.Ray:
		'''
		ABSTRACT
		'''
		pass

 	#================================
	# RayOutNominal
	#================================
	@property
	def RayOutNominal(self) -> tl.Ray:
		'''
		ABSTRACT
		'''
		pass

	#================================
	#  PROP: AngleInputNominal
	#================================
	@property
	def AngleInputNominal(self) -> float:
		"""
		In laboratory reference
		"""
		return self.RayInNominal.Angle
	@AngleInputNominal.setter
	def AngleInputNominal(self):
		raise ValueError('AngleInGrazingNominal can not be set.')


	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, N = 100, Length = 1, ArrowWidth = 1, Color = 'm'):
		'''
		ABSTRACT: BETTER TO EXIST
		'''
	#================================================
	#	 GetPositioningString()
	#================================================
	def GetPositioningString(self, TabIndex = 0):
		'''
		Introduced for debugging (when doing the focus sweep). It provides a fast way
		for writing alle the (supposed) necessary information about positions
		(centre, angle of incidence, etc).
		'''
		Str = TabIndex * '\t' + 'XYCentre:= %0.2e m, %0.2em\n' % (self.XYCentre[0], self.XYCentre[1])
		Str+= TabIndex * '\t' + 'AngleGrazing:= %0.2e rad\n' % (np.rad2deg(self.AngleGrazing))

		return

 	#=================

#==============================================================================
#	 CLASS: SourcePoint
#==============================================================================
class SourcePoint(object):
	_Behaviour = OPTICS_BEHAVIOUR.Source
	_IsSource = True
	_TypeStr = 'point'
	_TypeDescr = 'point source'
	_IsAnalytic = True


	#================================================
	#	 __init__
	#================================================
	def __init__(self, Lambda, XYOrigin = [0,0], AnglePropagation = 0 ):
		'''
		Defines a point source.
		AnglePropagation is used in order to position the following optical element

		Parameters
		----
		Lambda : Wavelength
		XYOrigin : [x,y] defining the origin in the absolute reference fraime

		'''
		self.Lambda = Lambda
		self.Name = 'point source @ %0.2fnm' % (self.Lambda *1e9)
		self.SetXYAngle_Centre(XYOrigin, AnglePropagation)

	#================================================
	#	 __str__
	#================================================
	def __str__(self):
		PropList = ['Lambda', 'XYCentre','Waist0', 'AnglePropagation']
		List = [PropName + ':= ' + str(getattr(self,PropName)) for PropName in PropList]
		return ('Gaussian source\n' + 20 * '-' + '\n'+ '\n'.join(List) + '\n' + 20 * '-' + '\n')


	#================================================
	#	 SetXYAngle_Centre
	#================================================
	def SetXYAngle_Centre(self, XYCentre, Angle):
		'''
		Parameters
		------------------
		XYCentre :

		Angle :
		'''
		self.XYOrigin = np.array(XYCentre)
		self.ThetaPropagation = Angle
		self.AnglePropagation = Angle


	#================================================
	#	 XYOrigin
	#================================================
	@property
	def XYOrigin(self):
		return self._XYOrigin
	@XYOrigin.setter
	def XYOrigin(self, value):
		self._XYOrigin = np.array(value)

	#================================================
	#	 XYCentre
	#================================================
	@property
	def XYCentre(self):
		return self._XYOrigin
	@XYCentre.setter
	def XYCentre(self, value):
		tl.ErrMsg.NoPropertySetAllowed('Use XYOrigin instead')

	#================================================
	#	 EvalField_XYSelf
	#================================================
	def EvalField_XYSelf(self,x=np.array(None) , y=np.array(None)):
		'''
			x and y are in the source reference frame

			#TODO: add normalization

		'''
		k = 2. * np.pi / self.Lambda
		R = np.sqrt(x**2 + y**2)
		return 1. / R * np.exp(1j * k * R)

	#================================================
	#	 EvalField_XYLab
	#================================================
	def EvalField_XYLab(self, x = np.array(None), y = np.array(None)):
		(x,y) = rm._MatchArrayLengths(x,y)
		k = 2* np.pi / self.Lambda
		R = np.sqrt((x-self.XYCentre[0])**2 + (y-self.XYCentre[1])**2)
		return 1. / R * np.exp(1j * k * R)

 	#================================
	# EvalField(N)
	#================================
	def EvalField(self, x1, y1, Lambda,  NPools=1,  **kwargs):
		'''
		Helper function.
		Propagates the field E0 from this optical element (x0,y0) onto the plane
		(x1, y1).

		Uses parameters stored in the object
		'''

		E1 = self.EvalField_XYLab(x1,y1)
		return E1




	#================================================
	#	 GetRayOutNominal
	#================================================
	@property
	def RayOutNominal(self):
		return tl.Ray(XYOrigin = self.XYCentre, Angle = self.AnglePropagation)

	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, Color = 'm', Length = 0.3, ArrowWidth = None, **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.

		'''
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		# a star, marking the centre
		plt.plot(self._XYOrigin[0], self._XYOrigin[1],  marker = '*', markersize = 10)
		RayOut = self.RayOutNominal
		U = tl.UnitVector(vx = RayOut.v[0], vy = RayOut.v[1], XYOrigin = self._XYOrigin)

		Length = Length if Length != None else 0.5
		U.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth)

		return FigureHandle

# ==============================================================================
# 	 CLASS: SourcePoint
# ==============================================================================
class _old(OpticsAnalytical):
	_Behaviour = OPTICS_BEHAVIOUR.Source
	_TypeStr = 'ps'
	_TypeDescr = 'Point Source'

	#================================================
	#	 FUN: __init__
	#================================================
	def __init__(self, Lambda, XOrigin = 0, YOrigin = 0):
		self.Lambda = Lambda
#		self.XOrigin = XOrigin
#		self.YOrigin = YOrigin
		self.XYCentre = np.array([XOrigin,YOrigin])
		self.Name = 'Point source @ %0.2fnm' % (self.Lambda *1e9)



 	#================================
	# SetXYAngle_Centre
	#================================
	def SetXYAngle_Centre(self, XYLab_Centre, AngleIn ):
		'''
		Set the element XYCentre and orientation angle.
		'''
		self._XYLab_Centre = XYLab_Centre
		self._AngleIn = AngleIn
		AngleTan = AngleIn + self.AngleGrazing
		# Defines: Versos, AngleNorm, AngleTan
		UV = tl.UnitVector(Angle = AngleTan + np.pi/2) # Old definition: when the primary variable was VersorNorm and not VersorTan
		self.VersorNorm = UV
		# self.VersorTan = tl.UnitVector(Angle = AngleTan) # attempt of new definition, but it is not safe

	#================================================
	#	 EvalField_XYSelf
	#================================================
	def EvalField_XYSelf(self, x = np.array(None), y = np.array(None)):
			'''
			Evaluates the field.
			Coordinates are given in the reference frame of the object.

			Evaluations in the "Self reference frame" are formally equivalent to the
			matematical evaluations of functions. Evaluations in the "Lab reference
			frame" account for translations and rotation of the 'self' object.

			e.g.
			Eval_Self(x,y) = f(x,y)
			Eval_Lab(x,y) = f(x-x0, y-y0)
			'''

			(x,y) = rm._MatchArrayLengths(x,y)
			k = 2. * np.pi / self.Lambda
			R = np.sqrt(x**2 + y**2)
			return 1. / R * np.exp(1j * k * R)

	#================================================
	#	 EvalField_XYLab
	#================================================
	def EvalField_XYLab(self, x = np.array(None), y = np.array(None)):
			'''
			Evaluates the field.
			Coordinates are given in the reference frame of the Laboratory.

			Evaluations in the "Self reference frame" are formally equivalent to the
			matematical evaluations of functions. Evaluations in the "Lab reference
			frame" account for translations and rotation of the 'self' object.

			e.g.
			Eval_Self(x,y) = f(x,y)
			Eval_Lab(x,y) = f(x-x0, y-y0)
			'''
#			R = np.sqrt((x - self.XOrigin)**2 + (y-self.YOrigin)**2)
			return self.EvalField_XYSelf(x - self.XOrigin, y - self.YOrigin)

def GaussianField(z,r, Lambda, Waist0):

	k = 2. * np.pi / Lambda
	RayleighRange = np.pi * Waist0**2 / Lambda
	RCurvature = z * (1. + (RayleighRange/z)**2)
	GouyPhase = np.arctan(z/RayleighRange)
	Waist = Waist0 * np.sqrt(1. + (z/RayleighRange)**2)

	Phase = -(k * z + k * r**2. / 2. / RCurvature - GouyPhase)
	Norm = Waist0 / Waist
	A = np.exp(-r**2 / Waist**2)

	E = Norm * A * np.exp(1j * Phase)
	return E

#==============================================================================
#	 CLASS: SourceGaussian
#==============================================================================
class SourceGaussian(OpticsAnalytical):
	_Behaviour = OPTICS_BEHAVIOUR.Source
	_IsSource = True
	_TypeStr = 'gauss'
	_TypeDescr = 'Gaussian Source'
	_IsAnalytic = True



	#================================================
	#	 __init__
	#================================================
	def __init__(self, Lambda, Waist0, M2 = 1, XYOrigin=[0,0], AnglePropagation=0, **kwargs):
		'''
		Defines a purely gaussian source (M factor =1).

		Parameters
		----
		Waist0 : Waist size in the equation of the electromagnetic field (not the Intensity!)

		'''
		super().__init__(**kwargs)

		self.Lambda = Lambda
		self.Waist0 = Waist0
		self.M2 = 1  # quality factor
		self.Name = 'Gaussian source @ %0.2fnm' % (self.Lambda * 1e9)
		self.SetXYAngle_Centre(XYOrigin, AnglePropagation)

	def __str__(self):
		PropList = ['Lambda', 'XYCentre','Waist0', 'AnglePropagation']
		List = [PropName + ':= ' + str(getattr(self,PropName)) for PropName in PropList]
		return ('Gaussian source\n' + 20 * '-' + '\n'+ '\n'.join(List) + '\n' + 20 * '-' + '\n')

	def Fwhm(self,z):
		return self.Waist(z) * 2 * np.sqrt(np.log(2))


	#================================================
	#	 SetXYAngle_Centre
	#================================================
	def SetXYAngle_Centre(self, XYCentre, Angle, **kwargs):
		'''
		Parameters
		------------------
		XYCentre :

		Angle :
		'''
		self.XYOrigin = np.array(XYCentre)
		self.ThetaPropagation = Angle
		self.AnglePropagation = Angle


	#================================================
	#	 XYOrigin
	#================================================
	@property
	def XYOrigin(self):
		return self._XYOrigin
	@XYOrigin.setter
	def XYOrigin(self, value):
		self._XYOrigin = np.array(value)

	#================================================
	#	 XYCentre
	#================================================
	@property
	def XYCentre(self):
		return self._XYOrigin
	@XYCentre.setter
	def XYCentre(self, value):
		tl.ErrMsg.NoPropertySetAllowed('Use XYOrigin instead')

	#================================================
	#	 RayleighRange
	#================================================
	@property
	def RayleighRange(self):
		'''
		Rayleigh Range, using the formula:

		.. math::
			z_r = \pi w_0^2 /(\lambda M^2)

		'''
		return   np.pi * self.Waist0**2 / self.Lambda/self.M2
	#================================================
	#	 ThetaDiv
	#================================================
	@property
	def ThetaDiv(self):
		'''
		Divergence of the gaussian field .

		.. math::
			\\theta = M^2\\frac{\\lambda}{\\pi w_0}

		'''
		return  self.M^2*self.Lambda/np.pi/self.Waist0

	#================================================
	#	 WaistZ
	#================================================
	def Waist(self, z):
		return self.Waist0 * np.sqrt(1+ (z/self.RayleighRange)**2)

	#================================================
	#	 RCurvature
	#================================================
	def RCurvature(self, z):
		#return z
		return z * (1+(self.RayleighRange/z)**2)

	#================================================
	#	 GouyPhase
	#================================================
	def GouyPhase(self,z):
		return np.arctan(z/self.RayleighRange)

	#================================================
	#	 Amplitude
	#================================================
	def Amplitude(self,r,z):
		return np.exp(-r**2/self.Waist(z)**2)
	#================================================
	#	 Phase
	#================================================
	def Phase(self, z,r):
		'''
		Returns the phase Phi in the exponential term Exp(ij * Phi)

		Uses the self frame reference
		'''
		k = 2 * np.pi / self.Lambda
		Ph = -((k*z + k *r**2/2/self.RCurvature(z) - self.GouyPhase(z)))
		ZeroPos = (z==0)  # gestisto eventuale singolarit?? nella fase
		try:
			Ph[ZeroPos] = 0
		except:
			pass
		return Ph

	#================================================
	#	 EvalField
	#================================================
	def Phase_XYLab(self, xLab=np.array(None), yLab=np.array(None)):
		'''
		Evaluates the Phase at (x,y), which are in the Lab Reference
		'''
		(xLab,yLab) = rm._MatchArrayLengths(xLab,yLab)
		#codice che dovrebbe funzionare ma che non va
		# Ruoto il piano x,y di Theta attorno all'origina della gaussiana
		myOrigin = self.XYOrigin
		# myTheta = -self.ThetaPropagation
		[zSelf,rSelf] = tl.RotXY(xLab,yLab, CentreOfRotation = myOrigin, Theta = - self.ThetaPropagation)
		zSelf = zSelf - myOrigin[0]
		rSelf = rSelf - myOrigin[1]

		return self.Phase(zSelf,rSelf)

	#================================================
	#	 Cycles
	#================================================
	def Cycles(self, x=np.array(None) , z=np.array(None)):
		'''
		z: distance (m) scalar
		x: 1darray, sampling
		'''
		return np.cos(self.Phase(x,z))

	#================================================
	#	 EvalField_XYSelf
	#================================================
	def EvalField_XYSelf(self,z=np.array(None) , r=np.array(None)):
		'''
			z,r are in the gaussian reference frame
			z (source reference) --> x (lab reference)
			r (source reference) --> y (lab reference)

		'''
		(z,r) = rm._MatchArrayLengths(z,r)
		# EQUATION: of the Normalized Gaussian field.
		# Normalized to the integrated power
		#Ph = (k*z + k *y**2/2/self.RCurvature(z) - self.GouyPhase(z))
		Norm =	 (self.Waist0 / self.Waist(z)) # Normalize peak to 1
		A = np.exp(-r**2/self.Waist(z)**2)
		E = Norm * A *	np.exp(1j * self.Phase(z, r))

		# Normalize to the integrated power
		I = np.abs(E)**2
		Norm2 = np.sqrt(np.sum(I))

		return E/Norm2


 	#================================
	# EvalField(N)
	#================================
	def EvalField(self, x1, y1, Lambda,  NPools = 1,  **kwargs):
		'''
		Helper function.
		Propagates the field E0 from this optical element (x0,y0) onto the plane
		(x1, y1).

		Uses parameters stored in the object
		'''
		# Evaluates the field
		# x1,y1: in the Lab reference
		E1 = self.EvalField_XYLab(x1,y1)
		return E1

	#================================================
	#	 EvalField
	#================================================
	def EvalField_XYLab(self, x=np.array(None), y=np.array(None)):
		'''
		Evaluates the field at (x,y), which are in the Lab Reference.

		**Uses** self.SmallDisplacements (if required)

		Parameters
		-----
		x,y : float np.array
			coordinates in the Lab Ref. Frame where to compute the field.

		Return
		-----
		E : 1d  complex np.array
			e.m. field
		'''

		(x,y) = rm._MatchArrayLengths(x,y)
		'''
		in qusta funciton ho introdotto il concetto per cui
		x ?? la coordinata nel sistema di riferimento esterno
		z ?? la distanza dal waist.
		'''

		#@todo completare i displacements

		if self.ComputationSettings.UseSmallDisplacements:
			DeltaTheta = self.SmallDisplacements.Rotation
			DeltaLong = self.SmallDisplacements.Long
		else:
			DeltaTheta = 0
			DeltaLong = 0

		# Ruoto il piano x,y di Theta attorno all'origina della gaussiana
		myOrigin = self.XYOrigin
		# myTheta = -self.ThetaPropagation
		[zg,yg] = tl.RotXY(x,y, CentreOfRotation = myOrigin, Theta = - self.ThetaPropagation - DeltaTheta)
		zg = zg - myOrigin[0]
		yg = yg - myOrigin[1]


		return self.EvalField_XYSelf(zg - DeltaLong ,yg)






	#================================================
	#	 GetRayOutNominal
	#================================================
	@property
	def RayOutNominal(self):
		return tl.Ray(XYOrigin = self.XYCentre, Angle = self.AnglePropagation)


	#================================
	# FUN: LensMagnification
	#================================
	def LensMagnification(self, s1,f):
		'''
		Computes the magnification of a gaussian beam through a thin lens.

		For a elliptic mirror, use 1/f = 1/f1 + 1/f2

		Parameters
		-------------
		s1 : float
			object-lenst distance
		f : float
			focal length.
		'''

		zr = self.RayleighRange
		a = (1-(s1/f))**2
		b = (zr/f)**2
		c =  (a+b)**0.5
		m = 1/c
		return m



	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, Color = 'm', Length = 0.3, ArrowWidth = None, **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.

		'''
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		# a star, marking the centre
		plt.plot(self._XYOrigin[0], self._XYOrigin[1],  marker = '*', markersize = 10)
		RayOut = self.RayOutNominal
		U = tl.UnitVector(vx = RayOut.v[0], vy = RayOut.v[1], XYOrigin = self._XYOrigin)

		Length = Length if Length != None else 0.5
		U.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth)

		return FigureHandle
#	 END CLASS: SourceGaussian
#==============================================================================

##==============================================================================
##	 CLASS: SourceGaussian
##==============================================================================
#class SourceGaussian(object):
#	_Behaviour = OPTICS_BEHAVIOUR.Source
#	_TypeStr = 'gauss'
#	_TypeDescr = 'Gaussian Source'
#	#================================================
#	#	 __init__
#	#================================================
#	def __init__(self, Lambda, Waist0, ZOrigin = 0, YOrigin = 0, Theta = 0 ):
#		self.Lambda = Lambda
#		self.Waist0 = Waist0
#		self.Name = 'Gaussian source @ %0.2fnm' % (self.Lambda *1e9)
#
#		self.ZOrigin = ZOrigin
#		self.YOrigin = YOrigin
#		self.RhoZOrigin = np.array([YOrigin, ZOrigin])
#		self.ThetaPropagation = Theta
#	def Fwhm(self,z):
#		return self.Waist(z) * 2. * np.sqrt(np.log(2))
#
#	#================================================
#	#	 RayleighRange
#	#================================================
#	@property
#	def RayleighRange(self):
#		return   np.pi * self.Waist0**2 / self.Lambda
#	#================================================
#	#	 ThetaDiv
#	#================================================
#	@property
#	def ThetaDiv(self):
#		return  self.Lambda/np.pi/self.Waist0
#
#	#================================================
#	#	 WaistZ
#	#================================================
#	def Waist(self, z):
#		return self.Waist0 * np.sqrt(1+ (z/self.RayleighRange)**2)
#
#	#================================================
#	#	 RCurvature
#	#================================================
#	def RCurvature(self, z):
#		return z * (1+(self.RayleighRange/z)**2)
#
#	#================================================
#	#	 GouyPhase
#	#================================================
#	def GouyPhase(self,z):
#		return np.arctan(z/self.RayleighRange)
#
#	#================================================
#	#	 Phase
#	#================================================
#	def Phase(self, z,y):
#		k = 2 * np.pi / self.Lambda
#		Ph = (k*z + k *y**2/2/self.RCurvature(z) - self.GouyPhase(z))
#		ZeroPos = (z==0)  # gestisto eventuale singolarit?? nella fase
#		Ph[ZeroPos] = 0
#		return Ph
#	#================================================
#	#	 Cycles
#	#================================================
#	def Cycles(self,x = np.array(None) , z = np.array(None)):
#		'''
#		z: distance (m) scalar
#		x: 1darray, sampling
#		'''
#		return np.cos(self.Phase(x,z))
#
#	#================================================
#	#	 EvalField_XYSelf
#	#================================================
#	def EvalField_XYSelf(self,z = np.array(None) , y = np.array(None)):
#		'''
#			z ed y sono nel sistema di riferimento della gaussiana
#		'''
#		(z,y) = _MatchArrayLengths(z,y)
#
#		k = 2 * np.pi / self.Lambda
#
#		Ph = (k*z + k *y**2/2/self.RCurvature(z) - self.GouyPhase(z))
#		ZeroPos = (z==0)  # gestisto eventuale singolarit?? nella fase
#		try:
#			Ph[ZeroPos] = 0
#		except:
#			pass
#		Norm =	 (self.Waist0 / self.Waist(z))
#		A = np.exp(-y**2/self.Waist(z)**2)
#		return Norm * A * np.exp(+1j*Ph)
#
#	Eval = EvalField_XYSelf
#	EvalField_XYOb = EvalField_XYSelf
#
#
#	#================================================
#	#	 EvalField
#	#================================================
#	def EvalField_XYLab(self, x = np.array(None), y = np.array(None)):
#		(x,y) = _MatchArrayLengths(x,y)
#		'''
#		in qusta funciton ho introdotto il concetto per cui
#		x ?? la coordinata nel sistema di riferimento esterno
#		z ?? la distanza dal waist.
#		Questo fa si Waist(z), Radius(z) e simili vogliano l z
#		'''
#
#		#codice che dovrebbe funzionare ma che non va
#		'''
#		# cambio di coordinate da (x,y) lab a (xg,yg)
#		XYOrigin = np.array([self.ZOrigin, self.YOrigin])
#		[zg, yg] = CartChange(x,y, NewOrigin = XYOrigin, Theta = self.ThetaPropagation)
#		'''
#		# Ruoto il piano x,y di Theta attorno all'origina della gaussiana
#		myOrigin = np.array([self.ZOrigin, self.YOrigin])
#		myTheta = -self.ThetaPropagation
#		[zg,yg] = tl.RotXY(x,y, Origin = myOrigin, Theta = - self.ThetaPropagation)
#		zg = zg - myOrigin[0]
#		yg = yg - myOrigin[1]
#
#		'''
#		[zg,yg] = tl.RotXY(x,y, Origin = myOrigin, Theta = - self.ThetaPropagation)
#		zg = zg - myOrigin[0]
#		yg = yg - myOrigin[1]
#		'''
#		return self.EvalField_XYOb(zg,yg)
#
##	 END CLASS: SourceGaussian
##==============================================================================



#==============================================================================
#	 CLASS: DependentNumerical
#==============================================================================
class OpticsNumericalDependent(OpticsNumerical):
	''' Implements optics which are automatically generated by another optical element
	(such as the screen in the focal plane of a detector).

	Before they can be used, they must be refreshed with .Refresh.
	The first time that any method is invoked, the object is automatically refreshed.
	But if the ParentOptics is changed, then the .Refresh method must be automatically invoked.

	It sounds clumsy.... I hope I will remove it aasap
	'''

	_TypeStr = 'NUM'
	_TypeDescr = "Dependent Numerical"
	_Behaviour = OPTICS_BEHAVIOUR.Mirror
	_IsAnalytic = False
	_PropList = 	['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
					  'XYStart', 'XYCentre', 'XYEnd']

	#================================
	# FUN: __init__
	#================================
	def __init__(self, ParentOptics: Optics, GetXYFunction, **kwargs):
		self.ParentOptics = ParentOptics
		self._GetXYFunction = GetXYFunction
		self._GetXYFunctionArgs = kwargs
		self._FirstTime = True




	#================================
	# FUN: Refresh
	#================================
	def Refresh(self):
#		self._x, self._y = self.GetXY(N=3)
#		self.XYStart = np.array([self._x[0], self._y[0]])
#		self.XYEnd = np.array([self._x[2], self._y[2]])
#		self.XYCentre = np.array([self._x[1], self._y[1]])
#		self._L = np.linalg.norm(self.XYEnd - self.XYStart)
		self._FirstTime = False


	#================================
	# FUN: _CheckRefresh
	#================================
	def _CheckRefresh(self):
		if self._FirstTime == True:
			self.Refresh(self)


	#================================
	# FUN: GetXY
	#================================
	def GetXY(self,N=None):
		my_kwargs = self._GetXYFunctionArgs
		try:
			N_in_args = my_kwargs.pop('N')
		except:
			pass

		return self._GetXYFunction(N=N, **my_kwargs)

	#================================
	# PROP: XYStart
	#================================
	@property
	def XYStart(self):
		x, y = self.GetXY(N=3)
		XYStart = np.array([x[0], y[0]])
		return XYStart

	#================================
	# PROP: XYEnd
	#================================
	@property
	def XYEnd(self):
		x, y = self.GetXY(N=3)
		XYEnd = np.array([x[2], y[2]])
		return XYEnd

	#================================
	# PROP: XYCentre
	#================================
	@property
	def XYCentre(self):
		x, y = self.GetXY(N=3)
		XYCentre= np.array([x[1], y[1]])
		return XYCentre

	#================================
	# PROP: L
	#================================
	@property
	def L(self):
		x, y = self.GetXY(N=2)
		XYStart = np.array([x[0], y[0]])
		XYEnd = np.array([x[1], y[1]])
		return  np.linalg.norm(XYEnd - XYStart)

	#================================
	# PROP: VersorTan
	#================================
	@property
	def VersorTan(self):
		x, y = self.GetXY(N=99)
		n1 = np.argmax([x[49], x[51]])
		n0 = np.argmin([x[49], x[51]])
		vx = x[n1] - x[n0]
		vy = y[n1] - y[n0]
		U = tl.UnitVector(vx = vx, vy = vy, XYOrigin = self.XYCentre)
		return U
	#================================
	# PROP: VersorNorm
	#================================
	@property
	def VersorNorm(self):
		Ut = self.VersorTan
		ut = self.VersorTan.v
		un = tl.UnitVectorNormal(ut)
		Un = tl.UnitVector(v = un, XYOrigin = Ut.XYOrigin)
		return Un
	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, N = 100, Length = 1, ArrowWidth = None, Color = 'y', **kwargs):
		'''
		Paint the object
		'''
		# Paint the object
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		x_oe, y_oe = self.GetXY(N)
		plt.plot(x_oe, y_oe, Color + '.')
		# mark the mirror centre
		##plt.plot(self.XYCentre[0], self.XYCentre[1], Color + 'x')
		# paint the normal versor
		##self.VersorNorm.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth)
		# paint the inputray
		##self.RayInNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'g', Shift = True)
		# paint the output ray
		##self.RayOutNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'c')
		return Fig.number
	#================================
	#  PROP: AngleGrazing
	#================================
	@property
	def AngleGrazing(self):
		return self._AngleGrazing
	@AngleGrazing.setter
	def AngleGrazing(self):
		raise ValueError('AngleGrazing non se pol set')



#==============================================================================
#	 CLASS: Segment
#==============================================================================
class Segment(OpticsNumerical):
	'''
	It grows as a replioca of MirrorPlane.
	I did it for building apertures etc.
	The transmission function is contained in OpticsNumerical

			Parameters
		---------------------
		XYLab_Centre : [x,y]
			Coordinates of the centre of the mirror
		AngleIn: float (radians)
			Angle of the incidence ray in the laboratory reference frame.
		GrazingAngle : angle, radians
			Grazing angle which must be preserved between the mirror and the InputAngleLab.
			It is used to compute MirrorAngle
		L : Physical size of the mirror
	Internal parameters
	-------------------
	The internal parameters which are stored in the object to define the plane
	mirror are

	- _XYLab_Centre : [x,y] the centre of the mirror in the lab reference frame
	- _VersorNorm : (type: UnitVector) the versor normal to the mirror surface
	- _L : the mirror physical size.

	Secondary but important parameters
	-------------------
	These parameters are stored in the object, and are linked to the primary ones.
	Some of them may be redundant, but the important point is that they are all
	synced with each other.

	- AngleGrazing: the grazing angle of incidence betweeen AngleIn and the mirror
	- AngleIn: the angle of the incident wavevactor (or ray) (in the laboratory reference frame)
	- AngleTan: the angle of the tangent to the mirror (in the lab reference frame)
	- AngleNorm: equal to AngleTan + np.pi/2, and equal to VersorNorm.vAngle.
	- XYStart: upstream point of the mirror
	- XYEnd: downstream point of the mirror

	'''
	_TypeStr = 'segment'
	_TypeDescr = "segment"
	_Behaviour = None
	_IsAnalytic = False
	_PropList = 	['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
					  'XYStart', 'XYCentre', 'XYEnd']

	#================================
	#  FUN: __init__
	#================================
	def __init__(self, L = None, AngleGrazing = None, XYLab_Centre = [0,0], AngleIn= 0):
		#Mirror.__init__(self)
		super(OpticsNumerical, self).__init__()
		'''
		Parameters
		---------------------
		XYLab_Centre : [x,y]
			Coordinates of the centre of the mirror
		AngleIn: float (radians)
			Angle of the incidence ray in the laboratory reference frame.
		AngleGrazing : angle, radians
			Grazing angle which must be preserved between the mirror and the InputAngleLab.
			It is used to compute MirrorAngle
		'''
		# BUILDING
		if tl.CheckArg([L, AngleGrazing]):
			self._L = L
			self._AngleGrazing = AngleGrazing
			self.SetXYAngle_Centre(XYLab_Centre, AngleIn)
		else:
			tl.ErrMsg.InvalidInputSet


	#================================
	#  FUN: __str__
	#================================
	def __str__(self):
#		PropList = ['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
#					  'XYStart', 'XYCentre', 'XYEnd']
		StrList = ['%s=%s' %( PropName, getattr(self,PropName)) for PropName in Segment._PropList ]
		return 'plane \n' + 20 * '-' + '\n' + '\n'.join(StrList) + '\n' + 20 * '-'

	#==============================
	#  PROP: VersorNorm
	#================================
	@property
	def VersorNorm(self) -> tl.UnitVector:
		return self._VersorNorm

	@VersorNorm.setter
	def VersorNorm(self, value) -> tl.UnitVector:
		self._VersorNorm = value #  UnitVersor type
		self._VersorNorm.XYOrigin = self.XYCentre

		self._AngleNorm = self._VersorNorm.vAngle
		self._AngleTan = self._VersorNorm.vAngle - np.pi/2
		self._UpdateParameters_Lines()
		self._UpdateParameters_XYStartEnd()

	#================================
	#  PROP: XYCentre
	#================================
	@property
	def XYCentre(self):
		# patch
		return np.array(self._XYLab_Centre)
	@XYCentre.setter
	def XYCentre(self,value):
		 self._XYLab_Centre = np.array(value)
		 self._UpdateParameters_Lines()
		 self._UpdateParameters_XYStartEnd()

	#==============================
	#  PROP: L
	#================================
	@property
	def L(self):
		return self._L
	@L.setter
	def L(self, value):
		self._L= value
		self._UpdateParameters_XYStartEnd()


	#================================
	#  PROP: AngleIn
	#================================
	@property
	def AngleIn(self):
		return self._AngleIn

	#================================
	#  PROP: AngleGrazing
	#================================
	@property
	def AngleGrazing(self):
		return self._AngleGrazing
	@AngleGrazing.setter
	def AngleGrazing(self):
		raise ValueError('AngleGrazing non se pol set')

	#================================
	#  PROP: AngleTan
	#================================
	@property
	def AngleTan(self):
		return self._AngleTan

	#================================
	#  PROP: AngleNorm
	#================================
	@property
	def AngleNorm(self):
		return self._AngleNorm

	#================================
	#  PROP: Line_Tan
	#================================
	@property
	def Line_Tan(self):
		'''
		Line np.tan is the line tangent to the mirror surface, viz the equation
		of the mirror itself
		'''
		m = np.tan(self.AngleTanLab)
		q = self.XYCentre[1] - m * self.XYCentre[0]
		return tl.Line(m,q)
#		return self._Line_Tan

	#================================
	#  PROP: XYStart
	#================================
	@property
	def XYStart(self):
		return self._XYLab_Start
	#================================
	#  PROP: XYEnd
	#================================
	@property
	def XYEnd(self):
		return self._XYLab_End


 	#================================
	# GetXY_IdealMirror(N)
	#================================
	def GetXY_Segment(self, N = 100  ):
		'''
		Return the coordinates of the ideal mirror

		Return
		--------------------
		x : np.array
			x points
		y : np.array
			y:point
		'''

		x = np.linspace(self.XYStart[0], self.XYEnd[0],N)
		y = self.Line_Tan.m*x +self.Line_Tan.q

		return x,y

 	#================================
	# GetXY
	#================================
	def GetXY(self, N, Options =['ideal'] ):
		return self.GetXY_Segment(N)

	#================================
	# Get_LocalTangentAngle
	#================================
	def Get_LocalTangentAngle(self, x0, y0, ProperFrame = False):
		return self.VersorTan.Angle

 	#================================
	# SetXYAngle_Centre
	#================================
	def SetXYAngle_Centre(self, XYLab_Centre, AngleIn ):
		self._XYLab_Centre = XYLab_Centre
		self._AngleIn = AngleIn
		AngleTan = AngleIn + self.AngleGrazing
		# Defines: Versos, AngleNorm, AngleTan
		UV = tl.UnitVector(Angle = AngleTan + np.pi/2) # Old definition: when the primary variable was VersorNorm and not VersorTan
		self.VersorNorm = UV
		# self.VersorTan = UnitVector(Angle = AngleTan) # attempt of new definition, but it is not safe



	#================================
	# FUN: _UpdateParameters_XYStartEnd
	#================================
	def _UpdateParameters_XYStartEnd(self):
		# Uses: _XYLab_Centre, _VersorNorm
		# Defines: XYStart, XYEnd
		# Called: in __init__
		# According to the y component of .VersorNorm, I define the
		# start and end points of the mirror.

		XY_a = self._XYLab_Centre + self.L/2 * self.VersorNorm.vNorm
		XY_b = self._XYLab_Centre - self.L/2 * self.VersorNorm.vNorm

		if XY_a[0] < XY_b[1]:
			self._XYLab_Start = XY_a
			self._XYLab_End = XY_b
		elif XY_a[0] >= XY_b[1]:
			self._XYLab_Start = XY_b
			self._XYLab_End = XY_a

	#================================
	# FUN: _UpdateParameters_Lines
	#================================
	def _UpdateParameters_Lines(self):
		# Uses: XYCentre, _AngleTan
		# Called: in init, When XYCentre is changed;

		m = np.tan(self._AngleTan)
		q = self.XYCentre[1] - m * self.XYCentre[0]
		self._Line_Tan = tl.Line(m, q)
	#================================================
	#	GetRayOutNominal
	#	INTERFACE FUNCTION
	# 	(called in Fundation.OpticalElement)
	#================================================


	#================================
	# PROP: GetRayInNominal
	#================================
	@property
	def RayInNominal(self):
		v = tl.UnitVector(Angle = self.AngleIn).v
		return tl.Ray(vx = v[0], vy = v[1], XYOrigin = self.XYCentre)

	#================================
	# PROP: RayOutNominal
	#================================
	@property
	def RayOutNominal(self):
		'''
		Equal to RayInNominal, but of oppposite sign.
		'''
		v = tl.UnitVector(Angle = self.AngleIn).v
		return tl.Ray(vx = -v[0], vy = -v[1], XYOrigin = self.XYCentre)

	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, N = 100, Length = 1, ArrowWidth = None, Color = 'm', **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.
		N is the number of samples.
		'''
		# Paint the mirror
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		x_mir, y_mir = self.GetXY_IdealMirror(N)
		plt.plot(x_mir, y_mir, Color + '.')
		# mark the mirror centre
		plt.plot(self.XYCentre[0], self.XYCentre[1], Color + 'x')
		# paint the normal versor
		self.VersorNorm.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth)
		# paint the inputray
		self.RayInNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'g', Shift = True)
		# paint the output ray
		self.RayOutNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'c')
		return FigureHandle
	#================================
	#  Draw
	#================================
	def Draw(self, N=100):
		x,y  = tl.geom.DrawSegmentCentred(self._L, self.XYCentre[0], self.XYCentre[1], self.Angle,N)
		return x,y
	#================================
	#  _Draw
	#================================
#==============================================================================
#	 CLASS: Obstruction
#==============================================================================
class Obstruction(Segment):
	'''
	It grows as a replioca of MirrorPlane.
	I did it for building apertures etc.
	The transmission function is contained in OpticsNumerical

			Parameters
		---------------------
		XYLab_Centre : [x,y]
			Coordinates of the centre of obstruction
		AngleIn: float (radians)
			Angle of the incidence ray in the laboratory reference frame (.
		GrazingAngle : angle, radians
			Grazing angle which must be preserved between the mirror and the InputAngleLab.
			It is used to compute MirrorAngle
		L : Physical size of the mirror

	Internal parameters
	-------------------
	The internal parameters which are stored in the object to define the plane
	mirror are

	- _XYLab_Centre : [x,y] the centre of the mirror in the lab reference frame
	- _VersorNorm : (type: UnitVector) the versor normal to the mirror surface
	- _L : the mirror physical size.

	'''
	_TypeStr = 'obs'
	_TypeDescr = "obstruction"
	_Behaviour = None
	_IsAnalytic = False
	_PropList = 	['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
					  'XYStart', 'XYCentre', 'XYEnd']

	#================================
	#  FUN: __init__
	#================================
	def __init__(self, L, D, AngleGrazing = np.pi/2, XYLab_Centre = [0,0], AngleIn = 0):
		super(Segment, self).__init__(L = L, AngleGrazing = AngleGrazing , XYLab_Centre = XYLab_Centre , AngleIn = AngleIn)

		self._ObstructionWidth = D
		self._L = L

	#================================
	#  FUN: TransmissionFunction
	#================================
	def TransmissionFunction(x,y):

		T = np.array(x) * 1
		if self.AngleGrazing == np.pi/2:
			ymax = np.max(self.XYStart[1], self.XYEnd[1])
			ymin= np.min(self.XYStart[1], self.XYEnd[1])
			PosList = (ymin > y > ymax)
			T[PosList] = 0
			return T



#
##==============================================================================
##	 CLASS: Metrology
##==============================================================================
#class FigureError():
#	self
#
#
##==============================================================================
##	 CLASS: Metrology
##==============================================================================
#class Metrology(object):
#
#
#
#
#	class Roughness():
#

#==============================================================================
#	 CLASS: Mirror
#==============================================================================
class Mirror(OpticsNumerical):
	'''
	Mirror specifications & positioning
	------
	L : mirror length
	XYStart, XYEnd : coords of first and last mirror pointss

	Abstract methods which must be implemented
	GetOutputRay : Compute the output ray (according to an imput ray)
	_EvalMirrorYProp : Evaluate the mirror equation over X domain, returning Y

	About Figure Error and Roughness
	------
	FigureErrors : N x M np.array containing M figure error profiles (N samples each)
	Roughness : RoughnessMaker object
	'''
	class _ClassOptions(object):
		def __init__(self):
			self.AUTO_UPDATE_MIRROR_LENGTH = False
			self.USE_FIGUREERROR = True
			self.USE_ROUGHNESS = False



	#================================
	# __init__[Mirror]
	#================================
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


		self.Options = Mirror._ClassOptions()
		# About Figure Error
		self._FigureErrors = []
		self._FigureErrorSteps = []
		self.LastFigureErrorUsed = np.array([])
		self.LastFigureErrorUsedIndex = None # the last figure error used

		# About Rougness
		self._Roughness = Noise.RoughnessMaker
		self.LastRoughnessUsed = np.array([])
		self._EvalWithX = True

		pass
	#================================
	# ABSTRACT: GetOutputRay(N)
	#================================
	def GetOutputRay():
		pass
	#================================
	# ABSTRACT: GetXY_IdealMirror(N)
	#================================
	def _EvalMirrorYProp(self,x, *args):
		''' 	Returns the coordinates of the mirror.

		'''
		pass

	#================================
	#  PROP: AngleGrazingNominal
	#================================
	@property
	def AngleGrazingNominal(self):
		return self._AngleGrazingNominal

	#================================
	# GetSampling(N) [Mirror]
	#================================
	def GetXY_Sampling(self, N, L):
		'''
		I sample the mirror (using the _EvalMirrorYProp method)  with uniform spacing
		(given by Step = L/N) 		along the tangent of the mirror.

		Parameters
		------
		N : int
			Number of points.
		L : float
			Physical length used to compute the step spacing Step = L/N.
			In ideal condition L is the nominal length of the mirror.
			If a figure error is used, then the measured legnth must be used.
		'''

		# Codice forse sbagliato ed inutilmente barocco
		# x,y = tl.SamplingAlongLine(self.AngleTanLab, self.XYCentre, L, N)
		L = L if L!= None else self.L
		XYStart, XYEnd = self._ComputeXYStartXYEnd(L)

		x = np.linspace(XYStart[0], XYEnd[0], N)
		m = self.AngleLab
		q = XYStart[1] - m*XYStart[0]

		return x,y


	#================================
	# _GetFigureErrorSummationSign
	#================================
	def _GetFigureErrorSummationSign(self):
		'''
		Basing on the direction of RayInNominal, it returns the sign that must have the height profile of the
		figure error.

		'''
		Ray = self.RayInNominal
		if np.abs(Ray.v[1]) > 1e-30: # if y component !=0
			YSign = np.sign(Ray.v[1])
			return - YSign
		else:
			XSign = np.sign(Ray.v[0])
			return -XSign

	#================================
	# GetXY_IdealMirror(N) [class: mirror]
	#================================
	def GetXY_IdealMirror(self, N, Sign=+1, ReferenceFrame=None, L=None):
		'''
			Vecchia versione. Volevo sostituirla con una nuova che andasse bene per tutti
			(specchi piani ed ellittici).
			Per il momento ho solo fatto un gran casino.
			La ripesco dal backup.

			Notice
			-----

			ReferenceFrame : Unused.
					Possible free parameter from Optics.GetXY_IdealMirror

			L: Unused

		'''
		x = np.linspace(self.XYStart[0], self.XYEnd[0], N)
		return [x,self.EvalMirrorY(x, Sign)]

	#================================
	# GetXY_IdealMirror(N) [mirror class]
	#================================
	def GetXY_IdealMirror__dismissed_and_wrong(self, N, Sign = +1, L = None, ReferenceFrame = 'lab'):
		'''
		descvrivere

		'''
		# Getting the x,y sampling (along the tangent to the mirror)
		#-----------------------------------------------------------------
		if L == None:  # nominal length
			x,y = self.GetXY_Sampling( N , self.L)
		else:	      #measured length
			x,y = self.GetXY_Sampling( N , L)

		# Evaluating the ellipse
		#-----------------------------------------------------------------
		if self._EvalWithX == True:
			y = self._EvalMirrorYProp(x, Sign)
		else:
			x = self._EvalMirrorYProp(y, Sign)


		# Rotating in the Lab Reference, if needed
		#-----------------------------------------------------------------
		if ReferenceFrame == 'lab':
			x,y = self._Transformation_XYPropToXYLab(x,y)
		return [x,self._EvalMirrorYProp(x, Sign)]

	#================================
	# GetXY_MeasuredMirror (class: Mirror)
	#================================
	def GetXY_MeasuredMirror(self, N, iFigureError = 0, Reference = 'lab' ):
		'''
		Returns the (x,y) coordinates of a "real" mirror, generated as
		Real mirror = Ideal Mirrir + Figure Error pofile + Roughness profile

		This function shall be called by self.GetXY


		Parameters
		-------
		N : int
			number of samples
		iFugreError : int
			Index of the FigureError to use
			If iFigureError = None, then iFigureError = iLastFigureErrorUsed + 1 is used.
			@todo: diatriba se iFigureError debba stare qui o in configuration setting
		Reference : string {lab,self}
			wheter the output is given in the lab reference or "self" reference

		Uses
		-----
		self.ComputationSettings.UseRoughness : (class member)

		Return
		-----
		x,y : arrays
			Coordinates of the mirror.

		'''
		N = int(N)
		# carico il figure error e, se necessario, lo ricampiono
		#-----------------------------------------------------------------
		if len(self._FigureErrors)-1 >= iFigureError:
			hFigErr  = self.FigureErrors[iFigureError]
			LMeasured = len(hFigErr) * self._FigureErrorSteps[iFigureError]
			self._L = LMeasured  # serve davvero?
			hFigErr  = rm.FastResample1d(hFigErr - np.mean(hFigErr  ), N)
		else:
			hFigErr   = np.zeros(N)
			LMeasured = self.L

		# Get the ideal mirror (in the self- Reference frame)
		# -----------------------------------------------------------------
		Mir_x, Mir_y = self.GetXY_IdealMirror(N, ReferenceFrame = 'self', L = LMeasured)
		#HACK: GetXY_IdealMirror and ReferenceFrame
		'''ReferenceFrame is something that was originally used only in EllipticalMirror
		Are we sure that we want to keep it as generic parameter in optics?
		What for Otics which do not need it? (e.g. PlaneMirror)
			=> Use None? good candidate
			=> Improve polimorfism?
			=> Use **kwargs ?
		'''

		# aggiungo la roughness (se richiesto, rigenero il noise pattern)
		#-----------------------------------------------------------------
		if self.ComputationSettings.UseRoughness == True:
			hRoughness = self.Roughness.MakeProfile(LMeasured, N)
			########################### added by L.Rebuffi
			if len(hRoughness) < N:
				filler = np.zeros(N-len(hRoughness))
				hRoughness = np.append(filler, hRoughness)
			##############################################
			self.LastRoughnessUsed = hRoughness
			myResidual = hFigErr + hRoughness
		else:
			myResidual = hFigErr
		#HINT: LastResidualUsed
		self.LastResidualUsed = myResidual
		self.LastFigureErrorUsed = myResidual
		self.LastFigureErrorUsedIndex = iFigureError

		# Add figure error - FigureErrorAdd
		# I Project the figure error on the Mirror Surface
		# -----------------------------------------------------------------
		# colpo di fulmine! :-)
		ThetaList = self.Get_LocalTangentAngle(Mir_x, Mir_y)
		ResidualToUse = myResidual * self._GetFigureErrorSummationSign()
		Mir_xx = Mir_x + ResidualToUse * np.sin(ThetaList)
		Mir_yy = Mir_y + ResidualToUse * np.cos(ThetaList)

		if Reference == 'lab':
			# Notice: This transformation is an IDENTITY by default. Only for specific
			# classes (e.g. MirrorElliptic) it really does something
			Mir_xx, Mir_yy = self._Transformation_XYPropToXYLab(Mir_xx, Mir_yy)

		return Mir_xx, Mir_yy

	#================================
	# GetXY_MeasuredMirror
	#================================
	def GetXY_MeasuredMirror_new_and_wrong(self, N, iFigureError = 0, Reference = 'lab' ):
		'''
		Returns the (x,y) coordinates of a "real" mirror, generated as
		Real mirror = Ideal Mirrir + Figure Error pofile + Roughness profile

		This function shall be called by self.GetXY

		Parameters
		-------
		N : int
			number of samples
		iFugreError : int
			Index of the FigureError to use
			If iFigureError = None, then iFigureError = iLastFigureErrorUsed + 1 is used.
			@todo: diatriba se iFigureError debba stare qui o in configuration setting
		Reference : string {lab,self}
			wheter the output is given in the lab reference or "self" reference

		Uses
		-----
		self.ComputationSettings.UseRoughness : (class member)

		Return
		-----
		x,y : arrays
			Coordinates of the mirror.

		'''

		# carico il figure error e, se necessario, lo ricampiono
		#-----------------------------------------------------------------
		if len(self._FigureErrors)-1 >= iFigureError:
			hFigErr  = self.FigureErrors[iFigureError]
			LMeasured = len(hFigErr) * self._FigureErrorSteps[iFigureError]
			self._L = LMeasured  # serve davvero?
			hFigErr  = rm.FastResample1d(hFigErr - np.mean(hFigErr  ), N)
		else:
			hFigErr   = np.zeros(N)
			LMeasured = self.L

		# Get the ideal ellipse (in the self- Reference frame)
		# -----------------------------------------------------------------
		Mir_x, Mir_y = self.GetXY_IdealMirror(N, ReferenceFrame = 'self', L = LMeasured)

		# aggiungo la roughness (se richiesto, rigenero il noise pattern)
		#-----------------------------------------------------------------
		if self.ComputationSettings.UseRoughness == True:
			hRoughness = self.Roughness.MakeProfile(LMeasured, N)
			########################### added by L.Rebuffi
			if len(hRoughness) < N:
				filler = np.zeros(N-len(hRoughness))
				hRoughness = np.append(filler, hRoughness)
			##############################################
			self.LastRoughnessUsed = hRoughness
			myResidual = hFigErr + hRoughness
		else:
			myResidual = hFigErr

		self.LastResidualUsed = myResidual
		self.LastFigureErrorUsed = myResidual
		self.LastFigureErrorUsedIndex = iFigureError

		# I Project the figure error on the Ellipse
		# -----------------------------------------------------------------
		ThetaList = self.Get_LocalTangentAngle(Mir_x, Mir_y)
		Mir_xx = Mir_x + myResidual * np.sin(ThetaList)
		Mir_yy = Mir_y + myResidual * np.cos(ThetaList)

		if Reference == 'lab':
			Mir_xx, Mir_yy = self._Transformation_XYPropToXYLab(Mir_xx, Mir_yy)

		return Mir_xx, Mir_yy

 	#================================
	# GetXY [Mirror]
	#================================
	def GetXY(self, N):
		'''
		Main User-interface function for getting the x,y points of the mirror
		in the laboratory reference frame.

		Uses the self.ComputationSettings parameters for performing the computation

		Parameters
		-----
		N : int
			Number of samples.

		Uses
		-----
		self.ComputationSettings : (class member)
			See computation settings.

		'''


		if self.ComputationSettings.UseIdeal == True:
			xLab, yLab = self.GetXY_IdealMirror(N)
		else:
			xLab, yLab = self.GetXY_MeasuredMirror(N)

		# Apply small perturbations?
		if self.ComputationSettings.UseSmallDisplacements:
			xLab, yLab = self._ApplySmallDisplacements(xLab, yLab)

		else:
			pass

		return xLab, yLab
#			print("1 Mirror.GetXY: Option set not implemented. \n Options = %s" % str(Options))

#	#================================
#	# VersorTan
#	#================================
#	@property
#	def VersorTan(self)-> UnitVector:
#		return self.VersorNorm.GetNormal()

	#================================
	# _SetMirrorCoordinates
	#================================
	def _SetMirrorCoordinates(self, XMid, L):
		'''
		Given the longitudinal (X) position of the middle-point of the mirror
		and the mirror length, it defines XYStart and XYEnd.
		'''

		XStart = XMid - 0.5*L
		self.XYStart = np.array([XStart, self.EvalY(XStart)])
		XEnd = XMid + 0.5* L
		self.XYEnd  = np.array([XEnd, self.EvalY(XEnd)])
		self._L = L

	#================================
	# PROP: Roughness
	#================================
	@property
	def Roughness(self):
		'''
		'''
		return self._Roughness
	#================================
	# PROP: FigureErrors
	#================================
	@property
	def FigureErrors(self): return self._FigureErrors
	#================================
	# PROP: FigureErrorSteps
	#================================
	@property
	def FigureErrorSteps(self): return self._FigureErrorSteps

	#================================
	# FigureErrorLoad
	#================================
	def FigureErrorLoad(self,
						h: float=None,
						Step: float=1e-3,
						File: str='',
						AmplitudeScaling: float=1,
						Append: bool=False,
						SubtractMean=False,
						FileFormat=0,
						SkipRows=0,
						AmplitudeSign = 1):

		'''
		Appends a 1darray to the list of Figure Errors.

		The function is the result of progressive coding, so it is far for being crystal-clear.

		In the ideal case, it would be nice to use the "File" parameter. However, pretty much
		depends on the file format, and the function is not trained to handle so many data formats.

		For this reason, it is safer to use "h" and "Step" arguments.

		Parameters
		--------------------
		h : 1d array.
			Figure error. 	Assumed to be evenly spaced. Stored in FigureErrors. Alternative to: File

		Step : Scalar
			lateral spacing of h samples. Stored in FigureErrorSteps.


		File : string
			Path to the data file

		AmplitudeScaling : float
			Factor multiplying the value of h.

		Append : bool
			If Append = False, it clears the existing list of FigureErrors.

		FileFormat: 0, 1, 2
			0: Single column (height)
			1: Single column (slopes)
			2: Two columns (position, height)

		SkipRows: int
			Number of rows to skip.

		@ToRepair: adjustment of mirror length
		'''
		# WARNING
		# I added this patch line on July 2020, afer creating  CoreOptics._GetFigureErrorSummationSign()
		# because a) in principle there should not be need of inverting figure error sign manually and
		# b) I have a lot of files where Amplitude is set to -1 manually. So the two effects would
		# compensate.
		#If you do want to invert amplitude, use InvertAmplitude = True instead

		# begin patch
		AmplitudeScaling = np.abs(AmplitudeScaling)
		AmplitudeSign = np.sign(AmplitudeSign)
		AmplitudeScaling *= AmplitudeSign
		# end patch

		# Data is read from file
		if h is None and File!= '':
			h = np.loadtxt(File) * AmplitudeScaling
		# Data is passed as argument
		else:
			h = h * AmplitudeScaling

		if SubtractMean:
			h = h - np.mean(h)
		if Append == False:
			# empties the buffer.
			self._FigureErrors = []
			self._FigureErrorSteps = []

		self._FigureErrors.append(h)
		self._FigureErrorSteps.append(Step)

		if self.Options.AUTO_UPDATE_MIRROR_LENGTH:
			NewL = len(h)*Step
			self._SetMirrorCoordinates(self.XYCentre[0], NewL)

	#================================
	# FigureErrorRemove
	#================================
	def FigureErrorRemove(self,i):
		self._FigureErrors.remove(i)

	#=============================================================#
	# FUN FigureErrorLoadFromFile
	#=============================================================#
	def FigureErrorLoadFromFile(self, PathFile : str,
						 FileType = FIGURE_ERROR_FILE_FORMAT.HEIGHT_ONLY,
						 Step = 1e-3,
						 Delimiter = '\t',
						 SkipLines = 0,
						 XScaling = 1e-3,
						 YScaling = 1,
						 **kwargs):
		'''
		This function is a helper function that read a figure error file, then calls the
		lower lever FigureErrorLoad function

		'''
		if FileType == FIGURE_ERROR_FILE_FORMAT.HEIGHT_ONLY:

			Height = tl.FileIO.ReadYFile(PathFile, SkipLines=SkipLines)
			Height *= YScaling
			Step = Step

		elif FileType == FIGURE_ERROR_FILE_FORMAT.POSITION_AND_HEIGHT:

			x, Height = tl.FileIO.ReadYFile(PathFile, SkipLines=SkipLines)
			x *= XScaling

			Height *= YScaling
			Step = np.mean(np.diff(x))

		elif FileType == FIGURE_ERROR_FILE_FORMAT.SLOPE_ONLY:

			x, Height = tl.FileIO.ReadYFile(PathFile, SkipLines=SkipLines)
			x *= XScaling

			Height *= YScaling
			Step = np.mean(np.diff(x))

		elif FileType == FIGURE_ERROR_FILE_FORMAT.ELETTRA_LTP_JAVA1:
			x,h, ComputedStep = tl.Metrology.ReadLtpLtpJavaFileA(PathFile,
												   Decimation = 2,
													ReturnStep = True,
													XScaling = 1e-3, # input is in mm
													YScaling = 1e-3)    # input isk in mm
			Height = h*YScaling
			Step = ComputedStep

		elif FileType == FIGURE_ERROR_FILE_FORMAT.ELETTRA_LTP_DOS:
			x,y,FileInfo  = tl.Metrology.ReadLtp2File(PathFile) # read slopes

			if PathFile.suffix.upper() == '.SLP':
				h = tl.Metrology.SlopeIntegrate(y,dx = FileInfo.XStep) # integrate slopes
			elif PathFile.suffix.upper() == '.HGT':
				h = y

			Height = h
			Step = FileInfo.XStep

		# update the parent object
		#-----------------------------------------------------------------------
		AmplitudeSign = np.sign(YScaling) # this is clumsy but was added after "colpo di fulmine" in optics
		self.FigureErrorLoad(h=Height,
							 Step=Step,
							 AmplitudeScaling=YScaling,
							 Append=False,
							 AmplitudeSign=np.sign(YScaling))
		return Height, Step

#	#================================
#	# FigureErrorAddToIdealProfile [Mirror]
#	#================================
#	def FigureErrorAddToIdealProfile(self, myResidual):
#		'''Assume che la lunghezza fisica di myResidual sia uguale a quella di self.L (che ?? ci?? che accate se Options.)
#		Requires
#		-------------------
#		- GetXY_IdealMirror(N)
#		- .Get_LocalTangentAngle
#
#		Design notes
#		-----
#		Based on: _AddResidualToMirrorElliptic
#		'''
#
#		N = size(myResidual)
#		[Mir_x, Mir_y] = self.GetXY_IdealMirror(N) # already in the lab frame
#
#		ThetaList = self.Get_LocalTangentAngle(Mir_x, Mir_y)
#		NewMir_x = Mir_x + myResidual * np.sin(ThetaList)
#		NewMir_y = Mir_y + myResidual * np.cos(ThetaList)
#		return (NewMir_x, NewMir_y)

#==============================================================================
#	 CLASS: MirrorPlane
#==============================================================================
class MirrorPlane(Mirror):
	'''

			Parameters
		---------------------
		XYLab_Centre : [x,y]
			Coordinates of the centre of the mirror
		AngleIn: float (radians)
			Angle of the incidence ray in the laboratory reference frame.
		GrazingAngle : angle, radians
			Grazing angle which must be preserved between the mirror and the InputAngleLab.
			It is used to compute MirrorAngle
		L : Physical size of the mirror
	Internal parameters
	-------------------
	The internal parameters which are stored in the object to define the plane
	mirror are

	- _XYLab_Centre : [x,y] the centre of the mirror in the lab reference frame
	- _VersorNorm : (type: UnitVector) the versor normal to the mirror surface
	- _L : the mirror physical size.

	Secondary but important parameters
	-------------------
	These parameters are stored in the object, and are linked to the primary ones.
	Some of them may be redundant, but the important point is that they are all
	synced with each other.

	- AngleGrazing: the grazing angle of incidence betweeen AngleIn and the mirror
	- AngleIn: the angle of the incident wavevactor (or ray) (in the laboratory reference frame)
	- AngleTan: the angle of the tangent to the mirror (in the lab reference frame)
	- AngleNorm: equal to AngleTan + np.pi/2, and equal to VersorNorm.vAngle.
	- XYStart: upstream point of the mirror
	- XYEnd: downstream point of the mirror

	'''
	_TypeStr = 'PM'
	_TypeDescr = "Plane Mirror"
	_Behaviour = OPTICS_BEHAVIOUR.Mirror
	_IsAnalytic = False
	_PropList = 	['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
					  'XYStart', 'XYCentre', 'XYEnd']
	_CommonInputSets = [(('L','Length' ),
						('AngleGrazing','Grazing Angle')),
					  ]
	_MementoVariables = ('_L')
	#================================
	#  FUN: __init__[MirroPlane]
	#================================
	def __init__(self,
			   L: 'user1'  = None,
			   AngleGrazing :'user1' = None,
			   XYLab_Centre = [0,0],
			   AngleIn : 'user1' = 0,
			   **kwargs):
		super().__init__(**kwargs)
		'''
		Parameters
		---------------------
		XYLab_Centre : [x,y]
			Coordinates of the centre of the mirror
		AngleIn: float (radians)
			Angle of the input ray in the laboratory reference frame.
		AngleGrazing : angle, radians
			Grazing angle which must be preserved between the mirror and the InputAngleLab.
			It is used to compute MirrorAngle
		'''
		# BUILDING
		if tl.CheckArg([L, AngleGrazing]):
			self._L = L
			self._AngleGrazingNominal = AngleGrazing
			self.SetXYAngle_Centre(XYLab_Centre, AngleIn)
		else:
			tl.ErrMsg.InvalidInputSet

		self._UpdateParameters_Lines()
		self._UpdateParameters_XYStartEnd()


	#================================
	#  FUN: __str__
	#================================
	def __str__(self):
#		PropList = ['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
#					  'XYStart', 'XYCentre', 'XYEnd']
		StrList = ['%s=%s' %( PropName, getattr(self,PropName)) for PropName in MirrorPlane._PropList ]
		return 'Plane mirror\n' + 20 * '-' + '\n' + '\n'.join(StrList) + '\n' + 20 * '-'

	#================================
	# PROP OVERRIDE:
	#================================
#	@property
#	def AngleLab(self) -> float:
#		return super().AngleLab.__get__()

#	@OpticsNumerical.AngleLab.setter
#	def AngleLab(self, Value):
#		super().AngleLab.__set__(Value)
#		self._UpdateParameters_XYStartEnd()
#		Debug.Print('si cazzo =========================')


	#================================
	#  PROP EXTENSION: XYCentre
	#================================
	def XYCentre(self,value):
		super.XYCentre = value
		self._UpdateParameters_XYStartEnd()

	#==============================
	#  PROP: L
	#================================
	@property
	def L(self):
		return self._L
	@L.setter
	def L(self, value):
		self._L= value
		self._UpdateParameters_XYStartEnd()



	#================================
	#  PROP: AngleInputLabNominal
	#================================
	@property
	def AngleInputLabNominal(self):
		'''
		Angle (in the Lab reference) of the incident beam.
		Computed using: AngleLab and AngleGrazingNominal
		Depends on Mirror type.

		'''
		return self.AngleLab - np.pi/2 - self.AngleGrazingNominal

#	#================================
#	#  PROP: AngleGrazing
#	#================================
#	@property
#	def AngleGrazing(self):
#		return self._AngleGrazing
#	@AngleGrazing.setter
#	def AngleGrazing(self):
#		raise ValueError('AngleGrazing non se pol set')

#	#================================
#	#  PROP: AngleTan
#	#================================
#	@property
#	def AngleTan(self):
#		return self._AngleTan
#
	#================================
	#  PROP: AngleNorm
	#================================
	@property
	def AngleNorm(self):
		return self._AngleNorm

	#================================
	#  PROP: Line_Tan
	#================================
	@property
	def Line_Tan(self):
		"""
		Line object, containing the tangent to the mirror
		"""
		return self._Line_Tan

	#================================
	#  PROP: XYStart
	#================================
	@property
	def XYStart(self):
		return self._XYLab_Start

	#================================
	#  PROP: XYEnd
	#================================
	@property
	def XYEnd(self):
		return self._XYLab_End


 	#================================
	# GetXY_IdealMirror(N)
	#================================
	def GetXY_IdealMirror(self, N=100, ReferenceFrame=None, L=None):
		'''
		Return the coordinates of the ideal mirror.

		Return
		--------------------
		x : array
			x points
		y : array
			y:point
		'''
		N = int(N)
		if (self.XYStart[0]!= self.XYEnd[0]):
			x = np.linspace(self.XYStart[0], self.XYEnd[0],N)
			y = self.Line_Tan.m*x +self.Line_Tan.q
		else: # handles the case of vertical mirror
			x = np.float(self.XYStart[0]) + np.zeros(N)
			y = np.linspace(self.XYStart[1], self.XYEnd[1],N)
		return x,y


	"""
 	#================================
	# GetXY
	#================================
	def GetXY(self, N, Options =['ideal'] ):
		'''
		Main User-interface function for getting the x,y points of the mirror
		in the laboratory reference frame.

		Options can be
		- 'ideal' : the ideal mirror profile is used (default)
		- 'perturbation' : instead of the nominal position of the mirror, the position of the mirror computed via  longitudinal, transverse and angular
		 "perturbations" around the nominal configuration.
		- 'figure error' : a figure error is added to the mirror profile, if possible
		- 'roughness' : a roughness profile is added to the mirror profile, if possible
		'''
		if 'ideal' in Options:
			return self.GetXY_IdealMirror(N)
		else:
			print("Mirror.GetXY: Option set not implemented. \n Options = %s" % str(Options))
	"""
	#================================
	# Get_LocalTangentAngle [MirrorPlane]
	#================================
	def Get_LocalTangentAngle(self, x0, y0, ProperFrame = False):
		return self.VersorTan.Angle

 	#================================
	# SetXYAngle_Centre [MirrorPlane]
	#================================
	def SetXYAngle_Centre(self, XYLab_Centre, Angle, WhichAngle =  TypeOfAngle.InputNominal, **kwargs ):
		'''
		Set the element XYCentre and orientation angle.
		CHECK CONTROLLARE: non mi ricordo pi?? che cosa siano gli angoli
		'''

		self.XYCentre = XYLab_Centre

		if WhichAngle == TypeOfAngle.Surface:  	 	 	 	# Angle is the Normal to the surface
			self.AngleLab = Angle

		elif WhichAngle == TypeOfAngle.InputNominal: 	 	# Angle is the angle of the input beam
			self.AngleTanLab = Angle + self.AngleGrazingNominal

		self._UpdateParameters_XYStartEnd()
		self._UpdateParameters_Lines()
#		AngleTan = AngleIn + self.AngleGrazing
		# Defines: Versos, AngleNorm, AngleTan
#		UV = UnitVector(Angle = AngleTan + np.pi/2) # Old definition: when the primary variable was VersorNorm and not VersorTan
#		self.VersorNorm = UV
		# self.VersorTan = UnitVector(Angle = AngleTan) # attempt of new definition, but it is not safe

 	#================================
	# SetXYA_IdealMirror(N)
	#================================
#	def GetXY_IdealMirror(self, N = 100  ):


	#================================
	# FUN: _UpdateParameters_XYStartEnd
	#================================
	def _UpdateParameters_XYStartEnd(self):
		# Uses: _XYLab_Centre, _VersorNorm
		# Defines: XYStart, XYEnd
		# Called: in __init__
		# According to the y component of .VersorNorm, I define the
		# start and end points of the mirror.

#		XY_a = self._XYLab_Centre + self.L/2 * self.VersorNorm.vNorm
#		XY_b = self._XYLab_Centre - self.L/2 * self.VersorNorm.vNorm

		XY_a = self.XYCentre + self.L/2 * self.VersorNorm.vNorm
		XY_b = self.XYCentre - self.L/2 * self.VersorNorm.vNorm

		if XY_a[0] < XY_b[1]:
			self._XYLab_Start = XY_a
			self._XYLab_End = XY_b
		elif XY_a[0] >= XY_b[1]:
			self._XYLab_Start = XY_b
			self._XYLab_End = XY_a

	#================================
	# FUN: _UpdateParameters_Lines
	#================================
	def _UpdateParameters_Lines(self):
		# Uses: XYCentre, _AngleTan
		# Called: in init, When XYCentre is changed;
		# 	 	 	in SetXYAngle_Centre
		pass
#		m = np.tan(self.AngleTanLab)
#		q = self.XYCentre[1] - m * self.XYCentre[0]
#		self._Line_Tan = Line(m, q)

	#================================
	# PROP _Line_Tan
	#================================
	@property
	def _Line_Tan(self):
		'''
		Line np.tan is the line tangent to the mirror surface, viz the equation
		of the mirror itself
		'''
		m = np.tan(self.AngleTanLab)
		q = self.XYCentre[1] - m * self.XYCentre[0]
		return tl.Line(m,q)


	#================================================
	#	GetRayOutNominal
	#	INTERFACE FUNCTION
	# 	(called in Fundation.OpticalElement)
	#================================================


	#================================
	# PROP: GetRayInNominal
	#================================
	@property
	def RayInNominal(self):
		v = tl.UnitVector(Angle = self.AngleInputLabNominal).v
		return tl.Ray(vx = v[0], vy = v[1], XYOrigin = self.XYCentre)

	#================================
	# PROP: RayOutNominal
	#================================
	@property
	def RayOutNominal(self):
		V = tl.UnitVector(Angle = self.AngleInputLabNominal)
		v_ref = tl.UnitVectorReflect(V.v, self.VersorNorm.v)
		return tl.Ray(vx = v_ref[0], vy = v_ref[1], XYOrigin = self.XYCentre)
	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, N = 100, Length = 1, ArrowWidth = 1, Color = 'm', **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.
		N is the number of samples.
		'''
		# Paint the mirror
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		x_mir, y_mir = self.GetXY_IdealMirror(N)
		plt.plot(x_mir, y_mir, Color + '.')
		# mark the mirror centre
		plt.plot(self.XYCentre[0], self.XYCentre[1], Color + 'x')
		plt.axis('equal')
		# paint the normal versor
		self.VersorNorm.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth)
		# paint the inputray
		self.RayInNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'g', Shift = True)
		# paint the output ray
		self.RayOutNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'c')
		return FigureHandle
	#================================
	#  Draw
	#================================
	def Draw(self, N=100):
		x,y  = tl.geom.DrawSegmentCentred(self._L, self.XYCentre[0], self.XYCentre[1], self.Angle,N)
		return x,y
	#================================
	#  _Draw
	#================================


#==============================================================================
#	 CLASS: MirrorElliptic
#==============================================================================
class MirrorElliptic(Mirror):
	'''
	Implements a (1d) elliptic mirror of equation

	:math:`x^2/a^2 + y^2/b^2 = 1 `

	Alpha : is the grazing incidence angle
	Theta : is the angle reffered to the reference frame.
	'''
	_TypeStr = 'KB'
	_TypeDescr = "KB Mirror"
	_Behaviour = OPTICS_BEHAVIOUR.Focus
	_IsAnalytic = False
	_CommonInputSets = [(('f1','Front focal length (p)' ),
						('f2','Rear focal length (q)'),
					   ('Alpha','Grazing angle'),
					   ('L','Length')),
					  (('a','Major axis'),
						('b','Minor axis'),
						('XProp_Centre','Absolute X'),
						( 'L','Length'))
					  ]
	_MementoVariables = ('f1', 'f2', '_AngleGrazingNominal', '_L', '_Sign')

#	_PropList = 	['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
#					  'XYStart', 'XYCentre', 'XYEnd']


	#================================
	# INIT
	#================================
	def __init__(self, a =None ,b = None, f1 = None, f2 = None, Alpha = None, L = None,
			  XProp_Centre = None,
			  MirXMid = None,
			  XYOrigin = np.array([0,0]),
			  RotationAngle = 0,
			  Face = 'down', **kwargs):

		'''
		Parameters - Set 1
		-------------------------
		a : float
			a coefficient
		b : float
			b coefficient
		XProp_Mid : float
			Position of the middle-point of the mirror, expressed in the Proper reference
			frame of the ellipse.
		L : float
			Mirror Length

		Parameters - Set 2
		-------------------------
		f1 : float
			Focal length 1 (from source to mirror centre)
		f2 : float
			Focal length 2 (from mirror centre to sample focal plane)
		Alpha : float (radians)
			Grazing incidence angle
		L : float
			Mirror Length

		Common Parameters (usually automatically set)
		-----------------------------
		XYOrigin : 1x2 array [optional]
			Origin of the frame reference.
			Common usage is set it to 0, then use other helper functions (such as SetFocusAt)
			in order to set it.
		RotationgAngle : float [optional]
			Rotation angle of the frame reference
			Common usage is set it to 0, then use other helper functions (such as SetFocusAt)
			in order to set it.
		'''

		super(MirrorElliptic, self).__init__(**kwargs)
		#Mirror.__init__(self)
		self._FigureErrors = []
		self._FigureErrorSteps = []
		self._Roughness = Noise.RoughnessMaker()
		self.Options = MirrorElliptic._ClassOptions()
		self.LastRoughnessUsed = np.array([])
		self.LastResidualUsed = np.array([])  #@todo tbdisc: LastFigureErrorUsed instead


		self.XYOrigin = XYOrigin
		self.RotationAngle = RotationAngle

		if Face == 'down':
			self._Sign = +1
		elif Face== 'up':
			self._Sign = -1

		# Set of input parameters #1
		# (more mathematical, less common)
		if tl.CheckArg([a,b, XProp_Centre, L]):

			#-------------------------------
			# Validating input
			#-------------------------------
			self._ValidateInput_Set1(a, b, XProp_Centre, L)
			self._UpdateParametersProp()
			self._UpdateAlphaFromThetaProp()
		# Set of input parameters #2
		# (more practical, more common)
		elif tl.CheckArg([f1,f2,Alpha,L]):
			# Input parameters
			#-------------------------------
			self._ValidateInput_Set2(f1,f2,Alpha,L)
			self._UpdateParametersProp()
			self._UpdateParametersLab()

		self.SetXYAngle_Origin(self.XYOrigin, self.RotationAngle) # calls _UpdataParametersLab()

	#================================
	# __disp__
	#================================
	def __str__(self):
		s0 = Optics.__str__(self) + '\n'
		s1 = 'XYCentre = [%0.3f, %0.3f]\n' % (self.XYCentre[0], self.XYCentre[1])
		s2 = '\n a=%0.2f\n b=%0.2f\n c=%0.2f\n f1=%0.2f\n f2=%0.2f\n\n' %(self.a, self.b, self.c, self.f1, self.f2)
		return s0+s1+s2

	#================================
	# _ValidateInput_Set1
	#================================
	def _ValidateInput_Set1(self, a,b, XProp_Centre, L):
		'''
		Called by __init__ is the input set of parameters #1 is used.

		Action
		------------------------
		Updates the reference-frame independent class attributes

		c :
			|
		f1,f2 :
			|
		Alpha :
			|
		'''

		# INPUT (which will be stored)
		self._a = a
		self._b = b
#		self._XProp_Centre = XProp_Centre
		self._L = L

		# COMPUTED 1
		self._c = np.sqrt(a**2 - b**2)

		# Computed 2 (intermediate)
		self._XYProp_F1 = np.array([-self.c, 0])
		self._XYProp_F2 = np.array([self.c,0])
		# -------------
		_YProp_Centre = np.array(self._EvalMirrorYProp(XProp_Centre))
		# -------------
		self._XYProp_Centre = np.array([XProp_Centre, _YProp_Centre])

		# Computed 3 (important)
		self._f1 = np.linalg.norm(self._XYProp_Centre - self._XYProp_F1)
		self._f2 = np.linalg.norm(self._XYProp_Centre - self._XYProp_F2)

		# Computed 4 (important)
		#self._UpdateParametersProp()

	#================================
	# _ValidateInput_Set2
	#================================
	def _ValidateInput_Set2(self,f1,f2,Alpha, L):
		'''
		Called by __init__ is the input set of parameters #1 is used.

		Action
		------------------------
		Updates the reference-frame independent class attributes

		a,b,c :
			|

		'''

		# Input parameters
		#-------------------------------
		self._f1 = f1
		self._f2 = f2
		self._Alpha = Alpha
		self._AngleGrazingNominal = Alpha
		self._L = L

		# computed parameters (primary)

	#-------------------------------
		self._a = 0.5*(f1+f2)
		self._c = 0.5 * np.sqrt(np.cos(Alpha)**2 * (f1+f2)**2 + np.sin(Alpha)**2 *(f1-f2)**2)
#		self._c = 0.5 * np.sqrt(f1**2 + f2**2 - 2*f1*f2*np.cos(np.pi - 2*Alpha))
		self._b = np.sqrt(self.a**2 - self.c**2)

		# computed 2 (aux)
		elle = 2*self._c
		_TmpArg = tl.Coerce(self._f2/elle * np.sin(np.pi - 2*Alpha),-1,1)
		self._ThetaProp = np.arcsin(_TmpArg)
		self._XYProp_F1 = [-self.c, 0]
		self._XYProp_F2 = [self.c,0]
		_XProp_Centre = f1*np.cos(self._ThetaProp) + self._XYProp_F1[0]
		_YProp_Centre = self._EvalMirrorYProp(_XProp_Centre)
		self._XProp_Centre = _XProp_Centre
		self._YProp_Centre = _YProp_Centre
		self._XYProp_Centre = np.array([_XProp_Centre, _YProp_Centre])

	#================================
	# _UpdateXYStartXYEndProp (*)
	#================================
	def _UpdateXYStartXYEndProp(self):
			# Finding start and end points of the mirror (in proper frame reference)
			# @todo: improve introducing the computation of ellipse arc length
			# (there must be a function finding the integral)

			XCentre= self._XYProp_Centre[0] # centre of the mirror
			a = self.a
			if (XCentre - 0.5 *self.L) >= -a: # the mirror do not go past the perielium
				XStart = XCentre - 0.5 *self.L
				YStart = self._EvalMirrorYProp(XStart, +1)
				Bool1 = True

			else: # the mirror lenght go past the perieliumn
				d = abs(XCentre - 0.5 *self.L +a)
				XStart = XCentre - d
				YStart = self._EvalMirrorYProp(XStart, -1)
				Bool1 = False

			if (XCentre + 0.5 *self.L) <= a: # the mirror do not go past the perielium
				XEnd = XCentre + 0.5 *self.L
				YEnd = self._EvalMirrorYProp(XEnd, +1)
				Bool2 = True
			else: # the mirror lenght go past the perieliumn
				d = abs(XCentre + 0.5 *self.L -a)
				XEnd = XCentre - d
				YEnd = self._EvalMirrorYProp(XEnd, -1)
				Bool2 = False

			# _EvalWithX is used in GetXY_IdealMirror, in order to understand how
			# to produce the sampling.
			if (Bool1 and Bool2) == True:
				self._EvalWithX = True
			else:
				self._EvalWithX = False

			self._XYProp_Start = np.array([XStart, YStart])
			self._XYProp_End  = np.array([XEnd, YEnd])

	#================================
	# _ComputeXYStartXYEnd(*)
	#================================
	def _ComputeXYStartXYEnd(self, L, ReferenceFrame ='lab'):
		#copied from 	_UpdateXYStartXYEndProp
		# I introduced that with L as parameter, in order to deal with a figure error profile
		# which is non exactly as long as self.L (the nominal length of the mirror)

			XCentre= self._XYProp_Centre[0] # centre of the mirror
			a = self.a
			if (XCentre - 0.5 *L) >= -a: # the mirror do not go past the perielium
				XStart = XCentre - 0.5 *L
				YStart = self._EvalMirrorYProp(XStart, +1)
				Bool1 = True

			else: # the mirror lenght go past the perieliumn
				d = abs(XCentre - 0.5 *L +a)
				XStart = XCentre - d
				YStart = self._EvalMirrorYProp(XStart, -1)
				Bool1 = False

			if (XCentre + 0.5 *self.L) <= a: # the mirror do not go past the perielium
				XEnd = XCentre + 0.5 *L
				YEnd = self._EvalMirrorYProp(XEnd, +1)
				Bool2 = True
			else: # the mirror lenght go past the perieliumn
				d = abs(XCentre + 0.5 * L -a)
				XEnd = XCentre - d
				YEnd = self._EvalMirrorYProp(XEnd, -1)
				Bool2 = False

			# _EvalWithX is used in GetXY_IdealMirror, in order to understand how
			# to produce the sampling.
			if (Bool1 and Bool2) == True:
				self._EvalWithX = True
			else:
				self._EvalWithX = False

			_XYProp_Start = np.array([XStart, YStart])
			_XYProp_End  = np.array([XEnd, YEnd])

			# ---- change the reference frame, if needed ----
			if ReferenceFrame == 'lab':
				XYStart = self._Transformation_XYPropToXYLab_Point(_XYProp_Start)
				XYEnd = self._Transformation_XYPropToXYLab_Point(_XYProp_End)
			elif ReferenceFrame =='self':
				XYStart = _XYProp_Start
				XYEnd = _XYProp_End

			return XYStart, XYEnd
	pass
	#================================
	# _UpdateParametersProp (*)
	#================================
	def _UpdateParametersProp(self):
		'''
			Finds the equation of the two arms in the Proper frame reference.
			Prop stands for 'Proper'.

			Requires
			-----------------------
			a,b

			_XYProp_F1, _XYProp_Centre, _XYProp_Start, _XYProp_End

			Updated Attributes
			------------------------
			p1Prop, p2Prop : coeffs of the the two arms
				|
			_pTanProp : coeffs of the line tangent to the centreof the mirror
				|
			_pTanProp_Angle : angle of the previous line
				|
			About the architercture
			------------------------
			Events such as the change of XYOrigin or of the rotation angle will
			result into a call to _UpdateParametersLab, which will convert the
			'Prop' parameters into 'Lab' parameters
				.
		'''
		# Finding start and end points of the mirror (in proper frame reference)
		# @todo: improve introducing the computation of ellipse arc length
		# (there must be a function finding the integral)
		XStart = self._XYProp_Centre[0] - 0.5*self.L
		self._XYProp_Start = np.array([XStart, self._EvalMirrorYProp(XStart)])
		XEnd = self._XYProp_Centre[0] + 0.5* self.L
		if XEnd > self.a:
			XEnd = self.a - abs(abs(self.a - self._XYProp_Centre[0]) - 0.5* self.L)
		self._XYProp_End  = np.array([XEnd, self._EvalMirrorYProp(XEnd)])

		self._UpdateXYStartXYEndProp()
		# Trovo asse: Sorgente- Centro Specchio (da mettere nella classe)
		[p2, p1] = self.TraceRay(self._XYProp_F1, self._XYProp_Centre)
		self._p1Prop = np.array(p1)
		self._p2Prop = np.array(p2)
		self._p1Prop_Angle = np.arctan(p1[0])
		self._p2Prop_Angle = np.arctan(p2[0])


		# equazione della tangente al centro dello specchio
		m = - self.b**2 / self.a**2 * self._XYProp_Centre[0] / self._XYProp_Centre[1]
		q =  self.b**2 / self._XYProp_Centre[1]

		self._pTanProp = np.array([m,q])
		self._pTanProp_Angle = np.arctan(m)
		self._ThetaProp = self._pTanProp_Angle




#		# angolo di pendenza proprio
#		elle = 2*self._c
##		self._ThetaProp = np.arcsin(self._f2/elle * np.sin(np.pi - 2*self.Alpha))
##		AlphaProp = self._Theta_to_Alpha(self._ThetaProp)
#
##		self.Alpha = self._ThetaProp_to_Alpha(self._ThetaProp)

	#================================
	# _UpdateParametersLab (*)
	#================================
	def _UpdateParametersLab(self):
		'''
			Updates the parameters which depend on the Laboratory reference frame,
			i.e. on the XYOrigin and on the RotationAngle attributes.

			XYF1, XYF2
				|
			Theta
				|
			_p1, _p2, _p1_Angle, _p2_Angle
				|
			_pTan, _pTan_Angle
				|
		'''

		# Rotation of Points
		self._XYLab_F1 = self._Transformation_XYPropToXYLab_Point(self._XYProp_F1)
		self._XYLab_F2 = self._Transformation_XYPropToXYLab_Point(self._XYProp_F2)

		self._XYLab_Centre =self._Transformation_XYPropToXYLab_Point(self._XYProp_Centre )
		self._XYLab_Start = self._Transformation_XYPropToXYLab_Point(self._XYProp_Start)
		self._XYLab_End = self._Transformation_XYPropToXYLab_Point(self._XYProp_End)


		# rotation of coefficients
		self._p1Lab = self._Transformation_PolyPropToPolyLab(self._p1Prop)
		self._p2Lab = self._Transformation_PolyPropToPolyLab(self._p2Prop)
		self._pTanLab = self._Transformation_PolyPropToPolyLab(self._pTanProp)
		self._p1Lab_Angle = np.arctan(self._p1Lab[0])
		self._p2Lab_Angle = np.arctan(self._p2Lab[0])


		# rotation of angles
		self._ThetaLab = np.arctan(self._pTanLab[0])
		self._pTanLab_Angle = np.arctan(self._pTanLab[0])

		# Injection to VersorTan (VersorTan is the primary VersorStuff of Optics numerical)
		#self.VersorTan = tl.UnitVector(Angle = 1* self._pTanLab_Angle )

		# Injection to VersorLab (VersorLab is linked to AngleLab and XYOrigin,
		# which are the basis of positioning in  Optics numerical)
		self.VersorLab = tl.UnitVector(Angle =  self._pTanLab_Angle - np.pi/2 - self.AngleGrazingNominal  )

	#================================
	# _SetMirrorCoordinates
	#================================
	def _UpdateMirrorCoordinates(self, XMid, L):
		'''
		Automatically sets the values of XYStart and XYEnd

		Parameters
		--------------------
		XMid : scalar
			X middle coordinate of the mirror
		L : scalar
			Length of the mirror

		Called...
		--------------------
		During the init of the object
		'''

		XStart = XMid - 0.5*L
		self.XYStart = np.array([XStart, self.EvalY(XStart)])
		XEnd = XMid + 0.5* L
		self.XYEnd  = np.array([XEnd, self.EvalY(XEnd)])
		self._L = L




	#================================
	# _UpdateFociiFromParameters_XYOrigin
	#================================
	def _UpdateFociiFromParameters_XYOrigin(self):
		'''
			Updates (shift) the positions of focii according to XYOrigin.

			Call info
			-------------------
			Intended to be called ONLY by the XYOrigin setter.
		'''
		self.XYF1 = np.array([-self.c, 0]) + self.XYOrigin
		self.XYF2 = np.array([self.c,0]) + self.XYOrigin

	#================================
	# _UpdateFociiFromParameters_XMid
	#================================
	def _UpdateFociiFromParameters_XMid(self, XMid, DeltaX):
		'''
		Dati La posizione dello specchio e la lunghezza, definisce f1 e f2
		'''
		YMid = self.EvalY(XMid)
		XStart = XMid - 0.5*DeltaX
		YStart = self.EvalY(XStart)
		XEnd = XMid + 0.5*DeltaX
		YEnd= self.Eval(XEnd)

		self.XYCentre = np.array([XMid, YMid])
		self.XYStart = np.array([XStart, YStart])
		self.XYEnd = np.array([XEnd, YEnd])

		self._f1 = np.linalg.norm(self.XYCentre - self.XYF1)
		#self._f1 = np.sqrt((self.XYCentre[0] - self.XYF1[0])**2 + (self.XYCentre[1] - self.XYF1[1])**2)
		self._f2 = np.linalg.norm(self.XYCentre - self.XYF2)
		#self._f2 = np.sqrt((self.XYCentre[0] - self.XYF2[0])**2 + (self.XYCentre[1] - self.XYF2[1])**2)
		self._L = DeltaX

	#================================
	# _EvalMirrorYProp (XProp)
	#================================
	def _EvalMirrorYProp(self, XProp, Sign = +1):
		'''
		Evaluates the ellipse equation in the Self reference frame.

		Valuta l'equazione dell'ellisse
		Uses Analytic expression
		Parameters
		----------------
		x : float
		'''
		x = np.array(XProp)
		# remove points which do not belong to ellipse domain.
		XProp = np.delete(XProp, [(XProp < -self.a) | (XProp > self.a)])
		return Sign*self.b * np.sqrt(1 - x**2 / self.a**2)
	#================================
	# _EvalMirrorXProp (YProp)
	#================================
	def _EvalMirrorXProp(self, YProp, Sign = +1):
		'''
		The same as _EvalMirrorYProp, except that X is computed as function of Y
		(self reference frame is used).

		I created this function for dealing with X points turning around perielium\afelium
		'''
		y = np.array(YProp)
		# remove points which do not belong to ellipse domain.
		YProp = np.delete(YProp, [(XProp < -self.b) | (XProp > self.b)])
		return Sign*self.a * np.sqrt(1 - y**2 / self.b**2)

#		if size(x) == 1:
#			return Sign*self.b * np.sqrt(1 - x**2 / self.a**2)
#		else:
#			# Understand if -a or +a belong to the XProp range.
#			BoolDic= {True:1 , False: -1}
#			BoolList = np.diff(XProp) > 0
#			SignList = [BoolDic[Bool] for Bool in BoolList] # SingList = [+1 +1 +1 +1 .... -1 -1 -1]
#			ForwardList = [SignList == +1]  #andata
#			BackwardList = not(ForwardList)
#
#			Result = XProp * 0
#			Result[ForwardList] = Sign*self.b * np.sqrt(1 - x**2 / self.a**2)
#			#Result[BackwardList]= -Sign*self.b * np.sqrt(1 - x**2 / self.a**2)
#			return Result
		# (old version)
#		tmp = Sign*self.b * np.sqrt(1 - x**2 / self.a**2)





	#================================
	# GetXY_FocalPlaneAtF2(Size,N)
	#================================
	def GetOpticalElement_DetectorAtF2(self, L= 1e-3 , Defocus = 0, ReferenceFrame = 'lab' ):
		'''
			Uses: XYF1, XYF2, XYCentre
			Length (m)
			N: # samples
		'''
		# I create a dummy plane mirror
		pm = MirrorPlane(L = L,
				   AngleGrazing = -np.pi/2,
				   XYLab_Centre = self.XYF2,
				   AngleIn = self.RayOutNominal.Angle + np.pi )
		return pm

	#================================
	# GetXY_FocalPlaneAtF2(Size,N)
	#================================
	def GetXY_TransversePlaneAtF2(self, N=2,L= 1e-3 , Defocus = 0, ReferenceFrame = 'lab' ):
		'''
			Uses: XYF1, XYF2, XYCentre
			Length (m)
			N: # samples
		'''
		# I create a dummy plane mirror, and I use its methods to get detector points. In a more elegant fashion, the class 'Segment' should exist.
		pm = MirrorPlane(L = L,
				   AngleGrazing = -np.pi/2,
				   XYLab_Centre = self.XYF2,
				   AngleIn = self.RayOutNominal.Angle + np.pi )
		x,y = pm.GetXY(N)
		return [x,y]

	#================================
	# GetXY_FocalPlaneAtF2(Size,N)
	#================================
	def Old_GetXY_TransversePlaneAtF2(self, N=2,Length = 1e-3 , Defocus = 0, ReferenceFrame = 'lab' ):
		'''
			Uses: XYF1, XYF2, XYCentre
			Length (m)
			N: # samples
		'''
		Size = Length
		RayOut = self.RayOutNominal

		[p1, p2] = self.TraceRay(self.XYF1, self.XYCentre)
		m = -1/p2[0]
		theta = np.arctan(m)
		thetaNorm = np.arctan(p2[0])
		DeltaXY = Defocus * np.array([np.cos(thetaNorm), np.sin(thetaNorm)])
		XY = self.XYF2 + DeltaXY
#		q = - self.XYF2[0] * m
		q = XY[1] - XY[0] * m
		p = np.array([m,q])

		Det_x0 = XY[0] - Size/2 * np.cos(theta)
		Det_x1 = XY[0] + Size/2 * np.cos(theta)
		x = np.linspace(Det_x0, Det_x1,N)
		y = np.polyval(p,x)

		if ReferenceFrame == 'lab':
			x,y = self._Transformation_XYPropToXYLab(x,y)
		return [x,y]

	#================================
	# GetY_IdealMirror(X)
	#================================
	def GetY_IdealMirror(self, x, Sign = +1, InputReferenceFrame = 'lab', OutputReferenceFrame = 'lab'):
		'''
		Similar to GetXY_IdealMirror, but wants the x coordinate as input instead
		of the number of samples N

		x can be either in the lab Reference of in the Self reference frame

		History
		------------------
		Inspired by GetXY_IdealMirror
		'''

		try:
			N = len(x)
			IsArray = True # I will return Y as an array
			y_dummy = np.zeros(N)
		except:
			IsArray = False # I will return Y as a float
			y_dummy = 0

		if InputReferenceFrame == 'lab':

			xSelf, dummy = self._Transformation_XYLabToXYProp(x,y_dummy)
		else:
			xSelf = x

		ySelf = self._EvalMirrorYProp(xSelf, Sign)

		if OutputReferenceFrame == 'lab':
			xOut,yOut = self._Transformation_XYPropToXYLab(xSelf,ySelf)
		else:
			xOut = xSelf
			yOut = ySelf
#		yOut = yOut if IsArray else yOut[0]

		return yOut

	"""
 	#================================
	# GetXY
	#================================
	def GetXY(self, N, Options =['ideal'] ):
		'''
		Main User-interface function for getting the x,y points of the mirror
		in the laboratory reference frame.

		Uses the self.ComputationSettings parameters for performing the computation

		Options is the old version
		Options can be
		- 'ideal' : the ideal mirror profile is used (default)
		- 'perturbation' : instead of the nominal position of the mirror, the position of the mirror computed via  longitudinal, transverse and angular
		 "perturbations" around the nominal configuration.
		- 'figure error' : a figure error is added to the mirror profile, if possible
		- 'roughness' : a roughness profile is added to the mirror profile, if possible
		'''

		if self.ComputationSettings.UseIdeal == True:
			return self.GetXY_IdealMirror(N)

		if self.ComputationSettings.UseSmallDisplacements:
			pass
			else:
			print("Mirror.GetXY: Option set not implemented. \n Options = %s" % str(Options))
		"""
	#================================
	# GetXY_CompleteEllipse(N)
	#================================
	def GetXY_CompleteEllipse(self, N, ReferenceFrame = 'lab'):

		# specchio
		Mir_xProp = np.linspace(-self.a, self.a, N)

		Mir_yProp_p = self._EvalMirrorYProp(Mir_xProp)
		Mir_yProp_m = self._EvalMirrorYProp(Mir_xProp[::-1], -1)

		Mir_x__ = np.append(Mir_xProp, Mir_xProp[::-1])
		Mir_y__ = np.append(Mir_yProp_p, Mir_yProp_m)

		if ReferenceFrame =='lab':
			Mir_x__, Mir_y__ = self._Transformation_XYPropToXYLab(Mir_x__, Mir_y__)

		return Mir_x__, Mir_y__



	#================================
	# GetXY_IdealMirror(N) [MirrorElliptic Class - Historic]
	#================================
	def GetXY_IdealMirror_historic(self, N, Sign = +1, ReferenceFrame = 'lab', L = None):
		'''
			Evaluates the MirrorElliptic only over the physical support of the mirror
			(within XStart and XEnd)
			N is the number of samples in X.

			 @TODO: define N of samples along the MirrorElliptic (ma serve?)
		'''
		""" VECCHIO
		x = np.linspace(self.XYStart[0], self.XYEnd[0], N)
		return [x,self._EvalMirrorYProp(x, Sign)]
		"""

		x = np.linspace(self._XYProp_Start[0], self._XYProp_End[0],N)
		y = self._EvalMirrorYProp(x, Sign)

		if ReferenceFrame == 'lab':
			x,y = self._Transformation_XYPropToXYLab(x,y)
		return x,y


	#================================
	# GetXY_IdealMirror(N)  [MirrorElliptic Class]
	#================================
	def GetXY_IdealMirror (self, N, Sign = +1, ReferenceFrame = 'lab', L = None):
		'''
			Evaluates the MirrorElliptic only over the physical support of the mirror
			(within XStart and XEnd)
			N is the number of samples in X.

			Parameters
			-----
			N : int

			ReferenceFrame : str {lab,self}

			 @TODO: define N of samples along the MirrorElliptic (ma serve?)

			 	L : is used by GetXY_MeasuredMirror, where L is not the nominal one, but the one computed from the
			figure error.

		'''
		#@todo: si dovrebbe decidere chi spaziare, se X o Y a seconda della tangente locale.
		N = int(N)
		# Shall I use  the Nominal Length L or Measured one?
		#-----------------------------------------------------------------
		if L==None: # the stored length self.L is used, hence the stored XYStart
			XYProp_Start = self._XYProp_Start
			XYProp_End =  self._XYProp_End
		else: # a new length is used (not the nominal one)
			XYProp_Start, XYProp_End = self._ComputeXYStartXYEnd(L, ReferenceFrame = 'self')


		# Evaluating the ellipse (in the Self Reference)
		#-----------------------------------------------------------------
		if self._EvalWithX == True:

			x = np.linspace(XYProp_Start[0], XYProp_End[0],N)
			y = self._EvalMirrorYProp(x, Sign)
		else:
			y = np.linspace(XYProp_Start[1], XYProp_End[1],N)
			x = self._EvalMirrorYProp(y, Sign)

		# Rotating in the Lab Reference, if needed
		#-----------------------------------------------------------------
		if ReferenceFrame == 'lab':
			x,y = self._Transformation_XYPropToXYLab(x,y)
		return x,y

	#================================
	# Get_LocalTangentAngle
	#================================
	def Get_LocalTangentAngle(self, x0, y0, ProperFrame = False):
		''' Return the angle (refferred ti x axis) of the tangent to the ellipse
			in the point x0,y0
		'''
		m = -self.b**2 / self.a**2 * x0/y0
		return np.arctan(m)


	#================================
	# GetXY_MeasuredMirror
	#================================

	def GetXY_MeasuredMirror__dismissed(self, N, iFigureError = 0, Reference = 'lab' ):

		# carico il figure error e, se necessario, lo ricampiono
		#-----------------------------------------------------------------
		if len(self._FigureErrors)-1 >= iFigureError:
			hFigErr  = self.FigureErrors[iFigureError]
			LMeasured = len(hFigErr) * self._FigureErrorSteps[iFigureError]
			self._L = LMeasured  # serve davvero?
			hFigErr  = rm.FastResample1d(hFigErr - np.mean(hFigErr  ), N)
		else:
			hFigErr   = np.zeros(N)
			LMeasured = self.L

		# Get the ideal ellipse (in the self- Reference frame)
		# -----------------------------------------------------------------
		Mir_x, Mir_y = self.GetXY_IdealMirror(N, ReferenceFrame = 'self', L = LMeasured)

		# aggiungo la roughness (se richiesto, rigenero il noise pattern)
		#-----------------------------------------------------------------
		if self.ComputationSettings.UseRoughness == True:
			hRoughness = self.Roughness.MakeProfile(LMeasured, N)
			########################### added by L.Rebuffi
			if len(hRoughness) < N:
				filler = np.zeros(N-len(hRoughness))
				hRoughness = np.append(filler, hRoughness)
			##############################################
			self.LastRoughnessUsed = hRoughness
			myResidual = hFigErr + hRoughness
		else:
			myResidual = hFigErr

		self.LastResidualUsed = myResidual


		# I Project the figure error on the Ellipse
		# -----------------------------------------------------------------
		ThetaList = self.Get_LocalTangentAngle(Mir_x, Mir_y)
		Mir_xx = Mir_x + myResidual * np.sin(ThetaList)
		Mir_yy = Mir_y + myResidual * np.cos(ThetaList)

		if Reference == 'lab':
			Mir_xx, Mir_yy = self._Transformation_XYPropToXYLab(Mir_xx, Mir_yy)

		return Mir_xx, Mir_yy
	#================================
	# SetXYAngle_Origin
	#================================
	def SetXYAngle_Origin(self,XYOriginNew, Angle = 0 ):
		'''
		Set the mirror such that the cartesian reference frame is placed at XYOriginNew at the given Angle.
		NOT FOR USERS: supposed to be invoked just durinf __init__
		'''
		XYOriginNew = np.array(XYOriginNew)
		if all(XYOriginNew == np.array([0,0])) and (Angle ==0):
			pass
		else:
			self._Transformation_Clear()
			self._Transformation_Add(Angle,
									-XYOriginNew,
									[0,0])
		self._UpdateParametersLab()

	#================================
	# SetXYAngle_UpstreamFocus
	#================================
	def SetXYAngle_UpstreamFocus(self, XYNewFocus, Angle=0,  WhichAngle='arm'):
		'''
		Set the mirror such that the upstream focus is in a given position with a
		given angle.
		SetXYA => Set XY coordinates and orientation Angle.

		'''
		if WhichAngle == 'arm' :
			a = self._p1Prop_Angle
			TotalAngle = Angle - a
			xNewCentre = -self._XYProp_F1[0]*np.cos(TotalAngle)+XYNewFocus[0]
			yNewCentre = -self._XYProp_F1[0]*np.sin(TotalAngle)+XYNewFocus[1]
			self._Transformation_Clear()
			self._Transformation_Add(TotalAngle,
									[0,0],
									[0,0])
			self._Transformation_Add(0,
									[xNewCentre,yNewCentre],
									self._XYProp_F1)
		else:
			print ('_SetFocusAt: Method not implemented yet with this ')
			pass
		self._UpdateParametersLab()

	#================================
	# SetXYAngle_Centre
	#================================
	def SetXYAngle_Centre(self,XYMirrorCentreNew, Angle = 0 ,  WhichAngle = 'arm1'):
		'''
		Set the mirror such that the mirror centre is in a given position with
		(its tangent) at a given angle.

		SetXYA => Set XY coordinates and orientation Angle.

		Set the centre of the optical element.
		In this case, the centre is intended to be the mirror centre.
		'''
		XYMirrorCentreNew = np.array(XYMirrorCentreNew)

		if WhichAngle == 'input':
			a = self._p1Prop_Angle
		elif WhichAngle == 'output':
			a = self._p2Prop_Angle
		elif WhichAngle == 'axis':
			a = 0
		TotalAngle = Angle - a

		self._Transformation_Clear()
		self._Transformation_Add(0,
								-self._XYProp_Centre + XYMirrorCentreNew,
								XYMirrorCentreNew)
		self._Transformation_Add(TotalAngle,
								[0,0] ,
								XYMirrorCentreNew)
		self._UpdateParametersLab()

#	#================================
#	# SetXYAngle
#	#================================
#	def SetXYAngle(self,XY,
#							Angle = 0 ,
#							WhichXY = TypeOfXY.MirrorCentre,
#							WhichAngle = TypeOfAngle.InputNominal):
#		'''
#		Generalised versione os SetXYAngle_Centre, SetXYAngle_Origin, etc...
#		It is intended to cave all the cases...let's hope
#		'''
#		XY = np.array(XY)
#
#		if WhichAngle == TypeOfAngle.InputNominal:
#			a = self._p1Prop_Angle
#		elif WhichAngle == TypeOfAngle.OutputNominal:
#			a = self._p2Prop_Angle
#		elif WhichAngle == TypeOfAngle.AxisOrigin:
#			a = 0
#		TotalAngle = Angle - a
#
#		self._Transformation_Clear()
#		self._Transformation_Add(0,
#								-self._XYProp_Centre+XYMirrorCentreNew,
#								XYMirrorCentreNew)
#		self._Transformation_Add(TotalAngle,
#								[0,0] ,
#								XYMirrorCentreNew)
#		self._UpdateParametersLab()

	#================================
	# _AddResidualToMirrorElliptic
	#================================
	def _AddResidualToMirrorElliptic(self, myResidual):
		# Assume che la lunghezza fisica di myResidual sia uguale a quella di self.L (che ?? ci?? che accate se Options.)
		N = len(myResidual)
		[Mir_x, Mir_y] = self.GetXY_IdealMirror(N)
		ThetaList = self._LocalTangent(Mir_x, Mir_y)
		NewMir_x = Mir_x + myResidual * np.sin(ThetaList)
		NewMir_y = Mir_y + myResidual * np.cos(ThetaList)
		return (NewMir_x, NewMir_y)


	# ---------------------------------------------------------
	# 	     MIRROR PROPERTIES
	#	They are independent of reference-frame
	#---------------------------------------------------------


	@property # Ellipse parameter a
	def a(self):		return self._a

	@property # Ellipse parameter b
	def b(self):		return self._b

	@property # Ellipse parameter c
	def c(self):		return self._c


	@property # Ellipse parameter f1
	def f1(self):		return self._f1

	@property # Ellipse parameter f2
	def f2(self):		return self._f2

	@property # Grazing angle

	def Alpha(self):		return self._Alpha

	@property # Mirror Length
	def L(self):		return self._L
	@L.setter
	def L(self, val): self._L = val


	@property # Magnification
	def M(self):		return self._f1/self._f2

	# ---------------------------------------------------------
	# 	     PUBLIC PROPERTIES (READ ONLY)
	#	in the Laboratory reference-frame
	#---------------------------------------------------------

#	@property
#	def VersorNorm(self):
#		return tl.UnitVector(Angle = self.pTan_Angle +np.pi/2, XYOrigin = self.XYCentre)
	# Upstream Focus

	@property
	def XYAxisOrigin(self):
		return np.array( self.XYOrigin)
	@XYAxisOrigin.setter
	def XYAxisOrigin(self,Value):
		self.XYOrigin = Value

	@property
	def XYF1(self):
		return  np.array(self._XYLab_F1)
	# Downstrem Focus
	@property
	def XYF2(self):
		return np.array( self._XYLab_F2)
	# Centre of the mirror
	@property
	def XYCentre(self):
		return np.array(self._XYLab_Centre)
	# Start point (upstream) of the mirror
	@property
	def XYStart(self):
		return np.array(self._XYLab_Start)
	# Endpoint (downstream) of the mirror
	@property
	def XYEnd(self):
		return  np.array(self._XYLab_End)
	#================================
	#  PROP: AngleGrazing
	#================================
	@property
	def AngleGrazing(self):
		return self._Alpha
	# Coefficients of Arm 1 (centre mirror to upstream focus - replica, maybe working)
	@property
	def f1_Angle(self):
		v  = self.XYCentre - self.XYF1 ;
		return np.arctan2(v[1], v[0]) ;
	@property
	def f2_Angle(self):
		v  = -self.XYCentre + self.XYF2 ;
		return np.arctan2(v[1], v[0]) ;

	# Coefficients of Arm 1 (centre mirror to upstream focus)
	@property
	def p1(self):
		return self._p1Lab
	# Coefficients of Arm 2 (centre mirror to downstream focus)
	@property
	def p2(self):
		return self._p2Lab
	# Angle of arm 1
	@property
	def p1_Angle(self):
		return self._p1Lab_Angle
	# Angle of arm 2
	@property
	def p2_Angle(self):
		return self._p2Lab_Angle
	# Coefficients of the line tangent to XYCentre
	@property
	def pTan(self):
		return self._pTanLab
	# Angle of pTan
	@property
	def pTan_Angle(self):
		return self._pTanLab_Angle
	#================================
	# TraceRay
	#================================
	def TraceRay(self, XYStart, XEnd):
		'''
			Parameters
			---------------
			XYStart : [x,y], a point in the space
			XEnd : x coordinate of the mirror

			Returns
			---------------
			IncidentRay : [p1,p0] coefficients describing the incident ray
			Reflected Ray : [p1,p0] coefficients describing the incident ray

			Dato l'ellisse (oggetto), il punto di partenza Start e la X di incidenza,
			trova il polinomio di ordine 1 (retta) del raggio incidente e di quello
			riflesso
		'''
		Start = XYStart
		End = XEnd
		a = self.a
		b = self.b
		if len(End) == 1:
			xEll = End
			yEll = self.EvalY(xEll)
		elif len(End) == 2:
			xEll = End[0]
			yEll = End[1]



		xStart = Start[0] ;
		yStart = Start[1] ;

		# raggio uscente (2)


		m0 = -b**2/a**2 * xEll/yEll ;
		m2 =  (yStart - yEll) / (xStart - xEll) ;

		Theta0 = np.arctan(m0) ;
		Theta2 = np.arctan2((yStart - yEll),(xStart - xEll)) ;
		Theta1 =+( -Theta2 + 2*Theta0 - np.pi) ;

		m1 = np.tan(Theta1) ;

		q = yEll - m1 * xEll ;

		p = [m1,q] ;
		p1 = p ;			# il raggio (1) (entrante)

		# raggio di partenza (1) ;

		q = yEll - m2 * xEll ;

		p = [m2,q] ;
		p2 = p ;		 # il raggio (2) uscente

		return p1, p2
	#================================
	# TraceRay
	#================================
	def TraceRay_Sfanculato(self, XYOrigin, XMirror,Sign = +1, InputReference = 'lab', OutputReference = 'lab'):
		'''
			Parameters
			---------------
			XYStart : [x,y], a point in the space
			XEnd : x coordinate of the mirror where the reflection occurs.

			Notice: info about mirror equation, local tangent etc are automatically retrieved

			Returns
			---------------
			IncidentRayCoeff : [p1,p0] coefficients describing the incident ray
			ReflectedRayCoeff : [p1,p0] coefficients describing the reflected ray

			Dato l'ellisse (oggetto), il punto di partenza Start e la X di incidenza,
			trova il polinomio di ordine 1 (retta) del raggio incidente e di quello
			riflesso
		'''

		DeltaXEnd = 0.01
		xEll = XMirror
		yEll = self.GetY_IdealMirror(xEll, Sign, InputReference, OutputReference)

		xStart = XYOrigin[0] ;
		yStart = XYOrigin[1] ;


		# Local tangent
		#----------------------------------------------------
		xEll_ = np.array([xEll - DeltaXEnd, xEll + DeltaXEnd])
		yEll_ = self.GetY_IdealMirror(xEll_, Sign, InputReference, OutputReference)
		vxTan = (xEll_[1] - xEll_[0])
		vyTan = (yEll_[1] - yEll_[0])
		vTan = np.array([vxTan, vyTan])
		VTan = tl.Vector(v = vTan)
		VNormal = VTan.GetNormal()
		vNormal = tl.UnitVectorNormal(vTan, Sign = -1 * Sign)

		pTan = np.polyfit( xEll_, yEll_,1)


		# Raggio entrante (rappresentato in 3 modi diversi... uffa)
		#----------------------------------------------------
		pIn = np.polyfit([xStart, xEll], [yStart, yEll],1)
		vIn = tl.Normalize(np.array([xEll - xStart, yEll - yStart]))
		#LineIn = tl.Line(m=pIn[1], q = pIn[0])
		#vIn = LineIn.v


		#Reflected ray
		#----------------------------------------------------
		vIn = tl.Normalize(vIn)
		vNormal = tl.Normalize(vNormal)
		vOut = tl.UnitVectorReflect(vIn, vNormal)
		VOut = tl.UnitVector(v = vOut, XYOrigin = [xEll, yEll])
		pOut = VOut.PolyCoeff


		return pIn, pOut

	#================================
	# TraceRay
	#================================
	def TraceRays(self, XYOrigin, XMirror, YMirror, InputReference = 'lab', OutputReference = 'lab'):
		'''
			Parameters
			---------------
			XYStart : [x,y], a point in the space
			XEnd : x coordinate of the mirror where the reflection occurs.

			Notice: info about mirror equation, local tangent etc are automatically retrieved

			Returns
			---------------
			pInList : [p1,p0] coefficients describing the incident ray
			pOutList : [p1,p0] coefficients describing the reflected ray

			Dato l'ellisse (oggetto), il punto di partenza Start e la X di incidenza,
			trova il polinomio di ordine 1 (retta) del raggio incidente e di quello
			riflesso
		'''


		N = len(XMirror)
		xStart = XYOrigin[0] ;
		yStart = XYOrigin[1] ;

		pInList = np.zeros([N-2, 2])
		pOutList = np.zeros([N-2, 2])
		for i in range(1, N-1) :

			xEll = XMirror[i]
			yEll = YMirror[i]

			# Local tangent
			#----------------------------------------------------
			xEll_ = np.array([XMirror[i-1] , XMirror[i+1]])
			yEll_ = np.array([YMirror[i-1] , YMirror[i+1]])
			vxTan = (xEll_[1] - xEll_[0])
			vyTan = (yEll_[1] - yEll_[0])
			vTan = np.array([vxTan, vyTan])
			VTan = tl.Vector(v = vTan)
			VNormal = VTan.GetNormal()
			vNormal = tl.UnitVectorNormal(vTan, Sign = -1 * self._Sign)

			pTan = np.polyfit( xEll_, yEll_,1)


			# Raggio entrante (rappresentato in 3 modi diversi... uffa)
			#----------------------------------------------------
			pIn = np.polyfit([xStart, xEll], [yStart, yEll],1)
			vIn = tl.Normalize(np.array([xEll - xStart, yEll - yStart]))
			#LineIn = tl.Line(m=pIn[1], q = pIn[0])
			#vIn = LineIn.v


			#Reflected ray
			#----------------------------------------------------
			vIn = tl.Normalize(vIn)
			vNormal = tl.Normalize(vNormal)
			vOut = tl.UnitVectorReflect(vIn, vNormal)
			VOut = tl.UnitVector(v = vOut, XYOrigin = [xEll, yEll])
			pOut = VOut.PolyCoeff

			pInList[i-1] = pIn
			pOutList[i-1] = pOut

		return pInList, pOutList
	#================================
	# _UpdateThetaPropFromAlpha
	#================================
	def _UpdateThetaPropFromAlpha(self):
		'''
			Computes the Theta angle (reffered to x axis)
			using Alpha angle (referred to mirro incidence plane)
		'''
#		m = -self.b**2/self.a**2 * self._XYProp_Centre[0] /self._XYProp_Centre[1]
#
#		# SIAMO SICURI? non manca un np.arctan?!?!?!
#		return abs(Alpha - abs(m ))
		TmpArg = tl.Coerce(TmpArg, -1,1)
		self._ThetaProp = np.arcsin(TmpArg)
		# @todo

	#================================
	# _UpdateAlphaFromThetaProp
	#================================
	def _UpdateAlphaFromThetaProp(self):
		'''
			Computes the Theta angle (reffered to x axis)
			using Alpha angle (referred to mirro incidence plane
		'''
#		m = -self.b**2/self.a**2 * self._XYProp_Centre[0] /self._XYProp_Centre[1]
#		return abs(ThetaProp - abs(np.arctan(m)))
		if self._pTanProp_Angle != self._ThetaProp:
			print ('Cazzo succede? 827')

		self._Alpha = abs(self._p1Prop_Angle) + abs(self._ThetaProp)

	#================================
	# _SourceDisplacement
	#================================
	def _SourceDisplacement(self, Long, Trans):
		'''
		Converts a (Longitudinal, Transverse) displacement of the source to a
		(x,y) displacement.

		Parameters
		----------------
		Long : longitudinal displacement
		Trans: Transverse displacement

		Notice: the reference axis is the joining line of the MirrorElliptic [Focus1 - Centre Mirrors]
		'''
		####o
		DeltaXOrigin = (Long* np.cos(self.p1_Angle) +
					Trans* np.sin(self.p1_Angle))
		DeltaYOrigin = (Long* np.sin(self.p1_Angle) +
					Trans* np.cos(self.p1_Angle))
		return DeltaXOrigin, DeltaYOrigin

	# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	#
	#	WISE 2.0 DEV++ section
	#
	# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



	@property
	def RayInNominal(self):
		RayIn = tl.Ray(x1 = self.XYCentre[0], y1 = self.XYCentre[1],
			  x0 = self.XYF1[0], y0 = self.XYF1[1])
		RayIn.XYOrigin = self.XYCentre
		return RayIn
	#================================================
	#	GetRayOutNominal
	#	INTERFACE FUNCTION
	# 	(called in Fundation.OpticalElement)
	#================================================
	@property
	def RayOutNominal(self):
		'''
       Return the nominal outcoming ray. Uses the member attributes
       of the object for the computation.
		'''
		RayOut = tl.Ray(x0 = self.XYCentre[0], y0 = self.XYCentre[1],
				  x1 = self.XYF2[0], y1 = self.XYF2[1])
		RayOut.XYOrigin = self.XYCentre
		return RayOut

	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, N = 500, Length = None, ArrowWidth = None, Color = 'm', Complete = False, **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.
		N is the number of samples.
		'''
		# Paint the mirror
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		# Old versione (20180103)
		#x_mir, y_mir = self.GetXY_IdealMirror(N)
		x_mir, y_mir = self.GetXY(N)
		plt.plot(x_mir, y_mir, Color + '.')


		# Paint the ellipse
		if Complete == True:
			x_mir, y_mir = self.GetXY_CompleteEllipse(N)
			plt.plot(x_mir, y_mir, Color + '.', markersize = 0.5)
			# mark the focii
			plt.plot(self.XYF1[0], self.XYF1[1], Color + 'x', markersize = 7)
			plt.plot(self.XYF2[0], self.XYF2[1], Color + 'x', markersize = 7)
		# finds a good arrow lenght
		if Length == None:
			Length = 0.1
		if ArrowWidth == None:
			ArrowWidth = Length * 0.3


		# paint the normal versor (green)
		self.VersorNorm.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'g')
		# paint the tangential versor (yellow)
		self.VersorTan.Paint(FigureHandle, Length = 2*Length, ArrowWidth = ArrowWidth,Color = 'y')
		# paint the inputray (blue)
		self.RayInNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'b', Shift = True)
		# paint the output ray (red)
		self.RayOutNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'r')

		plt.axis('equal')
		return FigureHandle


#==============================================================================
#	 CLASS: MirrorSpheric
#==============================================================================
class MirrorSpheric(Mirror):
	'''
	Implements a (1d) elliptic mirror of equation

	:math:`x^2/a^2 + y^2/b^2 = 1 `

	Alpha : is the grazing incidence angle
	Theta : is the angle reffered to the reference frame.
	'''
	_TypeStr = 'sph'
	_TypeDescr = "Spheric Mirror"
	_Behaviour = OPTICS_BEHAVIOUR.Focus
	_IsAnalytic = False
#	_PropList = 	['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
#					  'XYStart', 'XYCentre', 'XYEnd']
	_CommonInputSets = [(('R','Curvature Radius'),
						('L','Length' ),
						('AngleGrazing','Grazing Angle')),
					  ]


	#================================
	# INIT
	#================================
	def __init__(self, R, Alpha = None, L = None, XSelf_Centre = None,
			  MirXMid = None, XYOrigin = np.array([0,0]), RotationAngle = 0):
		'''
		Parameters
		-------------------------
		R : float
			Focal length 1 (from source to mirror centre)
		Alpha : float (radians)
			Grazing incidence angle
		L : float
			Mirror Length

		Common Parameters (usually automatically set)
		-----------------------------
		XYOrigin : 1x2 array [optional]
			Origin of the frame reference.
			Common usage is set it to 0, then use other helper functions (such as SetFocusAt)
			in order to set it.
		RotationgAngle : float [optional]
			Rotation angle of the frame reference
			Common usage is set it to 0, then use other helper functions (such as SetFocusAt)
			in order to set it.
		'''

		self.XYOrigin = XYOrigin
		self.RotationAngle = RotationAngle

		# Set of input parameters #1
		# (more mathematical, less common)

		if tl.CheckArg([R,Alpha,L]):
			# Input parameters
			#-------------------------------
			self._ValidateInput_Set2(R,Alpha,L)
			self._UpdateParametersProp()

		self.SetXYAngle_Origin(self.XYOrigin, self.RotationAngle) # calls _UpdataParametersLab()

	#================================
	# __disp__
	#================================
	def __str__(self):
		s0 = Optics.__str__(self) + '\n'
		s = '\n a=%0.2f\n b=%0.2f\n c=%0.2f\n f1=%0.2f\n f2=%0.2f\n\n' %(self.a, self.b, self.c, self.f1, self.f2)
		return s0+s

	#================================
	# _ValidateInput_Set1
	#================================
	def _ValidateInput_Set1(self, a,b, XProp_Centre, L):
		'''
		Called by __init__ is the input set of parameters #1 is used.

		Action
		------------------------
		Updates the reference-frame independent class attributes

		c :
			|
		f1,f2 :
			|
		Alpha :
			|
		'''

		# INPUT (which will be stored)
		self._a = a
		self._b = b
#		self._XProp_Centre = XProp_Centre
		self._L = L

		# COMPUTED 1
		self._c = np.sqrt(a**2 - b**2)

		# Computed 2 (intermediate)
		self._XYProp_F1 = np.array([-self.c, 0])
		self._XYProp_F2 = np.array([self.c,0])
		# -------------
		_YProp_Centre = np.array(self._EvalMirrorYProp(XProp_Centre))
		# -------------
		self._XYProp_Centre = np.array([XProp_Centre, _YProp_Centre])

		# Computed 3 (important)
		self._f1 = np.linalg.norm(self._XYProp_Centre - self._XYProp_F1)
		self._f2 = np.linalg.norm(self._XYProp_Centre - self._XYProp_F2)

		# Computed 4 (important)
		#self._UpdateParametersProp()

	#================================
	# _ValidateInput_Set2
	#================================
	def _ValidateInput_Set2(self,f1,f2,Alpha, L):
		'''
		Called by __init__ is the input set of parameters #1 is used.

		Action
		------------------------
		Updates the reference-frame independent class attributes

		a,b,c :
			|

		'''

		# Input parameters
		#-------------------------------
		self._f1 = f1
		self._f2 = f2
		self._Alpha = Alpha
		self._L = L

		# computed parameters (primary)

	#-------------------------------
		self._a = 0.5*(f1+f2)
#		self._c = 0.5 * np.sqrt(np.cos(Alpha)**2 * (f1+f2)**2 + np.sin(f1-f2)**2)
		self._c = 0.5 * np.sqrt(f1**2 + f2**2 - 2*f1*f2*np.cos(np.pi - 2*Alpha))
		self._b = np.sqrt(self.a**2 - self.c**2)

		# computed 2 (aux)
		elle = 2*self._c
		TmpArg = tl.Coerce(self._f2/elle * np.sin(np.pi - 2*Alpha),-1,1)
		self._ThetaProp = np.arcsin(TmpArg)
		self._XYProp_F1 = [-self.c, 0]
		self._XYProp_F2 = [self.c,0]
		_XProp_Centre = f1*np.cos(self._ThetaProp) + self._XYProp_F1[0]
		_YProp_Centre = self._EvalMirrorYProp(_XProp_Centre)
		self._XProp_Centre = _XProp_Centre
		self._YProp_Centre = _YProp_Centre
		self._XYProp_Centre = np.array([_XProp_Centre, _YProp_Centre])

	#================================
	# _UpdateParametersProp (*)
	#================================
	def _UpdateParametersProp(self):
		'''
			Finds the equation of the two arms in the Proper frame reference.
			Prop stands for 'Proper'.

			Requires
			-----------------------
			a,b

			_XYProp_F1, _XYProp_Centre, _XYProp_Start, _XYProp_End

			Updated Attributes
			------------------------
			p1Prop, p2Prop : coeffs of the the two arms
				|
			_pTanProp : coeffs of the line tangent to the centreof the mirror
				|
			_pTanProp_Angle : angle of the previous line
				|
			About the architercture
			------------------------
			Events such as the change of XYOrigin or of the rotation angle will
			result into a call to _UpdateParametersLab, which will convert the
			'Prop' parameters into 'Lab' parameters
				.
		'''
		# Finding start and end points of the mirror (in proper frame reference)
		#
		XStart = self._XYProp_Centre[0] - 0.5*self.L
		self._XYProp_Start = np.array([XStart, self._EvalMirrorYProp(XStart)])
		XEnd = self._XYProp_Centre[0] + 0.5* self.L
		self._XYProp_End  = np.array([XEnd, self._EvalMirrorYProp(XEnd)])

		# Trovo asse Sorgente- Centro Specchio (da mettere nella classe)
		[p2, p1] = self.TraceRay(self._XYProp_F1, self._XYProp_Centre)
		self._p1Prop = np.array(p1)
		self._p2Prop = np.array(p2)
		self._p1Prop_Angle = np.arctan(p1[0])
		self._p2Prop_Angle = np.arctan(p2[0])


		# equazione della tangente al centro dello specchio
		m = - self.b**2 / self.a**2 * self._XYProp_Centre[0] / self._XYProp_Centre[1]
		q =  self.b**2 / self._XYProp_Centre[1]

		self._pTanProp = np.array([m,q])
		self._pTanProp_Angle = np.arctan(m)
		self._ThetaProp = self._pTanProp_Angle




#		# angolo di pendenza proprio
#		elle = 2*self._c
##		self._ThetaProp = np.arcsin(self._f2/elle * np.sin(np.pi - 2*self.Alpha))
##		AlphaProp = self._Theta_to_Alpha(self._ThetaProp)
#
##		self.Alpha = self._ThetaProp_to_Alpha(self._ThetaProp)

	#================================
	# _UpdateParametersLab (*)
	#================================
	def _UpdateParametersLab(self):
		'''
			Updates the parameters which depend on the Laboratory reference frame,
			i.e. on the XYOrigin and on the RotationAngle attributes.

			XYF1, XYF2
				|
			Theta
				|
			_p1, _p2, _p1_Angle, _p2_Angle
				|



			_pTan, _pTan_Angle
				|
		'''

		# Rotation of Points
		self._XYLab_F1 = self._Transformation_XYPropToXYLab_Point(self._XYProp_F1)
		self._XYLab_F2 = self._Transformation_XYPropToXYLab_Point(self._XYProp_F2)

		self._XYLab_Centre =self._Transformation_XYPropToXYLab_Point(self._XYProp_Centre )
		self._XYLab_Start = self._Transformation_XYPropToXYLab_Point(self._XYProp_Start)
		self._XYLab_End = self._Transformation_XYPropToXYLab_Point(self._XYProp_End)


		# rotation of coefficients
		self._p1Lab = self._Transformation_PolyPropToPolyLab(self._p1Prop)
		self._p2Lab = self._Transformation_PolyPropToPolyLab(self._p2Prop)
		self._pTanLab = self._Transformation_PolyPropToPolyLab(self._pTanProp)
		self._p1Lab_Angle = np.arctan(self._p1Lab[0])
		self._p2Lab_Angle = np.arctan(self._p2Lab[0])


		# rotation of angles
		self._ThetaLab = np.arctan(self._pTanLab[0])
		self._pTanLab_Angle = np.arctan(self._pTanLab[0])

		# Injection to VersorTan (VersorTan is the primary VersorStuff of Optics numerical)
		self.VersorTan = tl.UnitVector(Angle = 1* self._pTanLab_Angle )



	#================================
	# _SetMirrorCoordinates
	#================================
	def _UpdateMirrorCoordinates(self, XMid, L):
		'''
		Automatically sets the values of XYStart and XYEnd

		Parameters
		--------------------
		XMid : scalar
			X middle coordinate of the mirror
		L : scalar
			Length of the mirror

		Called...
		--------------------
		During the init of the object
		'''

		XStart = XMid - 0.5*L
		self.XYStart = np.array([XStart, self.EvalY(XStart)])
		XEnd = XMid + 0.5* L
		self.XYEnd  = np.array([XEnd, self.EvalY(XEnd)])
		self._L = L




	#================================
	# _UpdateFociiFromParameters_XYOrigin
	#================================
	def _UpdateFociiFromParameters_XYOrigin(self):
		'''
			Updates (shift) the positions of focii according to XYOrigin.

			Call info
			-------------------
			Intended to be called ONLY by the XYOrigin setter.
		'''
		self.XYF1 = np.array([-self.c, 0]) + self.XYOrigin
		self.XYF2 = np.array([self.c,0]) + self.XYOrigin

	#================================
	# _UpdateFociiFromParameters_XMid
	#================================
	def _UpdateFociiFromParameters_XMid(self, XMid, DeltaX):
		'''
		Dati La posizione dello specchio e la lunghezza, definisce f1 e f2
		'''
		YMid = self.EvalY(XMid)
		XStart = XMid - 0.5*DeltaX
		YStart = self.EvalY(XStart)
		XEnd = XMid + 0.5*DeltaX
		YEnd= self.Eval(XEnd)

		self.XYCentre = np.array([XMid, YMid])
		self.XYStart = np.array([XStart, YStart])
		self	.XYEnd = np.array([XEnd, YEnd])

		self._f1 = np.linalg.norm(self.XYCentre - self.XYF1)
		#self._f1 = np.sqrt((self.XYCentre[0] - self.XYF1[0])**2 + (self.XYCentre[1] - self.XYF1[1])**2)
		self._f2 = np.linalg.norm(self.XYCentre - self.XYF2)
		#self._f2 = np.sqrt((self.XYCentre[0] - self.XYF2[0])**2 + (self.XYCentre[1] - self.XYF2[1])**2)
		self._L = DeltaX

	#================================
	# _EvalMirrorYProp (XProp)
	#================================
	def _EvalMirrorYProp(self, XProp, Sign = +1):
		'''
		Valuta l'equazione dell'ellisse
		Uses Analytic expression
		Parameters
		----------------
		x : float
		'''
		x = np.array(XProp)
		tmp = Sign*self.b * np.sqrt(1 - x**2 / self.a**2)
		return tmp



	#================================
	# GetXY_FocalPlaneAtF2(Size,N)
	#================================
	def GetOpticalElement_DetectorAtF2(self, L= 1e-3 , Defocus = 0, ReferenceFrame = 'lab' ):
		'''
			Uses: XYF1, XYF2, XYCentre
			Length (m)
			N: # samples
		'''
		# I create a dummy plane mirror
		pm = MirrorPlane(L = L,
				   AngleGrazing = -np.pi/2,
				   XYLab_Centre = self.XYF2,
				   AngleIn = self.RayOutNominal.Angle + np.pi )
		return pm

	#================================
	# GetXY_FocalPlaneAtF2(Size,N)
	#================================
	def GetXY_TransversePlaneAtF2(self, N=2,L= 1e-3 , Defocus = 0, ReferenceFrame = 'lab' ):
		'''
			Uses: XYF1, XYF2, XYCentre
			Length (m)
			N: # samples
		'''
		# I create a dummy plane mirror, and I use its methods to get detector points. In a more elegant fashion, the class 'Segment' should exist.
		pm = MirrorPlane(L = L,
				   AngleGrazing = -np.pi/2,
				   XYLab_Centre = self.XYF2,
				   AngleIn = self.RayOutNominal.Angle + np.pi )
		x,y = pm.GetXY(N)
		return [x,y]

	#================================
	# GetXY_FocalPlaneAtF2(Size,N)
	#================================
	def Old_GetXY_TransversePlaneAtF2(self, N=2,Length = 1e-3 , Defocus = 0, ReferenceFrame = 'lab' ):
		'''
			Uses: XYF1, XYF2, XYCentre
			Length (m)
			N: # samples
		'''
		Size = Length
		RayOut = self.RayOutNominal

		[p1, p2] = self.TraceRay(self.XYF1, self.XYCentre)
		m = -1/p2[0]
		theta = np.arctan(m)
		thetaNorm = np.arctan(p2[0])
		DeltaXY = Defocus * np.array([np.cos(thetaNorm), np.sin(thetaNorm)])
		XY = self.XYF2 + DeltaXY
#		q = - self.XYF2[0] * m
		q = XY[1] - XY[0] * m
		p = np.array([m,q])

		Det_x0 = XY[0] - Size/2 * np.cos(theta)
		Det_x1 = XY[0] + Size/2 * np.cos(theta)
		x = np.linspace(Det_x0, Det_x1,N)
		y = np.polyval(p,x)

		if ReferenceFrame == 'lab':
			x,y = self._Transformation_XYPropToXYLab(x,y)
		return [x,y]

 	#================================
	# GetXY
	#================================
	def GetXY(self, N, Options =['ideal'] ):
		'''
		Main User-interface function for getting the x,y points of the mirror
		in the laboratory reference frame.

		Options can be
		- 'ideal' : the ideal mirror profile is used (default)
		- 'perturbation' : instead of the nominal position of the mirror, the position of the mirror computed via  longitudinal, transverse and angular
		 "perturbations" around the nominal configuration.
		- 'figure error' : a figure error is added to the mirror profile, if possible
		- 'roughness' : a roughness profile is added to the mirror profile, if possible
		'''

		if 'ideal' in Options:
			return self.GetXY_IdealMirror(N)
		else:
			print("2 Mirror.GetXY: Option set not implemented. \n Options = %s" % str(Options))

	#================================
	# GetXY_CompleteEllipse(N)
	#================================
	def GetXY_CompleteEllipse(self, N, ReferenceFrame = 'lab'):

		# specchio
		Mir_xProp = np.linspace(-self.a, self.a, N)

		Mir_yProp_p = self._EvalMirrorYProp(Mir_xProp)
		Mir_yProp_m = self._EvalMirrorYProp(Mir_xProp[::-1], -1)

		Mir_x__ = np.append(Mir_xProp, Mir_xProp[::-1])
		Mir_y__ = np.append(Mir_yProp_p, Mir_yProp_m)

		if ReferenceFrame =='lab':
			Mir_x__, Mir_y__ = self._Transformation_XYPropToXYLab(Mir_x__, Mir_y__)

		return Mir_x__, Mir_y__

	#================================
	# GetXY_IdealMirror(N)
	#================================
	def GetXY_IdealMirror(self, N, Sign = +1, ReferenceFrame = 'lab'):
		'''
			Evaluates the MirrorElliptic only over the physical support of the mirror
			(within XStart and XEnd)
			N is the number of samples in X.

			 @TODO: define N of samples along the MirrorElliptic (ma serve?)
		'''
		""" VECCHIO
		x = linspace(self.XYStart[0], self.XYEnd[0], N)
		return [x,self._EvalMirrorYProp(x, Sign)]
		"""

		x = np.linspace(self._XYProp_Start[0], self._XYProp_End[0],N)
		y = self._EvalMirrorYProp(x, Sign)

		if ReferenceFrame == 'lab':
			x,y = self._Transformation_XYPropToXYLab(x,y)
		return x,y

	#================================
	# Get_LocalTangentAngle
	#================================
	def Get_LocalTangentAngle(self, x0, y0, ProperFrame = False):
		''' Return the angle (refferred ti x axis) of the tangent to the ellipse
			in the point x0,y0
		'''
		m = -self.b**2 / self.a**2 * x0/y0
		return np.arctan(m)


	#================================
	# GetXY_MeasuredMirror
	#================================

	def GetXY_MeasuredMirror(self, N, iFigureError = 0, GenerateRoughness = False, Reference = 'lab' ):
		# carico il figure error e, se necessario, lo ricampiono
		#-----------------------------------------------------------------
		if len(self._FigureErrors)-1 >= iFigureError:
			hFigErr  = self.FigureErrors[iFigureError]
			self._L = len(hFigErr) * self._FigureErrorSteps[iFigureError]
			hFigErr  = rm.FastResample1d(hFigErr - np.mean(hFigErr  ), N)
		else:
			hFigErr   = np.zeros(N)

		# aggiungo la roughness (se richiesto, rigenero il noise pattern)
		#-----------------------------------------------------------------

		if self.Options.USE_ROUGHNESS == True:
			hRoughness = self.Roughness.MakeProfile(self.L, N)

			########################### added by L.Rebuffi
			if len(hRoughness) < N:
				filler = np.zeros(N-len(hRoughness))
				hRoughness = np.append(filler, hRoughness)
			##############################################

			self.LastRoughnessUsed = hRoughness

			myResidual = hFigErr + hRoughness
		else:
			myResidual = hFigErr

		self.LastResidualUsed = myResidual
		self.LastFigureErrorUsed = myResidual
		self.LastFigureErrorUsedIndex = iFigureError
		# proiezione del FigError sull'ellisse
		# -----------------------------------------------------------------
		Mir_x, Mir_y = self.GetXY_IdealMirror(N)
		ThetaList = self.Get_LocalTangentAngle(Mir_x, Mir_y)

		Mir_xx = Mir_x + myResidual * np.sin(ThetaList)
		Mir_yy = Mir_y + myResidual * np.cos(ThetaList)

		if Reference == 'lab':
			Mir_xx, Mir_yy = self._Transformation_XYPropToXYLab(Mir_xx, Mir_yy)
		return Mir_xx, Mir_yy
	#================================
	# SetXYAngle_Origin
	#================================
	def SetXYAngle_Origin(self,XYOriginNew, Angle = 0 ):
		'''
		Set the mirror such that the cartesian reference frame is placed at XYOriginNew at the given Angle.
		NOT FOR USERS: supposed to be invoked just durinf __init__
		'''
		XYOriginNew = np.array(XYOriginNew)
		if all(XYOriginNew == np.array([0,0])) and (Angle ==0):
			pass
		else:
			self._Transformation_Clear()
			self._Transformation_Add(Angle,
									-XYOriginNew,
									[0,0])
		self._UpdateParametersLab()

	#================================
	# SetXYAngle_UpstreamFocus
	#================================
	def SetXYAngle_UpstreamFocus(self,XYNewFocus, Angle = 0 ,  WhichAngle = 'arm'):
		'''
		Set the mirror such that the upstream focus is in a given position with a
		given angle.
		SetXYA => Set XY coordinates and orientation Angle.

		'''
		if WhichAngle == 'arm' :
			a = self._p1Prop_Angle
			TotalAngle = Angle - a
			xNewCentre = -self._XYProp_F1[0]*np.cos(TotalAngle)+XYNewFocus[0]
			yNewCentre = -self._XYProp_F1[0]*np.sin(TotalAngle)+XYNewFocus[1]
			self._Transformation_Clear()
			self._Transformation_Add(TotalAngle,
									[0,0],
									[0,0])
			self._Transformation_Add(0,
									[xNewCentre,yNewCentre],
									self._XYProp_F1)
		else:
			print ('_SetFocusAt: Method not implemented yet with this ')
			pass
		self._UpdateParametersLab()

	#================================
	# SetXYAngle_Centre
	#================================
	def SetXYAngle_Centre(self,XYMirrorCentreNew, Angle = 0 ,  WhichAngle = 'arm1'):
		'''
		Set the mirror such that the mirror centre is in a given position with
		(its tangent) at a given angle.

		SetXYA => Set XY coordinates and orientation Angle.

		Set the centre of the optical element.
		In this case, the centre is intended to be the mirror centre.
		'''
		XYMirrorCentreNew = np.array(XYMirrorCentreNew)

		if WhichAngle == 'arm1':
			a = self._p1Prop_Angle
		elif WhichAngle == 'arm2':
			a = self._p2Prop_Angle
		elif WhichAngle == 'axis':
			a = 0
		TotalAngle = Angle - a

		self._Transformation_Clear()
		self._Transformation_Add(0,
								-self._XYProp_Centre+XYMirrorCentreNew,
								XYMirrorCentreNew)
		self._Transformation_Add(TotalAngle,
								[0,0] ,
								XYMirrorCentreNew)
		self._UpdateParametersLab()



	#================================
	# _AddResidualToMirrorElliptic
	#================================
	def _AddResidualToMirrorElliptic(self, myResidual):
		# Assume che la lunghezza fisica di myResidual sia uguale a quella di self.L (che ?? ci?? che accate se Options.)
		N = len(myResidual)
		[Mir_x, Mir_y] = self.GetXY_IdealMirror(N)
		ThetaList = self._LocalTangent(Mir_x, Mir_y)
		NewMir_x = Mir_x + myResidual * np.sin(ThetaList)
		NewMir_y = Mir_y + myResidual * np.cos(ThetaList)
		return (NewMir_x, NewMir_y)


	# ---------------------------------------------------------
	# 	     MIRROR PROPERTIES
	#	They are independent of reference-frame
	#---------------------------------------------------------


	@property # Ellipse parameter a
	def a(self):		return self._a

	@property # Ellipse parameter b
	def b(self):		return self._b

	@property # Ellipse parameter c
	def c(self):		return self._c


	@property # Ellipse parameter f1
	def f1(self):		return self._f1

	@property # Ellipse parameter f2
	def f2(self):		return self._f2

	@property # Grazing angle

	def Alpha(self):		return self._Alpha

	@property # Mirror Length
	def L(self):		return self._L
	@L.setter
	def L(self, val): self._L = val


	@property # Magnification
	def M(self):		return self._f1/self._f2

	# ---------------------------------------------------------
	# 	     PUBLIC PROPERTIES (READ ONLY)
	#	in the Laboratory reference-frame
	#---------------------------------------------------------

#	@property
#	def VersorNorm(self):
#		return tl.UnitVector(Angle = self.pTan_Angle +np.pi/2, XYOrigin = self.XYCentre)
	# Upstream Focus
	@property
	def XYF1(self):
		return  np.array(self._XYLab_F1)
	# Downstrem Focus
	@property
	def XYF2(self):
		return np.array( self._XYLab_F2)
	# Centre of the mirror
	@property
	def XYCentre(self):
		return np.array(self._XYLab_Centre)
	# Start point (upstream) of the mirror
	@property
	def XYStart(self):
		return np.array(self._XYLab_Start)
	# Endpoint (downstream) of the mirror
	@property
	def XYEnd(self):
		return  np.array(self._XYLab_End)
	#================================
	#  PROP: AngleGrazing
	#================================
	@property
	def AngleGrazing(self):
		return self._Alpha

	# Coefficients of Arm 1 (centre mirror to upstream focus)
	@property
	def p1(self):
		return self._p1Lab
	# Coefficients of Arm 2 (centre mirror to downstream focus)
	@property
	def p2(self):
		return self._p2Lab
	# Angle of arm 1
	@property
	def p1_Angle(self):
		return self._p1Lab_Angle
	# Angle of arm 2
	@property
	def p2_Angle(self):
		return self._p2Lab_Angle
	# Coefficients of the line tangent to XYCentre
	@property
	def pTan(self):
		return self._pTanLab
	# Angle of pTan
	@property
	def pTan_Angle(self):
		return self._pTanLab_Angle

	#================================
	# TraceRay
	#================================
	def TraceRay(self, XYStart, XEnd):
		'''
			Parameters
			---------------
			XYStart : [x,y], a point in the space
			XEnd : x coordinate of the mirror

			Returns
			---------------
			IncidentRay : [p1,p0] coefficients describing the incident ray
			Reflected Ray : [p1,p0] coefficients describing the incident ray

			Dato l'ellisse (oggetto), il punto di partenza Start e la X di incidenza,
			trova il polinomio di ordine 1 (retta) del raggio incidente e di quello
			riflesso
		'''
		Start = XYStart
		End = XEnd
		a = self.a
		b = self.b
		if len(End) == 1:
			xEll = End
			yEll = self.EvalY(xEll)
		elif len(End) == 2:
			xEll = End[0]
			yEll = End[1]



		xStart = Start[0] ;
		yStart = Start[1] ;

		# raggio uscente (2)


		m0 = -b**2/a**2 * xEll/yEll ;
		m2 =  (yStart - yEll) / (xStart - xEll) ;

		Theta0 = np.arctan(m0) ;
		Theta2 = np.arctan2((yStart - yEll),(xStart - xEll)) ;
		Theta1 =+( -Theta2 + 2*Theta0 - np.pi) ;

		m1 = np.tan(Theta1) ;

		q = yEll - m1 * xEll ;

		p = [m1,q] ;
		p1 = p ;			# il raggio (1) (entrante)

		# raggio di partenza (1) ;

		q = yEll - m2 * xEll ;

		p = [m2,q] ;
		p2 = p ;		 # il raggio (2) uscente

		return p1, p2
	#================================
	# _UpdateThetaPropFromAlpha
	#================================
	def _UpdateThetaPropFromAlpha(self):
		'''
			Computes the Theta angle (reffered to x axis)
			using Alpha angle (referred to mirro incidence plane)
		'''
#		m = -self.b**2/self.a**2 * self._XYProp_Centre[0] /self._XYProp_Centre[1]
#
#		# SIAMO SICURI? non manca un np.arctan?!?!?!
#		return abs(Alpha - abs(m ))
		tmpArg = tl.Coerce(self._f2/(2*self._c) * np.sin(np.pi - 2*self._Alpha),-1,1)
		self._ThetaProp = np.arcsin(TmpArg)
		# @todo

	#================================
	# _UpdateAlphaFromThetaProp
	#================================
	def _UpdateAlphaFromThetaProp(self):
		'''
			Computes the Theta angle (reffered to x axis)
			using Alpha angle (referred to mirro incidence plane
		'''
#		m = -self.b**2/self.a**2 * self._XYProp_Centre[0] /self._XYProp_Centre[1]
#		return abs(ThetaProp - abs(np.arctan(m)))
		if self._pTanProp_Angle != self._ThetaProp:
			print ('Cazzo succede? 827')

		self._Alpha = abs(self._p1Prop_Angle) + abs(self._ThetaProp)

	#================================
	# _SourceDisplacement
	#================================
	def _SourceDisplacement(self, Long, Trans):
		'''
		Converts a (Longitudinal, Transverse) displacement of the source to a
		(x,y) displacement.

		Parameters
		----------------
		Long : longitudinal displacement
		Trans: Transverse displacement

		Notice: the reference axis is the joining line of the MirrorElliptic [Focus1 - Centre Mirrors]
		'''
		DeltaXOrigin = (Long* np.cos(self.p1_Angle) +
					Trans* np.sin(self.p1_Angle))
		DeltaYOrigin = (Long* np.sin(self.p1_Angle) +
					Trans* np.cos(self.p1_Angle))
		return DeltaXOrigin, DeltaYOrigin

	# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	#
	#	WISE 2.0 DEV++ section
	#
	# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



	@property
	def RayInNominal(self):
		RayIn = tl.Ray(x1 = self.XYCentre[0], y1 = self.XYCentre[1],
			  x0 = self.XYF1[0], y0 = self.XYF1[1])
		RayIn.XYOrigin = self.XYCentre
		return RayIn
	#================================================
	#	GetRayOutNominal
	#	INTERFACE FUNCTION
	# 	(called in Fundation.OpticalElement)
	#================================================
	@property
	def RayOutNominal(self):
		'''
       Return the nominal outcoming ray. Uses the member attributes
       of the object for the computation.
		'''
		RayOut = tl.Ray(x0 = self.XYCentre[0], y0 = self.XYCentre[1],
				  x1 = self.XYF2[0], y1 = self.XYF2[1])
		RayOut.XYOrigin = self.XYCentre
		return RayOut

	#================================
	# FUN: Paint
	#================================
	def Paint(self, FigureHandle= None, N = 100, Length = None, ArrowWidth = None, Color = 'm', Complete = True, **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.
		N is the number of samples.
		'''
		# Paint the mirror
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		x_mir, y_mir = self.GetXY_IdealMirror(N)
		plt.plot(x_mir, y_mir, Color + '.')


		# Paint the ellipse
		if Complete == True:
			x_mir, y_mir = self.GetXY_CompleteEllipse(N)
			plt.plot(x_mir, y_mir, Color + '.', markersize = 0.5)
			# mark the focii
			plt.plot(self.XYF1[0], self.XYF1[1], Color + 'x', markersize = 7)
			plt.plot(self.XYF2[0], self.XYF2[1], Color + 'x', markersize = 7)
		# finds a good arrow lenght
		if Length == None:
			Length = 0.1
		if ArrowWidth == None:
			ArrowWidth = Length * 0.3


		# paint the normal versor (green)
		self.VersorNorm.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'g')
		# paint the tangential versor (yellow)
		self.VersorTan.Paint(FigureHandle, Length = 2*Length, ArrowWidth = ArrowWidth,Color = 'y')
		# paint the inputray (blue)
		self.RayInNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'b', Shift = True)
		# paint the output ray (red)
		self.RayOutNominal.Paint(FigureHandle, Length = Length, ArrowWidth = ArrowWidth, Color = 'r')


		return FigureHandle


#==============================================================================
#	 CLASS: Detector
#==============================================================================
class Detector(MirrorPlane):
	_TypeStr = 'DT'
	_CommonInputSets = [(('L','Length' ),
						('AngleGrazing','Grazing Angle')),
					  ]

	def __init__(self, L=None, AngleGrazing=None, XYLab_Centre=[0,0], AngleIn=0, **kwargs):
		# UseAsReference = False => Make detector transparent by default
		MirrorPlane.__init__(self, L, AngleGrazing, XYLab_Centre, AngleIn, **kwargs)
#		super().__init__(**kwargs)
		self.UseAsReference = False

#==============================================================================
#	 CLASS ABSTRACT: OpticsEfficiency
#==============================================================================
class OpticsEfficiency(Mirror):
	"""
	A selection of functions to calculate efficiency of the optical element:
	- reflectivity
	- transmitivity
	"""

	def __init__(self):
		super().__init__()

	def Reflectivity(self, n, k):
		"""
		Calculate reflectivity using Fresnel optical equations, Peatman, p. 119, 120. Peatman's definition is:
		widetilde(n) = n + ik
		CXRO parameters are delta and beta, with the following definition:
		widetilde(n) = (1-delta) - i beta

		Therefore, one must take n=(1-delta) and k=-beta.

		:param n: refractive index for X-rays at the wavelength
		:param k: extinction coefficient for X-rays at a wavelength
		:return: reflectivity of the multilayer
		"""

		theta = np.pi / 2. - self.AngleGrazingNominal

		a = np.sqrt(0.5 * (((n**2 - k**2 - np.sin(theta)**2)**2 + 4. * n**2 * k**2)**0.5 + (n**2 - k**2 - np.sin(theta)**2)))
		b = np.sqrt(0.5 * (((n**2 - k**2 - np.sin(theta)**2)**2 + 4. * n**2 * k**2)**0.5 - (n**2 - k**2 - np.sin(theta)**2)))

		R_s = ((a - np.cos(theta))**2 + b**2) / ((a + np.cos(theta))**2 + b ** 2)  # Polarization, perpendicular to incidence plane
		R_p = R_s * ((a - np.sin(theta) * np.tan(theta))**2 + b**2) / ((a + np.sin(theta) * np.tan(theta))**2 + b**2) # Polarization, parallel to incidence plane

		return R_s, R_p

#==============================================================================
#	 CLASS: TransmissionFunction
#==============================================================================
class Slits(OpticsNumerical):
	'''
	This class is introduced to cover the following needs:
		1 - introduce slits\apertures etc in a generic position along the optical axis (e.g. between the source and a mirror)
		2 - allow easy multiplication for transmission function (spherical waves, phase masks), either in a generic position
			along the beam, or just upstream\downstream a certain optical element.

		TransmissionMask can be thought as a segment where each point (x,y) is associated to a complex Transmission value,
		.GetXY returns (x,y)
		.GetT returns the transmission function

		The spatial/alignment behaviour of TransmissionMask  is the same as MirrorPlane.

		The behaviour is described by the TransmissionFunction, which must be defined in more specific classes
		(e.g. TransmsssionSlits, TransmissionSphericalWave, etc.	)

		Positioning behaviour
		-----
		If TransmissionMask.ComputationSettings.Action = 'UpstreamMultiplication' or 'DownstreamMoultiplication' then
		a) the position of the TransmissionMask is equal to that of the previous optical element.
		b) the computation of the field is a simple multipication
		c) 'small displacements' are not used

		If TransmissionMask.ComputationSettings.Action = 'Propagate' then
		a) the position of the TransmissionMask is computed as that of a plane mirror
		b) the computation of the field is computed via Huygens Fresnel.
	'''

	_TypeStr = 'SL'
	_TypeDescr = "Slits"
	_Behaviour = OPTICS_BEHAVIOUR.Slits
	_IsAnalytic = False
	_PropList = ['AngleIn', 'AngleGrazing', 'AngleTan', 'AngleNorm',
				 'XYStart', 'XYCentre', 'XYEnd']
	_MementoVariables = ('_L')
	# ================================
	#  FUN: __init__
	# ================================
	def __init__(self, L=None, AngleGrazing=np.pi/2., XYLab_Centre=[0, 0], AngleIn=0, **kwargs):
		super().__init__(**kwargs)  # No roughness, no small displacements, no figure error from super
		'''
		Init:
		Optics
		self.XY = array([XPosition, YPosition])
		self.SmallDisplacements = Optics._SmallDisplacements()
		self.ComputationSettings = Optics._ComputationSettings()
		self.Orientation = OPTICS_ORIENTATION.Any

		OpticsNumerical
		self._Transformation_List = [ [], [], [] ]
		self.AngleLab = 0
		self._XYLab_Centre = array([0,0])
		self.ComputationSettings = OpticsNumerical._ComputationSettings()

        Parameters
        ---------------------
        XYLab_Centre : [x,y]
            Coordinates of the centre of the mirror
        AngleIn: float (radians)
            Angle of the input ray in the laboratory reference frame.
        AngleGrazing : angle, radians
            Grazing angle which must be preserved between the mirror and the InputAngleLab.
            It is used to compute MirrorAngle
        '''
		# BUILDING
		if tl.CheckArg([L, AngleGrazing]):
			self._L = L
			self._AngleGrazingNominal = AngleGrazing
			self.SetXYAngle_Centre(XYLab_Centre, AngleIn)
		else:
			tl.ErrMsg.InvalidInputSet

		# self.SmallDisplacements = False
		self._FigureErrors = []
		self._UpdateParameters_Lines()
		self._UpdateParameters_XYStartEnd()
		self.UseAsReference = False

	# ================================
	#  FUN: __str__
	# ================================
	def __str__(self):
		StrList = ['%s=%s' % (PropName, getattr(self, PropName)) for PropName in Slits._PropList]
		return 'Slits \n' + 20 * '-' + '\n' + '\n'.join(StrList) + '\n' + 20 * '-'

	# ================================
	# PROP: FigureErrors
	# ================================
	@property
	def FigureErrors(self): return self._FigureErrors

	# ================================
	#  PROP: AngleGrazingNominal
	# ================================
	@property
	def AngleGrazingNominal(self):
		return self._AngleGrazingNominal

	# ================================
	# GetXY_IdealMirror(N)
	# ================================
	def GetXY_IdealMirror(self, N=100):
		'''
		Return the coordinates of the ideal mirror.

		Return
		--------------------
		x : array
			x points
		y : array
			y:point
		'''
		N = int(N)
		if (self.XYStart[0] != self.XYEnd[0]):
			#if self.AngleTanLab%(np.pi / 2.) == 0.:

			x = np.linspace(self.XYStart[0], self.XYEnd[0], N)
			y = self.Line_Tan.m * x + self.Line_Tan.q
		else:  # handles the case of vertical mirror
			x = np.float(self.XYStart[0]) + np.zeros(N)
			y = np.linspace(self.XYStart[1], self.XYEnd[1], N)
		return x, y

	# ================================
	# GetXY
	# ================================
	def GetXY(self, N):
		'''
		Main User-interface function for getting the x,y points of the mirror
		in the laboratory reference frame.
		Uses the self.ComputationSettings parameters for performing the computation parameters
		-----
		N : int
			Number of samples.

		Uses
		-----
		self.ComputationSettings : (class member)
			See computation settings.
		'''
		xLab, yLab = self.GetXY_IdealMirror(N)
		return xLab, yLab

	# ================================
	# _SetMirrorCoordinates
	# ================================
	def _SetMirrorCoordinates(self, XMid, L):
		'''
		Given the longitudinal (X) position of the middle-point of the mirror
		and the mirror length, it defines XYStart and XYEnd.
		'''

		XStart = XMid - 0.5 * L
		self.XYStart = np.array([XStart, self.EvalY(XStart)])
		XEnd = XMid + 0.5 * L
		self.XYEnd = np.array([XEnd, self.EvalY(XEnd)])
		self._L = L

	# ================================
	#  PROP EXTENSION: XYCentre
	# ================================
	def XYCentre(self, value):
		super.XYCentre = value
		self._UpdateParameters_XYStartEnd()

	# ==============================
	#  PROP: L
	# ================================
	@property
	def L(self):
			return self._L

	@L.setter
	def L(self, value):
		self._L = value
		self._UpdateParameters_XYStartEnd()

	# ================================
	#  PROP: AngleInputLabNominal
	# ================================
	@property
	def AngleInputLabNominal(self):
		'''
		Angle (in the Lab reference) of the incident beam.
		Computed using: AngleLab and AngleGrazingNominal
		Depends on Mirror type.
		'''
		return self.AngleLab - np.pi / 2 - self.AngleGrazingNominal

	# ================================
	#  PROP: AngleNorm
	# ================================
	@property
	def AngleNorm(self):
		return self._AngleNorm

	# ================================
	#  PROP: Line_Tan
	# ================================
	@property
	def Line_Tan(self):
		"""
		Line object, containing the tangent to the mirror
		"""
		return self._Line_Tan

	# ================================
	#  PROP: XYStart
	# ================================
	@property
	def XYStart(self):
		return self._XYLab_Start

	# ================================
	#  PROP: XYEnd
	# ================================
	@property
	def XYEnd(self):
		return self._XYLab_End

	# ================================
	# Get_LocalTangentAngle
	# ================================
	def Get_LocalTangentAngle(self, x0, y0, ProperFrame=False):
		return self.VersorTan.Angle

	# ================================
	# SetXYAngle_Centre
	# ================================
	def SetXYAngle_Centre(self, XYLab_Centre, Angle, WhichAngle=TypeOfAngle.InputNominal, **kwargs):
		'''
		Set the element XYCentre and orientation angle.
		CHECK CONTROLLARE: non mi ricordo pi?? che cosa siano gli angoli
		'''

		self.XYCentre = XYLab_Centre

		if WhichAngle == TypeOfAngle.Surface:  # Angle is the Normal to the surface
			self.AngleLab = Angle

		elif WhichAngle == TypeOfAngle.InputNominal:  # Angle is the angle of the input beam
			self.AngleTanLab = Angle + self.AngleGrazingNominal

		self._UpdateParameters_XYStartEnd()
		self._UpdateParameters_Lines()


	def _UpdateParameters_XYStartEnd(self):
		# Uses: _XYLab_Centre, _VersorNorm
		# Defines: XYStart, XYEnd
		# Called: in __init__
		# According to the y component of .VersorNorm, I define the
		# start and end points of the mirror.

		#		XY_a = self._XYLab_Centre + self.L/2 * self.VersorNorm.vNorm
		#		XY_b = self._XYLab_Centre - self.L/2 * self.VersorNorm.vNorm

		XY_a = self.XYCentre + self.L / 2. * self.VersorNorm.vNorm
		XY_b = self.XYCentre - self.L / 2. * self.VersorNorm.vNorm

		if XY_a[0] < XY_b[1]:
			self._XYLab_Start = XY_a
			self._XYLab_End = XY_b
		elif XY_a[0] >= XY_b[1]:
			self._XYLab_Start = XY_b
			self._XYLab_End = XY_a

	# ================================
	# FUN: _UpdateParameters_Lines
	# ================================
	def _UpdateParameters_Lines(self):
		# Uses: XYCentre, _AngleTan
		# Called: in init, When XYCentre is changed;
		# 	 	 	in SetXYAngle_Centre
		pass

	# ================================
	# PROP _Line_Tan
	# ================================
	@property
	def _Line_Tan(self):
		'''
		Line np.tan is the line tangent to the mirror surface, viz the equation
		of the mirror itself
		'''
		m = np.tan(self.AngleTanLab)
		q = self.XYCentre[1] - m * self.XYCentre[0]
		return tl.Line(m, q)

	# ================================================
	#	GetRayOutNominal
	#	INTERFACE FUNCTION
	# 	(called in Fundation.OpticalElement)
	# ================================================

	# ================================
	# PROP: GetRayInNominal
	# ================================
	@property
	def RayInNominal(self):
		v = tl.UnitVector(Angle=self.AngleInputLabNominal).v
		return tl.Ray(vx=v[0], vy=v[1], XYOrigin=self.XYCentre)

	# ================================
	# PROP: RayOutNominal
	# ================================
	@property
	def RayOutNominal(self):
		v = tl.UnitVector(Angle=self.AngleInputLabNominal).v
		return tl.Ray(vx=v[0], vy=v[1], XYOrigin=self.XYCentre)

	# ================================
	# FUN: Paint
	# ================================
	def Paint(self, FigureHandle=None, N=100, Length=1, ArrowWidth=1, Color='m', **kwargs):
		'''
		Paint the object (somehow... this is a prototype) in the specified figure.
		N is the number of samples.
		'''
		# Paint the mirror
		Fig = plt.figure(FigureHandle)
		FigureHandle = Fig.number
		x_mir, y_mir = self.GetXY_IdealMirror(N)
		plt.plot(x_mir, y_mir, Color + '.')
		# mark the mirror centre
		plt.plot(self.XYCentre[0], self.XYCentre[1], Color + 'x')
		# paint the normal versor
		self.VersorNorm.Paint(FigureHandle, Length=Length, ArrowWidth=ArrowWidth)
		# paint the inputray
		self.RayInNominal.Paint(FigureHandle, Length=Length, ArrowWidth=ArrowWidth, Color='g', Shift=True)
		# paint the output ray
		self.RayOutNominal.Paint(FigureHandle, Length=Length, ArrowWidth=ArrowWidth, Color='c')
		return FigureHandle

	# ================================
	#  Draw
	# ================================
	def Draw(self, N=100):
		x, y = tl.geom.DrawSegmentCentred(self._L, self.XYCentre[0], self.XYCentre[1], self.Angle, N)
		return x, y

#==============================================================================
#	 REDUNDANCIES
#==============================================================================
SourceGaussian_1d = SourceGaussian
SourcePoint_1d = SourcePoint

#=============================
#     ENUM: OPTICS_CLASSES
#=============================
class OPTICS_TYPE:
	Dummy = 0
	MirrorPlane = MirrorPlane
	EllipticalMirror = MirrorElliptic



