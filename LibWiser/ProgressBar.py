# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 20:10:48 2021

@author: Mike
"""
#%%

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
import time

# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow):
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)

		self.setWindowTitle("Progress bar")

		self.label = QLabel("This is a PyQt5 window!")
		self.label.setAlignment(Qt.AlignCenter)
		self.setCentralWidget(self.label)
		self._Tic = time.time()
		
	def SetValue(self, Total, Counter):
		self._Toc = time.time()
		_ComputationTimeMin = (self._Toc - self._Tic)/60
		self.label.setText('Process counter %d/%d \n Time for step: %0.1f min' %( Counter, Total,_ComputationTimeMin))
		
		self._Tic = time.time()
		self.update()
		

class ProgressBar():
	def __init__(self):
		self.App = QApplication(sys.argv)
		self.Window = MainWindow()
		self.Window.show()
		self.App.exec_()
		
	def Update(self, Total, Counter):
		self.Window.SetValue( Counter, Total)
		
#%%
PBar = ProgressBar()
for i in range(1,10):
	time.sleep(1)
	print(i)
	PBar.Update(i,10)
