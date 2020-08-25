'''
Line Equation
:math:`y = m x + q`
Author michele.manfredda@elettra.eu

'''

from __future__ import division
from LibWiser.must import *
import LibWiser
from LibWiser import Optics, Rayman as rm, ToolLib as tl
from LibWiser import Rayman
from LibWiser.ToolLib import  Debug
import inspect
from collections import OrderedDict
import numpy as np
import copy
from enum import Enum
import time
import warnings

from LibWiser.Optics import TypeOfAngle


#=============================
#     DICT: INSERT_MODE
#=============================
class INSERT_MODE:
	After = 1
	Before = 2
	Fork = 3

##=============================
##     DICT: POSITIONING_MODE
##=============================
#class P:
#	Absolute
#	Before = 1
#	After = 2


#===========================================================================
# 	STRUCT: ComputationResults
#===========================================================================
class ComputationResults(LibWiser.Scrubs.DataContainer):
	def __init__(self):
		self.Lambda = 0         #wavelength used
		self.NSamples = None
		self.Field = None   #e.e. field.
		self.X = None   #x coordinates (N samples)
		self.Y = None
		self.S = None   #the sampled points along the OE longitudinal axis
		self.Action = None
		self.Name = ''

	#============================
	# PROP Intensity
	#============================
	@property
	def Intensity(self):
		try:
			return abs(self.Field)**2
		except:
			return None

	#============================
	# PROP Hew
	#============================
	@property
	def Hew(self):
		'''
		returns the Half energy width
		'''

		Step = np.mean(np.diff(self.S))
		Hew, iHew = Rayman.HalfEnergyWidth_1d(self.Intensity, UseCentreOfMass = False, Step = Step)

		return Hew
		'''
		Field : can be either automatically filled as the result of propagation, or
		"manually" filled as the input field (i.e. the beginning of a propagation chain).
		'''


	#===========================================================================
# 	STRUCT: PropagationDirectives
#===========================================================================
class PropagationInfo(object):
	class Method:
		Numerical= 'numerical'
		Analytical= 'analytical'
		Ignore = 'ignore'
		AnaltyticalSource = 'analytical source'

	def __init__(self, Ignore = False):
		self.Ignore = Ignore

#===========================================================================
# 	STRUCT: ComputationSettingsForOpticalElement
#===========================================================================
class ComputationSettingsForOpticalElement(object):
	class Method:
		Numerical= 'numerical'
		Analytical= 'analytical'
		Ignore = 'ignore'
		AnaltyticalSource = 'analytical source'

	def __init__(self, Ignore = False):
		self.Ignore = Ignore
		self.NSamples = 2002
		self.UseCustomSampling = False
		self.OversamplingFactor = 1

		@property
		def NSamples (self):
			return self._NSamples
		@NSamples.setter
		def NSamples (self, value):
			self._NSamples = int(value)



#===========================================================================
# 	STRUCT: PositioningDirectives
#===========================================================================
class PositioningDirectives:
	'''
	Attribute of Fundation.OpticalElement (OE)
	Says how the OE must be physically positioned in the beamline.

	See: help of __init__ function for the description of parameters.
	2

	'''
	_PropList = ['ReferTo', 'What', 'Where', 'GrazingAngle',
				   'Distance', 'XYCentre', 'Angle', 'WhichAngle']
	class What:
		Centre = 'centre'
		UpstreamFocus = 'upstream focus'
		DownstreamFocus = 'downstream focus'

	class Where:
		Centre = 'centre'
		UpstreamFocus = 'upstream focus'
		DownstreamFocus = 'downstream focus'

	class ReferTo:
		AbsoluteReference = 'absolute'
		UpstreamElement = 'upstream'
		DownstreamElement = 'downstream'
		DoNotMove = 'fix'
		Source = 'source'
		Locked = 'locked'

	class WhichAngle:
		AxisOfTheSelfReferenceFrame = 'self' #default configuration
		FirstArmOfEllipticMirror = 'arm1'
		SecondArmOfEllipticMirror= 'arm2'

	def __init__(self, ReferTo = 'source', PlaceWhat = 'centre', PlaceWhere = 'centre',
					 Distance = 0., GrazingAngle = None, XYCentre = None, Angle = None, WhichAngle = 'axis',
					 *kwargs):
		'''
		[TODO] : means that the stuff still does not work.

		Parameters
		------------------
		ReferTo : string, member of PositioningDirectives.
		ReferTo. 	Says with respect to which optical element (in the layout) the current one will be installed. Misuses of this parameter may give rise to broken chain (e.g. in the chain oe1---oe2, oe1 has ReferTo = 'downstream', and oe2 has ReferTo = 'upstream), which will be reported somewhere. For the moment, let pay attention to it...
				- 'upstream' : place the current item respect with the previous one
				- 'downstream' : place the current item respect with the following one [TODO]
		What : string, member of PositioningDirectives.What
			- 'centre' : designates the centre of the optical element (the mirror centre, the source centre, etc...)
			- 'upstream focus' : designates the upstream focus of the optical element
			- 'downstream focus' : designates the downstream focus of the optical element [TODO]
		Where : string, member of PositioningDirectives.Where
			- 'absolute' : uses absolute positioning. The SetXYAngle method is invoked.   If used, PlaceWhat and PlaceWhere are ignored.
			- 'centre' : the same as above.
			- 'upstream focus' : the same as above.
			- 'downstream focus' : the same as above.

		Distance : if the positioning is 'centre to centre' then the distance is the 'centre to centre distance'.
			If it it is 'centre to focus', then Distance is an extra distance respect with the focus, etc.



		'''
		#
		self.ReferTo = ReferTo   	 	 	 	 	#The behaviour is well defined (mandatory)
		self.What = PlaceWhat 	 	 	 	 	 	#The behaviour is well defined (mandatory)
		self.Where = PlaceWhere 	 	 	 	 	#The behaviour is well defined (mandatory)
		self.Distance = Distance 	 	 	 	 	#The behaviour is well defined
		self.XYCentre = XYCentre if XYCentre != None else ([0,0] if ReferTo =='absolute' else None)

		self.GrazingAngle = GrazingAngle
		self.Angle = Angle if Angle != None else (0 if ReferTo =='absolute' else None)
		self.WhichAngle = WhichAngle

	def __str__(self):
		Msg = [ PropName + ':= ' +  str(getattr(self, PropName)) for PropName in  PositioningDirectives._PropList]
		return '\n'.join(Msg)
#	def __repr__(self):
#		print (self.__set__())
posdir_ = PositioningDirectives
#		self.X = None
#		self.Y = None


#class OPTICS_TYPE:
#	NotDef = 0
#	MirrorPlane = 1
#	EllipsoidalMirror = 2


#Name_DICT=  {OPTICS_TYPE.Dummy :'dummy',
#		OPTICS_TYPE.MirrorPlane : Optics.MirrorPlane._TypeStr ,
#		OPTICS_TYPE.EllipticalMirror : Optics.EllipticalMirror ._TypeStr}



#===========================================================================
# 	CLASS: TreeItem
#===========================================================================
class TreeItem(object):
	''' Protected attributes = Friend attributes.
	Friend class is Tree
	'''
	def __init__(self):
		self.Parent = None
		self.Children = []
		self.Name = None

	def __str__(self):
		return self.Name

	def __disp__(self):
		NameChildren= ','.join([Child.Name for Child in self.Children])
		NameParent = ('' if self.Parent == None else self.Parent.Name)
		Str = '[%s] ---- *[%s]*----[%s]' %( NameParent, self.Name,NameChildren)
		return Str

	# ===========================================
	# PROP: ParentContainer
	# ==========================================
	@property
	def ParentContainer(self):
		'''
		The Container (if exists) of this TreeItem object. A typical container can
		be a Tree object or (if the TreeItem is subclassed to an OpticalElement) a
		BeamlineElement object (which a subclass of TreeClass).

		Behavior
		----

		ParentCointainer must be updated by external functions (e.g. by Append, Insert function of
		Tree objects)
		'''
		return self._ParentContainer

	@ParentContainer.setter
	def ParentContainer(self, value):
		self._ParentContainer = value
	# ================================================
	#	PROP: UpstreamItemList
	# ================================================
	@property
	def UpstreamItemList(self):
		oeThis = self
		ItemList = []
		#improve: 10
		while oeThis.Parent != None:
			oeThis = oeThis.Parent
			ItemList.append(oeThis)
		return ItemList


	#================================================
	#	PROP: DonwstreamItemList
	#================================================
	@property
	def DonwstreamItemList(self):
		oeThis = self
		ItemList = []
		#improve: 10
		while len(oeThis.Children) > 0:
			oeThis = oeThis.Children[0]
			ItemList.append(oeThis)
		return ItemList

#===========================================================================
# 	CLASS: Tree
#===========================================================================
class Tree(object):

    #================================================
    #     __init__
    #================================================
	def __init__(self):
#		self._Items = dict()
		self._Items = OrderedDict()
		self._ActiveItem = None
		self._Name = ''
		self._FirstItem = None

    #================================================
    #     __getitem__
    #================================================
	def __getitem__(self,Key):
		'''
		Paramters
		--------------------
		Key : can be EITHER strinf (name) OR integer (position index)
		'''

		# The Key is an object
		if type(Key) == OpticalElement:
			return self._Items[Key.Name]

		# The Key is an integer
		elif type(Key) == int:
			return self._Items.items()[Key][1] # returns the object of the dictionary
		# The Key is a STRING
		elif type(Key) == str :
			return self._Items[Key]	# returns the object of the dictionary
		else:
			print('ERROR: in Tree.getItem! Type mismatch')
			return None

