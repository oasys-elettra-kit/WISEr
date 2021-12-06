# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 23:11:36 2020

@author: Mike - Manfredda
"""

import LibWiser.Scrubs as Scrubs
import LibWiser.Units as Units
import numpy as np
SNIPPET_COMMON_IMPORT = '''from LibWiser.EasyGo import* \n'''


#===========================================================================
# 	CLASS: Memento
#===========================================================================
'''
Design notes:
------------
Context: there is a main object (call base object), of which you want to
- store the ARGUMENTS used to create it
- store some relevant ATTRIBUTES. The attributes could refer to the BASE OBJECT itself, or to some sub-object.
Example:
Object (arg1, arg2)
 .attr1
 .attr2
 .subobj1
   ..subattr1
etc

Dealing with arg1,arg2 and attr1, attr2 is easy.
Dealing with subobj1 can be done in two ways:
	1) subobj1 has written inside the attributes that has to export 
	2) the attributes of SubObj1 which must be stored are specified somewhere
		either in BASE OBJECT, or in the function which BASE OBJECT calls to
		generate the code (for example, with some kind of user input)
		
	1) can sound very elegant => we can instruct the code to save ALL the SubAttributes.
		This nicely works with DataContainer
		
	2) Is less elegant, but easier to implement.


	The ideal way would be to merge the 2....
	
	
'''
class CodeGenerator_NEW_WIP():
	
	
#	def __init__(self, Target, Arguments, Attributes, ClassName = None):
#		self._TargetObject = Target # object of which store data
#		self._ArgumentList = Arguments # arguments necessary to create the object
#		self._AttributeList = Attributes # other attributes, to fill once the object is created.
#		
#		self._ShortClassName = type(Target).__name__  #example:Foundation.PositioningDirectives => PositioningDirectives
#		self._LongClassName = type(Target).__module__ + '.' + ShortClassName
#		
	def __init__(self, ListOfAttributeNames = []):
		self._CodeGeneratorAttributes = ListOfAttributeNames
		self._AttributeList = ListOfAttributeNames
		self._Coccode =1
		
#		RootAttrName = Scrubs.MakeValidPythonName(RootAttrName) if RootAttrName is not None else ShortClassName
		
	'''
	If this class is inherited by a parent class, it provides the parent class the GenerateCode method,
	which automatize the generation of initialization code.
	
	For doing so, GenerateCode parses the attributes contained in _InitCodeGeneratorAttributes
	
	For each attribute in the list, if the GenerateCode is available (i.e. the attribute is a class), then
	GenerateCodeis called. Else, the variable is converted to a string in the smartest way possible:
		- (that is, using the __str__ function, at this stage of the development :-)
	'''
	


	@classmethod
	def __ObjectHasGenerateCode(x):
		'''
		Return True if 'Object' supports code generation.
		
		Notes
		-------------
		Orifinally the code snippet was:
			if hasattr(ArgumentValue,'GenerateCode'):
				s = ArgumentValue.GenerateCode(KeyName, N + 1)	
		this can change in future.	
		
		Parameters
		----------
		x : must be an object
		
		Return
		-------
		str : code
			The generated 
		'''

		if hasattr(x,'GenerateCode'):
			return True	

	@classmethod
	def __ObjectGenerateCode(x, RootAttrName =None, N=0):
		'''
		Call the method for code generation
		'''
		return x.GenerateCode
	#==============================================================================
	#  FUN: FormatAttributeToString
	#==============================================================================	
	@classmethod
	def __FormatAttributeIntoString(AttrName, AttrValue, NIndentation = 0, FormatStyle = 0 ):
		'''
		Format the given attribute as a string
		
		Parameters
		------
		x : {str, float32, int, object}
		
			Value of the attribute to convert to string.
			
		FormatStyle : int
		
		- 0 => format as python code, example 'height = 1.5'
		
		'''
		N = NIndentation
		
		if Memento.__ObjectHasGenerateCode(AttrValue):
			StrOut = Memento.__ObjectGenerateCode(AttrValue, AttrName, N + 1)
			
		#---- IS THE ARGUMENT A BASE TYP? (float, string, integer, list,numpy array)
		else:
			
			'''================================================
			|| HOW TO FORMAT THE DIFFERENT KIND OF ATTRIBUTES
			||
			==================================================='''
			
			# example:
			# >>> PlaceWhere = 'centre'
			# >>> Distance = 1.2
			#etc...
			
			#=================================
			# str
			#=================================
			if type(AttrValue) == str:
				StrAttrValue = str(AttrValue)
			#=================================
			# None
			#=================================
			elif AttrValue is None:
				StrAttrValue = None
			#=================================
			# Float
			#=================================
			elif type(AttrValue) is float:
				StrAttrValue = Units.SmartFormatter((AttrValue, {'prefix': False, 'digits': 6}))
				StrAttrValue = '%0.6e' % AttrValue
			#=================================
			# INT
			#=================================
			elif type(AttrValue) is int:
				StrAttrValue = AttrValue
			#=================================
			# LIST
			#=================================				
			elif type(AttrValue) is list:
				StrAttrValue = str(AttrValue)
			#=================================
			# Numpy Array
			#=================================				
			elif type(AttrValue ) is np.ndarray:
				StrAttrValue = str(AttrValue)
				StrAttrValue = StrAttrValue.replace(' ', ',') 
			#=================================
			# UNDEFINED
			#=================================					
			else:
				StrAttrValue = str(AttrValue)
				
			if FormatStyle == 1:
				StrOut = (N+1) * '\t' + "%s = '%s'" % (KeyName, StrAttrValue )
			else:
				raise WiserException('Error: you tried to use a value of FormatStyle which is not implemented yet. Solution: this should not happen :-=')

		return StrOut	
	#==============================================================================
	#  FUN: GetAttrNameAndAliasName
	#==============================================================================	
	def _GetAliasAndKeyword(x):
		'''
		The "Alias" is how a certain attribute is stored in a class.
		The "Keyword" is the argument name that appears in the __init__ function.
		
		It is a good habit that the two coincide, BUT for older classes this can be no true.
		
		Parameters
		---------
		x : str|tuple
		
			If x is a string, then x is both _Keyword_ and _Alias_
			
			If x is a tuple, then x = (Alias, Keyword))
	
		Return
		----------
		(Alias, Keyword) : tuple
	
		'''
		if type(x) is tuple:
			AliasName = x[0]
			KeyName = x[1]
		else:
			KeyName = x
			AliasName = x
		return AliasName, KeyName
	
	
	
	def __GenerateCodeFromListOfAttributes(self, AttributeList,
										FirstString = '',
										RepatedString = '',
										 LastString = '', NIndentation = 0, Separator = '\n'):
		'''
		Return:
			FirstString +
				RepatedString + Attr1=Val1 + Separator +
				RepatedString + Attr2=Val2 + Separator + 
				RepatedString + Attr3=Val3 + Separator + 
			EndString
			
		For example: 
			FirstString = "MirrorElliptical("
			RepeatedString = ''
			EndString = ")"
		>>>
		MirrorElliptical( f1 =5, f2 = 100)
		
		Example2:
			FirstString = ""
			RepeatedString = '_.'
			EndString = ""			
		>>>
		_.Length = 4
		_.Lambda = 10
		
		'''
		StrList = list()
		for Argument in AttributeList:
			
			# GET THE Keyword and the Internal name(Alias) of the attribute
			AliasName, KeyName = Memento._GetAliasAndKeyword(Argument)
			try:
				# Get the value of the attribute that we want to store
				Value = getattr(self._TargetObject, AliasName) 
			except:
				raise Exception('''
					Error in InitCodeGenerator.GenerateCode applied to %s.
					 Attribute Name '%s' not found. Attribute Alias:%s.
					 How to solve: revise LibWiser code. ''' 
					 %  ( str(s), KeyName, AliasName))
				return s
			# Convert the value to string.
			StrValue = Memento.__FormatAttributeIntoString(KeyValue, Value, N) #=> example "x=1"
			#Append the string to the chain 
			StrList.append(StrValue)
		
		return FirstString + Separator.join(StrList) + LastString
	
		
				
	#===========================================================================
	# 	FUN: GenerateCode
	#===========================================================================	
	def _GenerateCodeForInitEnsemble(self, OwnerObjectName =None, NIndentation = 0):
		'''
		Valid for any kind of OpticalElement
		
		
		Paramters
		------
		OwnerObjectName : str
			Is the name of the OpticalElement, eg "OwnerObjectName = OpticalElement(....)"
		'''
		ShortClassName = type(self).__name__  #example:Foundation.PositioningDirectives => PositioningDirectives
		LongClassName = type(self).__module__ + '.' + ShortClassName
		OwnerObjectName = Scrubs.MakeValidPythonName(OwnerObjectName) if OwnerObjectName is not None else ShortClassName
		AttributeList = self._ArgumentList
		FirstString = NIndentation*'\t' + "%s =%s(" %(OwnerObjectName, LongClassName)
		RepeatedString = '' 
		LastString = ")"
		Separator = ',\n'

		s = self.__GenerateCodeFromListOfAttributes(AttributeList, FirstString, RepeatedString, LastString, NIndentation, Separator)
				
#		if N==0:
#			s = list(s)
#			s.pop(-1)
#			s.pop(-1)
#			s= ''.join(s)
#		return s
	
	def _GenerateCodeForAttributeEnsemble(self, OwnerObjectName = '_'):
		'''
		'''
		
		AttributeList = self._AttributeList
		FirstString = '' 
		RepeatedString = "OwnerObjectName" + "."
		LastString = ''
		Separator = '\n'

		s = self.__GenerateCodeFromListOfAttributes(AttributeList, NIndentation = NIndentation, Separator = Separator)
		return s  
		
	
#===========================================================================
# 	CLASS: CodeGenerator
#===========================================================================
class CodeGenerator():
	'''
	If this class is inherited by a parent class, it provides the parent class the GenerateCode method,
	which automatize the generation of initialization code.
	
	For doing so, GenerateCode parses the attributes contained in _InitCodeGeneratorAttributes
	
	For each attribute in the list, if the GenerateCode is available (i.e. the attribute is a class), then
	GenerateCodeis called. Else, the variable is converted to a string in the smartest way possible:
		- (that is, using the __str__ function, at this stage of the development :-)
	'''
	
	def __init__(self, ListOfAttributeNames = []):
		self._CodeGeneratorAttributes = ListOfAttributeNames
		self._Coccode =1
		
	#==============================================================================
	#  FUN: GetAttrNameAndAliasName
	#==============================================================================	
	def _GetAttrNameAndAliasName(x):
		'''
		Handles the fact that, in certain cases, the name of the variable (stored in the class) and 
		the name of the parameter used in the init function are different. This -up to now- happens
		only with CoreOptics/CoreOpticsElement... but has to be handled :-)
	
		AttrName -> The name of the attribute 
		AliasName -> The name that appears in __init__(...)
	
		'''
		if type(x) is tuple:
			AttrName = x[0]
			AliasName = x[1]
		else:
			AttrName = x
			AliasName = x
		return AttrName, AliasName
	#===========================================================================
	# 	FUN: GenerateCode
	#===========================================================================	
	def GenerateCode(self, RootAttrName =None, N=0):
		'''
		Valid for any kind of OpticalElement
		
		
		Paramters
		------
		RootAttrName : str
			Is the name of the OpticalElement, eg "RootAttrName = OpticalElement(....)"
		'''
		ShortClassName = type(self).__name__  #example:Foundation.PositioningDirectives => PositioningDirectives
		LongClassName = type(self).__module__ + '.' + ShortClassName
		RootAttrName = Scrubs.MakeValidPythonName(RootAttrName) if RootAttrName is not None else ShortClassName
		
		# Writes the line (e.g.)
		# PositioningDirectives = Foundation.PositioningDirectives(\n
		s = N*'\t' + "%s =%s(" %(RootAttrName, LongClassName)
		
		for AttrName in self._CodeGeneratorAttributes:
			
			AttrName, AliasName = CodeGenerator._GetAttrNameAndAliasName(AttrName)
			try:
				Attr = getattr(self,AttrName) 
				# self is the parent object, which is expected to contain the attributes
				# that we want to store.
			except:
				raise Exception('''
					Error in InitCodeGenerator.GenerateCode applied to %s.
					 Attribute Name '%s' not found. Attribute Alias:%s.
					 How to solve: revise LibWiser code. ''' 
					 %  ( str(s), AttrName, AliasName))
				return s
					
			if hasattr(Attr,'GenerateCode'):
# 					s+= (N+1) * '\t' + "%s = %s" % (RootAttrName, Attr.GenerateCode)
				s+= Attr.GenerateCode(AliasName, N+1)	
			else:
				
				'''================================================
				|| HOW TO FORMAT THE DIFFERENT KIND OF ATTRIBUTES
				||
				==================================================='''
				
				# example:
				# PlaceWhere = 'centre'
				# Distance = 1.2
				#etc...
				
				#=================================
				# Attr
				#=================================
				if type(Attr) == str:
					AttrVal = str(Attr)
					s+= (N+1) * '\t' + "%s = '%s',\n" % (AliasName, AttrVal)
				#=================================
				# None
				#=================================
				elif Attr is None:
					AttrVal = None
					s+= (N+1) * '\t' + "%s = %s,\n" % (AliasName, AttrVal)
					
				#=================================
				# Float
				#=================================
				elif type(Attr) is float:
					AttrVal = Units.SmartFormatter((Attr, {'prefix': False, 'digits': 6}))
					AttrVal = '%0.6e' % Attr
					s+= (N+1) * '\t' + "%s = %s,\n" % (AliasName, AttrVal)
				#=================================
				# INT
				#=================================
				elif type(Attr) is int:
					AttrVal = Attr
					s+= (N+1) * '\t' + "%s = %d,\n" % (AliasName, AttrVal)
				#=================================
				# LIST
				#=================================				
				elif type(Attr) is list:
					AttrVal = str(Attr)
					s+= (N+1) * '\t' + "%s = %d,\n" % (AliasName, AttrVal)
				#=================================
				# Numpy Array
				#=================================				
				elif type(Attr ) is np.ndarray:
					AttrVal = str(Attr)
					AttrVal = AttrVal.replace(' ', ',') 
					s+= (N+1) * '\t' + "%s = %d,\n" % (AliasName, AttrVal)

				#=================================
				# UNDEFINED
				#=================================					
				else:
					AttrVal = str(Attr)
					s+= (N+1) * '\t' + "%s = %s,\n" % (AliasName, AttrVal)
						

		s+= N*'\t' + '),\n'
		if N==0:
			s = list(s)
			s.pop(-1)
			s.pop(-1)
			s= ''.join(s)
		return s
#%%===================================================
#	FUN: GenerateCodeForBeamlineElements		
#%====================================================
def GenerateCodeForBeamlineElements(Beamline):
	CodeStack =[]
	# Get the list of the elements, in a suitable python format and
	# convert it to a STRING (that can be executed)
	ItemNameList = Beamline.ItemNameList
	ItemNameList = [ Scrubs.MakeValidPythonName(_) for _ in ItemNameList]
	ItemNameListString = str(ItemNameList).replace("'","") # remove the '
	
	BeamlineName = Beamline.Name
	
	BeamlineName = BeamlineName  if  Scrubs.IsValidPythonName(BeamlineName) else 'WiserBeamline'
	
	for Item in Beamline.ItemList:
#		MyName = Scrubs.MakeValidPythonName(Item.Name)
		CodeStack.append(Item.GenerateCode(Item.Name))
	
	
	CodeStack.append('%s = BeamlineElements(%s)' %(BeamlineName, ItemNameListString))
	CodeStack.append('%s.RefreshPositions()' % BeamlineName)
	CodeBuffer = '\n'.join(CodeStack)
	
	#Prepend Libraries
	
	CodeBuffer = SNIPPET_COMMON_IMPORT + CodeBuffer
	return CodeBuffer
			