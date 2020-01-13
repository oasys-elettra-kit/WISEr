# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 17:07:51 2019

@author: Mike
"""

#%% Standard import snippet (20190826)
#=======================================================================
import importlib



# LibWISEr aliases
#=======================================================================
from LibWISEr.must import *   #continuously subject to  revision and discussion

import LibWISEr.ToolLib as tl
ToolLib  = tl
import LibWISEr.Paths as Paths
import LibWISEr.Rayman as rm
Rayman = rm
import LibWISEr.Foundation as Foundation
import LibWISEr.Optics as Optics
import LibWISEr.Noise as Noise
import LibWISEr.FermiSource as Fermi

# Worth of mention objects / Frequently used aliases
#=======================================================================
from LibWISEr.Foundation import OpticalElement


# Common numerical/scientifical base
import winsound
import matplotlib as mp
import matplotlib.pyplot as pp
import numpy as np
from numpy import array
import csv


importlib.reload(Foundation)
importlib.reload(Optics)
importlib.reload(tl)
importlib.reload(rm)
#%% =======================================================================