#    #================================================
#    #     __setitem__
#    #================================================
#	def __setitem__(self,Name):
#		try:
#			return self._Items[Name]
#		except:
#			return self._Items[Name]

    #================================================
    #     __str__
    #================================================
	def __str__(self):
		"""
		# Old code: I should improve __iter__ and __getitem__ for this class :-)
		StrList = [itm.__disp__() for itm in self]
		return '\n'.join(StrList)
		"""
		StrList = ['']
		Itm0 = self.FirstItem
		StrList.append(Itm0.__disp__())
		while True:
			if len(Itm0.Children) == 0:
				break
			else:
				Itm1 = Itm0.Children[0]
				StrList.append(Itm1.__disp__())
				Itm0 = Itm1
		return 'Name:' + self.Name + 'n'+ 10*'=' + '\n'+ '\n'.join(StrList)

	#================================================
	#	FirstItem
	#================================================
	@property
	def FirstItem(self):
		return self._FirstItem

	#================================================
	#	LastItem
	#================================================
	@property
	def LastItem(self):
		return self.ItemList[self.NItems-1]

	#================================================
	#	PROP: Name
	#================================================
	@property
	def Name(self):
		return self._Name
	@Name.setter
	def Name(self,x):
		self._Name = str(x)

	#================================================
	#	ItemList
	#================================================
	@property
	def ItemList(self):
		t0 = self.FirstItem
		if t0 != None:
			List = []
			while True:
				List.append(t0)
				if len(t0.Children) > 0:
					t0 = t0.Children[0]
				else:
					break
			return List
		else:
			return []


	#================================================
	#	NItems
	#================================================
	@property
	def NItems(self):
		return size(self.ItemList)
		'''return size(self._Items.items())''' # why did I do it that way?

    #================================================
    #     Insert
    #================================================
	def Insert(self,
			NewItem,
			ExistingName = None,
			Mode = INSERT_MODE.After,
			NewName = None):

		'''
		Paramters
		---------
		NewItem : Fundation.OpticalElement
			Object to add (Assignement will be used)
		ExistingItem : String | Fundation.OpticalElement
			Reference Item
		Mode : INSERT_MODE. type
			INSERT_MODE.After, INSERT_MODE.Before, INSERT_MODE.Fork
		NewName : string
			Shorthand for changing NewItem.Name. Maybe I'll remove it
		'''
		NewName = (NewName if not(NewName==None) else NewItem.Name )
#		if NewName == None and NewItem.Name == None):
#			print ('ERROR: No Name specified in Tree.Insert method')
#		elif NewName == None and NewItem.Name != None:
#			pass
#		elif NewName != None:
#				NewItem.Name

		# This one is the first item of the tree
		if len(self._Items) == 0:
			NewItem.Parent = None
			NewItem.Children = []
			self._FirstItem = NewItem
		else:
		# There are already other items in the tree
			if ExistingName == None:
				raise ValueError("Tree.Insert ERROR: I don't know where to place this new optical element. You gave me a name I can not find")
				return 0

			ItemA = self._Items[ExistingName]
			# INSERT AFTER (default)
			if Mode == INSERT_MODE.After:
				# Update NewItem (second, or middle)
				NewItem.Parent = ItemA
				NewItem.Children = ItemA.Children
				# update ItemA (first)
				del ItemA.Children
				ItemA.Children =  [NewItem]
				# update ItemB (last)
				for Child in NewItem.Children:
					Child.Parent = NewItem
			# INSERT BEFORE
			elif Mode == INSERT_MODE.Before:
				# NewItem will be the first one of the tree
				if ItemA.Parent == None:
					# update NewItem
					NewItem.Parent = []
					NewItem.Children = ItemA
					# update ItemA
					ItemA.Parent = NewItem
					# update Tree Prop
					self.FirstItem = NewItem
				# NewItem is a generic item
				else:
					pass
					# codice da fare per 'INSERT BEFORE
			# FORK
			elif Mode == INSERT_MODE.Fork:
				NewItem.Parent = ItemA
				ItemA.Children.append(NewItem)

		# ASSIGNMENT
#		TmpDict = {NewName : NewItem}
		self._Items[NewName] = NewItem

		self._ActiveItem= NewItem

    #================================================
    #     Insert
    #================================================
	def Append(self, NewItem,  posdirective = None, NewName = None):
		NewItem.Name = (NewName if NewName != None else NewItem.Name)

		if self._ActiveItem == None:
			ExistingItem = None
		else:
			ExistingItem = self._ActiveItem.Name
		self.Insert(NewItem,
					ExistingName = ExistingItem,
					NewName = NewName,
					Mode = INSERT_MODE.After)
    #================================================
    #     GetFromTo
    #================================================
	def GetFromTo(self, FromItem,  ToItem = None):
		'''
		Returns the item comprised between FromItem and ToItem within self.ItemList
		(included)
		'''

		# Use all the items in the beamline
		if FromItem == None and ToItem == None:
			return self.ItemList
		# Use just a selection between FromItem and ToItem
		ItmList = self.ItemList
		iStart = ItmList.index(FromItem)
		iEnd = ItmList.index(ToItem)
		iStart = iStart if iStart != None else 0
		iEnd = iEnd +1 if iEnd != None else  self.NItems

		return ItmList[iStart:iEnd]

#===========================================================================
# 	CLASS: OpticalElement
#===========================================================================
class OpticalElement(TreeItem):
	'''
	- If Name is None, then the name is automatically assigned.
	'''
	__NameCounter = {} # PRIVATE
	_LastInstance = 13


    #================================================
    #     __init__[OpticalElement]
    #================================================
	def __init__(self, CoreOpticsElement = None, Name = None, IsSource = False,
					PositioningDirectives = None,
					ComputationSettings = None,
					*kwargs):
		#self.ChainControl = ChainControlObject()
		OpticalElement._LastInstance = 130
		TreeItem.__init__(self)
		self._IsSource = IsSource
		self.PositioningDirectives = PositioningDirectives
		self._ComputationSettings = ComputationSettings if ComputationSettings != None else ComputationSettingsForOpticalElement()

		self.Results = ComputationResults()			# this data field should be discontinued
		self.PropagationData = self.Results     # this one should be encouraged

		Element = CoreOpticsElement
		# Item is a class of Optics. Object is created (not recommended)
		if inspect.isclass(Element):
			Class = Element
			Element = Class()
		else:
			pass

		if Element == None:
			print ('OpticalElement(....): a None object is passed as element. Be careful')
			self.CoreOptics = None
			self.__Type = 'None'
			self.__TypeStr = 'nn'

		else:
			self.CoreOptics = Element # contains a link to an Optics object
			self.__Type = type(self.CoreOptics)
			self.__TypeStr = self.CoreOptics._TypeStr

		self.Name = (Name if Name!= None else self.__GetNewName())
		self.RayIn = None
		self.RayOut = None

		self.__NOutput = 0  # Abstract: N of output beams.
#		self.x = 0

		# If Element has 'absolute' positioning, then its position is refreshed immediately.
		# There are 2 good reasons:
		# 1. there is no need to wait for the other beamline elements to be deployed
		# 2. another element may need the position of this element for its further 'absolute' positioning.
		# mocambo
#		if PositioningDirectives.ReferTo == 'absolute' :
#			PositioningDirectives_UpdatePosition(self,None)

		OpticalElement._LastInstance = 1301
    #================================================
    #     __str__[OpticalElement]
    #================================================
	def __str__(self):
		Str = '\n -.-.-.-.-.-.-.-.-.-.-. <begin Optical Element>\n'
		Str += ('OE: %s ' % self.Name)
		Str += self.CoreOptics.__str__()
		Str +=('-.-.-.-.-.-.-.-.-.-.-. <end Optical Element>\n')
		return Str

    #================================================
    #     __disp__[OpticalElement]
    #================================================
	def __disp__(self):
			'''
			Displays the beamline elements in the form
			[0]---[1*]---[2]
			[1]---[2*]---[3]
			'''
			NameChildren = ','.join([Child.Name for Child in self.Children])
			NameParent = ('' if self.Parent == None else self.Parent.Name)
			#	    # Old String: I displayed the XYCentre [MM]
			#		Str = '[%s] ---- *[%s]*----[%s]\t\t *XYCentre* = %0.2e, %0.2e' % (
			#		NameParent, self.Name, NameChildren, self.XYCentre[0], self.XYCentre[1])
			#

			print(self.GeneralDistanceFromParent(Reference=False))
			Str = '[%s] ---- *[%s]*----[%s]' % (NameParent, self.Name, NameChildren)
			# Additional Stuff (such as the distance from previous element, etc...)

			Str += '\t\tDeltaZ=%0.2f m, Z=%0.2f m' % (self.GeneralDistanceFromParent(Reference=False), self.DistanceFromSource)


			return Str
	#==========================================
	# FUN: GetNSamples[OpticalElement]
	#==========================================
	def GetNSamples(self, Lambda = None):
		'''
		Returns the proper number of samples to use for ThisOpticalElement in
		propagation the field as UpstreamElement(0) ----> ThisElement(1).

		If (self.ComputationSettings.UseCustomSampling == True), then the N of samples
		set by the user is used.

		If UpstreamElement is Analytic, then DownstreamElement is used to compute the samples

		The number of samples for oe1 is N1 = L0 * L1/(Lambda * z01) (L0 and L1 are the projections with respect to z01).

		L0 is the size of oe0, which is the upstream optical element to oe1.

		If oe0 is analytic, then the number of samples is computed using L1 (the size of oe1). If there are no numerical element downstream oe1, then self.DefaultSamples is used.
		'''
		# In order to compute info on oe1,
		# info on oe0 are required.
		# If oe0 is analytical, info on oe2 are used.
		Debug.Print('GetNSamples:', 0)
		Debug.Print('Current: %s' % self.Name,  1 )
		Debug.Print('Upstream Element %s' % self.Parent.Name, 1 )


		if (self.ComputationSettings.UseCustomSampling == True) or (Lambda == None) :
			return self.ComputationSettings.NSamples


		# The upstream element is numerical (easiest case)
		#--------------------------------------------------------
		if self.Parent.CoreOptics._IsAnalytic == False:
			_NSamples = GetNSamples_OpticalElement(Lambda, self.Parent, self)

		# The upstream element is analytical (a mess)
		#--------------------------------------------------------
		else:
			# Find first OE after oe1 which is not analytical.
			# If there are no Children, then CustomSampling is used
			ChildrenList = self.DonwstreamItemList
			if ChildrenList == []:
				return self.ComputationSettings.NSamples
			for oeChild in ChildrenList:
#				print(oeChild.Name + 40 *'&')
				if oeChild.CoreOptics._IsAnalytic == False:
					_NSamples = GetNSamples_OpticalElement(Lambda, self, oeChild)

					Debug.Print('Mutual sampling bw <%s>-<%s>' % (self.Name, oeChild.Name))
					break
				else: # no other elements downstream
					return self.ComputationSettings.NSamples
		return _NSamples


	#===========================================
	# FUN: ComputeSampling_2Body
	#==========================================
	@staticmethod
	def GetNSamples_2Body(Lambda: float, oe0 , oe1) -> int:
		z = np.linalg.norm(oe1.CoreOptics.XYCentre - oe0.CoreOptics.XYCentre)
		L0 = oe0.CoreOptics.L
		L1 = oe1.CoreOptics.L
		Theta0 = oe0.CoreOptics.VersorNorm.Angle
		Theta1 = oe1.CoreOptics.VersorNorm.Angle
#		Alpha0 = oe0.CoreOptics.Angle
		return rm.ComputeSamplingA(Lambda, z, L0, L1, Theta0, Theta1, oe1.ComputationSettings.OversamplingFactor)
