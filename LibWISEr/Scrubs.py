# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 16:52:40 2020

Still to define if it will be kept

@author: Mike - Manfredda
"""



#==============================================================================
#  Class: DataContainer
#==============================================================================
class DataContainer():
	'''
	DataContainer class is a struct-like object conceived for easy-to-use data
	storage. It is designed with user-friendliness in mind rather than performance.
	So it is more suitable for gathering many light-wight data rather than heavy-weight
	ones.

	See Also
	-----
	The function will have remarking ramifications in the development of WISErLab plotting
	and data storage tools.

	Example 1
	-----
	>>> D = DataContainer()
	D.Name = 'lambda'
	D.Value = 5e-9
	D.Unit = 'm'
	print(D)

	Example 2
	-----
	>>> D = DataContainer(Name = 'lambda', Value = 5e-9, Unit = 'm')
	print(D)

	'''
	#==============================
	#  FUN: __init__
	#==============================
	def __init__(self, **kwargs):

		Items = list( kwargs.items())

		#Loop on Parameter list
		for Item in Items:
			setattr(self,Item[0], Item[1]) # e.g. ParameterName = ParameterValue

	#==============================
	#  FUN: __repr__
	#==============================
	def __repr__(self):
		AttrStrList, AttrStrObj = ListAttr(self, ReturnObject = True)

		Str = str(type(self)) + '\n'
		for i,AttrStr in enumerate(AttrStrList):
			Str = Str + AttrStr + ':\t' + str(AttrStrObj[i]) + '\n'

		return Str
	#==============================
	#  FUN: __str__
	#==============================
	def __str__(self):
		return __repr__(self)

	pass
a = DataContainer(x=1)
#==============================================================================
#  FUN: ListAttributes
#==============================================================================
def ListAttr(x, TypeList = None, Preset = None, ReturnObject = False):
	'''

    Listra gli attributi di un oggetto (oggetto, classe, istanza, whatever)
    restituiendo l'elenco dei nomi e degli oggetti.,

    Type : serve per filtrare un tipo specifico.

    Parameters
    ------------------------
    x : whatever
        Can be any kind of python object. So for instance it can be either a TangoDevice object or a TangoDevice.Tango object

    TypeList : list
        List of type to include in the result list. Examples:
			*int*
			*[int]*
			*[int, float]*
			*[numpy.ndarray, int, str]*

		PresetTypeList : string
			Experimental: defines sets of commonly used types. The behavior oh this parameter
			is entirely defined within the code of the function. Currently implemented values:
				- 'math' : corresponds to TypeList = [int, float, numpy.ndarray]
				- 'mathstr' : corresponds to TypeList = [int, float, numpy.ndarray, str]

			Preset type are appended to TypeList.

		Note
		-----
		If one wants to implement recursive search... still to be defined
	'''
	from numpy import ndarray
	Presets = {'math' :[int, float, ndarray],
					'math' :[int, float, str, ndarray]}

	strAttr = [iAttr for iAttr in dir(x) if not callable(iAttr) and not iAttr.startswith("__")]
	if ReturnObject:
		objAttr = [getattr(x,iAttr) for iAttr in strAttr]
	else:
		objAttr = None
	strAttrOut  = []
	objAttrOut  = []

	if Preset is not None:
		try:
			TypeList = Presets[Preset]
		except:
			pass

	# If Type is specified, it filters...
	if TypeList is not None:
     # force cast to list if not...
		TypeList = TypeList if type(TypeList)== list else [TypeList]
        # seleziona solo i tipi di TypeList
		for i, Obj in enumerate(objAttr):
			if any([type(Obj) == Type for Type in TypeList]):
				strAttrOut.append(strAttr[i])
				if ReturnObject:
					objAttrOut.append(objAttr[i])
	# Does not use filtering if not.
	else:

			strAttrOut = strAttr
			objAttrOut = objAttr

	if ReturnObject:
		return strAttrOut, objAttrOut
	else:
		return strAttrOut

#==============================================================================
#  FUN: ListAttributes
#==============================================================================
def ListAttrRecursive(x, TypeList = None, Preset = None,
					  RecursionTypeList = type, RecursionDepth = 3,
					  Sep = '/'):
	'''
	Magnificient and brilliant function that recursively lists the attributes of an object,
	inspecting also the child object whose type is specified in the RecursionTypeList.

	The function was designed in order to use classes as data container, and subsequently
	to use data container together with WISErLab functions for Saving HDF5 files.

	This is a typical example.
	>>>
		class DataCont():
			pass

		Pippo = DataCont()
		Pippo.x = 12
		Pippo.y = 120
		Pippo.w=DataCont()
		Pippo.w.ww = DataCont()
		Pippo.w.info = 'ciao'
		Pippo.w.ww.xx =  555

		a,b = ListAttrRecursive(Pippo, TypeList = None, Preset = None,   RecursionTypeList = DataCont, RecursionDepth = 3)

		print(a)


	'''

	# Force cast of data type
	if type(RecursionTypeList) is not list:
		RecursionTypeList = [RecursionTypeList]

	if type(TypeList) is not list:
		TypeList = TypeList

	AttrStr0, AttrObj0 = ListAttr(x, TypeList, Preset, True)

	for i, Obj in enumerate(AttrObj0):
		Str = AttrStr0[i]
		if any([type(Obj) == Type for Type in RecursionTypeList ]):

			AttrStr1, AttrObj1 = ListAttrRecursive(Obj, TypeList, Preset, RecursionTypeList)
			# pre-pend DataStr to each AttrStr1
			AttrStr1 = [Str + Sep + _ for _ in AttrStr1] # concatenate string
			AttrStr0 = AttrStr0 + AttrStr1  # append to list
			AttrObj0 = AttrObj0 + AttrObj1  # append to list

			del(AttrStr0[i])
			del(AttrObj0[i])

#
#	for i, DataObj in enumerate(DataAttrObj):
#		DataStr = DataAttrStr[i]
#		AttrStr1, AttrObj1 = ListAttr(DataObj, TypeList, Preset, ReturnObject = True)

	return AttrStr0, AttrObj0
	#force to list



#==============================================================================
#  FUN: ListClassProps
#==============================================================================
def ListClassProps(myClass, strOwnerClass = ''):
    strAttr = [iAttr for iAttr in dir(myClass) if not callable(iAttr) and not iAttr.startswith("__")]
    objAttr = [getattr(myClass,iAttr) for iAttr in strAttr]
    return strAttr, objAttr

#==============================================================================
#  FUN: ListClassPropsStr
#==============================================================================
def ListClassPropsStr(myClass, strOwnerClass = ''):
    strAttr = [iAttr for iAttr in dir(myClass) if not callable(iAttr) and not iAttr.startswith("__")]
    # objAttr = [getattr(myClass,iAttr) for iAttr in strAttr]
    return strAttr

#==============================================================================
#  FUN: ListClassObjects
#==============================================================================
def ListClassObjects(myClass, strOwnerClass = ''):
    strAttr = [iAttr for iAttr in dir(myClass) if not callable(iAttr) and not iAttr.startswith("__")]
    objAttr = [getattr(myClass,iAttr) for iAttr in strAttr]
    return objAttr