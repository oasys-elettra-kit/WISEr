# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 14:08:31 2016

@author: Mic
"""
from numpy import ones, exp, log10, linspace, unique, round, log2, ceil, pi, sqrt, hstack, trapz
from numpy.fft import fft, fftshift, ifft, ifftshift
from numpy.random import rand
from scipy.interpolate import interp1d, splrep, splev
from scipy.integrate import trapz
import matplotlib.pyplot as plt
from LibWISEr.must import *
import numpy as np
import LibWISEr.Rayman as rm
Gauss1d =  lambda x ,y : None
from scipy import interpolate as interpolate

class FunctionCollection:
	'''
	Ensemble of possible Psd Functions.
	Each element is a callable Psd.
	Most used are
		PsdFuns.PowerLaw(x,a,b)
		PsdFuns.Interp(x, xData, yData)
	'''
	class PsdFunctions:
		@staticmethod
		def Flat(x, *args):
			return ones([1, len(x)])
		@staticmethod
		def PowerLaw(x, a, b):
			return a*x**b
		@staticmethod
		def Gaussian(x, sigma, x0=0):
			return exp(-(x-x0)**2 / (2*sigma**2))#sqrt(a / pi) * exp(- a * (x-x0)**2)
		@staticmethod
		def Interp(x, xData, yData):
			if xData[1] > xData[0]:
				xData = xData[::-1]
				yData = yData[::-1]
			f = interp1d(xData, yData)
			return f(x)

	# These functions are used when fitting. They're scaled by e.g. log10(f)
	class FitFunctions:
		@staticmethod
		def PowerLawLog(x, a, b):
			return log10(a*x**b)


def PsdFun2Noise_1d(N,dx, PsdFun, PsdArgs):
	'''
		Generates a noise pattern based an the Power spectral density returned
		by PsdFun
	'''
	x = np.arange(0,N//2+1, dx)
	yHalf = PsdFun(x, *PsdArgs)
	y = Psd2NoisePattern_1d(yHalf, Semiaxis = True 	)
	return  x,y



def CheckRegularSpacing(xAxis):
	difference = xAxis[1:] - xAxis[:-1]
	isRegular = False
	if len(unique(round(difference, 9))) == 1:
		isRegular = True

	return isRegular

# def CheckPowerOfTwo(xAxis):
# 	isPowerOfTwo = False
# 	if log2(len(xAxis)) - int(log2(len(xAxis))) == 0:
# 		isPowerOfTwo = True
#
# 	return isPowerOfTwo
#============================================================================
#	FUN: 	PsdArray2Noise_1d_v2
#============================================================================
def PsdArrayToNoise(qPsd, yPsd, L, outputLength):
	'''
	Returns Noise in [m]
	'''

	L_um = L * 1e6
	L_nm = L * 1e9

	N2 = outputLength // 2
	df = (2. * pi) / L  # fMin - minimal spacing in frequency domain (PSD)

	# if self.OperationMode == COMPUTE_FROM_MODEL:
	#
	# elif self.OperationMode == LOAD_PSD_FIT_WITH_MODEL:
	#
	# elif self.OperationMode == LOAD_PSD_AND_RESAMPLE:
	#
	# elif self.OperationMode == LOAD_HEIGHT_PROFILE:

	# First check if the PSD array has:
	# - regular spacing
	# - 2^N samples
	# - max. frequency is F_max

	# Define min and max frequency
	fMin = min(qPsd)
	fMax = max(qPsd)
	xSpline = qPsd  # Only called xSpline for the purpose of resampling

	# Make x axis with regular spacing and length equal to the mirror for the spline
	if not CheckRegularSpacing(xSpline):
		xSpline = linspace(fMin, fMax, num=N2)
		# Interpolate the PSD with a spline
		if qPsd[1] < qPsd[0]:
			fun = splrep(qPsd[::-1], yPsd[::-1], s=2)
		else:
			fun = splrep(qPsd, yPsd, s=2)

		ySpline = splev(xSpline, fun) # Interpolate on regular xSpline grid

	elif CheckRegularSpacing(xSpline):
		print('X-axis already has regular spacing. No resampling...')
		ySpline = yPsd

	#plt.plot(xSpline, ySpline, 's', markersize=3, label='Spline regular interp', linestyle='none', markeredgewidth=0.3)
	#plt.plot(xToConvertCheck, yPsdToConvert, '+', markersize=3, label = 'Spline to convert', linestyle='none', markeredgewidth=0.3)
	#plt.legend()


	# Take iFFT to generate roughness
	noiseiFFT = PsdArrayToNoiseKernel(ySpline, L/(outputLength-1))

	return real(noiseiFFT)

def PsdFunctionToNoise(xxPsd, Function, L, N, *args):
	'''

	:param xxPsd:
	:param Function:
	:param L: length of the sample
	:param N: number of points
	:param args: any additional arguments for the Function
	:return:
	'''
	return

def CheckPsdIntegral(xPsd, yPsd):
	'''
	Return the integral of Psd. Used in sanity check.
	:return:
	'''

	return trapz(yPsd, x=xPsd)

def PsdArrayToNoiseKernel(yPsd, dx): # Rename to noise
	'''
	Generates roughness from (q, y)
	:param yyPsd: y-axis of the PSD, corresponding to xxPSD
	:param dq: spacing
	:return: Noise pattern in real space (spatial coordinates, deviations)
	'''

	# Mirror the yyPsd over 0
	if len(yPsd) % 2 == 0:
		yPsdToConvert = hstack((yPsd[:0:-1], 0, yPsd[1:-1]))
	else:
		yPsdToConvert = hstack((yPsd[:0:-1], 0, yPsd[1:]))

	# Generate random phases on interval [0, 2pi)
	randomPhases = ones(len(yPsdToConvert)) * 2. * pi

	# Convert PSD to A(f(k)) and assign random phases to it
	yPsdAmplitude = sqrt(yPsdToConvert) #sqrt(1. / (dx * 1000.) * yyPsdToConvert)

	yPsdAmplitudeShifted = fftshift(yPsdAmplitude)
	yPsdComplex = yPsdAmplitudeShifted * exp(1j * randomPhases) #####* len(yPsd)

	print('len(yPsd)-1 / dx = ', (len(yPsd)-1) / dx)

	# Apply inverse Fourier transform
	roughness = (len(yPsd)-1) / dx * ifft(yPsdComplex)  # Now the roughness will have 2*outputLength+1 elements

	return roughness# * 1e-9

#============================================================================
#	FUN: 	Psd2Noise
#============================================================================
def PsdArray2Noise_1d(PsdArray, N, Semiaxis = True, Real = True):
	'''
	Generates a noise pattern whose Power Spectral density is given by Psd.

	Parameters
	---------------------
	Psd :  1d array
		Contains the numeric Psd (treated as evenly spaced array)

	Semiaxis :
		0 : does nothing
		1 : halvens Pds, then replicates the halven part for left frequencies,
			producing an output as long as Psd
		2 : replicates all Pds for lef frequencies as well, producing an output
			twice as long as Psd
	Real : boolean
		If True, the real part of the output is returned (default)

	Returns:
	---------------------
		An array of the same length of Psd
	'''

	if Semiaxis == True:
		yHalf = PsdArray
		PsdArrayNew = np.hstack((yHalf[-1:0:-1], yHalf))
		idelta = len(PsdArrayNew) - N
		if idelta == 1:# piu lungo
			PsdArrayNew = PsdArrayNew[0:-1] # uguale
		elif idelta == 0:
			pass
		else:
			print('Error!  len(PsdArrayNew) - len(PsdArray) = %0d' % idelta)
	y = np.fft.fftshift(PsdArrayNew)
	r = 2*pi * np.random.rand(len(PsdArrayNew))

	f = np.fft.ifft(y * exp(1j*r))

	if Real:
		return real(f)
	else:
		return f
Psd2Noise_1d = PsdArray2Noise_1d
#============================================================================
#	FUN: 	NoNoise_1d
#============================================================================
def NoNoise_1d(N, *args):
	return np.zeros([1,N])

#============================================================================
#	FUN: 	GaussianNoise_1d
#============================================================================
def GaussianNoise_1d(N,dx, Sigma):
	'''
	PSD(f) = exp(-0.5^f/Sigma^2)
	'''
	x = np.linspace( - N//2 *dx, N//2-1 * dx,N)
	y = exp(-0.5*x**2/Sigma**2)
	return Psd2NoisePattern_1d(y)


#============================================================================
#	FUN: 	PowerLawNoise_1d
#============================================================================
def PowerLawNoise_1d(N, dx, a, b):
	'''
	PSD(x) = a*x^b
	'''
	x = np.arange(0,N//2+1, dx)
	yHalf = a * x**b
#	y = np.hstack((yHalf[-1:0:-1], 0, yHalf[1:-1]))
	return Psd2NoisePattern_1d(y, Semiaxis = True)

#============================================================================
#	FUN: 	CustomNoise_1d
#============================================================================
def CustomNoise_1d(N, dx, xPsd, yPsd):
	xPsd_, yPsd_ = rm.FastResample1d(xPsd, yPsd,N)
	return Psd2NoisePattern_1d(yPsd_, Semiaxis = True)

#============================================================================
#	CLASS: 	NoiseGenerator
#============================================================================
class PsdGenerator:
	NoNoise = staticmethod(NoNoise_1d)
	Gauss  = staticmethod(GaussianNoise_1d)
	PowerLaw = staticmethod(PowerLawNoise_1d)
	NumericArray = staticmethod(CustomNoise_1d)



#============================================================================
#	FUN: 	FitPowerLaw
#============================================================================
def FitPowerLaw(x,y):
	'''
	Fits the input data in the form
		y = a*x^b
	returns a,b
	'''
	import scipy.optimize as optimize

	fFit = lambda p, x: p[0] * x ** p[1]
	fErr = lambda p, x, y: (y - fFit(p, x))

	p0 = [max(y), -1.0]
	out = optimize.leastsq(fErr, p0, args=(x, y), full_output=1)

	pOut = out[0]

	b = pOut[1]
	a = pOut[0]

#	indexErr = np.sqrt( covar[0][0] )
#	ampErr = np.sqrt( covar[1][1] ) * amp

	return a,b

#==============================================================================
# 	CLASS: RoughnessMaker
#==============================================================================

class RoughnessMaker(object):

	class Options():
		FIT_NUMERIC_DATA_WITH_POWER_LAW  = True
		AUTO_ZERO_MEAN_FOR_NUMERIC_DATA = True
		AUTO_FILL_NUMERIC_DATA_WITH_ZERO  = True
		AUTO_RESET_CUTOFF_ON_PSDTYPE_CHANGE = True

	def __init__(self):
		self.PsdType = FunctionCollection.PsdFunctions.PowerLaw
		self.PsdParams = np.array([1,1])
		self._IsNumericPsdInFreq = None
		self.CutoffLowHigh = [None, None]
		self.ProfileScaling = 1
		return None

	@property
	def PsdType(self):
		return self._PsdType
	@PsdType.setter
	def PsdType(self, Val):
		'''
		Note: each time that the Property value is set, self.CutoffLowHigh is
		reset, is specified by options
		'''
		self. _PsdType = Val
		if self.Options.AUTO_RESET_CUTOFF_ON_PSDTYPE_CHANGE == True:
			self.PsdCutoffLowHigh  = [None, None]

	#======================================================================
	# 	FUN: PdfEval
	#======================================================================
	def PsdEval(self, N, df, CutoffLowHigh = [None, None]):
		'''
		Evals the PSD in the range [0 - N*df]
		It's good custom to have PSD[0] = 0, so that the noise pattern is
		zero-mean.

		Parameters:
		----------------------
			N : int
				#of samples
			df : float
				spacing of spatial frequencies (df=1/TotalLength)
			CutoffLowHigh : [LowCutoff, HighCutoff]
				if >0, then Psd(f<Cutoff) is set to 0.
						if None, then LowCutoff = min()
		Returns :  fAll, yPsdAll
		----------------------
			fAll : 1d array
				contains the spatial frequencies
			yPsd : 1d array
				contains the Psd
		'''

		'''
		The Pdf is evaluated only within LowCutoff and HoghCutoff
		If the Pdf is PsdFuns.Interp, then LowCutoff and HighCutoff are
		automatically set to min and max values of the experimental data
		'''
		StrMessage = ''
		def GetInRange(fAll, LowCutoff, HighCutoff):
			_tmpa  = fAll >= LowCutoff
			_tmpb = fAll <= HighCutoff
			fMid_Pos  = np.all([_tmpa, _tmpb],0)
			fMid = fAll[fMid_Pos]
			return fMid_Pos, fMid

		LowCutoff, HighCutoff = CutoffLowHigh
		fMin = 0
		fMax = (N-1)*df
		fAll = np.linspace(0, fMax, N)
		yPsdAll = fAll* 0 # init

		LowCutoff = 0 if LowCutoff == None else LowCutoff
		HighCutoff = N*df if HighCutoff == None else HighCutoff



		# Numeric PSD
		# Note: by default returned yPsd is always 0 outside the input data range
		if self.PsdType == FunctionCollection.PsdFunctions.Interp:
			# Use Auto-Fit + PowerLaw
			if self.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW == True:
					xFreq,y = self.NumericPsdGetXY()
					p = FitPowerLaw(1/xFreq,y)
					_PsdParams = p[0], -p[1]
					LowCutoff = np.amin(self._PsdNumericX)
					HighCutoff = np.amin(self._PsdNumericX)
					fMid_Pos, fMid = GetInRange(fAll, LowCutoff, HighCutoff)
					yPsd = FunctionCollection.PsdFunctions.PowerLaw(fMid, *_PsdParams )
			# Use Interpolation
			else:
				# check Cutoff
				LowVal = np.amin(self._PsdNumericX)
				HighVal = np.amax(self._PsdNumericX)
				LowCutoff = LowVal if LowCutoff <= LowVal else LowCutoff
				HighCutoff = HighVal if HighCutoff >= HighVal else HighCutoff


				# Get the list of good frequency values (fMid) and their positions
				# (fMid_Pos)
				fMid_Pos, fMid = GetInRange(fAll, LowCutoff, HighCutoff)

				##yPsd = self.PsdType(fMid, *self.PsdParams)
				## non funziona, rimpiazzo a mano
				yPsd =  FunctionCollection.PsdFunctions.Interp(fMid, self._PsdNumericX, self._PsdNumericY)

		# Analytical Psd
		else:
			fMid_Pos, fMid = GetInRange(fAll, LowCutoff, HighCutoff)
			yPsd = self.PsdType(fMid, *self.PsdParams)

		# copying array subset
		yPsdAll[fMid_Pos] = yPsd

		return fAll, yPsdAll

	#======================================================================
	# 	FUN: _FitNumericPsdWithPowerLaw
	#======================================================================
# in disusos
	def _FitNumericPsdWithPowerLaw(self):
		x,y = self.NumericPsdGetXY()
		if self._IsNumericPsdInFreq == True:
			p = FitPowerLaw(1/x,y)
			self.PsdParams = p[0], -p[1]
		else:
			p = FitPowerLaw(x,y)
			self.PsdParams = p[0], p[1]


	#======================================================================
	# 	FUN: MakeProfile
	#======================================================================
	def MakeProfile(self, L,N):
		'''
			Evaluates the psd according to .PsdType, .PsdParams and .Options directives
			Returns an evenly-spaced array.
			If PsdType = NumericArray, linear interpolation is performed.

			:PARAM: N: # of samples
			:PARAM: dx: grid spacing (spatial frequency)

			returns:
				1d arr
		'''


		if self.PsdType == FunctionCollection.PsdFunctions.Interp:
			# chiama codice ad hoc
			L_mm = L*1e3
			yRoughness = PsdArray2Noise_1d_v2(self._PsdNumericX, self._PsdNumericY, L_mm, N)
		else:
			print('Irreversible error. The code was not completed to handle this instance')
		return yRoughness * self.ProfileScaling
#		f, yPsd = self.PsdEval(N//2 + 1,df)


		# Special case
#		if self.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW == True:
#			self.PsdParams = list(FitPowerLaw(*self.NumericPsdGetXY()))
#			yPsd = PsdFuns.PowerLaw(x, *self.PsdParams)
#		else: # general calse
#			yPsd = self.PsdType(x, *self.PsdParams)

#		yRoughness  = Psd2Noise_1d(yPsd, N, Semiaxis = True)


#		x = np.linspace(0, N*dx,N)
#		# Special case
#		if self.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW == True:
#			self.PsdParams = list(FitPowerLaw(*self.NumericPsdGetXY()))
#			y = PowerLawNoise_1d(N, dx, *self.PsdParams)
#		else: # general calse
#			y = self.PsdType(N,dx, *self.PsdParams)
#		return y
	Generate = MakeProfile
	#======================================================================
	# 	FUN: NumericPsdSetXY
	#======================================================================
	def NumericPsdSetXY(self,x,y):
		self._PsdNumericX = x
		self._PsdNumericY = y


	#======================================================================
	# 	FUN: NumericPsdGetXY
	#======================================================================

	def NumericPsdGetXY(self):
		try:
			return self._PsdNumericX, self._PsdNumericY
		except:
			print('Error in RoughnessMaker.NumericPsdGetXY. Maybe the data file was not properly loaded')
	#======================================================================
	# 	FUN: NumericPsdLoadXY
	#======================================================================
	def NumericPsdLoadXY(self, FilePath, xScaling = 1, yScaling = 1 , xIsSpatialFreq = True):
		''' @TODO: specificare formati e tipi di file

		Parameters
		----------------------------
		xIsSpatialFreq : bool
						true If the first column (Read_x_values) contains spatial
						frequencies. False if it contains lenghts. Default = True
		xScaling, yScaling: floats
						Read_x_values => Read_x_values * xScaling

						Read_y_values => Read_y_values * yScaling

						Sometimes, properly setting the x and y scaling values may be confusing (although just matter of high-school considerations). On this purpose, the property .RoughnessMaker.ProfileScaling property can be used also..ProfileScaling is the scale factor that acts on the output of MakeProfile() function only.

		remarks
						--------
						pippo

		'''

		try:
			self._IsNumericPsdInFreq = xIsSpatialFreq

			s = np.loadtxt(FilePath)
			x = s[:,0]
			y = s[:,1]

			x = x * xScaling
			y = y * yScaling

			# inversion of x-axis if not spatial frequencies
			if xIsSpatialFreq == False:
				f = 1/x
			else:
				f = x
			# array sorting
			i = np.argsort(f)
			f = f[i]
			y = y[i]
			# I set the Cutoff value of the class according to available data
			self.PsdCutoffLowHigh = [np.amin, np.amax(f)]

			# I set class operating variables
			self.PsdType = FunctionCollection.PsdFunctions.Interp
			self.PsdParams = [f,y]


			# Auto-set
			# fill 0-value (DC Component)
	#		if self.Options.AUTO_FILL_NUMERIC_DATA_WITH_ZERO == True:
	#			if np.amin(x >0):
	#				x = np.insert(x,0,0)
	#				y = np.insert(y,0,0)	# 0 in psd => 0-mean value in the noise pattern


			# sync other class values
			self.NumericPsdSetXY(f, y)
		except:
			pass

		def Generate(self, N = None, dx = None, CutoffLowHigh = [None, None]):
			'''
			Parameters
				N: # of output samples
				dx: step of the x axis
			Note: generates an evenly spaced array
			'''
			L = dx * N
			df = 1/L
			fPsd, yPsd = self.PsdEval(N//2 +1  , df = df,
											CutoffLowHigh = CutoffLowHigh )
			h = Psd2Noise_1d(yPsd, Semiaxis = True)

			return  h

	#======================================================================
	# 	FUN: NumericPsdCheck
	#======================================================================
	def NumericPsdCheck(self, N, L):

		df = 1/L
		# Stored data
		ff,yy = self.NumericPsdGetXY()
		# Evaluated data
		fPsd, yPsd = self.PsdEval(N, df)


		plot(fPsd, np.log10(yPsd),'x')
		plot(ff, np.log10(yy),'.r')
		plt.legend(['Evaluated data', 'Stored data'])
		plt.suptitle('Usage of stored data (PSD)')

		fMax = df*(N//2)
		fMin = df
		StrMsg = ''
		_max = np.max(ff)
		_min = np.min(ff)
		print('fMax  query = %0.1e m^-1' % fMax )
		print('fMax data= %0.1e m^-1 = %0.2e um^-1' % (_max, (_max * 1e6) ))
		print('fMin query= %0.1e m^-1' % fMin )
		print('fMin data= %0.1e m^-1 = %0.2e um^-1' % (_min, (_min * 1e6) ))

		return StrMsg