#		return rm.ComputeSampling(Lambda, z, L0, L1, Alpha0, Alpha1, oe1.ComputationSettings.OversamplingFactor)
	#===========================================
	# PROP: IsSource
	#==========================================
	@property
	def IsSource(self):
		return self._IsSource

	#===========================================
	# PROP: PositioningDirectives
	#==========================================
	@property
	def PositioningDirectives(self):
		return self._PositioningDirectives
	@PositioningDirectives.setter
	def PositioningDirectives(self, value):
		self._PositioningDirectives = value



   #===========================================
   #     GetNewName
   #==========================================
	def __GetNewName(self):


		# the counter for this kind of optics is already >=1
		try:
			Counter = OpticalElement.__NameCounter[self.__Type]
			Counter += 1
			OpticalElement.__NameCounter[self.__Type] = Counter
		# the counter for this kind of optics has not beet initialised yet
		except:
			Counter = 1
			OpticalElement.__NameCounter.update({self.__Type : Counter})
			print ('-------------------------')
			print (self.__TypeStr)
			print ('-------------------------')
		return self.__TypeStr + '%02d' % Counter


	#================================================
	#	PROP: ComputationSettings (get,set)
	#================================================
	@property
	def ComputationSettings(self):
		return self._ComputationSettings
	@ComputationSettings.setter
	def ComputationSettings(self,value):
		self._ComputationSettings = value

	#================================================
	#	PROP: ComputationData (get,set)
	#================================================
	@property
	def ComputationData(self):
		return self.Results
	@ComputationData.setter
	def ComputationData(self,value):
		self.Results = value

	#================================================
	#	PROP: ComputationResults (get,set)
	#================================================
	@property
	def ComputationResults(self):
		'''
		#XXX TBDisc
		To be discontinued in favor of ComputationData
		'''
		return self.Results
	@ComputationResults.setter
	def ComputationResults(self,value):
		self.Results = value


	#================================================
	#	Paint (tunnel)
	#================================================
	def Paint(self, hFig = None,**kwargs):
		return self.CoreOptics.Paint(**kwargs)

	#================================================
	#	GetXY(tunnel)
	#================================================
	def GetXY(self, N):
		return self.CoreOptics.GetXY(N)

	#================================================
	#	FUN: GetRayOutNominal (tunnel)
	#================================================
	@property
	def RayOutNominal(self):
		return self.CoreOptics.RayOutNominal

	#================================================
	#	PROP: XYCentre (tunnel)
	#================================================
	@property
	def XYCentre(self):
		return self.CoreOptics.XYCentre


#	#================================================
#	#	PROP: DistanceFromParente (deferred)
#	#================================================

#	@property
#	def DistanceFromParent(self):
#		'''
#		Distance from parent optical element.
#		'''
#		if self.Parent != None:
#			return np.linalg.norm(self.XYCentre - self.Parent.XYCentre)
#		else:
#			return 0

#	#================================================
#	#	PROP: DistanceFromSource
#	#================================================
#	@property
#	def DistanceFromSource(self):
#		'''
#		Distance from the source.
#		'''
#		ItemList =  self.UpstreamItemList
#		Distances = np.array([oe.DistanceFromParent for oe in ItemList])
#		return sum(Distances) + self.DistanceFromParent


	@property
	def DistanceFromParent(self):
		'''
		Distance from parent optical element corresponds to the optical distance between the element (self)
		and the first optical element with the same orientation and UseAsReference flag True (obtained with
		>>> self.GetParent(SameOrientation=True, OnlyReference=True))

		'''

		if self.Parent != None:
			distance = np.linalg.norm(self.XYCentre - self.GetParent(SameOrientation=True, OnlyReference=True).XYCentre)
		elif self.Parent == None:
			distance = 0
		else:
			raise ValueError('Something wrong in DistanceFromParent!')

		return distance

	# # ================================================
	# #	PROP: DistanceFromSource
	# # ================================================
	# @property
	# def DistanceFromSource(self):
	# 	'''
	# 	Distance from the source.
	# 	'''
	# 	ItemList = self.UpstreamItemList
	# 	Distances = np.array([oe.DistanceFromParent for oe in ItemList])
	# 	return sum(Distances) + self.DistanceFromParent

	# ================================================
	#	PROP: DistanceFromSource
	# ================================================
	@property
	def DistanceFromSource(self):
		'''
		Distance from the source.
		'''
		ItemList = self.UpstreamItemList # First element is the closest element, last element is the source
		ItemListSameOrientation = []
		for oe in ItemList:
			if (((oe.CoreOptics.Orientation == self.CoreOptics.Orientation) or
					(oe.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC) or
					(oe.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ANY)))\
					and oe.CoreOptics.UseAsReference == True:
				ItemListSameOrientation.append(oe)

		distances = np.array([oe.DistanceFromParent for oe in ItemListSameOrientation])
		return sum(distances) + self.DistanceFromParent

	# ================================================
	#	FUNC: GetParent
	# ================================================

	def GetParent(self, SameOrientation=False, OnlyReference=False):
		'''
		Returns the first parent accounting for the following flags> SameOrientation, OnlyReference.

		Parameters
		-----

		SameOrientation : bool
			if Ture, it returns the first parent elemenents for which .CoreOptics.Orientation is
			the same as self object.

		OnlyReference : bool
			if True it returns the first parent elements for which  CoreOptics.UseAsReference = True

		'''

		#def HaveSameOrientation(oeX, oeY):
		#	return ((oeX.CoreOptics.Orientation == oeY.CoreOptics.Orientation) or
		#	 (oeX.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC) or
		#	 (oeX.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ANY))

		GetParentResult = None

		if SameOrientation and OnlyReference:
			for oe in self.UpstreamItemList:
				if HaveSameOrientation(oe, self) and oe.CoreOptics.UseAsReference:
					GetParentResult = oe
					break
		elif SameOrientation and not OnlyReference:
			for oe in self.UpstreamItemList:
				if HaveSameOrientation(oe, self):
					GetParentResult = oe
					break
		else:
			for oe in self.UpstreamItemList:
				if OnlyReference:
					if oe.CoreOptics.UseAsReference:
						GetParentResult = oe
						break
				elif not OnlyReference:
					GetParentResult = oe
					break

		# Raise a warning in case if GetParent remains None
		if GetParentResult == None:
			warnings.warn("GetParent returned None!")

		return GetParentResult

	def GetDistanceFromParent(self, SameOrientation=False, OnlyReference=False):
		'''
		High level function to calculate the distance to parent.

		Dev notes
		-----
		It uses the distance from source and requires XYCentre to be already computed.
		Best version (20201023) - AF + MM
		'''
		result = self.DistanceFromSource - self.GetParent(SameOrientation=SameOrientation, OnlyReference=OnlyReference).DistanceFromSource
		return result

	def GeneralDistanceFromParent(self, Orientation=True, Reference=True):
		'''
		Generalized DistanceFromParent. As DistanceFromParent is a property and linked to a lot of other things
		in the code, this was added later for correct __str__ behaviour.
		It corresponds to the optical distance between the element (self) and the first optical element with the
		Orientation and Reference.
		>>> self.GetParent(SameOrientation=Orientation, OnlyReference=Reference))
		'''

		if self.Parent != None:
			distance = np.linalg.norm(self.XYCentre - self.GetParent(SameOrientation=Orientation, OnlyReference=Reference).XYCentre)
		elif self.Parent == None:
			distance = 0
		else:
			raise ValueError('Something wrong in GeneralDistanceFromParent!')

		return distance


#===========================================================================
# 	CLASS: BeamlineElements
#===========================================================================
class BeamlineElements(Tree):
	#================================================
	#     __init__
	#================================================
	#
#	def __init__(self):
#		Tree.__init__(self)

	class _ClassComputationSettings:
		def __init__(self):
			self.NPools = 1
			self.NRoughnessPerOpticalElement = 1
			self.NFigureErrorsPerOpticalElement = 1
			self.UseFigureError = False
			self.UseRoughness = False
			self.iRoughness = 0
			self.iFigureError = 0
			self.OrientationToCompute = [Optics.OPTICS_ORIENTATION.ANY]
			self._TotalComputationTimeMinutes = 0


		@property
		def iComputation(self):
			return self.NRoughnessPerOpticalElement * self.iFigureError + self.iRoughness
		@property
		def NComputations(self):
			return self.NRoughnessPerOpticalElement * self.NFigureErrorsPerOpticalElement

	#================================================
	#  FUN: __init__
	#================================================
	def __init__(self):
		Tree.__init__(self)
		self.ComputationSettings = BeamlineElements._ClassComputationSettings()

	#================================================
	#  PROP: Source
	#================================================
	@property
	def Source(self):
		'''
		Return the 'Source' element in the sequence of element.
		What is the Source? The element such that .IsSource=True.
		A gaussian Source is a Source
		'''

		for Itm in self.ItemList:
			if Itm.IsSource == True:
				return Itm
			else:
				return None
		return None

