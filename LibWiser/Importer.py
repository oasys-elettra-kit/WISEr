# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 17:07:51 2019

@author: Mike
"""

#%% Standard import snippet (20190826)
#=======================================================================
import importlib
import numpy as np
import winsound
import matplotlib as mp
import matplotlib.pyplot as pp
import LibWISEr.Rayman as rm
import LibWISEr.Foundation as Fundation
import LibWISEr.Optics as Optics
import LibWISEr.ToolLib as tl
import LibWISEr.ToolLib
from LibWISEr.must import *
from LibWISEr.Fundation import OpticalElement
from numpy import array
import csv
import FermiSource as Fermi

importlib.reload(Fundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)
#%% =======================================================================