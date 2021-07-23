'''
Line Equation
:math:`y = m x + q`
Author michele.manfredda@elettra.eu

'''

from __future__ import division
from LibWiser.must import *
import LibWiser
from LibWiser import Optics, Rayman as rm, ToolLib as tl
from LibWiser import ToolLib
from LibWiser import Rayman
from LibWiser.ToolLib import  Debug
import inspect
from collections import OrderedDict
import numpy as np
import copy
from LibWiser.Scrubs import Enum
import time
import warnings

from LibWiser.Optics import TypeOfAngle, OPTICS_ORIENTATION
from LibWiser.CodeGeneratorVisitor import CodeGenerator
import LibWiser.CodeGeneratorVisitor as CGVisitor
from LibWiser.Exceptions import WiserException, PrintValues
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
	@Intensity.setter
	def Intensity(self,x):
		raise WiserException(r'''The intensity is automatically computed from the Field, 
						   and it can not be set. This is a programming error ''')
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
			
	@property
	def NSamples(self):
		return self._NSamples
	
	@NSamples.setter
	def NSamples(self,N):
		try:
			NSamples = int(N)
			self._NSamples = NSamples
		except:
			raise Exception('Error: <NSamples> was not a valid integer. N = <%s>' % str(N))
			pass
		



#===========================================================================
# 	STRUCT: PositioningDirectives
#===========================================================================
class PositioningDirectives(CodeGenerator):
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

	def __init__(self, 
			  ReferTo = 'source', 
			  PlaceWhat = 'centre', 
			  PlaceWhere = 'centre',
			  Distance = 0., 
			  GrazingAngle = None, 
			  XYCentre = None, 
			  Angle = None, 
			  WhichAngle = 'axis',
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
		super().__init__(['ReferTo',('What','PlaceWhat'),('Where','PlaceWhere'), 'GrazingAngle','Distance'])
		
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
	
# 	def GetInitCode(self):
# 		'''
# 		Return a string containing the python code which generate the object.
# 		
# 		1) Only information originally used in the init function are used: computation data, cross-links,
# 		delayed associations are ignored.
# 		
# 		2) Some classes accepts different combinations of input parameters. The GetInitCode functions typically
# 		choose one of these sets and hardcode the,
# 		'''
# 		'''
# 						PositioningDirectives = Foundation.PositioningDirectives(
# 						ReferTo = 'source',
# 						PlaceWhat = 'centre',
# 						PlaceWhere = 'centre',
# 						Distance = 41.4427)'''
# 						
# 		ClassName = type(self).__name__ #Foundation.PositioningDirectives
# 		ClassShortName = "PositioningDirectives"
# 		s= "PositioningDirectives =%s(" % ClassName
# 		s+= "\n\tReferTo = '%s' " % self.ReferTo
# 		s+= "\n\tPlaceWhat = '%s' " % self.PlaceWhat
# 		s+= "\n\tPlaceWhere =  '%s' " % self.PlaceWhere
# 		s+= "\n\tDistance = %0.6f" % self.Distance
# 		s+= ")"
# 		
# 		return s
	
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
		__HardcodedStyle = 1
		NameChildren= ','.join([Child.Name for Child in self.Children])
		NameParent = ('' if self.Parent == None else self.Parent.Name)
		
		if __HardcodedStyle == 0:
			Str = '[%s] ---- *[%s]*----[%s]' %( NameParent, self.Name,NameChildren)
		else:
			Str = '*[%s]*' % self.Name 
		
		return Str

	@property
	def Name(self):
		return self._Name
	@Name.setter
	def Name(self,x):
		self._Name = x
		
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

		ParentCointainer is updated by TreeItem.Insert 
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
class Tree( CodeGenerator):

    #================================================
    #     __init__
    #================================================
	def __init__(self, ItemList = None):
#		self._Items = dict()
		
		self._Items = OrderedDict()
		self._ActiveItem = None
		self._Name = ''
		self._FirstItem = None


		if ItemList is not None:
			for Item in ItemList:
				if type(Item) is str:
					ItemToAdd = globals()[Item] # does not work
				else:
					ItemToAdd = Item
				self.Append(Item)
				
    #================================================
    #     __getitem__
    #================================================
	def __getitem__(self,Key):
		'''
		Paramters
		--------------------
		Key : can be EITHER strinf (name) OR integer (position index)
		'''

		def ItemNotFound(Key = None):
			raise Exception('Tree.__getitem__, Item not found. Specified item:\n"%s"' % Key)
		# The Key is an object
		try:
			try:
				return self._Items[Key.Name]
			except:
				ItemNotFound(Key.Name)
		except:
			pass
		# The Key is an integer
		if type(Key) == int:
			try:
				return self._Items.items()[Key][1] # returns the object of the dictionary
			except:
				ItemNotFound(Key)
		# The Key is a STRING
		elif type(Key) == str :
			try:
				return self._Items[Key]	# returns the object of the dictionary
			except:
				ItemNotFound(Key)
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
		Uses the _:_disp__ function of the Item class
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
		'''
		It is a secondary attribute (its value is built upon that of primary attributes).
		
		It bases on the primary attribute: FirstItem
		
		It should be named GetItemList NOT ItemList
		'''
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

	@property
	def ItemNameList(self):
		return [_.Name for _ in self.ItemList]
		
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

		# Update the ParentContainer attribute		
		NewItem.ParentContainer = self
		
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
	def Append(self, NewItem,  posdirective = None, NewName = None,
			AppendAllIfList = True):
		'''
		Append NewItem to the tree structure.
		
		If NewItem is a list, then all the items in the list are appended.
		'''
		
		#Case: NewItem is a list of items
		if ((type(NewItem) is list) or (type(NewItem) is tuple)) and AppendAllIfList:
			for _ in NewItem:
				self.Append(_)
		#Case: NewItem is a single item (usual)
		else:
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
    #     Remove
    #================================================
	def Remove(self, KeyOrItem):
		
		raise Exception("Remove does not work! Fix it to use it")
		
		if type(KeyOrItem) is not list:
			KeyOrItem = [KeyOrItem]
			
		
		for _ in KeyOrItem:
		
			# get the element within the Tree
			if type(_) == int:
				Item = self.ItemList[_]
			else:
				Item = _			
				
			# cuts and paste the link with parent and children
			HasParent = Item.Parent is not None
			HasChildren = Item.Children is not None
			
			if HasParent and HasChildren:
				#links parent to children
				Item.Parent.Children = Item.Children
				#links children toparents
				for Child in Item.Children:
					Child.Parent = Item.Parent
			
			if HasParent and not(HasChildren):
				#free the parent from children
				Item.Parent = None
				
			if HasChildren and not(HasParent):
				#free the children from parent
				for Child in Item.Children:
					Child.Parent = None
					
			
			
			
			
    #================================================
    #     GetFromTo
    #================================================
	def GetFromTo(self, FromItem = None,  ToItem = None):
		'''
		Returns the item comprised between FromItem and ToItem within self.ItemList
		(included)
		'''
		

		# Use all the items in the beamline
		if FromItem == None and ToItem == None:
			return self.ItemList
		else:
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
class OpticalElement(TreeItem, CodeGenerator):
	'''
	- If Name is None, then the name is automatically assigned.
	'''
	__NameCounter = {} # PRIVATE
	_LastInstance = 13


    #================================================
    #     __init__[OpticalElement]
    #================================================
	def __init__(self, 
				  CoreOpticsElement = None,
				  Name = None,
				  IsSource = False, # IsSource denotes the
				  PositioningDirectives = None,
				  ComputationSettings = None,
				  VirtualOffset = 0,
					*kwargs):
		# The baroque notation I used for 'CoreOptics' is because the name of the
		# attribute (stored in the class) and the name of the parameter (of the init function) 
		# are different. The format is (attribute name, parameter name)
		CodeGenerator.__init__(self,['Name', 'IsSource', ('CoreOptics', 'CoreOpticsElement'),'PositioningDirectives'])
		
		#self.ChainControl = ChainControlObject()
		OpticalElement._LastInstance = 130
		TreeItem.__init__(self)
		self._IsSource = IsSource
		self.PositioningDirectives = PositioningDirectives
		self._VirtualOffset = VirtualOffset
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
			# update the parent container
			self.CoreOptics.ParentContainer = self

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
		
		try:
			ParentContainerName = self.ParentContainer.Name
		except:
			ParentContainerName = 'Not Assigned'
			
		StrBuffer = ['\t<begin OpticalElement>',
			   'Name: %s ' % self.Name,
			   'ParentContainer: %s' % ParentContainerName,
			   '\t\t <begin CoreOptics> ',
			 self.CoreOptics.__str__(),
			 '\t\t< End CoreOptics>',
			 '\t<end OpticalElement>\n']
			 
		return '\n'.join(StrBuffer)

    #================================================
    #     __disp__[OpticalElement]
    #================================================
	def __disp__(self):
			'''
			Displays the beamline elements in the form
			[0]---[1*]---[2]
			[1]---[2*]---[3]
			
			OR
			
			in the form
			[0]
			[1]
			[2]
			
			'''
			import textwrap
			 
			NameChildren = ','.join([Child.Name for Child in self.Children])
			NameParent = ('' if self.Parent == None else self.Parent.Name)
			#	    # Old String: I displayed the XYCentre [MM]
			#		Str = '[%s] ---- *[%s]*----[%s]\t\t *XYCentre* = %0.2e, %0.2e' % (
			#		NameParent, self.Name, NameChildren, self.XYCentre[0], self.XYCentre[1])
			#


			DistanceFromParent = self.GetDistanceFromParent(False,False)
#			print(self.GeneralDistanceFromParent(Reference=False))
#			print(DistanceFromParent)

			# print(self.GeneralDistanceFromParent(Reference=False))

			Str = '[%s] ---- *[%s]*----[%s]' % (NameParent, self.Name, NameChildren)
			
			Str = '*[%s]*' % self.Name
			
			N = 15
			Str = Str.ljust(N)
			Str = Str[0:N-1]
			# Additional Stuff (such as the distance from previous element, etc...)
			
			
			Str += '\t(%s), dZ=%0.2f m, Z=%0.2f m, %s' % (
					self.CoreOptics.Orientation.name[0],
					   self.GetDistanceFromParent(False), 
				self.DistanceFromSource, 
				self.CoreOptics.GetSummary())
			

			return Str
		
	#===========================================
	# PROP: CoreOpticsElement
	#==========================================
	@property
	def CoreOpticsElement(self):
		return self._CoreOpticsElement
	
	@CoreOpticsElement.setter
	def CoreOpticsElement(self, value : Optics.Optics):
		value.ParentContainer = self
		self._CoreOpticsElement= value


		
	#==========================================
	# FUN: GetNSamples[OpticalElement]
	#==========================================
	def GetNSamples(self,
				 Orientation,
				 UseCustomSampling = None):
		'''
		Returns the proper number of samples to use for ThisOpticalElement in
		propagation the field as UpstreamElement(0) ----> ThisElement(1).

		The wavelength is delivered by *BeamlineElements.Lambda*

		Parameters
		--------
		UseCustomSampling : {None|bool}
			If *None*, uses OpticalElement.ComputationSettings.UseCustomSampling
			
		'''

		# Link to default
		if UseCustomSampling is None:
			UseCustomSampling  = self.ComputationSettings.UseCustomSampling
		
		# Use custom sampling
		if UseCustomSampling == True:
			return self.ComputationSettings.NSamples
		else:
			# This section is conceptually wrong:
			# The intelligence for computing the sampling should stay here.
			# However, I put it at the Container level (BeamlineElements). This generates a lot of dependencies, tc.
			# However, once this is clearly stated, the code is still maintaneable.
			SampleList, ElementList = self.ParentContainer.GetSamplingListAuto(Orientation)
			
			try:
				SelfIndex = ElementList.index(self)
			except:
				raise WiserError("I did not found 'self' element in element list. Solution: unknown")
				
			return SampleList[SelfIndex]
		
		return NSamples


	#===========================================
	# FUN: ComputeSampling_2Body
	#==========================================
	@staticmethod
	def GetNSamples_2Body(Lambda: float, oe0 , oe1) -> int:
		'''
		THIS IS THE FUNCTION REALLY USED TO COMPUTE THE SAMPLING.
		It uses: Rayman.ComputeSamplingA
		''' 
		z = np.linalg.norm(oe1.CoreOptics.XYCentre - oe0.CoreOptics.XYCentre)
		L0 = oe0.CoreOptics.L
		L1 = oe1.CoreOptics.L
		Theta0 = oe0.CoreOptics.VersorNorm.Angle
		Theta1 = oe1.CoreOptics.VersorNorm.Angle
#		Alpha0 = oe0.CoreOptics.Angle
		a = oe1.ComputationSettings.OversamplingFactor
		return rm.ComputeSamplingA(Lambda, z, L0, L1, Theta0, Theta1, 10)
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
		return np.array(self.CoreOptics.XYCentre)


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
		BASE FUNCTION for computing the distance b\w OpticalElements.
		
		WARNING: It considers only the "Reference" optical elements, i.e.
		detectors and slits are typically ignored.
		
		If you want something more versatile, use GetDistanceFromParent, instead.
		
		Distance from parent optical element corresponds to the optical distance between the element (self)
		and the first optical element with the same orientation and UseAsReference flag True (obtained with
		>>> self.GetParent(SameOrientation=True, OnlyReference=True))

			20210630: it adds OpticalElement._VirtualOffset to the computation.
		(Introduced to handle the numerical sources, which often
		would ideally be at 0, but are not.)
		
		'''

		Parent = self.GetParent(SameOrientation=True, OnlyReference=True)

		if Parent != None:
			distance = np.linalg.norm(self.XYCentre - Parent.XYCentre)
			if Parent._IsSource: #20210630
				distance += Parent._VirtualOffset

		elif Parent == None: # self is the source
			distance = 0
			distance += self._VirtualOffset
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
		Distance from the source
		
		USES: OpticalElement.DistanceFromParent
		
		'''
		#patch added 20210630
		# Why? it was working before...
		# Consequence of workingon numerical source
		if self._IsSource:
			return 0 
		#
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
	#	FUN: GetChild
	# ================================================
	def GetChild(self, 				  
				 Orientation=Optics.OPTICS_ORIENTATION.ANY,
				 UseAsReference = None,
				 Ignore = None,
				 ChildBranch = 0):
		'''
		
		Parameters
		------
		Orientation : Optics.OPTICS_ORIENTATION
			Only elements that match *Orientation* are taken
			
		UseAsReference : bool|None
			If True/False, only elements which are marked (or NOT Marked) as 'reference' are taken.
			If None, the filter is not used.
			
		Ignore: bool|None
			If None, the filter is not used.
			If True/False, only elements whose CoreOptics.ComputationData.Ignore matches are considered.
			
		ChildBranch : int
			Select which branch must be considered.
			Up to know, no other branch than 0 has aver been used.
			
		self = presto
		 Orientation=Optics.OPTICS_ORIENTATION.HORIZONTAL
		 Ignore = None
		  ChildBranch = 0
		  
		  presto.GetChild(Orientation  = Optics.OPTICS_ORIENTATION.HORIZONTAL)
		  presto.GetChild()
		'''
		
		GoOn = True
		CurrentChild = self
		ReturnElement = None
		NOfIgnoredElements = 0
		IgnoredElements = [] # list that contains all the elements with Ignore = True 
		i = 0
		while GoOn:
			i+=1
			try:
				CurrentChild = CurrentChild.Children[ChildBranch]
			except:
				# No child found
				return None
			
			CurrentParent = CurrentChild.Parent
			
			#Filters for the orientation
			#---------------------------------------------------------
			# Any Orientation?
			if CheckOrientation(CurrentChild, Orientation):
				pass
			else:
				continue
			 
			#Filters for "Ignore"
			#---------------------------------------------------------
			if Ignore == None:
				pass
			else:
				if CurrentChild.ComputationSettings.Ignore == True:
					NOfIgnoredElements +=1
					IgnoredElements.append(CurrentChild)
					
				if CurrentChild.ComputationSettings.Ignore == Ignore:
					pass
				else:
					continue
				
			#Filters for Reference
			#---------------------------------------------------------		
			if UseAsReference is None:
				pass
			else:
				if CurrentChild.CoreOptics.UseAsReference == UseAsReference:
					pass
				else:
					continue
			# If all the check are passed, the current element is returned	
			ReturnElement = CurrentChild
			GoOn = False
			
			if i > 100:
				raise WiserException('Error in GetChild: the while loop got stucked. It was stopped after 100 iterations.')
			
		return ReturnElement
			
			
	
	
	# ================================================
	#	FUNC: GetNextPropagationChild
	# ================================================
	def GetNextPropagationChild(self, Orientation = None):
		'''
		Returns the next element which must be used for propagation. 
		
		If necessary, creates the virtual Child.
		
		Orientation: if None, self.CoreOptics.Orientation is used. However beware,
		it the optical element is isotropic this will return inconsistent result.
		
		----------------------
		'''
		class MoreInfo():
			IgnoredElements = []
		
		pass
	
		if Orientation is None:
			if ((self.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC) 
				or (self.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ANY)):
					raise WiserException ("Error in GetNextPropagationChild: the orientation specified was ANY or ISOTROPIC.")
			else:
				Orientation = self.CoreOptics.Orientation
				 
		#XXX def GetNextPropagationChild
		RawElementList = self.ParentContainer.GetElementList(oeStart=self,
					oeEnd=None, 
					Orientation=Orientation,
					Ignore = None)
		
		FilteredElementList = self.ParentContainer.GetElementList(oeStart=self,
					oeEnd=None, 
					Orientation=self.CoreOptics.Orientation,
					Ignore = False)
		
		try:
			NextChild = FilteredElementList[1]
		# This is the last element
		except:
			return None
			
		#There is need to create a virtual element
		if len(FilteredElementList) < len(RawElementList):
			Distance = self.ParentContainer.GetDistance(self, NextChild)
			ReturnOE = self.ParentContainer._MakeVirtual(NextChild, 
										   self,
										  Distance)	
		else:
			ReturnOE = NextChild
		return ReturnOE
	# ================================================
	#	FUNC: GetParent [OpticalElement]
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

		#20210630 - PATCH
		# Before it was no needed, why?
		# However, now, it sounds good to me...
		if self._IsSource:
			return None
		
		
		# end of patch
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
			warnings.warn("OpticalElement: %s" % self.Name)
			raise Exception('''GetParent returned None! This occurs when
							   - There is no Reference optical element
							   - ...
							      OpticalElement = %s''' % self.Name)

		return GetParentResult
	
#	#================================================
#	#  FUN: GetParentWithSameOrientation
#	#================================================
#	def GetParentWithSameOrientation(self):
#		'''
#		Return the first element with the same orientation.
#		Technically it is not a parent... but here it is.
#		
#		'''
#		MyOrientation = self.CoreOptics.Orientation
#		
#		Goon = True
#		Current = self
#		while Goon:
#			if Current.Parent is None:
#				return None
#			elif Current.Parent.CoreOptics.Orientation == MyOrientation:
#				return Current.Parent
#			else:
#				Current = self.Parent
				
	def GetDistanceFromSource(self):
		'''
		Alias function for the proeprty: DistanceFromSource
		'''
		return self.DistanceFromSource
	
	def GetDistanceFromParent(self, SameOrientation=False, OnlyReference=False):
		'''
		Advanced function, that implements more arguments than GetDistanceFromParent
	
		USES: OpticalElement.DistanceFromSource
		
		WARNING: The dependency chain is quite complicated.
		
		DistanceFromParent->DistanceFromSource->GetDistanceFromParent
		
		
		
		Parameters
		-----
		SameOrientation : bool
			If _true_, measures the distance from the closest upstream element
			that has the same orientation.
			
		OnlyReference: bool
			if _true_, measures the distance from the closes upstream element
			that is marked as "reference" (e.g. detectors, slits are excluded).
		
		High level function to calculate the distance to parent.
		The parent can be filtered by orientation, reference type.

		Dev notes
		-----
		It uses the distance from source and requires XYCentre to be already computed.
		Best version (20201023) - AF + MM
		'''
		Parent = self.GetParent(SameOrientation=SameOrientation, OnlyReference=OnlyReference)
		
		if Parent is not None:
			result = self.DistanceFromSource - Parent.DistanceFromSource
		else:
			if self._IsSource:
				result = 0
			else:
				raise WiserException(r'''
						 The parent element is None, but the current element
						 is not a source, as one would expect to be.
						 Why?
				''')
		return result

	def GeneralDistanceFromParent(self, Orientation=True, Reference=True):
		
		#DEPRECATED??
		'''
		Generalized DistanceFromParent. As DistanceFromParent is a property and linked to a lot of other things
		in the code, this was added later for correct __str__ behaviour.
		It corresponds to the optical distance between the element (self) and the first optical element with the
		Orientation and Reference.
		>>> self.GetParent(SameOrientation=Orientation, OnlyReference=Reference))
		'''
		raise Exception(" Message for MManfredda: GeneralDistanceFromParent is deprecated. Use GetDistanceFromParent instead.")
		if self.Parent != None:
			try:
				a = self.XYCentre
				b = self.GetParent(SameOrientation=Orientation, OnlyReference=Reference).XYCentre
				distance = np.linalg.norm( a- b)
				
			except TypeError as Error:
				raise 	WiserException("""
							  
				Error here. Possible cause: did you call .RefreshBeamline method?
				""", "ByGeneralDistanceFromParent", Args = ['a','b'])
		elif self.Parent == None:
			distance = 0
		else:
			raise ValueError('Something wrong in GeneralDistanceFromParent!')

		return distance

	# ================================================
	#	PROP: PlotIntensity [OpticalElement]
	# ================================================
	def PlotIntensity(self,
				   FigureIndex =None, 
				   Label = None, 
				   Normalization = 'max',
				   SetPeakAtZero = False,
				   ManualIntensity = []):
#		ToolLib.CommonPlots.IntensityAtOpticalElement(self)
		'''
		Parameters
		-----------------------
		
		Normalization : str
			Can be 
			-'int' normalize wrt the integral
			-'max' normalize wrt the maximum value
			-None|else does not normalize
		''' 
		
		try:
			y = self.ComputationData.Intensity
			x = self.ComputationData.S
		except:
			raise Exception("I attempted to plot the Intensity of %s, but I found no data." % self.Name)
			
		if x is None or y is None:
			
			return None
		
		
		if Normalization =='int':
			NN = sum(y)
			TitleDecorator = '(Plot normalized wrt int)'
		elif Normalization =='max':
			NN = np.max(y)
			TitleDecorator = '(Plot normalized wrt max)'
		else:
			NN = 1
			TitleDecorator = '(Raw)'
			
		y = y/NN 
		# it does not really work
		xToPlot, xPrefix = LibWiser.Units.GetAxisSI(x)
		
		
#		xToPlot = x*1e-6
#		xPrefix =
		
		plt.figure(FigureIndex)
		Label = Label if not( Label is None) else ('%s, $\lambda: %0.1f nm$' % ( self.Name, self.ComputationData.Lambda*1e9)  )
		
		
		# Center peak value to zero
		if SetPeakAtZero:
			MaxIndex = y.argmax()
			MaxX = xToPlot[MaxIndex]
			xToPlot -= MaxX
		
		plt.plot(xToPlot, y, label = Label)
		# Layout
		#--------------------------------------------------------------
		plt.xlabel('S [%sm]' % xPrefix)
		plt.ylabel('I (a.u)')
		plt.title('Element: %s %s' % (self.Name, TitleDecorator))
		plt.legend()
		plt.show()
	# ================================================
	#	PROP: PlotFigureError [OpticalElement]
	# ================================================
	def PlotFigureError(self,
					 FigureIndex =None, 
					 Label = None,
					 FigureErrorIndex = 0, 
					 TitleDecorator = '',
					 PlotIntensity = True ):
		
		if FigureErrorIndex>=0:
#			x,h = self.CoreOptics.FigureError_GetProfile(FigureErrorIndex)		
			x,h = self.CoreOptics.FigureError_GetProfileAligned(FigureErrorIndex)
			
		else:
			# that's a workaround for getting x
			Index = self.CoreOptics.LastFigureErrorUsedIndex
#			x,h = self.CoreOptics.FigureError_GetProfile(Index)
#			NToPlot = x * len(h)
			if Index is None:
				return None
			x,h = self.CoreOptics.FigureError_GetProfileAligned(Index)
		if len(x) > 0:
					
			# This part can be included in a function
			xToPlot, xPrefix = LibWiser.Units.GetAxisSI(x)
			yToPlot, yPrefix = LibWiser.Units.GetAxisSI(h)
			
			# Plot figure error
			#--------------------------------------------------------------		
			plt.figure(FigureIndex)
			plt.plot(xToPlot, yToPlot, label = Label)
			
			# Plot Intensity, if available
			#--------------------------------------------------------------					
			if PlotIntensity:
				try:
					I = self.ComputationData.Intensity
					yyToPlot = I/max(I) * max(yToPlot)
					S  = LibWiser.ToolLib.MakeZeroOffset(self.ComputationData.S) 
					xxToPlot, xxPrefix = LibWiser.Units.GetAxisSI(S)
					plt.plot(xxToPlot,yyToPlot,'k', label = 'Intensity')
				except:
					pass
			# Layout
			#--------------------------------------------------------------
			plt.xlabel('S [%sm]' % xPrefix)
			plt.ylabel('Height Profile [%sm]' % yPrefix)
			plt.title('Figure error at %s %s (light comes from above)' % (self.Name, TitleDecorator))
			plt.legend()
		else:
			pass
			#raise Warning('Plor Figure Error: no data found')
#===========================================================================
# 	CLASS: BeamlineElements
#===========================================================================
class BeamlineElements(Tree):

	class _ClassComputationSettings:
		def __init__(self, ParentContainer):
			self.ParentContainer = ParentContainer
			self.NPools = 1
			self.NRoughnessPerOpticalElement = 1
			self.NFigureErrorsPerOpticalElement = 1
			self.UseFigureError = False
			self.UseRoughness = False
			self.iRoughness = 0
			self.iFigureError = 0
			self.OrientationToCompute = []
			self._TotalComputationTimeMinutes = 0
			self.AllowRepeatedNames = False #When accessing the elements as BeamlineElements[Name], having repeated names is  forbidden! However, in all the other cases, repeated names are not a problem per se.
			self._CollectiveCustomSampling = None


		@property
		def iComputation(self):
			return self.NRoughnessPerOpticalElement * self.iFigureError + self.iRoughness
		@property
		def NComputations(self):
			return self.NRoughnessPerOpticalElement * self.NFigureErrorsPerOpticalElement

		@property
		def CollectiveCustomSampling(self):
			return self._CollectiveCustomSampling
		@CollectiveCustomSampling.setter
		def CollectiveCustomSampling(self, Value):
			if type(Value) is not bool:
				raise Exception("Value must be a boolean")
				
			self._CollectiveCustomSampling = Value
			BeamlineElements.SetAllUseCustomSampling(self.ParentContainer, Value)
			
	#================================================
	#  FUN: __init__
	#================================================
	def __init__(self, ItemList = None):
		Tree.__init__(self, ItemList)
		self.ComputationSettings = BeamlineElements._ClassComputationSettings(ParentContainer = self)



    #================================================
    #   FUN: __str__ [BeamlineElements]
    #================================================
	def __str__(self):
		
		"""
		Uses TreeItem.__disp__
		
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
    #   FUN: __str__ [BeamlineElements]
    #================================================
	def Print(self, Orientation = OPTICS_ORIENTATION.ANY, 
		   ApplyIgnore = True ):
		'''
		The same as print(BeamlineElements), but can choos the orientation to print
		and some other flags
		
		ApplyIgnore : {bool|None}
			If False => show alla the elements
			If True => show the elements with (Ignore = False) [so, it "ignores the element to be ignored"]
		'''
		
		
		IgnoreValueToMatch = {False : None, True : False}[ApplyIgnore] # baroque line just to map False into None, etc...
		
		ItemList = self.GetElementList(Orientation = Orientation,
								 Ignore = IgnoreValueToMatch)
		
		StrList = ['']
		for Item in ItemList:
			StrList.append(Item.__disp__())
			
		print(20 * '=')	
		print( 'Beamline Name:' + self.Name)
		print( '\n'.join(StrList))
		print(20 * '=')		

		
		
	#================================================
	#  PROP: Source [BeamlineElements]
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
	
	@property
	def MainLambda(self):
		'''
		Return the wavelength of the beamline. The wavelength is picked
		from the first element which has a valid
		OpticalElement.CoreOptics.Lambda attribute.
		
		All the sources must have.
		'''
		Found= False
		
		# Method1) Search for an item which has a 'Lambda' attribute
		for Item in self.ItemList:
			try:
					Lambda = Item.CoreOptics.Lambda
					Found = True
					break
			except:
				pass	
			
		if Found:
			return Lambda
		else:
			
			 #METHOD2) Search for the first item which has a valid ComputationData.Lambda
			for Item in self.ItemList:
				try:
						Lambda = Item.ComputationData.Lambda
						Found = True
						break
				except:
					pass				 
			if Found:
				return Lambda
				raise WiserException('''BeamlineElements.MainLambda could not identify 
								 the lambda of the simulation. BeamlineElements.Name =%s''' %
								 self.Name)
	#================================================
	#  PROP: Source
	#================================================
	@property
	def LightSource(self):
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


	
	
	@property
	def ComputationMinutes(self):
		return self._TotalComputationTimeMinutes

	#================================================
	#  PROP: Lambda
	#================================================
#	@property
#	def Lambda(self):
#		'''
#		Return the wavelength of the simulation.
#		There are different cases.
#		1) the source is analytical => Lambda is stored in its properties
#		2) the source is any kind of OpticsNumericalobject (e.g. a mirror)
#			=> Lambda is stored in the ComputationData
#		3) The source is a VirtualSource, which means that there must be another
#			optical element delivering the light. For the moment, I assume
#			that such an element is a SourceWavefront object.
#		'''
#		
#		ClassOfTheSource = type(self.Source.CoreOptics)
#		
#		#1) the source is analytical		
#		if issubclass(ClassOfTheSource, LibWiser.Optics.SourceAnalytical):
#			# The source is analytical, so it directly has the info on the lambda
#			Lambda = Source.CoreOptics.Lambda
#		#2) The source is a generic numericaloptics element
#		elif (issubclass(ClassOfTheSource, LibWiser.Optics.SourceNumerical) 
#				 and not (ClassOfTheSource  == LibWiser.Optics.SourceVirtual)):
#			Lambda = Source.ComputationData.Lambda
#			
#		# The "source" is a virtual source
#		elif ClassOfTheSource  == LibWiser.Optics.SourceVirtual:
#			# Check that there is at least  one child (i.e. the SourceWavefront)
#			try:
#				Child = self.Source.GetChildren()[0]
#			except:
#				raise WiserException('''The Virtual Source itself does not contain 
#						 infos about the wavelength. Append a SourceWavefront object 
#						 to the beamline to specify the wavelength''')
#			#if ok, try to get the wavelenght from the child,
#			# that should be a SourceWavefront.
#			
#			try:
#				Lambda = Child.Lambda
#			except:
#				raise WiserException("BeamlineElements.Lambda failed. Why? Check the code")
#				
#		return Lambda
	@property
	def Lambda(self):
		return self.MainLambda
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


		#Check if there are repeated names.
		if not self.ComputationSettings.AllowRepeatedNames:
			self._CheckIfRepeatedNames() 


		#Here Oncewe thought to put
		DefaultOrientation = self._GetFirstOrientedElement().CoreOptics.Orientation
		
#		if len(self.ComputationSettings.OrientationToCompute) ==0:
#			raise WiserException("""
#				OrientationToCompute is empty. WISER could try to
#				default it, but this behavior was inhibeted since
#				it generated misunderstandings.
#				Mike knows what to do.
#			""")
		if len(self.ComputationSettings.OrientationToCompute) ==0:
			self.ComputationSettings.OrientationToCompute = [DefaultOrientation]
			
			print(20 * '=x' + """ \nn
			 RefeshPositions:\Orientation defaulted to %s, according to the first non-isotropic
			element of the beamline.""" % DefaultOrientation )	
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
				The optical element to place. The other info (parent elements, etc)
				are got as attributes of oeY.

			Behavior
			------------------
			- If PositioningDirectives has ReferTo='locked' then the positioning of the present element is not computed.
				This shall be used for elements whose position has already been computed in another BeamlineElements object,
				and you don't want to recompute all the sequence.
				I introduced this when I do the focus sweep, keeping an optical element fixed ('locked') and moving the screen
				only.
			- Upstream reference is working nice.
			- Downstream focus will find the firs element (with the same orientation) that has f2 as attribute, then
			will use f2 as positioning distance
			- UseAsReference=False means that the Element is not considerend for positioning other elements.

			Developer notes
			------------------
			Bases on: XYCentre, SetXYAngle_Centre,  GetParent(...), DistanceFromParent

			Curiosity: why is this function here? And it is not a member of Optical element?

		'''
		Pd = oeY.PositioningDirectives
		
		
		print('Positioning: %s' % oeY.Name)

		if oeY.IsSource == False:
			oeX = oeY.GetParent(SameOrientation=False, OnlyReference=True) # Get XY coordinates from the oeX
			oeXSameOrientation = oeY.GetParent(SameOrientation=True, OnlyReference=True)
			VirtualOffset = oeY.ParentContainer.Source._VirtualOffset
		
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
				
				realDistance += VirtualOffset 
				
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

				#FIX 4 Aljosa
				#@TODO
				#If there is an error here, probably the beamline has a non logical
				#sequence of V and H elements. We should investigate
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

			else:
				raise ValueError('Wrong or un-implemented PositioningDirectives!')

		else:
			# NOT IMPLEMENTED :-)
			print('PositioningDirectives.PARSE =: \t%s\n\t Code not implemented yet :-)' % Pd.ReferTo)
			pass
		Debug.print('<\end Parse>', 4)





	#================================================
	#  FUN: SetIgnoreList
	#================================================
	def SetIgnoreList(self,ElementList, Ignore : bool = True):
		'''
		Specify which elements must be ignored or not
		
		
		Dev notes
		---------------------------
		This function accepts only data in the format: (element list, single value for all).
		More refined compbinations such as (element list, value list), or 
		((element1, value1)...(elementN, valueN )) should be possible via SetPropertyForAll,
		which however does not work yet.
		'''
		
		for ItemName in ElementList:
			self[ItemName].CoreOptics.ComputationSettings.Ignore = Ignore
			
			
	#================================================
	#  FUN: SetAllNSamples [BeamlineElements]
	#================================================
	def SetAllNSamples(self,N):
		'''set the same number of manual sampling for all the optical elements''
		''' 
		for Item in self.ItemList:
			try:
				Item.ComputationSettings.NSamples = N
			except:
				pass

	def SetAllUseCustomSampling(self,x : bool):
		'''set the same number of manual sampling for all the optical elements''
		''' 
		for i, Item in enumerate(self.ItemList):
			try:
				self.ItemList[i].ComputationSettings.UseCustomSampling= x
			except:
				raise Exception
	
	def SetPropertyForAll(self, PropertyName, PropertyValue):
		for Item in self.ItemList:
			try:
				setattr(PropertyName, PropertyValue)
			except:
				pass

	#================================================
	#  FUN: GetSamplingList [BeamlineElements]
	#================================================
	def GetSamplingList(self, 
					 Orientation = None, 
					 UseCustomSampling = None,
					 Verbose = True,
					 ReturnNames  = False):

		# If not specified, I choose the orientation of the first oriented element
		# Then I return the sampling list for all the elements with that orientation (or ANY orientation)
		
		if Orientation is None:
			OrientationToCompute = self._GetFirstOrientedElement().CoreOptics.Orientation
		else:
			OrientationToCompute  = Orientation
		
		SamplingList = []
		ElementList = []
			
		for OE in self.GetElementList(Orientation = OrientationToCompute,
									 Ignore = False):
			NSamples = OE.GetNSamples(Orientation, UseCustomSampling)
			SamplingList.append(NSamples)
			ElementList.append(OE)
			
		if ReturnNames:
			NameList = [_.Name for _ in ElementList]
			return SamplingList, ElementList, NameList
		else:
			return SamplingList, ElementList			
	#================================================
	#  FUN: GetSamplingList [BeamlineElements]
	#================================================
	def GetSamplingListAuto(self, 
					 Orientation = None, 
					 Verbose = True,
					 ReturnNames  = False):
		"""
		Helper function (for debug, not used by the computation engine)
		
		Returns a list of K elements, where K is the number of itemns in
		OrientationToCompute.
		
		if K =1, then a list like  [[100, 432, 5023,...]] is returned.
		
		
		Returns a list containing the sampling used for each optical element

		Dev Notes
		---------------------
		This function has a "Manager" approach: the intelligence is contained in
		this function, and very little is demanded to the members of the 
		objects (OpticalElement).
		
		A more modern design, suggests to reverse this: implement an
		evolved intelligence in the "GetSampling" method of OpticalElement, and
		make this function just receive the output.
		To to this, I should code a "GetPropagationParent", which handles the
		case of virtual element. This function is not ready now. So I keep this design.
		
		"""
		
		# If not specified, I choose the first oriented element.
		if Orientation is None:
			OrientationToCompute = self._GetFirstOrientedElement().CoreOptics.Orientation
		else:
			OrientationToCompute  = Orientation
		
		SamplingList = []
		ElementList = []
			
		for OE in self.GetElementList(Orientation = OrientationToCompute,
									 Ignore = False):
			if OE.CoreOptics._IsAnalytic:
				NSamples = None
			else:
				NextPropagationChild = OE.GetNextPropagationChild(Orientation = OrientationToCompute)
				if NextPropagationChild  is not None:
					NSamples = OE.GetNSamples_2Body(self.Lambda, OE, NextPropagationChild)
#					NSamples = GetNSamplesTwoBody(self.Lambda, OE, NextPropagationChild)
				else:
					# there is no next element
					pass
			SamplingList.append(NSamples)
			ElementList.append(OE)
			
		if ReturnNames:
			NameList = [_.Name for _ in ElementList]
			return SamplingList, ElementList, NameList
		else:
			return SamplingList, ElementList
				 
	#================================================
	#  FUN: GetSamplingList [BeamlineElements]
	#================================================
	def GetSamplingList2(self, Orientation = None, 
					 Verbose = True):
		"""
		Helper function (for debug, not used by the computation engine)
		
		Returns a list of K elements, where K is the number of itemns in
		OrientationToCompute.
		
		if K =1, then a list like  [[100, 432, 5023,...]] is returned.
		
		
		Returns a list containing the sampling used for each optical element

		Dev Notes
		---------------------
		This function has a "Manager" approach: the intelligence is contained in
		this function, and very little is demanded to the members of the 
		objects (OpticalElement).
		
		A more modern design, suggests to reverse this: implement an
		evolved intelligence in the "GetSampling" method of OpticalElement, and
		make this function just receive the output.
		To to this, I should code a "GetPropagationParent", which handles the
		case of virtual element. This function is not ready now. So I keep this design.
		
		"""
		
		SamplingResultList = []
		NameResultList = []
		for OrientationToCompute in self.ComputationSettings.OrientationToCompute:
			SamplingList = []
			ElementList = []
			
			for OE in self.GetElementList(Orientation = OrientationToCompute,
										 Ignore = False):
				
				if OE.CoreOptics._IsAnalytic:
					NSamples = None
				else:
					NextPropagationChild = OE.GetNextPropagationChild(Orientation = OrientationToCompute)
					if NextPropagationChild  is not None:
						NSamples = OE.GetNSamples_2Body(self.Lambda, OE, NextPropagationChild)
					else:
						# there is no next element
						pass
					
				SamplingList.append(NSamples)
				ElementList.append(OE.Name)
					
			SamplingResultList.append(SamplingList)
			NameResultList.append(ElementList)
			
		return SamplingResultList, NameResultList
		
		
#		import copy
		# temporarily set the UseCustomSampling to True, if required
#		DummySelf = copy.deepcopy(self)
##		Memento = [] # variable used to store the effective value of "UseCustomSampling"
#		if ForceAutoSampling:
#			for Item in DummySelf.ItemList:
##				Memento.append(Item.ComputationSettings.UseCustomSampling)
#				Item.ComputationSettings.UseCustomSampling = False
#		
#		DummySelf.ComputeFields(oeStart = None, oeEnd = None, Dummy = True, Verbose = True)
#		NList = []
#		NameList = []
#		for i, Oe in enumerate(DummySelf.ItemList):
#			NList.append( Oe.ComputationResults.NSamples)
#			NameList.append(Oe.Name)
#			if Verbose:
#				print("%s\t%s" % ( NameList[i], str(NList[i])))

		# restore the UseCustomSampling
#		if ForceAutoSampling:
#			for i,Item in enumerate(self.ItemList):
#				Item.ComputationSettings.UseCustomSampling = Memento[i]
		return NList, NameList

	# ================================================
	#  FUN: ComputeFields
	# ================================================
	def ComputeFields(self, 
				   oeStart=None, 
				   oeEnd=None, 
				   Dummy=False, 
				   Verbose=True):
		"""
		Select the orientations and pass them individually to ComputeFieldsMediator, which is nothing else but the old
		ComputeFields.

		Parameters
		-----
		
		oeStart : Foundation.OpticalElement OR string
			Start optical element. Can be object or key
		oeEnd : Foundation.OpticalElement OR String
			End optical element. Can be object or key
		"""
		import datetime
		
		print('Computation started at:')
		Tic = time.time()
		
		#Attempt to assign by key
		if type(oeStart) is str:
			try:
				oeStart = self[oeStart]
			except:
				WiserException("OpticalElement not found", 
				   By = 'ComputeFields',
				   Args = ['oeStart'])

		if type(oeEnd) is str:
			try:
				oeEnd = self[oeEnd]
			except:
				WiserException("OpticalElement not found", 
				   By = 'ComputeFields',
				   Args = ['oeEnd'])
		
		#Check if OrientationToCompute is not empty
		try:
			if len(self.ComputationSettings.OrientationToCompute) ==0: 
				raise Exception('Error: the list Foundation.BeamlineElements.OrientationToCompute is empty.')
				return None
		except:
			_OrientationToCompute = self.ComputationSettings.OrientationToCompute
			raise WiserException("Warning, OrientationToCompute is a single value, not a list. This is a very common mistake. Even if a single orientation is used, it must be a list.")
		
		
		#Do the main loop
		for Orientation in self.ComputationSettings.OrientationToCompute:
			self.ComputeFieldsMediator(oeStart, oeEnd, Dummy, Verbose, Orientation)
		Toc = time.time()

		self._TotalComputationTimeMinutes = (Toc-Tic)/60
		print('Computation terminated at:')
		print(datetime.datetime.now())

	# ================================================
	#  FUN: ComputeFieldsMediator
	# ================================================
	def ComputeFieldsMediator(self, 
						   oeStart=None,
						    oeEnd=None,
							Dummy=False,
							Verbose=True,
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
#		if (oeStart == self.FirstItem) and (oeStart.IsSource == True):
#			try:
#				Lambda = self.FirstItem.CoreOptics.Lambda
#			except:
#				Lambda = oeStart.ComputationResults.Lambda
#		else:
#			Lambda = oeStart.ComputationResults.Lambda
		Lambda = self.MainLambda
		k = 0
		Ind = 1
		NoeList = len(oeList)
		
		# ---- Loop on optical elements
		for ioeThis, oeThis in enumerate(oeList):
#			Debug.Print(50 * '=')
			tic = time.time()
			Debug.Print('Compute Fields %d/%d' %( ioeThis+1	, NoeList), NIndent = 0, Header = True)

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
				Action = 'Element Ignored'
				Debug.print('\tAction:' + Action)
			# ----------------------------------------------
			# case:  The present element is a Wavefront, so it already has a field
			# ----------------------------------------------
			elif (isinstance(oeThis.CoreOptics, LibWiser.Optics.SourceWavefront)):
				Action = 'no Action (Field already stored in the OpticalElement)'
				Debug.print('\tAction:' + Action)
				
				PropInfo.oeLast = oeThis
				pass

			# ----------------------------------------------
			# case:  Compute the field (on this element)
			# ----------------------------------------------
			else:

				# ----------------------------------------------
				# the past element oeLast is Analitical
				# ----------------------------------------------
				# I require to transform oeThis --> Virtual(oeThis)
				if PropInfo.oeLast.CoreOptics._IsAnalytic == True:
					Action = 'Evaluating analytical function (of previous OE on THIS one)'
					Debug.print('\tAction: ' + Action, Ind)

					# Transform oeThis --> oeV (virtual optical element)
					oeV = self._MakeVirtual(oeThis, PropInfo.oeLast,
											PropInfo.TotalPath + oeThis.GetDistanceFromParent(SameOrientation=True, 
															 OnlyReference=False)) if PropInfo.N > 0 else oeThis
				 
					 
					NSamples = oeV.GetNSamples(Orientation = Orientation)
#					NSamples = GetNSamplesTwoBody(Lambda, PropInfo.oeLast, oeThis)
					
					xV, yV = oeV.GetXY(NSamples)
					# update registers

					if (xV is None) or (yV is None):
						raise WiserException('GetXY(NSamples) returned None (1)', Args = ['NSamples'])
						
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
					
					NSamples = oeThis.GetNSamples(Orientation = Orientation)
#					NSamples = GetNSamplesTwoBody(Lambda, PropInfo.oeLast, oeThis)
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
						xThis = []
						yThis = []
						oeThis.Results.Field = []
						Debug.pr('NSamples', Ind + 1)
					else:
						Debug.print('Computing field (Numeric)', Ind)
						Debug.print('source object = %s' % PropInfo.oeLast.Name, Ind )
						Debug.print('target object = %s' % oeThis.Name, Ind )
						Debug.pr('NSamples', Ind + 1)

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
				
				toc = time.time()
				ComputationTime = (toc-tic)/60
				Debug.Print('\tComputation time:\t %0.2f min'  %  ComputationTime)
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
				oeThis.Results.ComputationTime = ComputationTime
				# ----------------------------------------------
				# ITERATE TO THE NEXT Computing field => PropInfo
				# ----------------------------------------------
				PropInfo.oeLast = oeThis
				PropInfo.TotalPath = 0
				PropInfo.N = 0
			Debug.Print('END OF COMPUTATION' , NIndent = 0, Header = True)
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
	def _MakeVirtual(self, 
				  oeY: OpticalElement, 
				  oeX: OpticalElement, 
				  Distance: float ) -> OpticalElement:
		'''
		Create a virtual element from oeY with respect to oeX

		Parameters
		----
		oeY : OpticalElement
			The Optical element which WILL BECOME virtual
			
		oeX : OpticalElement
			The reference one.
			
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
	#XXX def PickOeList
	def _PickOeList(self, 
				 oeStart=None, 
				 oeEnd=None, 
				 Orientation=Optics.OPTICS_ORIENTATION.ANY,
				 Ignore = None):
		"""
		Return a list of OE contained between oeStart and oeEnd of given orientation.
		If oeStart = None, it starts from the first element.
		If oeEnd = None, it finishes up to the last element.
		
		Parameters
		-----------
		
		IgnoreValue : [False, True,None]:
			If None, does not filter for *OpticalElement.Value*
			
		Returns
		---------------------------
		OrientedOEList
		
		OEStart
		
		OEEnd
		"""

		if self.ItemList == []:
			raise WiserException("Attention! The Beamline is empty :-). Perhaps you commented something while composing it...")
		oeStart = self.FirstItem if oeStart == None else oeStart
		oeEnd = self.LastItem if oeEnd == None else oeEnd
		
		# Picking just a subportion of oeList, if required by oeStart, oeEnd
		oeList = self.GetFromTo(oeStart, oeEnd)
		oeListOriented = []
		for _ in oeList:
			DoAppend = True
			# Pass => will be added
			
			#Filters for the orientation
			#---------------------------------------------------------
			# Any Orientation value is ok
			if (Orientation == Optics.OPTICS_ORIENTATION.ANY or
				Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC):
				pass
			else: 
				# Does Orientation value match?
				if (_.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ANY or
					_.CoreOptics.Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC or
						_.CoreOptics.Orientation == Orientation):
					pass
				else:
					DoAppend = False

			#Filters for "Ignore"
			#---------------------------------------------------------
			# Any Ignore value is ok
			if Ignore == None:
				pass
			else:
				## Does Orientation value match?
				if _.ComputationSettings.Ignore == Ignore:
					pass
				else:
					DoAppend = False
					
			if DoAppend:
				oeListOriented.append(_)
				

		if len(oeListOriented) == 0:
			oeStart = None
			oeEnd = None
		else:
			oeStart = oeListOriented[0]
			oeEnd = oeListOriented[-1]

		return oeListOriented, oeStart, oeEnd

	def _GetFirstOrientedElement(self, Orientation = None):
		ElementList, oeStart, oeEnd = self._PickOeList()
		
		for _ in ElementList:
			MyOrientation = _.CoreOptics.Orientation 
			if Orientation is None: 
				if  (MyOrientation == Optics.OPTICS_ORIENTATION.VERTICAL or
									   MyOrientation == Optics.OPTICS_ORIENTATION.HORIZONTAL):
					return _
			else:
				if MyOrientation == Orientation:
					return _
		return _
			
	# ================================================
	#  FUN: _CheckIfRepeatedNames
	# ================================================		
	def _CheckIfRepeatedNames(self, Verbose = False):
		'''
		Scan across the names of the optical element to
		check if there are repeated names.
		
		Repeated names can create unexpected behavior and shall be avoided
		'''
		NameList = []
		for Item in self.ItemList:

			if Item.Name in NameList:
				repeated_name = Item.Name
				raise WiserException('''Foundation.BeamlineElements => has repeated
						 Names. The beamline elements should have different
						 names in scripting. If you want to disable this warning,
						 switch BeamlineElements.ComputationSettings.AllowRepeatedNames''',
						  Args = ['repeated_name'])
			else:
				NameList.append(Item.Name)
		if Verbose :
			print(NameList)
		return False
	# ================================================
	#  FUN: GetSubBeamline
	# ================================================		 	
	def GetSubBeamline(self,
					Orientation = Optics.OPTICS_ORIENTATION.ANY ):
		'''
		Returns a BeamlineElements object which contains only the elements
		specified by the Orientation parameter.
		
		Notice: the returned object is DIFFERENT from the current beamline object.
		If you want to access the same elements of the current Beamline object,
		use GetElementList instead
		
		'''
		ElementList = self.GetElementList(oeStart = None, 
									oeEnd = None,
									Orientation = Orientation)
		
		NewBeamline = BeamlineElements()
		NewBeamline.Append(ElementList)
		NewBeamline.RefreshPositions()
		return NewBeamline
	
	# ================================================
	#  FUN: GetSubBeamlineCopy
	# ================================================		 	
	def GetSubBeamlineCopy(self,
					Orientation = Optics.OPTICS_ORIENTATION.ANY ):
		'''
		Returns a BeamlineElements object which contains only the elements
		specified by the Orientation parameter.
		
		Notice: the returned object is DIFFERENT from the current beamline object.
		If you want to access the same elements of the current Beamline object,
		use GetElementList instead
		
		'''
		import copy
		# copy the elements
		ElementList = self.GetElementList(oeStart = None, 
									oeEnd = None,
									Orientation = Orientation)
		NewElementList = []
		for Element in ElementList:
			NewElementList.append(copy.deepcopy(Element))
			
		NewBeamline = BeamlineElements()
		NewBeamline.Append(NewElementList)
		NewBeamline.RefreshPositions()
		
		#copy the ComputationSettings
		NewBeamline.ComputationSettings = copy.deepcopy(self.ComputationSettings)
		
		return NewBeamline

#	# ================================================
#	#  FUN: GetSubBeamline
#	# ================================================		 	
#	def GetSubBeamlineCopy(self,
#					Orientation = Optics.OPTICS_ORIENTATION.ANY ):
#		'''
#		Returns a BeamlineElements object which contains only the elements
#		specified by the Orientation parameter.
#		
#		Notice: the returned object is DIFFERENT from the current beamline object.
#		If you want to access the same elements of the current Beamline object,
#		use GetElementList instead
#		
#		'''
#		import copy
#		# strategy0: copy the bl and then removes the extra elements
##		NewBeamline = copy.deepcopy(self)
##		ElementList = NewBeamline.GetElementList(oeStart = None, 
##									oeEnd = None)
##		ListOfRemovedElementsIndex = []
##		for i,Element in enumerate(ElementList):
##			if Element.CoreOptics.Orientation == Orientation:
##				pass
##			else:
##				NewBeamline.Remove(Element)
##				ListOfRemovedElementsIndex.append(i)
##				
##		return NewBeamline
##		
#	# Strategy1: create a list of copies
#		
#		
#		# init the new beamline
#		NewBeamline = BeamlineElements()
#		# Copy the elements(with specified orientation)
#		ElementList = self.GetElementList(oeStart = None, 
#											 oeEnd = None,
#											 Orientation= Orientation)
#		NewElementList = [] 
#		for Element in ElementList:
#			NewElementList.append(copy.deepcopy(Element))
#		NewBeamline.Append(NewElementList)
#		
#		# Copy the computation settings
#		NewBeamline.ComputationSettings = copy.deepcopy(self.ComputationSettings)
#		
#		return NewBeamline
#		#
#		
#			
##		# Strategy2: just use the same list of references.
###		NewElementList = ElementList
##			
##
##		NewBeamline = BeamlineElements()
##		NewBeamline.Append(NewElementList)
##		NewBeamline.RefreshPositions()
##		
##		
##		#Strategy3: copy the whole Beamline, then REMOVE the unwanted items
##		NewBeamline = copy.deepcopy(self)
#		
##		NewElementNameList = [_.Name for _ in NewElementList]
##		
##		for _ in self.GetElementList():
##			
##			Name = _.Name
##			if Name is not in NewElementNameList:
##				self.Remove(Name)
#		
		
	
	# ================================================
	#  FUN: GetElementList
	# ================================================		
	#XXX def getElementList 
	def GetElementList(self, oeStart=None,
					oeEnd=None, 
					Orientation=Optics.OPTICS_ORIENTATION.ANY,
					Ignore = None):	
		'''
		Get The list of elements between *oeStart* and *oeEnd*.
		Accepts filtering
		'''
		
		oeListOriented, oeStart, oeEnd = self._PickOeList(oeStart, oeEnd, Orientation, Ignore)
		return oeListOriented
	
	# ================================================
	#  FUN: GetElementList
	# ================================================		 
	def GetElementToPropagateList(self, oeStart=None,
					oeEnd=None, 
					Orientation=Optics.OPTICS_ORIENTATION.ANY):	
		oeListOriented, oeStart, oeEnd = self._PickOeList(oeStart, oeEnd, Orientation)
		return oeListOriented
	
	# ================================================
	#  FUN: GetOpticalPath
	# ================================================
	def GetOpticalPath(self, oeStart: OpticalElement, oeEnd: OpticalElement):
		"""
		Computes the path length between oeStart and oeEnd
		"""
		return abs(oeStart.DistanceFromSource - oeEnd.DistanceFromSource)


	# ================================================
	#  FUN: GetOpticalPath
	# ================================================
	def GetDistance(self, oeStart: OpticalElement, oeEnd: OpticalElement):
		"""
		Computes the path length between oeStart and oeEnd
		"""
		return abs(oeStart.DistanceFromSource - oeEnd.DistanceFromSource)
	
	#================================================
	#  FUN: Paint
	#================================================
	def Paint(self,hFig = 1, Length = 1 , ArrowWidth = 0.2,N=100,
		   OrientationAny = False,
		   Labels = True):
		# improve 101
		Elements = self.ItemList
		
		for Element in Elements:
			HasSameOrientation = (Element.CoreOptics.Orientation in self.ComputationSettings.OrientationToCompute)
			if OrientationAny or HasSameOrientation:
				Element.CoreOptics.Paint(hFig, Length = Length , ArrowWidth = ArrowWidth, N = N, 
							 Labels = Labels)
            
		plt.grid(True)
		plt.show()

	def PrintComputationTime(self):
		print('Computation tim: %0.2f minutes' % self.ComputationMinutes)
		
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


	# ================================================
	#	PROP: PlotIntensity [BeamlineElements]
	# ================================================
	def PlotIntensity(self,StartFigureIndex = None, Label = None, Normalization = 'int'):
		'''
		Create a list of plots each one containing the intensity on that optical element.
		'''
		
		#Loop on the elements of the beamline
		k = 0
		for i, Item in enumerate(self.ItemList):
			#Plots only if the element is of the same kind of OrientationToComupte
			#it can be a bad or good idea.

			if Item.CoreOptics.Orientation in self.ComputationSettings.OrientationToCompute:
				
				# Choose the figure index
				if StartFigureIndex is not None:
#					k+=1
					FigureIndex = StartFigureIndex +i
				else:
					FigureIndex  = None
					
				# Do the plot
				#@todo: thisfunction does strange things
#				Item.PlotIntensity(FigureIndex = FigureIndex,
#								  Label = Label, 
#								      Normalization = Normalization)
				try:
					#corrected 2021-06-23
					Item.PlotIntensity(FigureIndex = FigureIndex,
								   Label = Label,
								   Normalization = Normalization
								   )
				except:
					#old
					ToolLib.CommonPlots.IntensityAtOpticalElement(Item, 
													  FigureIndex = FigureIndex,
													  Label = Label)
					
	#================================================
	#  FUN: GenerateCode
	#================================================
	def GenerateCode(self):
		 return CGVisitor.GenerateCodeForBeamlineElements(self)			


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

	
def CheckOrientation(OpticalElement, 
					 Orientation =Optics.OPTICS_ORIENTATION.ANY,
					 CompareWith = None):
	'''
	Parameters
	------
	OpticalElement : OpticalElement
		The element of which to check the orientation
		
	Orientation : orientation
		The reference orientation
		
	CompareWith : OpticalElement
		as an altarnative to Orientation, you can specify another optical element.
	'''	
	
	try:
		Orientation = CompareWith.CoreOptics.Orientation
	except:
		pass
	
	if (Orientation == Optics.OPTICS_ORIENTATION.ANY) or (Orientation == Optics.OPTICS_ORIENTATION.ISOTROPIC):
		return True
	else:
		return (OpticalElement.CoreOptics.Orientation == Orientation)
		
#================================================
#     PositioningDirectives_UpdatePosition
#================================================
def PositioningDirectives_UpdatePosition(oeY: OpticalElement, oeX: OpticalElement):
	'''
	
		WARNING: 20210630 MMan
			in the code this function is used only once in _MakeVirtual.
			It works, but it does not seem to cover all the cases
			(for instance, the one where the reference is the Source).
			
			THERE IS ANOTHER FUNCTION: BeamlineElements
			
			
			
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
			d_pd = Foundation.PositioningDirectives(
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
			t = Foundation.BeamlineElements()
			t.Append(FocussingOe)
			t.Append(d)
			t.RefreshPositions()

			#Compute the field
			#--------------------------------------------------------------
			pass

#==========================================
# FUN: GetNSamples_OpticalElement
#==========================================
def GetNSamplesTwoBody(Lambda: float, 
					   oe0 : OpticalElement, 
					   oe1: OpticalElement) -> int:
	'''
		:param Lambda: wavelength
		:param oe0: optical element 1
		:param oe1: optical element 2
		:return: sampling
		Calculate sampling between two subsequent optical elements, according to Raimondi, Spiga, A&A (2014), eq. 12
		
		'''
	raise Exception("using this")
	if oeCurrent.ComputationSettings.UseCustomSampling == True:
		return oeCurrent.ComputationSettings.NSamples
	
	try:
		
#		z = np.linalg.norm(oe1.CoreOptics.XYCentre - oe0.CoreOptics.XYCentre)
#		L0 = oe0.CoreOptics.L
#		L1 = oe1.CoreOptics.L
#		Theta0 = oe0.CoreOptics.VersorNorm.Angle
#		Theta1 = oe1.CoreOptics.VersorNorm.Angle
#		return rm.ComputeSamplingA(Lambda, z, L0, L1, Theta0, Theta1, oe1.ComputationSettings.OversamplingFactor)
	
	
		z = oe0.ParentContainer.GetDistance(oe0,oe1)
		L0 = oe0.CoreOptics.L  # Size of element 1
		L1 = oe1.CoreOptics.L  # Size of element 2
		Theta1 = pi / 2. + oe1.CoreOptics.VersorNorm.Angle  # Grazing incidence angle
		print('=o=' * 20)
		print(oe1.Name)
		print(z)
		print(L0)
		print(L1)
		print(Theta1)
		if z==0:
			raise WiserException('''
						  ERROR, the distance between two subsequent elements is 0. 
						  This case (which may have a physical meaning), can not be treated in the present version
						  of WISER.''',
						  Args = [('oe0', oe0.Name ), ('oe1', oe1.Name),('z', z), ('L0', L0), ('L1', L1), ('Theta1', Theta1), ('N', N)  ])

		N = 4. * pi * L0 * L1 * abs(sin(Theta1)) / (Lambda * z)  # Sampling
		print('Number of points: {}'.format(int(N)))
		N = int(N) * 10
		
		return N
	except:
		oe0_name = oe0.Name
		oe1_name = oe1.Name
		raise WiserException('''Something is wrong while computing the number of samples. Check the
							   Distance between optical element (it can be 0) and/or the orientation.''',
									     'GetNSamples_OpticalElement',
										['oe0 ', 'oe1_name', 'z','L0', 'L1' ,'Theta1','N', 'Lambda'  ])
		return None

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
	
	raise Exception("using this 2")
	try:
		z = np.linalg.norm(oe1.CoreOptics.XYCentre - oe0.CoreOptics.XYCentre)  # distance between the elements
		L0 = oe0.CoreOptics.L  # Size of element 1
		L1 = oe1.CoreOptics.L  # Size of element 2
		Theta1 = pi / 2. + oe1.CoreOptics.VersorNorm.Angle  # Grazing incidence angle
		print('=o=' * 20)
		print(oe1.Name)
		print(z)
		print(L0)
		print(L1)
		print(Theta1)
		if z==0:
			raise WiserException('''
						  ERROR, the distance between two subsequent elements is 0. 
						  This case (which may have a physical meaning), can not be treated in the present version
						  of WISER.''',
						  Args = [('oe0', oe0.Name ), ('oe1', oe1.Name),('z', z), ('L0', L0), ('L1', L1), ('Theta1', Theta1), ('N', N)  ])

		N = 4. * pi * L0 * L1 * abs(sin(Theta1)) / (Lambda * z)  # Sampling
		print('Number of points: {}'.format(int(N)))
		N = int(N)
		return N
	except:
		oe0_name = oe0.Name
		oe1_name = oe1.Name
		raise WiserException('''Something is wrong while computing the number of samples. Check the
							   Distance between optical element (it can be 0) and/or the orientation.''',
									     'GetNSamples_OpticalElement',
										['oe0 ', 'oe1_name', 'z','L0', 'L1' ,'Theta1','N', 'Lambda'  ])
		return None
									      

#	z = np.linalg.norm(oe1.CoreOptics.XYCentre - oe0.CoreOptics.XYCentre)  # distance between the elements
#	L0 = oe0.CoreOptics.L  # Size of element 1
#	L1 = oe1.CoreOptics.L  # Size of element 2
#	Theta1 = pi / 2. + oe1.CoreOptics.VersorNorm.Angle  # Grazing incidence angle
#
#	if z==0:
#		raise WiserException('''
#					  ERROR, the distance between two subsequent elements is 0. 
#					  This case (which may have a physical meaning), can not be treated in the present version
#					  of WISER.''',
#					  Args = [('oe0', oe0.Name ), ('oe1', oe1.Name),('z', z), ('L0', L0), ('L1', L1), ('Theta1', Theta1), ('N', N)  ])
#
#	N = 4. * pi * L0 * L1 * abs(sin(Theta1)) / (Lambda * z)  # Sampling
#	print('Number of points: {}'.format(int(N)))
#	N = int(N)
#	return N

									   	


# ================================================
#  FUN: FocusSweep
# ================================================
def FocusSweep(oeFocussing, 
			   DefocusList, 
			   DetectorSize=50e-6, 
			   		  StartAtNominalFocus = True,
			  Distance = 0,
			   AngleInNominal=np.deg2rad(90)):
	''' 
	EXTENSIVE FOCUS SCAN
	Created for computing the field on a detector placed nearby the focal plane of
	oeFocussing. It performs an EXTENSIVE scan by computing the field at
	the distances specified in DefocusList
	
	The function assumes that a field is olready computed on oeFocussing.
	If 
	
	Parameters
	------
	oeFocussing: 		
		Foundation.OpticalElement. It is the optical element that focusses radiation
	
	DefocusList: array like
		The list of the positions from the *nominal focus* at which the detector is place. 
		
	AngleInNominal : float (rad)
		Grazing angle of the detector. Default is pi/2. Normally not used.
		
		Example [1,2,3]

	Return
	--------
	ResultList : a list of OpticalElement._ClassComputationResults. The
		_electromagnetic field_ is here.

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

	if StartAtNominalFocus:
		d_pd = PositioningDirectives(
			ReferTo='upstream',
			PlaceWhat='centre',
			PlaceWhere='downstream focus',
			Distance=0)
	else:
		raise Warning("Gaurda che non funziona, anche se non so perché... correggere!")
		d_pd = PositioningDirectives(
			ReferTo ='upstream',
			PlaceWhat ='centre',
			PlaceWhere = 'centre',
			Distance = Distance)
	
	d = OpticalElement(
		d_k,
		PositioningDirectives=d_pd,
		Name='detector')

	oeFocussing._IsSource = True  # MUSTBE!
	oeFocussing.PositioningDirectives.ReferTo = 'locked'
	oeFocussing.CoreOptics.Orientation = Optics.OPTICS_ORIENTATION.ANY
	NSamples = oeFocussing.ComputationResults.NSamples
	if NSamples is None:
		raise Exception("oeFocussing -> NSamples = <None> in FocusSweep. oeFocussing.Name = <%s>" % oeFocussing.Name)
	
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
		BestHew = None
		BestDefocus = None
		
	for (i, Distance) in enumerate(DistanceList):
		# I set the Position the detector at distance = Distance
		# ------------------------------------------------------------
		d.PositioningDirectives.Distance = Distance
		t.RefreshPositions()
		t.ComputeFields(Verbose=False)

		# Debug.print('%i/%i) dz = %0.2f mm' %(i,N, Distance *1e3),2)

		More.Dist[i] = np.linalg.norm(oeFocussing.CoreOptics.XYF2 - d.CoreOptics.XYCentre)
		More.XYCentre[i] = d.CoreOptics.XYCentre

		# Debug.print(oeFocussing.CoreOptics.GetPositionString(1))
		# print(d.CoreOptics.XYCentre)
		# Debug.print(d.CoreOptics.GetPositionString(1))

		# Preparing and storing the results
		# -----------------------------------------------------------
		DeltaS = np.mean(np.diff(d.Results.S))  # Sample spacing on the detector

		ResultList[i] = copy.deepcopy(d.ComputationResults)
#		I = abs(d.ComputationResults.Field) ** 2
		A2 = abs(d.ComputationResults.Field) ** 2
		I = A2 / max(A2) # Normalized intensity
		(Hew, Centre) = rm.HalfEnergyWidth_1d(I, Step=DeltaS, UseCentreOfMass = False) # FocusSweep
		try:
			(a, x0, Sigma) = tl.FitGaussian1d(I, d.ComputationResults.S)
		except:
			(a, x0, Sigma) = [None, None, None]
		HewList[i] = Hew
		SigmaList[i] = Sigma

	# Analyze the obtained caustics (minumum value, etc)
	#=============================================================
	# Find minimum of HEW over Hew Plot
	#=============================================================
	from scipy.interpolate import UnivariateSpline
	IndexBest = np.argmin(HewList)
	x = ToolLib.GetAround(DefocusList, IndexBest, 2)
	y = ToolLib.GetAround(HewList, IndexBest, 2)
	
	
	NN = len(x)
	if NN >3:
		try:
			Interpolant = UnivariateSpline(x, y, s = len(x))
			xQuery = np.linspace(x[0], x[-1], 100)
			yQuery =  Interpolant(xQuery)
			_ = np.argmin(yQuery)
			More.BestHew = yQuery[_]
			More.BestDefocus = xQuery[_]	
		except:
			raise Exception("""Error in Foundation.FocusSweep, command 'UnivariateSpline(x,y,s)\n. Length = %d. Try
					  to increase the search range defined by DefocusList.""" % NN)
	else:
		try:
			More.BestHew = HewList[IndexBest]
			More.BestDefocus = DefocusList[IndexBest]
		except:
			raise Exception('sticazzi')
	#@todo
	

	#=============================================================
	
	IntensityList =[]
	for _ in ResultList:
		IntensityList.append(_.Intensity) 
	More.IntensityList = IntensityList 	
	More.DefocusList = DefocusList
	return (ResultList, HewList, SigmaList, More)
# ================================================
#  FUN: FocusFind
# ================================================
def FocusFind(oeFocussing,	 
			     DefocusRange = (-10e-3, 10e-3),
			  DetectorSize=200e-6,
			  MaxIter = 31,
			  XTolerance = 1e-4,
			  StartAtNominalFocus = True,
			  Distance = 0,
			  AngleInNominal=np.deg2rad(90)):
	'''
	OPTIMIZED FOCAL SCAN
	Find the best focus. Similar to FocusSweep, except that it does not provide the
	full sampling of the DefocusRange, but it uses an optimization algorithms to find
	the best focus as fast as possible.

	Faster, perhaps less fancy.
	
	If *StartAtNominalFocus* is True (default),
	
	If *StartAtNominalFocus* is False, the search starts at distance *Distance* from *oeFocussing*.
	

	For automation purposes, when producing publication-quality plots,
	it could be a nice idea to use feed FocusSweep with the
	results of FocusFind.

	Parameters
	------
	oeFocussing : OpticalElement
		optical element that focusses radiation. The detector is **automatically** placed in the focus of
		``oeFocussing``. This is don by hardcoding the positioning directive *place at downstream focus*,
		which must be implemented.
		 
	DefocusList : array like
		List of defocus distances
		
	StartAtNominalFocus : bool
		If **true**,  the search starts at the nominal downstream focus
		of *oeFocussing*. **The positioning directive** "place at downstream focus must be implemented".
		If **False**, the search starts at distance *Distance* from *oeFocussing*.
	
	Distance : float
		Used only with *StartAtNominalFocus = False*.
		
		

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
	- S : 1d array(real) :
		Transversal coordinate at the best focus (detector)

	- OptResult : OptimizationResult object
				Contains the results of the optimization

	Notes
	--------
	-In the test I did, convergence was reached within few (5-7) iterations,
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
	
	if StartAtNominalFocus:
		d_pd = PositioningDirectives(
			ReferTo='upstream',
			PlaceWhat='centre',
			PlaceWhere='downstream focus',
			Distance=0)
	else:
		d_pd = PositioningDirectives(
			ReferTo ='upstream',
			PlaceWhat ='centre',
			PlaceWhere = 'centre',
			Distance = Distance)
		
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
								  args=(d,t), method='brent', tol=XTolerance, options={'maxiter': MaxIter, 'xtol' : XTolerance})

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
	Results.S = d.ComputationData.S
#	Results.BestCompudationDate = d.ComputationData

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





#%% Corrected Sampling for items with different orientation.


#%% Fine
