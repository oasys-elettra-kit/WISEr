# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 22:18:10 2020

@author: Mike - Manfredda
"""
from LibWiser.WiserImport import *
from LibWiser.must import *
import LibWiser.FermiSource as FermiSource
import LibWiser.WiserImport as lw
import LibWiser.Optics as Optics
from LibWiser.Foundation import OpticalElement
import LibWiser.Enums as Enums
from LibWiser.Exceptions import WiserException

from LibWiser.ToolLib import CommonPlots
SmartPlot = CommonPlots.SmartPlot

from time import time
from LibWiser.Scrubs import UpdateDictionary

HORIZONTAL = Enums.OPTICS_ORIENTATION.HORIZONTAL
VERTICAL = Enums.OPTICS_ORIENTATION.VERTICAL
ANY = Enums.OPTICS_ORIENTATION.ANY
