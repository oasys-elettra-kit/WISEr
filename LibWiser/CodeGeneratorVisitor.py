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
			