#	#================================================
#	#  FUN: RefreshPositions
#	#================================================
#	def RefreshPositions(self):
#		'''
#		Uses the data stored in PositioningDirectives of each OpticalElement in
#		order to set the physical positions of each optical element.
#		In so doing, the optical rays are computed as well.
#
#		If some element is OpticsNumericalDependent, then the Positioning operation
#		is not done. The .Refresh method is invoked instead (at the end of all
#		the positioning operation list)
#		'''
#
#		# places an item respect with its parent (if there is any)
#		# improve 101
#		oeRecoveryList = []
#		oeList = self.ItemList
#		k = 0
#		kTot = len(oeList)
#		for oeY in oeList:
#			k +=1
#			Debug.print('%d/%d -  Positioning "%s"' % (k,kTot, oeY.Name),3)
#
#			if oeY.PositioningDirectives != None:
#
#				# Who is the reference element?
#				#----------------------------------------------------------------
#				if oeY.PositioningDirectives.ReferTo == 'upstream':
#					oeX = oeY.Parent
#				elif oeY.PositioningDirectives.ReferTo == 'locked':
#					oeX = None
#				elif oeY.PositioningDirectives.ReferTo == 'source':
#					oeX = self.Source
#				elif oeY.PositioningDirectives.ReferTo == 'absolute':
#					oeX = None
#				else:
#					oeX = oeY.Parent										# even if oeY.Parent = None, that's ok. The function will handle it.
#				#----------------------------------------------------------------
#
#				PositioningDirectives_UpdatePosition(oeY, oeX)
#			else:
#				oeRecoveryList.append(oeY)
#
#		# AD HOC for OpticsNuemricalDependent oe
#		for oe in oeRecoveryList:
#			oe.CoreOptics.Refresh()

	# ================================================
	#  FUN: RefreshPositions
	# ================================================
	def RefreshPositions(self):
		'''
		Uses the data stored in PositioningDirectives of each OpticalElement in
		order to set the physical positions of each optical element.
		In so doing, the optical rays are computed as well.

		If some element is OpticsNumericalDependent, then the Positioning operation
		is not done. The .Refresh method is invoked instead (at the end of all
		the positioning operation list)
		'''

		# places an item respect with its parent (if there is any)
		# improve 101

		oeRecoveryList = []
		oeList = self.ItemList
		k = 0
		kTot = len(oeList)
		for oeY in oeList:
			k += 1
			Debug.print('%d/%d -  Positioning "%s"' % (k, kTot, oeY.Name), 3)

			if oeY.PositioningDirectives != None:
				self.ApplyPositioningDirectives(oeY)
			else:
				oeRecoveryList.append(oeY)

		# AD HOC for OpticsNuemricalDependent oe
		for oe in oeRecoveryList:
			oe.CoreOptics.Refresh()

	# ================================================
	#     PositioningDirectives_UpdatePosition
	# ================================================
	@staticmethod
	def ApplyPositioningDirectives(oeY: OpticalElement):
		'''

			Parameters
			------------------
			oeY : OpticalElement
				The optical element to place

			Behavior
			------------------
			- If PositioningDirectives has ReferTo='locked' then the positioning of the present element is not computed.
				This shall be used for elements whose position has already been computed in another BeamlineElements object,
				and you don't want to recompute all the sequence.
				I introduced this when I do the focus sweep, keeping an optical element fixed ('locked') and moving the screen
				only.
			- Upstream reference is workin as one expects to
			- Downstream focus will find the firs element (with the same orientation) that has f2 as attribute, then
			will use f2 as positioning distance
			- UseAsReference=False means that the Element is not considerend for positioning other elements.

			Developer notes
			------------------
			Bases on: XYCentre, SetXYAngle_Centre,  GetParent(...), DistanceFromParent

			Curiosity: why is this function here? And it is not a member of Optical element?

		'''
		Pd = oeY.PositioningDirectives

		if oeY.IsSource == False:
			oeX = oeY.GetParent(SameOrientation=False, OnlyReference=True) # Get XY coordinates from the oeX
			oeXSameOrientation = oeY.GetParent(SameOrientation=True, OnlyReference=True)

		# Somehow posdir_ was defined before in class PositioningDirectives as posdir_ = PositioningDirectives
		# -------------------------------------------
		if Pd.ReferTo == posdir_.ReferTo.DoNotMove:
			pass

		# =============================================================================================
		# ABSOLUTE POSITIONING
		# =============================================================================================
		elif Pd.ReferTo == posdir_.ReferTo.AbsoluteReference:

			# set position
			# Debug.print(Pd.XYCentre, 5)

			oeY.CoreOptics.SetXYAngle_Centre(Pd.XYCentre, Pd.Angle, WhichAngle=Pd.WhichAngle)

		# =============================================================================================
		# LOCKED POSITIONING
		# =============================================================================================
		elif Pd.ReferTo == 'locked':
			'''
			XYCentre and Angle of the OpticalElement are not changed at all.
			Typically used if the OE has been created via deepcopy . Example: FocusSweep function.
			'''
			pass
		# =============================================================================================
		# REFERENCE = PREVIOUS or SOURCE or DOWNSTREAM
		# =============================================================================================
		elif ((Pd.ReferTo == posdir_.ReferTo.UpstreamElement) or (Pd.ReferTo == 'source')):

			RayIn = oeXSameOrientation.CoreOptics.RayOutNominal  # The incident ray
			LastXY = oeXSameOrientation.CoreOptics.XYCentre # XY position of the same orientation

			# =============================================================================================
			#  Set the XYCentre1   at a certain Distance from XYCentre2
			# =============================================================================================
			if (Pd.What == 'centre' or Pd.What == 'upstream focus') and Pd.Where == 'centre':

				# All the conditions select the last arm as distance, as this is the one used in SetXYAngle_Centre
				if Pd.ReferTo == 'source' and Pd.What == 'centre':
					realDistance = Pd.Distance - oeXSameOrientation.DistanceFromSource
				elif Pd.ReferTo == 'source' and Pd.What == 'upstream focus':
					realDistance = oeY.CoreOptics.f1 - oeXSameOrientation.DistanceFromSource
				else:
					if Pd.ReferTo != 'source' and Pd.What == 'upstream focus':
						realDistance = oeY.CoreOptics.f1
					else:
						realDistance = Pd.Distance

					# If a normal optical element is given, first calculate the distance to the oeXSameOrientation.
					# Then the newXYCentre can be calculated from the distance.

					if oeX != oeXSameOrientation:
						realDistance = oeX.DistanceFromSource - oeXSameOrientation.DistanceFromSource + realDistance

				newXYCentre = LastXY + realDistance * tl.Normalize(RayIn.v)
				oeY.CoreOptics.SetXYAngle_Centre(newXYCentre, RayIn.Angle, WhichAngle=TypeOfAngle.InputNominal)

			# =============================================================================================
			#  Set the XYCentre1   at the Dowstream focus. Used for detectors
			# =============================================================================================
			elif Pd.What == 'centre' and Pd.Where == 'downstream focus':
				# When doing FocusSweep, use 'locked' for the virtual source and go into this case...
				'''
				Behavior:
				if oeXSameOrientation has a focus, then uses it as reference. If not, it looks for the first suitable one.
				'''

				try:
					#FIX 4 Aljosa
					if hasattr(oeXSameOrientation.CoreOptics, 'f2'):
						realDistance = oeXSameOrientation.CoreOptics.f2

					else: # Find the first suitable one
						oeXSameOrientationCurrent = oeXSameOrientation
						realDistance = oeXSameOrientationCurrent.DistanceFromParent
						oeXSameOrientationCurrent = oeXSameOrientationCurrent.GetParent(SameOrientation=True, OnlyReference=True)

						while not hasattr(oeXSameOrientationCurrent.CoreOptics, 'f2'):
							realDistance = oeXSameOrientationCurrent.DistanceFromParent + realDistance
							oeXSameOrientationCurrent = oeXSameOrientationCurrent.GetParent(SameOrientation=True, OnlyReference=True)

						realDistance = oeXSameOrientationCurrent.CoreOptics.f2 - realDistance

						#realDistance: distance from the last element with the same orientation
					newXYCentre = LastXY + (Pd.Distance + realDistance) * tl.Normalize(RayIn.v)
					oeY.CoreOptics.SetXYAngle_Centre(newXYCentre, RayIn.Angle, WhichAngle=TypeOfAngle.InputNominal)
				except:
					raise ValueError("No focusing O.E. (e.g. elliptic mirror) found!")
			else:
				raise ValueError('Wrong or un-implemented PositioningDirectives!')

		else:
			# NOT IMPLEMENTED :-)
			print('PositioningDirectives.PARSE =: \t%s\n\t Code not implemented yet :-)' % Pd.ReferTo)
			pass
		Debug.print('<\end Parse>', 4)

	#================================================
	#  FUN: GetSamplingList
	#================================================
	def GetSamplingList(self, Verbose = True, ForceAutoSampling = False):
		"""
		Helper function (for debug, not used by the computation engine)
		Returns a list containing the sampling used for each optical element

		"""
		# temporarily set the UseCustomSampling to True, if required
		Memento = []
		if ForceAutoSampling:
			for Item in self.ItemList:
				Memento.append(Item.ComputationSettings.UseCustomSampling)
				Item.ComputationSettings.UseCustomSampling = False

		self.ComputeFields(oeStart = None, oeEnd = None, Dummy = True, Verbose = False)
		NList = []
		NameList = []
		for i, Oe in enumerate(self.ItemList):
			NList.append( Oe.ComputationResults.NSamples)
			NameList.append(Oe.ComputationResults.Name)
			if Verbose:
				print("%s\t%s" % ( NameList[i], str(NList[i])))

		# restore the UseCustomSampling
		if ForceAutoSampling:
			for i,Item in enumerate(self.ItemList):
				Item.ComputationSettings.UseCustomSampling = Memento[i]
		return NList, NameList

	# ================================================
	#  FUN: ComputeFields
	# ================================================
	def ComputeFields(self, oeStart=None, oeEnd=None, Dummy=False, Verbose=True):
		"""
		Select the orientations and pass them individually to ComputeFieldsMediator, which is nothing else but the old
		ComputeFields.

		Parameters
		-----
		"""
		Tic = time.time()
		for Orientation in self.ComputationSettings.OrientationToCompute:
			self.ComputeFieldsMediator(oeStart, oeEnd, Dummy, Verbose, Orientation)
		Toc = time.time()

		self._TotalComputationTimeMinutes = (Toc-Tic)/60
	# ================================================
	#  FUN: ComputeFieldsMediator
	# ================================================
	def ComputeFieldsMediator(self, oeStart=None, oeEnd=None, Dummy=False, Verbose=True,
							  Orientation=Optics.OPTICS_ORIENTATION.ANY) -> OpticalElement.ComputationData:
		"""
		Perform a single simulation along the beamline.
		This is the first function of this kind that we have created, and it does not do averages if
		many FigureErrors or Roughness profiles are used. If you want to do that,
		use ComputeFieldsAndAverage

		If StartElement = None, then the computation of the e.m. fields starts
		from the first element of the sequence.

		Parameters
		-----
		Dummy : True/False
			if False, the computation is not really performed.
			Useful to get the list of the sampling


		Return
		-----
		oeList Used.

		"""

		Debug.On = Verbose

		Action = 'not defined'

		# Buffer structure which is used to propagate the signal along the elements
		# -------------------------
		class PropInfo:
			oeLast = None
			TotalPath = 0  # path from the last active element used.
			N = 0

		oeList, oeStart, oeEnd = self._PickOeList(oeStart, oeEnd, Orientation)

		if len(oeList) < 2:
			return None

		PropInfo.oeLast = self.FirstItem if oeStart.Parent is None else oeStart.GetParent(SameOrientation=True)

		#		oeStart = self.FirstItem if oeStart == None else oeStart
		#		oeEnd = self.LastItem if oeEnd == None else oeEnd
		#		#Picking just a subportion of oeList, if required by oeStart, oeEnd
		#		oeList = self.GetFromTo(oeStart, oeEnd)
		#		oeStart = oeList[0]

		# Select the wavelength (CRITICAL)
		# CRITICAL: Where shall I get Lambda from?
		# If oeStart is a source, then from its properties.
		# Else, from the previous computed field.
		if (oeStart == self.FirstItem) and (oeStart.IsSource == True):
			try:
				Lambda = self.FirstItem.CoreOptics.Lambda
			except:
				Lambda = oeStart.ComputationResults.Lambda
		else:
			Lambda = oeStart.ComputationResults.Lambda

		k = 0
		Ind = 1
		NoeList = len(oeList)
		for ioeThis, oeThis in enumerate(oeList):
