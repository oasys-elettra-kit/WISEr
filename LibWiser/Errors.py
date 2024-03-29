# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 11:18:22 2021

@author: Mike - Manfredda
"""
import warnings


import warnings

def Warn(x:Warning):
	warning.warn(x)
	
class SmartException(Exception):
	
	def __init__(self, Message = 'A generic Errour Occurred', By =None, Args = []):
		'''
		
		Parameters
		------
		Mssage : Str
		
			message to display
			
		Args : List of name-value Tuples
		
			List of two-element tuples in the form [(name1, value1), (name2, value2),...]
			used to display more info.
		'''
		
		self._Message = Message
		self.Args = Args
		
		
		ExtraMsg = []
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
		
#a = GenericError('Item not  found', By = 'kernel', Args=[('a',1)])
#raise a
#
#
#raise GenericError('I could no go on')
#raise BeamlineElementNotFoundError()
