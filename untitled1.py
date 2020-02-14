# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 14:33:59 2020

@author: Mike - Manfredda
"""

#%%
x = 1
def fa():
	print (x)
#	global y
	y = 100

	def fb():
#		global y
		print(y)
	fb()
fa()