#			Debug.Print(50 * '=')
			Debug.Print('Compute Fields %d/%d' %( ioeThis	, NoeList), NIndent = 0, Header = True)
#			Debug.Print(50 * '=')

			Debug.Print('\tProcessing:\t'  + oeThis.Name)
			# ----------------------------------------------
			# case: the present element is the Source
			# ----------------------------------------------
			if oeThis.IsSource == True:
				# if oeThis.CoreOptics._Behaviour == 'source' : # This was the first way to do it
				Action = 'no Action'
				Debug.print('\tAction:' + Action)
				pass
			# ----------------------------------------------
			# case: the present element must be Ignored
			# ----------------------------------------------
			elif (oeThis.ComputationSettings.Ignore == True):
				PropInfo.TotalPath += oeThis.GetDistanceFromParent(SameOrientation=True, OnlyReference=False)
				PropInfo.N += 1

			# ----------------------------------------------
			# case:  Compute the field (on this element)
			# ----------------------------------------------
			else:

				# ----------------------------------------------
				# oeLast is Analitical
				# ----------------------------------------------
				# I require to transform oeThis --> Virtual(oeThis)
				if PropInfo.oeLast.CoreOptics._IsAnalytic == True:
					Action = 'Evaluating analytical function (of previous OE on THIS one)'
					Debug.print('\tAction: ' + Action, Ind)

					# Transform oeThis --> oeV (virtual optical element)
					oeV = self._MakeVirtual(oeThis, PropInfo.oeLast,
											PropInfo.TotalPath + oeThis.GetDistanceFromParent(SameOrientation=True, OnlyReference=False)) if PropInfo.N > 0 else oeThis
					NSamples = oeV.GetNSamples(Lambda)

					xV, yV = oeV.GetXY(NSamples)
					# update registers

					# ----------------------------------------------
					# Dummy? (Analytic Branch)
					# ----------------------------------------------
					if Dummy == True:
						oeThis.Results.Field = 0
						xThis = None
						yThis = None
					else:
#						Debug.print('Computing field (Analytic)', Ind , True)
#						Debug.print('source object = %s' % PropInfo.oeLast.Name, Ind + 1)
#						Debug.print('target object = %s' % oeThis.Name, Ind + 1)
#						Debug.pv('NSamples', Ind + 1)

						# --------------------------------------------
						# DATA ==>  Storage
						# --------------------------------------------
						oeThis.Results.Field = PropInfo.oeLast.CoreOptics.EvalField(
							xV,
							yV,
							Lambda=Lambda)
						# -----------------------------------------------------

						xThis, yThis = oeThis.GetXY(NSamples)
#						Debug.Print('Detailed info', NInd = Ind + 1)
#						Debug.Print(20 * '.', NInd = Ind+1)
#						Debug.print('oeLast.Name = %s' % PropInfo.oeLast.Name, Ind + 1)
#						Debug.print('oeThis.Name = %s' % oeThis.Name, Ind + 1)
#						Debug.print('len(oeThis.ComputedField) = %d' % len(oeThis.Results.Field), Ind + 1)
#						Debug.print('xLast = -- not defined', Ind + 1)
#						Debug.print('yLast = -- not defined', Ind + 1)
#						Debug.print('len xThis = %d' % len(xThis), Ind + 1)
#						Debug.print('len yThis = %d' % len(yThis), Ind + 1)

					PropInfo.N = 0
					PropInfo.TotalPath = 0
					PropInfo.oeLast = oeThis
				# ----------------------------------------------
				# oeLast is Numerical
				# ----------------------------------------------
				else:
					Action = 'Evaluating numerical Huygens Fresnel (on oeThis): ' + oeThis.Name
					Debug.print('Action: ' + Action, Ind)

					# oeThis --> xThis, yThis
					# oeLast --> xLast, yLast
					#			 ELast
					#						  |=> NSamples
					#										|=> Propagate =>

					# TODO: trovare il campionamento N.
					NSamples = oeThis.GetNSamples(Lambda)

					# oeLast is a numerical source and we want to preserve the same sampling
					# If 'Last field' is different from 0
					if tl.IsArray(PropInfo.oeLast.Results.Field):
						NSamples = len(PropInfo.oeLast.Results.Field)

					xThis, yThis = oeThis.CoreOptics.GetXY(NSamples)
					# ----------------------------------------------
					# Dummy? (Huygens branch)
					# ----------------------------------------------
					if Dummy == True:
						oeThis.Results.Field = 0
						xThis = None
						yThis = None
						Debug.pr('NSamples', Ind + 1)
					else:
#						Debug.print('Computing field (Numeric)', Ind)
#						Debug.print('source object = %s' % PropInfo.oeLast.Name, Ind )
#						Debug.print('target object = %s' % oeThis.Name, Ind )
#						Debug.pr('NSamples', Ind + 1)

						# definizione di promemoria
						# EvalField(self, x1, y1, Lambda, E0, NPools = 3,  Options = ['HF']):

						oeThis.Results.Field = PropInfo.oeLast.CoreOptics.EvalField(
							xThis,
							yThis,
							Lambda=Lambda,
							E0=PropInfo.oeLast.Results.Field,
							NPools=1)

						xLast, yLast = PropInfo.oeLast.GetXY(NSamples)
#						Debug.print('oeLast.Name = %s' % PropInfo.oeLast.Name, Ind + 1)
#						Debug.print('oeThis.Name = %s' % oeThis.Name, Ind + 1)
#						Debug.print('len(oeThis.ComputedField) = %d' % len(oeThis.Results.Field), Ind + 1)
#						Debug.print('xLast = -- not defined', Ind + 1)
#						Debug.print('yLast = -- not defined', Ind + 1)
#						Debug.print('len xThis = %d' % len(xThis), Ind + 1)
#						Debug.print('len yThis = %d' % len(yThis), Ind + 1)

					Debug.print('Computing field (Numeric)', Ind)
					Debug.print('source object = %s' % PropInfo.oeLast.Name, Ind )
					Debug.print('target object = %s' % oeThis.Name, Ind )
					Debug.Print('NSamples =%d' % NSamples, Ind)

					Debug.Print('More info', NIndent = Ind )
					Debug.Print(20 * '.', NIndent= Ind)
					Debug.print('oeLast.Name = %s' % PropInfo.oeLast.Name, Ind )
					Debug.print('oeThis.Name = %s' % oeThis.Name, Ind )
					Debug.print('len(oeThis.ComputedField) = %d' % len(oeThis.Results.Field), Ind )
#					Debug.print('xLast = -- not defined', Ind + 1)
#					Debug.print('yLast = -- not defined', Ind + 1)
					Debug.print('len xThis = %d' % len(xThis), Ind )
					Debug.print('len yThis = %d' % len(yThis), Ind )
				# ----------------------------------------------
				# DATA => Storage
				# ----------------------------------------------
				oeThis.Results.NSamples = NSamples
				oeThis.Results.X = xThis
				oeThis.Results.Y = yThis
				oeThis.Results.S = rm.xy_to_s(xThis, yThis)
				oeThis.Results.Action = Action
				oeThis.Results.Lambda = Lambda
				oeThis.Results.Name = oeThis.Name
				# ----------------------------------------------
				# Computing field => PropInfo
				# ----------------------------------------------
				PropInfo.oeLast = oeThis
				PropInfo.TotalPath = 0
				PropInfo.N = 0

		return oeList

	#================================================
	#  FUN: ComputeFields
	#================================================
	def ComputeFieldsAdvanced(self, oeStart = None, oeEnd = None, Dummy = False, Verbose = True):
		'''
		This function propagates the fields and performs the averages.

		'''
		NRoughness = self.ComputationSettings.NRoughnessPerOpticalElement
		NFigureErrors = self.ComputationSettings.NFigureErrorsPerOpticalElement
		NComputations = self.ComputationSettings.NComputations
#		for self.ComputationSettings.iRoughness

		# Loop on figure errors

		pass

