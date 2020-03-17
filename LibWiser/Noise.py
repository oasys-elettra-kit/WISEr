# -*- coding: utf-8 -*-
"""

Created on Thu Jul 07 14:08:31 2016

ù@author: Mic

"""

from __future__ import division
from LibWiser.must import *
import numpy as np
import LibWiser.Rayman as rm
import LibWiser.ToolLib as tl
Gauss1d =  lambda x ,y : None
from scipy import interpolate as interpolate


class PsdFuns:
	'''
		Ensemble of possible Psd Functions.
		Each element is a callable Psd.
		Most used are
			PsdFuns.PowerLaw(x,a,b)
			PsdFuns.Interp(x, xData, yData)
	'''
	@staticmethod
	def Flat(x, *args):
		N = len(x)
		return np.zeros([1,N]) +1
	@staticmethod
	def PowerLaw(f,a,b):
		'''
		Power Law Function in the form

		**PowerLaw(f) = a*f^b**

		Parameters
		----
		f : array
			Spatial frequency
		a : float

		b : float

		returns
		----
		PowerLaw(f) = a*f^b
		'''
		return a*f**b
	@staticmethod
	def Gaussian(x,sigma, x0=0):
		return np.exp(-0.5 * (x-x0)**2/sigma**2)
	@staticmethod
	def Interp(x, xData, yData):
		f = interpolate.interp1d(xData, yData)

		return f(x)




