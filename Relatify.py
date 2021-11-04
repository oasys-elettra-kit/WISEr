# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 00:10:35 2021

@author: Mike
"""

#===========================================================================
# 	CLASS: TreeItem
#===========================================================================
class TreeItem(object):
	''' Protected attributes = Friend attributes.
	Friend class is Tree
	'''
	def __init__(self):
		self.Parents = [] 
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
	
		
	# ================================================
	#	PROP: UpstreamItemList
	# ================================================
	@property
	def UpstreamItemList(self):
		oeThis = self
		ItemList = []

		for Parent in self.Parents:
			while oeThis.Parents != []:
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
		
class Item(Foundation.TreeItem):
	pass


class UnionItem(Foundation.TreeItem):
	
	def __init__(self, Parent1, Parent2):
		
		self._Parent1 = Parent1
		self._Parent2 = Parent2
		
		
	@property
	def Parent1(self):
		return self._Parent1
	@Parent1.setter
	def Parent1(self,x):
		self._Parent1 =x
		
	@property
	def Parent2(self):
		return self._Parent2
	@Parent2.setter
	def Parent2(self,x):
		self._Parent2 =x
		
	@property
	def Parents(self):
		return [self.Parent1, self.Parent2]
	