#	#================================================
#	#  FUN: ComputeFields
#	#================================================
#	def ComputeFields(self, oeStart = None, oeEnd = None, Dummy = False, Verbose = True):
#		'''
#		Perform a single simulation along the beamline.
#		This is the first function that we have created, and does not do averages if
#		many FigureErrors or Roughness profiles are used.
#		The improved function is ComputeFieldsAndAverage
#
#		If StartElement = None, then the computaiton of the e.m. fields starts
#		from the first element of the sequence.
#		'''
#
#		Debug.On = Verbose
#
#
#		Action = 'not defined'
#
#		# Buffer structure which is used to propagate the signal along the elements
#		#-------------------------
#		class PropInfo:
#			oeLast = None
#			TotalPath = 0			#path from the last active element used.
#			N = 0
#
#		PropInfo.oeLast = self.FirstItem
#
#		oeStart = self.FirstItem if oeStart == None else oeStart
#		oeEnd = self.LastItem if oeEnd == None else oeEnd
#
#
#		#Picking just a subportion of oeList, if required by oeStart, oeEnd
#		oeList = self.GetFromTo(oeStart, oeEnd)
#		oeStart = oeList[0]
#		#Select the wavelenght (CRITICAL)
#		# CRITICAL: Where shall I get Lambda from?
#		# If oeStart is a source, then from its properties.
#		# Else, from the previous computed field.
#		if (oeStart == self.FirstItem) and (oeStart.IsSource==True):
#			try:
#				Lambda = self.FirstItem.CoreOptics.Lambda
#			except:
#				Lambda = oeStart.ComputationResults.Lambda
#		else:
#			Lambda = oeStart.ComputationResults.Lambda
#
#
#
#		k = 0
#		Ind = 1
#		for oeThis in oeList:
#			Debug.Print('\n\nCompute Fields>>-----------------\n\t Processing: '  + '\t' + oeThis.Name)
#			#----------------------------------------------
#			# case: the present element is the Source
#			#----------------------------------------------
#			if oeThis.IsSource == True :
#			#if oeThis.CoreOptics._Behaviour == 'source' : # This was the first way to do it
#				Action = 'no Action'
#				Debug.print('\t Action:' + Action)
#				pass
#			#----------------------------------------------
#			# case: the present element must be Ignored
#			#----------------------------------------------
#			elif (oeThis.ComputationSettings.Ignore == True):
#				PropInfo.TotalPath += oeThis.DistanceFromParent
#				PropInfo.N += 1
#
#			#----------------------------------------------
#			# case: we have to Compute the field (on this element)
#			#----------------------------------------------
#			else:
#
#				#----------------------------------------------
#				# oeLast is Analitical
#				#----------------------------------------------
#				# I require to transform oeThis --> Virtual(oeThis)
#				if PropInfo.oeLast.CoreOptics._IsAnalytic == True:
#					Action = 'Evaluating analytical function (of previous OE on THIS one)'
#					Debug.print('Action: ' + Action,Ind)
#
#					# Transform oeThis --> oeV (virtual optical element)
#					oeV = self._MakeVirtual(oeThis, PropInfo.oeLast, PropInfo.TotalPath + oeThis.DistanceFromParent) if PropInfo.N > 0 else oeThis
#					NSamples = oeV.GetNSamples(Lambda)
#
#					xV, yV = oeV.GetXY(NSamples)
#					# update registers
#					if Dummy == True:
#						oeThis.Results.Field  = 0
#					else:
#						Debug.print('Computing field (Analytic)', Ind+1, True)
#						Debug.print('source object = %s' % PropInfo.oeLast.Name, Ind+1)
#						Debug.print('target object = %s' % oeThis.Name, Ind+1)
#						Debug.pr('NSamples', Ind+1)
#
#						#--------------------------------------------
#						# DATA ==>  Storage
#						#--------------------------------------------
#						oeThis.Results.Field = PropInfo.oeLast.CoreOptics.EvalField(
#												xV,
#												yV,
#												Lambda = Lambda)
#						#-----------------------------------------------------
#
#						xThis, yThis = oeThis.GetXY(NSamples)
#						Debug.print('oeLast.Name = %s' % PropInfo.oeLast.Name, Ind+1)
#						Debug.print('oeThis.Name = %s' % oeThis.Name, Ind+1)
#						Debug.print('len(oeThis.ComputedField) = %d' % len(oeThis.Results.Field), Ind+1)
#						Debug.print('xLast = -- not defined', Ind+1)
#						Debug.print('yLast = -- not defined', Ind+1)
#						Debug.print('len xThis = %d'  % len(xThis), Ind+1)
#						Debug.print('len yThis = %d'  % len(yThis), Ind+1)
#
#					PropInfo.N = 0
#					PropInfo.TotalPath = 0
#					PropInfo.oeLast = oeThis
#				#----------------------------------------------
#				# oeLast is Numerical
#				#----------------------------------------------
#				else:
#					Action = 'Evaluating numerical Huygens Fresnel (on oeThis)'
#					Debug.print('Action: ' + Action, Ind)
#
#					# oeThis --> xThis, yThis
#					# oeLast --> xLast, yLast
#					#			 ELast
#					#						  |=> NSamples
#					#										|=> Propagate =>
#
#					# TODO: trovare il campionamento N.
#					NSamples = oeThis.GetNSamples(Lambda)
#
#					# oeLast is a numerical source and we want to preserve the same sampling
#					if len(PropInfo.oeLast.Results.Field) > 0:
#						NSamples = len(PropInfo.oeLast.Results.Field)
#
#					xThis, yThis = oeThis.CoreOptics.GetXY(NSamples)
#					if Dummy == True:
#						oeThis.Results.Field= 0
#					else:
#						Debug.print('Computing field (Numeric)', Ind+1)
#						Debug.print('source object = %s' % PropInfo.oeLast.Name, Ind+1)
#						Debug.print('target object = %s' % oeThis.Name, Ind+1)
#						Debug.pr('NSamples', Ind+1)
#
#						# definizione di promemoria
#						# EvalField(self, x1, y1, Lambda, E0, NPools = 3,  Options = ['HF']):
#
#
#						oeThis.Results.Field = PropInfo.oeLast.CoreOptics.EvalField(
#												xThis,
#												yThis,
#												Lambda = Lambda,
#												E0 = PropInfo.oeLast.Results.Field ,
#												NPools = self.ComputationSettings.NPools )
#
#
#
#						xLast, yLast = PropInfo.oeLast.GetXY(NSamples)
#						Debug.print('oeLast.Name = %s' % PropInfo.oeLast.Name, Ind+1)
#						Debug.print('oeThis.Name = %s' % oeThis.Name, Ind+1)
#						Debug.print('len(oeThis.ComputedField) = %d' % len(oeThis.Results.Field), Ind+1)
#						Debug.print('xLast = -- not defined', Ind+1)
#						Debug.print('yLast = -- not defined', Ind+1)
#						Debug.print('len xThis = %d'  % len(xThis), Ind+1)
#						Debug.print('len yThis = %d'  % len(yThis), Ind+1)
#
#				#----------------------------------------------
#				# DATA => Storage
#				#----------------------------------------------
#				oeThis.Results.NSamples = NSamples
#				oeThis.Results.X= xThis
#				oeThis.Results.Y = yThis
#				oeThis.Results.S = rm.xy_to_s(xThis, yThis)
#				oeThis.Results.Action = Action
#				oeThis.Results.Lambda = Lambda
#				#----------------------------------------------
#				# Computing field => PropInfo
#				#----------------------------------------------
#				PropInfo.oeLast = oeThis
#				PropInfo.TotalPath = 0
#				PropInfo.N = 0
#			# end if (ignore, source, etc.) -----------------
#		# end for


	#================================================
	#  FUN: _MakeVirtual
	#================================================
	def _MakeVirtual(self, oeY: OpticalElement, oeX: OpticalElement, Distance: float ) -> OpticalElement:
		'''
		Create a virtual element from oeY with respect to oeX

		Similar to STANDALONE PositioningDirectives_UpdatePosition
		except that the positioning operation should performed using:
		What = 'centre', Where = 'centre' and Distance.

		A copy of oeY is created.
		'''
		oeV = copy.deepcopy(oeY)
		oeV._Parent = oeX # Force rethe -assignment of Parent element.
		Pd = PositioningDirectives(ReferTo = 'upstream',
							 PlaceWhat = 'centre',
							 PlaceWhere = 'centre',
							 Distance = Distance, # external
							 GrazingAngle = oeY.CoreOptics.AngleInputNominal)
		oeV.PositioningDirectives = Pd
		PositioningDirectives_UpdatePosition(oeV, oeX)
		return oeV

	# ================================================
	#  FUN: _PickOeList
	# ================================================
	def _PickOeList(self, oeStart=None, oeEnd=None, Orientation=Optics.OPTICS_ORIENTATION.ANY):
		"""
		Return a list of OE contained between oeStart and oeEnd of given orientation.
		If oeStart = None, it starts from the first element.
		If oeEnd = None, it finishes up to the last element.
		"""

		oeStart = self.FirstItem if oeStart == None else oeStart
		oeEnd = self.LastItem if oeEnd == None else oeEnd
		# Picking just a subportion of oeList, if required by oeStart, oeEnd
		oeList = self.GetFromTo(oeStart, oeEnd)
		oeListOriented = []
		for _ in oeList:
			# Any Orientation?
			if (Orientation == Optics.OPTICS_ORIENTATION.ANY or
				Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC):
				oeListOriented.append(_)

			#Have the same orientation?
			elif (_.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ANY or
				_.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC or
					_.CoreOptics.Orientation == Orientation):
				oeListOriented.append(_)

		if len(oeListOriented) == 0:
			oeStart = None
			oeEnd = None
		else:
			oeStart = oeListOriented[0]
			oeEnd = oeListOriented[-1]

		return oeListOriented, oeStart, oeEnd

	# ================================================
	#  FUN: GetOpticalPath
	# ================================================
	def GetOpticalPath(self, oeStart: OpticalElement, oeEnd: OpticalElement):
		"""
		Computes the path length between oeStart and oeEnd
		"""
		return abs(oeStart.DistanceFromSource - oeEnd.DistanceFromSource)

	#================================================
	#  FUN: Paint
	#================================================
	def Paint(self,hFig = 1, Length = 1 , ArrowWidth = 0.2):
		# improve 101
		Elements = self.ItemList
		for Element in Elements:
			Element.CoreOptics.Paint(hFig, Length = Length , ArrowWidth = ArrowWidth)
            
		plt.grid('on')

	#================================================
	#  FUN: PaintMiniatures
	#================================================
	def PaintMiniatures(self, Length = 1 , ArrowWidth = 0.2):
		# improve 101
		Elements = self.ItemList
		k = 1
		for i, Element in enumerate(Elements):
			hFig = Element.CoreOptics.Paint(None, Length = None , ArrowWidth = None, 			Complete =  False)
			plt.figure(hFig)
			plt.title('%d) - %s' %(i,Element.Name))
			print(Element.Name + ' onto figure ' + str(hFig))

#===========================================================================
# 	CLASS: MakePositioningDirectives
#===========================================================================
class MakePositioningDirectives:
	@staticmethod
	def Empty():
		return  PositioningDirectives()
	@staticmethod
	def Absolute(XYCentre, Angle ):
		PD = PositioningDirectives()
		PD.ReferTo ='absolute'
		PD.IsAbsolute = True
		PD.UseFollowing = False
		PD.UsePrevious = False
		PD.XYCentre = XYCentre
		PD.Angle = Angle
		return PD

	@staticmethod
	def ReferToPrevious(Distance, GrazingAngle = 0, PlaceWhat = 'centre', PlaceWhere = 'centre' ):
		PD = PositioningDirectives()
		PD.PlaceWhat = PlaceWhat
		PD.PlaceWhere = PlaceWhere
		PD.Distance = Distance
		PD.GrazingAngle = GrazingAngle
		return PD

	@staticmethod
	def AtFocus(GrazingAngle = None):
		PD= PositioningDirectives()
		PD.UseFollowing = False
		PD.UsePrevious = True
		PD.AtFocus = True
		PD.GrazingAngle = GrazingAngle



#class MakePositioningDirectives:
#	@staticmethod
#	def Empty():
#		return  PositioningDirectives()
#	@staticmethod
#	def Absolute(X,Y, GrazingAngle = None):
#		PD = PositioningDirectives()
#		PD.IsAbsolute = True
#		PD.UseFollowing = False
#		PD.UsePrevious = False
#		PD.X = X
#		PD.Y = Y
#		PD.GrazingAngle = GrazingAngle
#		return PD
#	@staticmethod
#	def ReferToPrevious(Distance, GrazingAngle = None ):
#		PD = PositioningDirectives()
#		PD.UseFollowing = False
#		PD.UsePrevious = True
#		PD.Distance = Distance
#		PD.GrazingAngle = GrazingAngle
#		return PD
#	@staticmethod
#	def AtFocus(GrazingAngle = None):
#		PD= PositioningDirectives()
#		PD.UseFollowing = False
#		PD.UsePrevious = True
#		PD.AtFocus = True
#		PD.GrazingAngle = GrazingAngle

	'''
	PlaceCentreAfterFocus
	PlaceCentreAfterCentre
	PlaceFocusAfterCentre
	PlaceFocusAfterFocus
	'''
