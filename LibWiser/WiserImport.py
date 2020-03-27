# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 17:07:51 2019

@author: Mike
"""

#%% Standard import snippet (20190826)
#=======================================================================
import importlib



# LibWiser aliases
#=======================================================================
from LibWiser.must import *   #continuously subject to  revision and discussion

import LibWiser.ToolLib as tl
ToolLib  = tl
import LibWiser.Paths as Paths
import LibWiser.Rayman as rm
Rayman = rm
import LibWiser.Foundation as Foundation
import LibWiser.Optics as Optics
import LibWiser.Noise as Noise
import LibWiser.FermiSource as Fermi
import LibWiser.Scrubs
import LibWiser.Units as Units
# Worth of mention objects / Frequently used aliases
#=======================================================================
from LibWiser.Foundation import OpticalElement


# Common numerical/scientifical base
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