#============================================================================
#	FUN: 	MakeFrequencies
#============================================================================
def MakeFrequencies(L,N, IsWaveNumber = True):
	'''
	Returns the (Spatial) frequencies corrisponding to a signal of length(or duration)
	L with N samples.

	q = 1/L *  np.arange(0,N//2+1)

	If IsWaveNumber = True,

	q = 2*pi/L *  np.arange(0,N//2+1)
	'''
	a = 2*np.pi if IsWaveNumber == True else 1
	dq = a / L
	qRange = dq * np.arange(0,N//2+1)
	return qRange
#============================================================================
#	FUN: 	PsdAnalytic2Noise
#============================================================================
def PsdAnalytic2Noise(L0,N0, PsdFun, PsdArgs, q1Min = None, q1Max = None, qIsWaveNumber = True):
	'''
		Generates a noise pattern based an the Power spectral density returned
		by PsdFun. The Bandwidth can be specified using qMin and qMax, which are the
		spatial frequencies. The explicit specification of the bandwidth is **strongly** recommended.

	Parameters
	-----
	L0 : float
		Material length of the windows signal (e.g. length, or time duration)

	N0 : integer
		Number of samples.
		It must be ** N < qMax/qMin**

	PsdFun : function
		Function used to evaluate the Power Spectral Density

	*PsdArgsm **kwPsdargs
		Parameters for PsdFun
	'''
	piFact = 2 * np.pi if qIsWaveNumber == True else 1
	N0 = N0/2

#	dq = 2*np.pi / L # minimum max-wavelength <=> min frequency
#	qRange = dq * np.arange(0,N//2+1)

	q0Min = (np.pi * 2 / L0)
	q0Max = (np.pi * N0 / L0)

	q1Min = q1Min if q1Min is not None else q0Min
	q1Max = q1Max if q1Max is not None else q0Max
	N1 = q1Max/q1Min
	q1Range = np.linspace(q1Min,q1Max,N1)
	q0Range = np.linspace(q0Min, q0Max, N0)

	iq1 = int(np.floor(q1Min/q0Min))

#	x = np.arange(0, N//2+1, dx)
	y1Half = PsdFun(qRange, *PsdArgs)
	y0Half = np.zeros(N0)
	y0Half[iq1: iq1 + len(y1Half)] = y1Half

	NoiseSignal = PsdNumeric2Noise(y0Half, IsHalfBandwidth = True, ZeroDC = True )
	return NoiseSignal, y0Half

#============================================================================
#	FUN: 	PsdNumeric2Noise
#============================================================================
def PsdNumeric2Noise(PsdArray, IsHalfBandwidth = True, ZeroDC = True, Real = True):
	'''
	Generates a noise pattern whose Power Spectral density is given by Psd.

	Returns
	----
	Noise : real array
		Noise signal, whose Power Spectrum corresponds to the input one, given by
		PsdArray.

		- **The DC component** of Noise is at N//2, where N = len(PsdArray).
		- **The positive bandwidth** of Noise is Noise[N//2,-1]

    Examples
    ------
    >>> np.fft.fft(np.exp(2j * np.pi * np.arange(8) / 8))
    array([ -3.44505240e-16 +1.14383329e-17j,
             8.00000000e+00 -5.71092652e-15j,
             2.33482938e-16 +1.22460635e-16j,
             1.64863782e-15 +1.77635684e-15j,
             9.95839695e-17 +2.33482938e-16j,
             0.00000000e+00 +1.66837030e-15j,
             1.14383329e-17 +1.22460635e-16j,
             -1.64863782e-15 +1.77635684e-15j])

	'''
	# The input PSD is only on Half-Bandwidth, so the effective PSD is
	# reconstructed by taking the simmetric one with respect to DC compoentn
	if ZeroDC:
		PsdArray[0] = 0
	N = len(PsdArray)
	if IsHalfBandwidth == True:
		PsdArrayNew = tl.MirrorArray(PsdArray)
	else:
		PsdArrayNew = PsdArray

	PsdArrayNew = np.fft.fftshift(PsdArrayNew) # Power Spectrum (shifted)


	N = len(PsdArrayNew)
	Phi = 2*np.pi * np.random.rand(N) # random phases

	# The noise signal is proportional to the Spectrum, i.e. to sqrt(PS)
	# N**2 => normalization
	S = np.sqrt(PsdArrayNew) * np.exp(1j*Phi)
	s = np.fft.ifft(S, norm = 'ortho')
	s = s
	return s

#Psd2Noise_1d = PsdArray2Noise_1d
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
		self.PsdType = PsdFuns.PowerLaw
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
		if self.PsdType == PsdFuns.Interp:
			# Use Auto-Fit + PowerLaw
			if self.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW == True:
					xFreq,y = self.NumericPsdGetXY()
					p = FitPowerLaw(1/xFreq,y)
					_PsdParams = p[0], -p[1]
					LowCutoff =  np.amin(self._PsdNumericX)
					HighCutoff = np.amin(self._PsdNumericX)
					fMid_Pos, fMid = GetInRange(fAll, LowCutoff, HighCutoff)
					yPsd = PsdFuns.PowerLaw(fMid, *_PsdParams )
			# Use Interpolation
			else:
				# check Cutoff
				LowVal =  np.amin(self._PsdNumericX)
				HighVal = np.amax(self._PsdNumericX)
				LowCutoff = LowVal if LowCutoff <= LowVal else LowCutoff
				HighCutoff = HighVal if HighCutoff >= HighVal else HighCutoff


				# Get the list of good frequency values (fMid) and their positions
				# (fMid_Pos)
				fMid_Pos, fMid = GetInRange(fAll, LowCutoff, HighCutoff)

				##yPsd = self.PsdType(fMid, *self.PsdParams)
				## non funziona, rimpiazzo a mano
				yPsd =  PsdFuns.Interp(fMid, self._PsdNumericX, self._PsdNumericY)

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


		if self.PsdType == PsdFuns.Interp:
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
			self.PsdType = PsdFuns.Interp
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
#============================================================================
#	FUN: 	HewScatteringContribution
#============================================================================
def HewScatteringContribution (Lambda, GrazingAngle, Kn,n):
	return (Kn/(n-1)) **(1/(n-1)) * (np.sin(GrazingAngle)/Lambda) **(3-n)/(n-1)