# ================================================
#	HaveSameOrientation
# ================================================
def HaveSameOrientation(oeX, oeY):
	return ((oeX.CoreOptics.Orientation == oeY.CoreOptics.Orientation) or
	 (oeX.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC) or
	 (oeX.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ANY))
#================================================
#     PositioningDirectives_UpdatePosition
#================================================
def PositioningDirectives_UpdatePosition(oeY: OpticalElement, oeX: OpticalElement):
	'''
		MILESTONE function: finds the location of optical element oeY
		starting from optical	element oeX according to the info contained
		in oeY.PositioninDirectives

		It is a two-argument function.

		In the future it should be put in
		OpticalElement.SetPosition
		and maybe implemented in an external class ('Visitor pattern')

		Paramters
		------------------
		oeY : OpticalElement
			The optical element to place
		oeX : OpticalElement
			The optical element to use as reference. Can be None if
			PositioningDirectives.IsAbsolute = True


		Notice
		------------------
		- If PositioningDirectives has ReferTo='absolute', oeX is not used
		- If PositioningDirectives has ReferTo='locked' then the positioning of the present element is not computed.
			This shall be used for elements whose position has already been computed in another BeamlineElements object,
			and you don't want to recompute all the sequence.
			I introduced this when I do the focus sweep, keeping an optical element fixed ('locked') and moving the screen
			only.
		- If PositioningDirectiveshas flag=UseFollowing, oeX is supposed to be the subsequent	optical element respect with oeY.
		- According to the type of oeY and oeX, different strategies for computing the positioning may be used.

		Developer note
		------------------
		This function, in order to work, expects that some (or all) of the following member
		functions are defined in the object OpticalElement.CoreOptics
		(This object is typically an instance of Optics.MirrorPlane, Optics.EllipticalMirror,
		Optics.SourceGaussian, etc...)

		(ni = Not Implemented yet)

		- XYCentre

		- SetXYAngle_Centre
		- SetXYAngle_UpstreamFocus
		- SetXYA_DownstreamFocus (ni)


	'''
	Pd = oeY.PositioningDirectives
	_DebugTab = 3

	oeX_Name = oeX.Name if oeX != None else 'None'

	Debug.print('<begin Parse Positioning>',_DebugTab )
	Debug.print('type: %s' % type(oeY.CoreOptics),_DebugTab+1 )
	Debug.print('Positioning: oeY = %s; \t oeX = %s' %(oeY.Name, oeX_Name),_DebugTab +1)
	Debug.print(str(Pd),5)


	# Don't do nothing
	# Created for leaving the allipse AxisOrigin into [0,0].
	# Actually it is not that safe.
	#-------------------------------------------
	if 	Pd.ReferTo == posdir_.ReferTo.DoNotMove:
		pass

	# ABSOLUTE POSITIONING
	#-------------------------------------------
	elif Pd.ReferTo == posdir_.ReferTo.AbsoluteReference:

		Debug.print('Absolute positioning', _DebugTab+1)

		# set position
		Debug.print( Pd.XYCentre,5)

		oeY.CoreOptics.SetXYAngle_Centre(Pd.XYCentre, Pd.Angle, WhichAngle = Pd.WhichAngle)

	elif Pd.ReferTo == 'locked':
		Debug.print('Locked positioning', _DebugTab)

	# ==============================================================================
	# REFERENCE:=
	# 	-PREVIOUS ELEMENT or
	#	-DOWNSTREAM ELEMENT or
	#	-SOURCE
	# ==============================================================================
	elif ((Pd.ReferTo == posdir_.ReferTo.UpstreamElement) or (Pd.ReferTo == 'source')):

		Debug.print('positioning respect with upstream element', _DebugTab+1)
		RayIn = oeX.CoreOptics.RayOutNominal	# the incident ray
		RayIn2 = tl.Ray(Angle = RayIn.Angle, XYOrigin = [0,0])

		#........................................
		#  put centre Distance away from centre
		#........................................
		if Pd.What == 'centre' and Pd.Where == 'centre':

			# Set position
			newXYCentre = oeX.CoreOptics.XYCentre + Pd.Distance * tl.Normalize(RayIn.v)
			oeY.CoreOptics.SetXYAngle_Centre(newXYCentre, RayIn.Angle, WhichAngle = TypeOfAngle.InputNominal)

			Debug.print('RayIn:= ' + str(RayIn.v), _DebugTab+1)
			Debug.print('RayIn2:= ' + str(RayIn2.v), _DebugTab+1)
#			Debug.print('oeY.RayIn:= ' + str(oeY.CoreOptics.RayOutNominal.v), _DebugTab+1)

		#........................................
		#  put upstreamfocus into centre
		#........................................
		elif Pd.What == 'upstream focus' and Pd.Where=='centre':
			# Set position
			oeY.CoreOptics.SetXYAngle_UpstreamFocus(oeX.XYCentre, RayIn.Angle)

		#........................................
		#  put centre into downstream focus
		#........................................
		elif Pd.What == 'centre' and Pd.Where=='downstream focus':
         # It is equivalent to put 'centre' into 'centre' with distance
         # equal to f2. e.g. oeX: detector, oeY: KB mirror

         # Set position
		 #hwired
			v =  oeX.RayOutNominal.UnitVectorAtOrigin.v
			#newXYCentre = oeX.CoreOptics.XYCentre + (Pd.Distance + oeX.CoreOptics.f2) * oeX.RayOutNominal.v
			#newXYCentre = oeX.CoreOptics.XYCentre + oeX.CoreOptics.f2 * v
			newXYCentre = oeX.CoreOptics.XYCentre + (Pd.Distance + oeX.CoreOptics.f2) * v
			tmp_ = np.linalg.norm(newXYCentre - oeX.CoreOptics.XYF2)


			oeY.CoreOptics.SetXYAngle_Centre(newXYCentre, RayIn.Angle)


		else:
			print('fottiti')

	else:
		# NOT IMPLEMENTED :-)
		print('PositioningDirectives.PARSE =: \t%s\n\t Code not implemented yet :-)' % Pd.ReferTo)
		pass
	Debug.print ('<\end Parse>',4)

	#================================================
	#  FUN: ComputeCaustics
	#================================================
	def ComputeCaustics(self, FocussingOe:OpticalElement, DefocusList, DetectorSize = 50e-6):
		'''
		Computes the Caustics

		Returns
		----
		Hew : scalar, half energy width
		WaistHew : scalar, half energy width at the waist (minimum value of Hew)
		WaistDefocus : scala, longitudinal location of the waist
		'''

		for (i, Defocus) in enumerate(DefocusList):

			# detector (h)
			#------------------------------------------------------------
			d_k = Optics.Detector(
								L = DetectorSize,
								AngleInNominal = np.deg2rad(90) )
			d_pd = Fundation.PositioningDirectives(
								ReferTo = 'upstream',
								PlaceWhat = 'centre',
								PlaceWhere = 'downstream focus',
								Distance = Defocus)
			d = OpticalElement(
								d_k,
								PositioningDirectives = d_pd,
								Name = 'detector')

			# Assemblamento beamline
			#------------------------------------------------------------
			t = None
			t = Fundation.BeamlineElements()
			t.Append(FocussingOe)
			t.Append(d)
			t.RefreshPositions()

			#Compute the field
			#--------------------------------------------------------------
			pass

#==========================================
# FUN: GetNSamples_OpticalElement
#==========================================
def GetNSamples_OpticalElement(Lambda: float, oe0 : OpticalElement, oe1 : OpticalElement) -> int:
	'''
		:param Lambda: wavelength
		:param oe0: optical element 1
		:param oe1: optical element 2
		:return: sampling
		Calculate sampling between two subsequent optical elements, according to Raimondi, Spiga, A&A (2014), eq. 12
		'''

	z = np.linalg.norm(oe1.CoreOptics.XYCentre - oe0.CoreOptics.XYCentre)  # distance between the elements
	L0 = oe0.CoreOptics.L  # Size of element 1
	L1 = oe1.CoreOptics.L  # Size of element 2
	Theta1 = pi / 2. + oe1.CoreOptics.VersorNorm.Angle  # Grazing incidence angle

	N = 4. * pi * L0 * L1 * abs(sin(Theta1)) / (Lambda * z)  # Sampling
	print('Number of points: {}'.format(int(N)))

	return int(N)


# ================================================
#  FUN: FocusSweep
# ================================================
def FocusSweep(oeFocussing, DefocusList, DetectorSize=50e-6, AngleInNominal=np.deg2rad(90)):
	''' Created for computing the field on a detector placed nearby the focal plane of
	oeFocussing : Focussing element
	oeFocussing : optical element that focusses radiation
	DefocusList :

	Return
	--------
	ResultList : a list of OpticalElement._ClassComputationResults

	HewList : an array of Half Energy Width of the INTENISTY

	SigmaList : an array of Sigma, computed as result of gaussian fitting ON THE INTENSITY

	More :	Other stuff
	'''
	DistanceList = DefocusList
	oeFocussing = copy.deepcopy(oeFocussing)
	# creating dummydetector
	# ------------------------------------------------------------
	d_k = Optics.Detector(
		L=DetectorSize,
		AngleGrazing=AngleInNominal)

	d_pd = PositioningDirectives(
		ReferTo='upstream',
		PlaceWhat='centre',
		PlaceWhere='downstream focus',
		Distance=0)
	d = OpticalElement(
		d_k,
		PositioningDirectives=d_pd,
		Name='detector')

	oeFocussing._IsSource = True  # MUSTBE!
	oeFocussing.PositioningDirectives.ReferTo = 'locked'
	oeFocussing.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.ANY
	NSamples = oeFocussing.ComputationResults.NSamples
	oeFocussing.ComputationSettings.NSamples = NSamples
	oeFocussing.ComputationSettings.UseCustomSampling = True

	d.ComputationSettings.NSamples = NSamples
	d.ComputationSettings.UseCustomSampling = True

	# Bemaline elments
	# ------------------------------------------------------------
	t = None
	t = BeamlineElements()
	t.Append(oeFocussing)
	t.Append(d)
	t.ComputationSettings.NPools = 1

	# Buffer
	# ------------------------------------------------------------
	N = len(DistanceList)
	Debug.On = False
	ResultList = [ComputationSettingsForOpticalElement] * N
	HewList = np.zeros(N)
	SigmaList = np.zeros(N)

	# Debug.print('Running: Fundation.FocusSweep',1)

	class More():
		Dist = np.zeros(N)
		XYCentre = np.zeros([N, 2])

	for (i, Distance) in enumerate(DistanceList):
		# I set the Position the detector at distance = Distance
		# ------------------------------------------------------------
		d.PositioningDirectives.Distance = Distance
		print(i)
		t.RefreshPositions()
		t.ComputeFields(Verbose=False)

		# Debug.print('%i/%i) dz = %0.2f mm' %(i,N, Distance *1e3),2)

		More.Dist[i] = np.linalg.norm(oeFocussing.CoreOptics.XYF2 - d.CoreOptics.XYCentre)
		More.XYCentre[i] = d.CoreOptics.XYCentre

		# Debug.print(oeFocussing.CoreOptics.GetPositionString(1))
		print(d.CoreOptics.XYCentre)
		# Debug.print(d.CoreOptics.GetPositionString(1))

		# Preparing and storing the results
		# -----------------------------------------------------------
		DeltaS = np.mean(np.diff(d.Results.S))  # Sample spacing on the detector

		ResultList[i] = copy.deepcopy(d.ComputationResults)
		I = abs(d.ComputationResults.Field) ** 2
		A2 = abs(d.ComputationResults.Field) ** 2
		I = A2 / max(A2)
		(Hew, Centre) = rm.HalfEnergyWidth_1d(I, Step=DeltaS, UseCentreOfMass = False) # FocusSweep
		try:
			(a, x0, Sigma) = tl.FitGaussian1d(I, d.ComputationResults.S)
		except:
			(a, x0, Sigma) = [None, None, None]
		HewList[i] = Hew
		SigmaList[i] = Sigma

	# Analyze the obtained caustics (minumum value, etc)

	return (ResultList, HewList, SigmaList, More)
