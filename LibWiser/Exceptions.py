# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 11:18:22 2021

@author: Mike - Manfredda
"""
import warnings


import warnings

def RaiseWarning(w):
	'''
	Raise a warning.
	
	w can be either a Warning object or a string.
	If w is a string, the Warning(w) object is created.
	'''
	
	if type(w) is str:
		w = Warning(w)
	try:
		warnings.warn(w)
	except:
		raise Exception("Error while raising a warning (yep, it is ironic, don't you think0?")
	
def PrintValues(Message = 'VariableValues', Args = []):
	import inspect
	'''
	
	Parameters
	------
	Mssage : Str
	
		message to display
		
	Args : List of Tuples
	
		List of two-element tuples in the form [(name1, value1), (name2, value2),...]
		used to display more info.
	'''
	
	
	
	ExtraMsg = []
	
	# I have only variable names: ['a', 'b', 'c']
	if len(Args) > 0 :
		if type(Args[0]) is not tuple:
			Frame = inspect.currentframe()
			CallerLocals = Frame.f_back.f_locals
		
		for _ in Args:
			try:
				Label = _
				ValueStr =  str(CallerLocals[_])  
				ExtraMsg.append('%s: %s' % (Label, ValueStr))
			except:
				ExtraMsg.append('%s: Not Found' % Label)
	# I have variable names and their labels
	else:
		for _ in Args:
			try:
				ExtraMsg.append('%s: %s' % (_[0], str(_[1])))
			except:
				pass
	message = '\n'.join(ExtraMsg)
	
	print(message)
			

class SmartException(Exception):
	
	def __init__(self, Message = 'A generic Errour Occurred', By =None, Args = []):
		import inspect
		'''
		
		Parameters
		------
		Mssage : Str
		
			message to display
			
		Args : List of Tuples
		
			List of two-element tuples in the form [(name1, value1), (name2, value2),...]
			used to display more info.
		'''
		
		self._Message = Message
		self.Args = Args
		
		
		ExtraMsg = []
		
		# I have only variable names: ['a', 'b', 'c']
		if len(Args) > 0 :
			if type(Args[0]) is not tuple:
				Frame = inspect.currentframe()
				CallerLocals = Frame.f_back.f_locals
			
			for _ in Args:
				try:
					Label = _
					ValueStr =  str(CallerLocals[_])  
					ExtraMsg.append('%s: %s' % (Label, ValueStr))
				except:
					ExtraMsg.append('%s: Not Found' % Label)
		# I have variable names and their labels
		else:
			for _ in Args:
				try:
					ExtraMsg.append('%s: %s' % (_[0], str(_[1])))
				except:
					pass
		message = Message + '\n' + '\n'.join(ExtraMsg)
		
		
		if By is not None:
			message += '\nGenerated by: %s' % By
			
		self.message = message
		super().__init__(self.message)

WiserException = SmartException

class BeamlineElementNotFoundError(SmartException):
	def __init__(self, **kwargs):
		self.Message = '''Beamline Element not found while using a key.
						Example: Beamline['source'] returned an error because
						'source' is not a valid key.
						Solution: check the key value, or use try...except
						'''
		super().__init__(self.Message, **kwargs  )

class MissingParameterError(WiserException):
	def __init__(self,  By = None, Args = [], **kwargs):
		self.Message = '''The following parameter(s) is (are) missing: '''
		super().__init__(self.Message,By, Args, **kwargs  )    
		
#a = GenericError('Item not  found', By = 'kernel', Args=[('a',1)])
#raise a
#
#
#raise GenericError('I could no go on')
#raise BeamlineElementNotFoundError()