# ================================================
#  FUN: FocusFind
# ================================================
def FocusFind(oeFocussing,	  DefocusRange = (-10e-3, 10e-3),
			  DetectorSize=200e-6,
			  MaxIter = 31,
			  AngleInNominal=np.deg2rad(90)):
	'''
	Find the best focus. Similar to FocusSweep, except that it does not provide the
	full sampling of the DefocusRange, but it uses an optimization algorithms to find
	the best focus as fast as possible.

	Faster, perhaps less fancy.

	For automation purposes, when producing publication-quality plots,
	it could be a nice idea to use feed FocusSweep with the
	results of FocusFind.

	Parameters
	------
	oeFocussing : Focussing element
	oeFocussing : optical element that focusses radiation
	DefocusList : array like
		List of defocus distances

	Return
	--------
	Results : struct-like class
		with the following attributes

	- BestField : 1d-array (complex)
				Field at the best focus
	- BestDefocus : scalar (real)
				Defocus of the best spot
	- BestHew : scalar (real)
				Half energy width of the best spot

	- OptResult : OptimizationResult object
				Contains the results of the optimization

	Notes
	--------
	In the test I did, convergence was reached within few (5-7) iterations,
	with BestDefocus of the order of 10mm (which was a pretty high value, indeed!).
	N of samples used: 1e4, lambda=2nm [MMan2020]

	'''

	from scipy import optimize as opt

	oeFocussing = copy.deepcopy(oeFocussing)
	# creating dummydetector
	# ------------------------------------------------------------
	d_k = Optics.Detector(
		L=DetectorSize,
		AngleGrazing=AngleInNominal)

	d_pd = PositioningDirectives(
		ReferTo='upstream',
		PlaceWhat='centre',
		PlaceWhere='downstream focus',
		Distance=0)
	d = OpticalElement(
		d_k,
		PositioningDirectives=d_pd,
		Name='detector')

	oeFocussing._IsSource = True  # MUSTBE!
	oeFocussing.PositioningDirectives.ReferTo = 'locked'
	oeFocussing.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.ANY
	NSamples = oeFocussing.ComputationResults.NSamples
	oeFocussing.ComputationSettings.NSamples = NSamples
	oeFocussing.ComputationSettings.UseCustomSampling = True

	d.ComputationSettings.NSamples = NSamples
	d.ComputationSettings.UseCustomSampling = True

	# Bemaline elments
	# ------------------------------------------------------------
	t = None
	t = BeamlineElements()
	t.Append(oeFocussing)
	t.Append(d)

	# Buffer Variabnles
	#------------------------------------------------------------
	DefocusList = []


	# Function to Minimize
	# ------------------------------------------------------------
	def ComputeHew(Defocus, d,t):
		# I set the Position the detector at Defocus = Defocus
		# ------------------------------------------------------------
		d.PositioningDirectives.Distance = Defocus
		t.RefreshPositions()
		# Perform the computation
		t.ComputeFields(Verbose=False)
		I = abs(d.ComputationData.Field) ** 2
		DeltaS = np.mean(np.diff(d.Results.S))  # Sample spacing on the detector
		(Hew, Centre) = rm.HalfEnergyWidth_1d(I, Step=DeltaS, UseCentreOfMass = False) # Compute the HEW in Focus Find

		return Hew

#	OptResult = opt.minimize_scalar(ComputeHew,
#								 method='bounded',
#								 bounds = DefocusRange,
#								 tol = 1e-8,
#								 options = {'maxiter' : MaxIter, 'disp' : True},
#								 args = (d,t)
#								 )


	OptResult = opt.minimize_scalar(ComputeHew,
								  args=(d,t), method='brent', tol=None, options={'maxiter': 31})

#	OptResult = opt.minimize_scalar(ComputeHew,
#								 method='brent',
#								 bounds = DefocusRange,
#								 options = {'maxiter' : MaxIter, 'disp' : True},
#								 args = (d,t)
#								 )
#	OptResult = opt.minimize_scalar(ComputeHew,
#								method='brent',
#								a = DefocusRange[0],
#								b = DefocusRange[1],
#								full_output = True,
#								xtol = 0.3e-3,
#								args = (d,t)
#								 )

#	OptResult = opt.minimize(HewToMinimize,
#								  x0 = 2.5 ,
#								method = 'Powell',
#								options = {'xtol' :  0.2e-3},
#								args = (d,t)
#								 )
	class Results():
		pass

	Results.BestField = d.ComputationData.Field
	Results.BestDefocus = OptResult.x
	Results.BestHew = OptResult.fun
	Results.OptResult = OptResult

	return Results

# ================================================
#  FUN: FocusFind
# ================================================
def FocusSweep2(oeFocussing,
			  DefocusList ,
			  DetectorSize=50e-6,
			  AngleInNominal=np.deg2rad(90)):
	'''

	Debug purposes

	'''

	from scipy import optimize as opt
	oeFocussing = copy.deepcopy(oeFocussing)
	# creating dummydetector
	# ------------------------------------------------------------
	d_k = Optics.Detector(
		L=DetectorSize,
		AngleGrazing=AngleInNominal)

	d_pd = PositioningDirectives(
		ReferTo='upstream',
		PlaceWhat='centre',
		PlaceWhere='downstream focus',
		Distance=0)
	d = OpticalElement(
		d_k,
		PositioningDirectives=d_pd,
		Name='detector')

	oeFocussing._IsSource = True  # MUSTBE!
	oeFocussing.PositioningDirectives.ReferTo = 'locked'
	oeFocussing.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.ANY
	NSamples = oeFocussing.ComputationResults.NSamples
	oeFocussing.ComputationSettings.NSamples = NSamples
	oeFocussing.ComputationSettings.UseCustomSampling = True

	d.ComputationSettings.NSamples = NSamples
	d.ComputationSettings.UseCustomSampling = True

	# Bemaline elments
	# ------------------------------------------------------------
	t = None
	t = BeamlineElements()
	t.Append(oeFocussing)
	t.Append(d)

	# Buffer Variabnles
	#------------------------------------------------------------
	N = len(DefocusList)
	HewList = np.zeros(N)

	# ComputeHew
	# ------------------------------------------------------------
	def ComputeHew(Defocus, d,t):
		# I set the Position the detector at Defocus = Defocus
		# ------------------------------------------------------------
		d.PositioningDirectives.Distance = Defocus
		t.RefreshPositions()
		# Perform the computation
		t.ComputeFields(Verbose=False)
		I = abs(d.ComputationData.Field) ** 2
		DeltaS = np.mean(np.diff(d.Results.S))  # Sample spacing on the detector
		(Hew, Centre) = rm.HalfEnergyWidth_1d(I, Step=DeltaS, UseCentreOfMass = False) # Compute the HEW

		return Hew

	# Focus Sweep
	# ------------------------------------------------------------
	for iDefocus, Defocus in enumerate( DefocusList):
		Hew = ComputeHew(Defocus, d,t)
		HewList[iDefocus] = Hew

	return HewList
#================================================
#  FUN: ZSweep
#================================================
def ZSweep(oeStart, DistanceList, DetectorSize = 50e-6, AngleInNominal = np.deg2rad(90)):
	''' Created for computing the field on a detector placed nearby the focal plane of
    oeFocussing : Focussing element

	'''


	# creating dummydetector
	#------------------------------------------------------------
	d_k = Optics.Detector(
    						L=DetectorSize,
    						AngleInNominal = AngleInNominal)

	d_pd = PositioningDirectives(
    						ReferTo = 'upstream',
    						PlaceWhat = 'centre',
    						PlaceWhere = 'centre',
    						Distance = 0)
	d = OpticalElement(
    						d_k,
    						PositioningDirectives = d_pd,
    						Name = 'detector')

	oeStart._IsSource = True # MUSTBE!
	oeStart.PositioningDirectives.ReferTo = 'locked'
   # Bemaline elments
	#------------------------------------------------------------
	t = None
	t = BeamlineElements()
	t.Append(oeStart)
	t.Append(d)

	# Buffer
	#------------------------------------------------------------
	N = len(DistanceList)
	Debug.On = True
	ResultList = [ComputationSettingsForOpticalElement] * N
	HewList = np.zeros(N)
	Debug.print('Running: Fundation.ZSweep',1)

	class More():
		Dist = np.zeros(N)
		XYCentre = np.zeros([N,2])

	for (i,Distance) in enumerate(DistanceList):
		# Position the detector at distance = Distance
		#------------------------------------------------------------
		d.PositioningDirectives.Distance = Distance
		t.RefreshPositions()
		t.ComputeFields(Verbose = False)

		Debug.print('%i/%i) dz = %0.2f mm' %(i,N, Distance *1e3),2)

		More.Dist[i] = np.linalg.norm(oeStart.CoreOptics.XYCentre - d.CoreOptics.XYCentre)
		More.XYCentre[i] = d.CoreOptics.XYCentre

		# Preparing and storing the results
		#-----------------------------------------------------------
		DeltaS = np.mean(np.diff(d.Results.S)) # Sample spacing on the detector

		ResultList[i] = copy.deepcopy(d.ComputationResults)
		(Hew, Centre) = rm.HalfEnergyWidth_1d(abs(d.ComputationResults.Field)**2, Step = DeltaS)
		HewList[i] = Hew

	return (ResultList, HewList, SigmaList, More)






#%% Fine
