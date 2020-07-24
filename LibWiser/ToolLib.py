# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 11:58:09 2017

@author: Mic
"""
from __future__ import division
import scipy
import LibWiser.must  as must
from LibWiser.must import *
from collections import namedtuple
from LibWiser.Units import Units
import inspect
import logging
import os
from scipy.signal import square
from pathlib import Path as MakePath
import LibWiser.Paths as Paths


#================================
#  FUN: PathGetExtension
#================================
def PathGetExtension(Path):
	filename, file_extension = os.path.splitext(Path)
	return file_extension
#================================
#  FUN: PathSplit
#================================
def PathSplit (Path):
	'''
	Returns a tuple containing the single elements of a path.
	e.g. "d:\home\kitchen\pan.txt" => ("d:" , "home" , "kitchen", "pan.txt")

	(It Should be platform independent:).
	'''
	Path = os.path.normpath(Path)
	return Path.split(os.sep)

#================================
# FUN: PathJoin
#================================
def PathJoin (path, *paths):
	'''
	It behaves like os.path.join except that the behavior is as follows

	>>> PathJoin("d:", "folder")
	> d:\\folder

	rather than

	>>> PathJoin("d:", "folder")
	> d:folder
	'''
	# Workaround, for handling Windows Units Letters
	if len(path)==2 and path[1] == ':':
		path = path + os.path.sep

	return MakePath(path, *paths)
#	return os.path.join(path, *paths )

#================================
#  PathCreate
#================================
def PathGetFileNameWithoutExtension(Path):
	return os.path.splitext[0]
#================================
#  PathCreate
#================================
def PathCreate(Path, IsFile = True):
	'''
	Create a path, if not existing.

	Parameters
	-----
	Path : string
		Can be either a path to a folder (e.g. d:\pippo, /home/pippo),
		either a path to a file (e.g. d:\pippo\pluto.txt, /home/pippo/pluto.txt).

		In the latter case, it must be IsFile = True

	IsFile : bool
		It must be set to True when Path is a path to a filf

	Return
	------
	- False: if the path has not been created (i.e. it was already existing)

	- False: if the path has been created (i.e. it was not already existing)

	'''
	Path = os.path.dirname(Path) if IsFile else Path
	if os.path.exists(Path):
		return False
	else:
		os.makedirs(Path)
		return True

#================================
#  RunFile
#================================
def ExecFile(FilePath):
	'''
	Executes a python file.

	'''
	FilePath = MakePath(FilePath)
	if FilePath.exists():
		scriptContent = open(FilePath, 'r').read()
		exec(scriptContent)
	else:
		pass

##================================================================
##  GetWiserPath
##================================================================
#def GetWiserPath():
#	'''
#	Returns the parent folder containing LibWiser fodler
#
#	Architecture Notes
#	----
#	To be tested on unix.
#	Check if better solutions are possible.
#	Created to handle the DATA folder containing the figure error files,
#	and the cross platform path routing.
#
#	'''
#	WorkingFile = must.__file__
#	WorkingFileItems  = PathSplit(WorkingFile)
#	WorkingPath =  os.path.join( *WorkingFileItems[0:-2])
#	return WorkingPath
#
#PathWiser = GetWiserPath() # the WiserPath variable is sent to the namespace

#================================================================
#  ErrMsg
#================================================================
class ErrMsg:
	@staticmethod
	def NoPropertySetAllowed(More = ''):
		raise ValueError('Property set metod is not allowed.\n%s' % More)

	def InvalidInputSet(More=''):
		raise ValueError('Ivalid input parameter set used.' % More)

#================================================================
#  CLASS Debug
#================================================================
class Debug():

	On = True
	_OldValue = True

	@staticmethod
	def MakeTmpH5File(Name):
		return MakePath( Paths.Main / (Name + '.h5'))

	PathTemporaryH5File  = MakePath(Paths.Main / 'tmp_file2.h5')
#	PathTemporaryH5File  = ''
	'''
	logging.basicConfig(filename = FileName, filemode='w', format='%(message)s || %(asctime)s')
	logging.warning('Starting simulation: N = %d', N)
	logging.warning(Str)

	'''
	import h5py
	#================================
	#  PutData
	#================================
	def PutData(Name,Value, FileName = None):
		'''
		Put data to the temporary H5File
		'''
		Path = Debug.PathTemporaryH5File if FileName is None else MakePath( Paths.Main / (FileName + '.h5'))
		FileIO.SaveToH5(Path, [(Name, Value)], dict(), Mode = 'a')

	#================================
	#  GetData
	#================================
	def GetData(Name, FileName= None):
		'''
		Read data from the temporary H5File
		'''
		Path = Debug.PathTemporaryH5File if FileName is None else MakePath( Paths.Main / (FileName + '.h5'))
		try:
			File = h5py.File(Path)
			Data = File[Name]
			File.close()
			return Data
		except:
			File.close()
			return None




	def Print(Str = '', NIndent = 0, Header = False):
		if Debug.On :
			Str = (NIndent * '\t' + '%s') % Str
			Str= Str.replace('\n','\n' + NIndent * '\t')
			Str = Str if Header == False else (30 * '=-' + '\n' + Str + '\n' + 30 * '=-'+'\n')
			print(Str)

	def print(Str ='', NIndent = 0, Header = False):
		if Debug.On :
			Debug.Print(Str, NIndent, Header)

	def pr(LocalVarName, More = ''):
		frame = inspect.currentframe()
		if Debug.On :
			try:
				print(LocalVarName + ':= ' + str(frame.f_back.f_locals[LocalVarName]) + ' ' + More)
			except:
				pass
			finally:
				del frame

	def pv(LocalVarName, NIndent = 0, More = ''):
		if Debug.On :
			frame = inspect.currentframe()
			Tab = NIndent * '\t'
			if True:
				try:
					print(Tab + LocalVarName + ':= ' + str(frame.f_back.f_locals[LocalVarName]) + ' ' + More)
				except:
					pass
				finally:
					del frame




#================================================================
#  IsArray
#================================================================
def IsArray(x):
	return isinstance(x,np.ndarray)

#================================================================
#  IsScalar
#================================================================
def IsScalar(x):
	return isinstance(x,float) or isinstance(x,int)


#================================================================
#  CheckArg
#================================================================
def CheckArg(NotNoneArgs, NoneArgs = []):
	'''
	Returns if ALL the values in ArgList are not none.

	I use it for initializing object which admit different paramenters, e.g.

	a = Point(x,y)    # in rectangular coordinates
	b = Point(r,phi)   # in polar cooordinates.

	'''


	a = all([arg is not None for arg in NotNoneArgs])
	if len(NoneArgs) == 0:
		return a
	else:
		return a and all([arg is None for arg in NoneArgs])


#	a = all([arg != None for arg in NotNoneArgs])
#	#a = (NotNoneArgs != None) # all the elements ARE != None
#	if len(NoneArgs) == 0:
#		return a
#	else:
#		return a and all([arg ==None for arg in NoneArgs])
#		#return a and (NoneArgs == None)

def Oversample(x = np.array([]), N=1):
	'''
	Adds sampling points in the x vector.
	E.g. Oversample([0,1], N=1) => [0, 0.5,1]
	Preserves x[0] and x[end]
	'''
	x = np.array([])
	for i, xi in enumerate(x):
		x = np.append()

#def CombinedRange(ListOfTuples, UseLinspace = False):
#	'''
#	ListOfTuples is a list of tuples containing the parameters
#	of the scansion. Each tuple is in the form
#
#	( (Start, Stop, A) (Value) ) or
#	( (Start, Stop, A) (StartValue, StopValue))
#
#	The N of samples of the second variables are the same of the firs one.
#
#	if UseLinspace = True, then Step is the number of samples, and the
#	np.linspace function is called instead.
#
#	'''
#	# preconditioning
#	if type(ListOfTuples) is list:
#		pass
#	else:
#		ListOfTuples = list(ListOfTuples)
#
#	if UseLinspace:
#		RangeFunction = np.linspace
#	else:
#		RangeFunction = np.arange
#
#	for iTuple, Tuple in ListOfTuples:
#
#		for iSubtuple, Subtuple in
#		Start = Tuple[0]
#		Stop = Tuple[1]
#		A = Tuple[2]
#		Array = list(RangeFunction(Start,Stop,A))
#		N = len(Array)





	pass
#================================
#  SamplingOverLine
#================================
def SamplingAlongLine(Theta, XYCentre, Length, NSamples = None, Step = None):
	'''
	Samples a line of angle Theta centred at XYCentre with a given Step.

	I created the function for properly sampling a plane or elliptical mirror.
	It makes sense to use this one for sampling an elliptical mirror if the
	figure error is measured with an LTP profilometer (uniform spacing along
	a railw)
	Either the total Length or the Number of samples NSamples must be specified

    Parameters
    ----------
	Theta :
		angle (radians)
	XYCentre :  2d array
		(x,y) centre of the line
	Step : float
		distance between two samples (along the linge)
	Length : float
		total length to cover (along the line)
	NSamples : int
		(alternative to Length), number of samples

	'''

	m = np.tan(Theta)
	q = XYCentre[1] - m*XYCentre[0]
	L_ = abs(Length * np.cos(Theta)	)
	x_start = XYCentre[0] - L_/2
	x_end = XYCentre[0] + L_/2

	if  Step!= None and Step >0:
		N = Length/Step
	elif NSamples !=None and NSamples > 0:
		N = NSamples

	x = np.linspace(x_start, x_end, N)
	y = m*x+q
	return x,y
#================================================================
#  RMat
#================================================================
def RMat(Theta):
	'''
	Returns the rotation matrix for an angle Theta.
	'''
	return [[cos(Theta), -sin(Theta)],
				[sin(Theta), cos(Theta)]]

#================================================================
#  RotXY
#================================================================
def RotXY(x,y, Theta = 0, CentreOfRotation = np.array([0,0])):
	'''
	Rotates the arrays x (1d) and y (1d) of Theta AROUND the CentreOfRotation

	Parameters
	----------------
	x : 1d array
		x coordinates
	y : 1d array
		y coordinates
	Theta : scalar (rad)
		Rotation angle
	CentreOfRotation : [x,y]
		Point around which the rotation is performed.By default is set to [0,0]

	Returns
	-----------------
	x : rotated x

	y : rotated y

	Examples
	----------------
	>>> import numpt as np
	>>> RotXY(0,1,45 * np.pi/180)
	>>> Out[12]: (array([-0.70710678]), array([ 0.70710678]))
	'''
	if Theta == 0:
		return (np.array(x), np.array(y))
	Theta = -Theta # non so perch?? il -1, odio le matrici di rotazione.
	Vxy = np.column_stack((x,y))
	U  = dot(Vxy - CentreOfRotation, RMat(Theta)) + CentreOfRotation
	return (U[:,0], U[:,1])

#================================================================
#  RotPoly
#================================================================
def RotPoly(P, NewOrigin = np.array([0,0]), Angle = 0, Deg = False):
	'''
	Returns the coefficients of the rotated polynomial in the
	Parameters
	----------------------
	P : 1d-array
		Polynomial coefficients [x^n .... n^0]
	NewOrigin : 1x2 array
		[x,y] of the new origin
	Angle : scalr ( rad)
		Rotation Angle
	'''
	P = np.array(P)
	N =   len(P)-1 # degree of the polynomial
	if N <1:
		print('Errror: Polynomial order too low (<1), finding coefficient is useles...')
		return None

	x = np.linspace(0,N, N+1)
	y = np.polyval(P,x)

	x_new, y_new = RotXY(x,y, Angle ,NewOrigin)

	# Polynomial fit
	P_new = np.polyfit(x_new, y_new, N)
	P_new2 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
#	P_new3 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
	return P_new2

#================================================================
#  RotPoint
#================================================================
def RotPoint(XY, Theta = 0, CentreOfRotation = np.array([0,0])):
	'''
	The same as RotXY, but with input (x1, y1) intead of
	[x1...xn] , [y1 ... yn]
	'''
	(x,y) =  RotXY(XY[0], XY[1], Theta = Theta, CentreOfRotation = CentreOfRotation)
	return np.array([x, y])

#================================================================
#  RotVersor
#================================================================
def RotVersor(V, Angle, Deg = False):
	'''
	Rotate the versor V = (Vx, Vy)

	'''
	if Deg== True:
		Angle = Angle * np.pi/180

	if (Angle == 0) or np.linalg.norm(V)==0:
		return V
	else:
		U = RotXY(V[0], V[1], Angle)
		return np.array([U[0][0], U[1][0] ])

#================================
#  Normalize
#================================
'''
Normalize an array
'''
def Normalize(v):
	v = np.array(v)
	return v/norm(v)

def NormAmp(x):
	'''

	'''
	a = max(x)
	b = min(x)
	return (x-b) /(a-b)
#================================
#  UnitVectorNormal
#================================
def UnitVectorNormal(v, Sign = +1):
	'''
	Performs a rotation of Sign * pi/2 of v.

	>>> return  rm.RotXY(v, Sign * np.pi/2)
	'''
	nx,ny = RotXY(v[0], v[1], Sign * np.pi/2)

	nx = 0 if abs(nx) < 1e-16 else nx[0]
	ny = 0 if abs(ny) < 1e-16 else ny[0]
	return np.array([nx,ny])
#================================
#  UnitVectorReflect
#================================
def UnitVectorReflect(v, n):
	'''
	Parameters
	-------------
	v : vector-like (vx,vy)
		Unit vector of the incident beam
	n : vector-like
		normal of the mirror surface


	v and n should be unit vectors. If they are not, they are automatically
	normalized.
	'''
	v = np.array(v) # vector to be reflected
	n = np.array(n) # versor normal to the surface
	v = v / norm(v)
	n = n / norm(n)

	t = np.dot(n,v); # scalar product
#		print(v)
#		print(n)
#		print(norm(v))
#		print(norm(n))
#		print(t)
	if t >= 0:
	  u = v;
	else:
	  u = v - 2 * n * t;
	return u

#================================
#  FitSphericalWave
#================================
def FitSphericalWave1d(Phi,s, Lambda):
	'''

	Performs the quadratic fit over the phase Phi and returns the curvature
	Radii.

	Interpolation kernel copied from:
	From: http://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html

	Parameters
	-----
	Phi : array like
		phase of the spherical wave

	s : array
		coordinate points.

	'''
	x = s
	y = Phi * Lambda/2/np.pi # convertion from phase to heigth profile

	from scipy import optimize
	method_2 = "leastsq"
	# coordinates of the barycenter
	x_m = np.mean(x)
	y_m = np.mean(y)

	def calc_R(xc, yc):
	    """ calculate the distance of each 2D points from the center (xc, yc) """
	    return sqrt((x-xc)**2 + (y-yc)**2)

	def f_2(c):
	    """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
	    Ri = calc_R(*c)
	    return Ri - Ri.mean()

	center_estimate = x_m, y_m
	center_2, ier = optimize.leastsq(f_2, center_estimate)

	xc_2, yc_2 = center_2
	Ri_2       = calc_R(*center_2)
	R_2        = Ri_2.mean()                  #_2 is because this is method#2 from the url I copied from.
	residu_2   = sum((Ri_2 - R_2)**2)
#	residu2_2  = sum((Ri_2**2-R_2**2)**2)
#	ncalls_2   = f_2.ncalls


	return R_2

#================================
#  FitGaussian1d
#================================
def FitGaussian1d(y, x = None, PlotFigure=None):
	'''
	Easy way for fitting gaussian curve.

	It's quick and dirty, but it should work

	Returns
	----
	[a, x0, sigma] : Amplitude, mean value, standard deviation
	'''
	from scipy.optimize import curve_fit
	from scipy import exp
	# HELPER FUNCTION
	def gaus(x,a,x0,sigma):
		return a*exp(-(x-x0)**2/(2*sigma**2))
	#------------------------------------------
	n = len(y)
	if x is None:
		x = np.arange(0,N)

	mean = sum(x*y)/n
	sigma = np.sqrt(sum(y*(x-mean)**2)/n)
	amplitude = max(y)
	try:
		popt,pcov = curve_fit(gaus,x,y,p0=[amplitude,mean,sigma])
		popt[2] = abs(popt[2])




		# Plot figure if required
		if PlotFigure!= None:
			if PlotFigure> 1:
				plt.figure(PlotFigure)
				plot(x,y)
				xfit = np.linspace(min(x), max(x), 100)
				yfit = gaus(xfit,popt[0], popt[1], popt[2])
				plot(xfit,yfit,'o')

		return popt
	except:
		return np.nan, np.nan, np.nan
#================================
	#  Coerce
   #================================
def Coerce(x, Min, Max):
	return Min if x < Min else Max if x > Max else x

#================================
#  L2XY
   #================================
def L_2_XY(f, L, XStart,  Sign = +1, Tolerance = 1e-3, GuessStep = 1e-4, iMax = 1e5):
	'''
	For a given function y = f(x) and a starting point XStart,
	it finds the point XEnd such that the length of the curve
	f(x) from XStart to XEnd equals L

	We have originally written it for accurately finding the XStart, XEnd points of
	an elliptic mirror.

	'''

	# Single path integral
	XStep = GuessStep * Sign
	XOld = XStart
	YOld = f(XStart)
	i=0
	LSum = 0
	while True:
		XNew = XOld + XStep
		YNew = f(XNew)[0]
		DeltaL = norm(np.array([XNew, YNew])- np.array([XOld, YOld]))
		LSum = LSum + DeltaL

		i = i+1

		if LSum >= L: # raggiunta la lunghezza
			if (LSum - L) > Tolerance:
				# ripeti con step pi?? piccolo
				pass #???
			else:
				return (XNew, YNew)
		else: # da rifare
			if i >= iMax:
				return None
			pass
	pass







#================================
#  MinHew
#================================
def MinHew(Hew, Threshold = 1e-15):
	'''
	Rough way of finding the minimum value of the Hew, without fitting.
	Finds the minimum. If different values are repeated, then the central element
	is chosen.

	Equality is to the best of Threshold

	'''
	iMin = np.argmin(Hew) # position of the minimum
	Delta = Hew - Hew[iMin]  # differences.
	Bools = Delta < Threshold
	# find the first True value
	First = next(i for i in range(len(Bools)) if Bools[i]  == True)
	Last = next(i for i in np.arange(len(Bools)-1,-1,-1) if Bools[i]  == True)

	#Performs a quadratic fit

	return int(np.floor( (First + Last)/2))



#================================
#  FitParabola
#================================
def FitParabola(x, y ):
	"""
	Helper function that performs a parabolic fit on x,y and returns
	the parabola parameter in a common fashion

	Parameters
	-----
	x : array
		x
	y : array
		y

	Return
	------
	Struct containing:
		a,b,c,Focus, Vertex

	"""

	class Output:
		a = None
		b = None
		c = None
		Focus = None
		Vertex = None

	#Performs a quadratic fit
	p = np.polyfit(x,y,2)
	a = p[0]
	b = p[1]
	c = p[2]
	Delta = b**2  -4*a*c

	xv = -b/2/a           # Vertex
	yv = -Delta/4/a

	xf = -b/2/a           # focus
	yf = (1-Delta)/a/a ;

	Output.a = a
	Output.b = b
	Output.c = c
	Output.Focus = np.array([xf,yf])
	Output.Vertex= np.array([xv,yv])

	return Output
#================================
#  FindWaist
#================================
def FindWaist(W, Z = None, Threshold = 1e-15):
	'''
	Find the waist of the beam of transverse size W and longitudinal axis Z.

	Parameters
	-----
	W : array like (y-like)
		Beam size, typically the HEW (or the sigma, or whatever). It must have
		a local minimum

	Z : array like (x-like)
		longitudinal coordinate

	Return
	-----
	NumericWaist : (position, size)
		coordinates of the minimum of (W,Z) found as the minimum value of W

	FittedWaist : (position, size)
		coordinates of the minimum of (W,Z) computed with a parabolic fit

	'''
	iMin = np.argmin(W) 	       # position of the minimum
	Delta = W - W[iMin]        # differences.
	Bools = Delta < Threshold

	# find the first True value
	First = next(i for i in range(len(Bools)) if Bools[i]  == True)
	Last = next(i for i in np.arange(len(Bools)-1,-1,-1) if Bools[i]  == True)
	#Min: is the Min Value
	MinIndex = int(np.floor( (First + Last)/2))    # position of the central minimum
	MinValue = W[MinIndex]
	MinZ = Z[MinIndex] if Z is not None else MinValue

	#Fit = FitParabola(Z,W) # old way
	#MinFitValue = Fit.Vertex[1]
	#MinFitZ = Fit.Vertex[0]
	#NumericWaist = (MinZ, MinValue)

	# Find waist by gaussian fit
	#----------------------------------------------------------
	'''I pick the N boundaries values close to the minimum value
	'''

	x_to_fit = Z
	y_to_fit = W

	try:
		Fit = sp.interpolate.splrep(x_to_fit, y_to_fit, s = 0)
		x_new = np.linspace(x_to_fit[MinIndex - 3], x_to_fit[MinIndex + 3], 100)
		y_new = sp.interpolate.splev(x_new, Fit)
		# I find the numeric minimum of the spline
		Min_i = np.argmin(y_new)
		Min_y = y_new[Min_i]
		Min_x = x_new[Min_i]
		MinFitZ = Min_x     #redundant assignment (for clarity)
		MinFitValue = Min_y  #redundant assignment (for clarity)
	except:
		MinFitZ = MinZ
		MinFitValue = MinValue
	NumericWaist = (MinZ, MinValue)
	FittedWaist = (MinFitZ, MinFitValue)


	return NumericWaist, FittedWaist




#==============================================
#FUN MatrixSaveWithHeader
#==============================================
def MatrixSave(FileName, A, x = None, y = None, Format = '%.18e'):
	'''
	Save a file containing a Matrix Z, the arrays X,Y representing the axis.
	If required, prepends to the data section an header section containing
	labels and unit of the data contained.

	'''
#==============================================
#FUN SaveMatrix
#==============================================
def SaveMatrix(FileName, A, x = None, y = None, Format = '%.18e'):
	"""
	Save a Matrix (NxM) into a txt file.
	If wanted, the axes x and y are saved as well.

	The final output is
	A11 A12 ... A1N
	...
	AM1 AM2 ... AMN

	if x and y are None

	or

	NaN x1   x2 ...  xN
	y1  A11 A12 ... A1N
	...
	yM  AM1 AM2 ... AMN

	if x and y are specified.

	Parameters
	------------
	A : NxM matrix
		input matrix
	x : 1d array
		long M
	y : 1d array
		long N
	"""
	# Ensures that the path exists
	PathCreate(FileName,True)

	if x is  None and y is None:
		AAA = A
	else:
		RowName = x
		ColName = np.insert(y,0,None )
		AA = np.vstack((RowName, A))
		AAA = np.column_stack([ColName, AA])

	np.savetxt(FileName,AAA, fmt = Format)

#================================
#  PhaseUnwrap
#================================
#def PhaseUnwrap(Ph):
#	N = len(Ph)
#	PhNew = 0 * Ph
#
#	Ph = Ph - Ph[0]
#	for (i,phi) in enumerate(Ph):
#		if i=0:
#			continue
#		else:
#			pass
#
#
#


def MirrorArray(x, Factor = +1):
	'''
	given x = [0,1,2]

	returns y = [2,1,0,1,2] if MakeNegate = False or
		y = [2,1,0,1,2] if MakeNegate = True
	'''

	x = np.array(x)
	return np.hstack(( Factor*x[-1:0:-1], x[:-1]))
def PowerSpectrum(x):
	return abs(np.fft.fft(x, norm = 'ortho'))**2
def SlitCreate(SizeN, NSlits = 1, SlitKernel = [1]):
	'''
	This function was first created for simulating the diffraction from 2 or more slits.

	Parameters
	----
	SizeN : the total size (in samples) of the mask,

	NSlits : the total number of slits (1,2, etc...)

	SlitKernel : the transmission function of each slit. Can be complex.

	Example: create an array with 20 elements, 2 slits, each one 3 pixel large.
	SlitCreate(20,2, [1,1,1]).


	'''

	fList =np.floor(np.linspace(0,SizeN, NSlits+2)[1:-1])
	iList = [int(f) for f in fList]
	A = np.zeros([SizeN])  # the total domain of the signal
	A[iList] = 1 # the 'lattice' position of the signal (e.g. locations of the slits)
	K = np.array(SlitKernel) # the kernel function (e.g. slit width)
	S = np.convolve(A,K)
	return S

class geom:

	#================================
	#  PointsToLine
    #================================
	@staticmethod
	def PointsToLine(x0,y0,x1,y1):
		'''
		Returns
		--------
		m, q
		Line equation y=m*x+q
		'''
		x = [x0,x1]
		y = [y0,y1]

		p = np.polyfit(x,y,1)
		q = p[0]
		m = p[1]
		return m,q


#	def PolarToLine(x0, y0, angle):
#		m = np.atan(angle)
#		return m,q

	#================================
    #  StepAlongLine
    #================================
	@staticmethod
	def StepAlongLine(step, m,q, x0 = 0 , sign = +1):
		'''
		Returns
		-----------------
		x_end, y_end
		'''
		y0 = m*x0 + q
		a = 1+m**2
		b = -2*x0 - 2*y0*m + 2*m*q
		c = -step**2 + x0**2 + y0**2 +q**2 - 2*y0*q

		x = (-b + sign* np.sqrt(b**2 - 4*a*c))/2/a
		y = m*x+q

		return x,y

	 #================================
    #  StepAlongDirection
    #================================
	@staticmethod
	def StepAlongDirection(x0 , y0, step, angle,  sign = +1):
		'''
		Parameters
		----------
		step : length of the movement
		angle : inclination angle (radians)
		x0, y:origin : points
		'''
		# horizontal displacement
		if (angle == 0) or (angle == np.pi) :
			if angle == np.pi:
				sign = sign * -1 ;
			x = x0 + step*sign
			y = y0

		# vertical displacement
		elif	(angle == np.pi/2) or (angle == - np.pi/2) :
			if angle == - np.pi/2:
				sign = sign* -1
			x = x0
			y = y0 + step*sign

		# generic displacement
		else:
			m = np.tan(angle)
			q =   -m* x0 + y0
			angle_mod = np.mod(angle, 2 * np.pi)
			if (0 <= angle_mod <= np.pi /2) or (3/2*np.pi < angle_mod <= 2 * np.pi):
				sign = 1*sign
#				print('sign kept')
			else:
				sign = -1*sign
#				print('inverto segno')

			x,y = geom.StepAlongLine(step, m,q,x0, sign)
		return x,y
	#================================
    #  IntersectLine
    #================================
	@staticmethod
	def IntersectLine(Poly1,Poly2):
		'''
		Intersects two lines.
		-------------
		Poly1 and Poly2  are in the form [m, q]
		where the line equation is :math:`y = m x + q`.

		Returns
		------------
		x, y : scalars
			Point of intersection.
		'''
		x0 = (Poly2[1] - Poly1[1])/(Poly1[0] - Poly2[0])
		y0 = Poly1[0] * x0 + Poly1[1]

		return (x0,y0)



	#================================
	#  UnitVectorNormal
	#================================
	@staticmethod
	def UnitVectorNormal(v, Sign = +1):
		'''
		Performs a rotation of Sign * pi/2 of v.

		>>> return  rm.RotXY(v, Sign * np.pi/2)
		'''
		nx,ny = RotXY(v[0], v[1], Sign * np.pi/2)

		nx = 0 if abs(nx) < 1e-16 else nx
		ny = 0 if abs(ny) < 1e-16 else ny
#		print 10 * '==='
#		print(nx)
#		print (ny)
		return np.array([nx,ny])

	#================================
	#  UnitVectorReflect
	#================================
	@staticmethod
	def UnitVectorReflect(v, n):
		'''
		Parameters
		-------------
		v : vector-like
			Unit vector of the incident beam
		n : vector-like
			normal of the mirror surface


		v and n should be unit vectors. If they are not, they are automatically
		normalized.
		'''
		v = np.array(v)
		n = np.array(n)
		v = v / norm(v)
		n = n / norm(n)

		t = np.dot(n,v);
#		print(v)
#		print(n)
#		print(norm(v))
#		print(norm(n))
#		print(t)
		if t >= 0:
		  u = v;
		else:
		  u = v - 2 * n * t;
		return u


#
#		Angle1 = np.arctan(m1)
#		# incident ray
#		Ray0 = geom.Ray(Angle0, [x0,y0])

#		# intersection
#		(x2, y2) = geom.IntersectLine([Ray0.m, Ray0.q], [m1,q1])
##		q3 = x2 * (m1**2 + 1)\m1 + q1
#
#		Angle2 = 0*np.pi - Angle0 + Angle1
#		return x2, y2, Angle2

	#================================
	#  DrawCircle
	#================================
	@staticmethod
	def DrawCircle(R,x0=0,y0=0,N=100):
		an = np.linspace(0, 2*np.pi, 100)
		return R*np.cos(an), R*np.sin(an)

	#================================
    #  DrawSegment
    #================================
	@staticmethod
	def DrawSegment(x0,y0,x1,y1, N=2):
		'''
		Returns
		--------------
		x,y : 1d arrays containing the points of the segment.
		'''
		x = [x0,x1]
		y = [y0,y1]
		p = np.polyfit(x,y,1)
		x = np.linspace(x0,x1,N)
		y = np.polyval(p,x)
		return x,y

	#================================
    #  DrawSegmentCentred
    #================================
	@staticmethod
	def DrawSegmentCentred(L, x0, y0, Angle, N=2):
		xEnd,yEnd =     geom.StepAlongDirection(L/2, Angle, x0,y0, sign=+1)
		xStart,yStart = geom.StepAlongDirection(L/2, Angle, x0,y0, sign=-1)
		x,y = geom.DrawSegment(xStart,yStart,xEnd,yEnd,N)
		return x,y








#	#==============================================================================
#	#	 CLASS: Ray_old
#	#==============================================================================
#	class Ray_old(Line):
#		''' Essentially, a Ray object contains the coeffcient of a line + info about
#			the origin of the Ray + info about the end of the Ray, in the case of a
#			focussed beam.
#			Angles are expressed in radians
#			Theta
#			q, XYStart,
#			Lenght
#			XYEnd
#		'''
#		#======================
#		#	 __init__
#		#======================
#		def __init__(self, Angle = None, XYOrigin = np.array([0,0])):
#
#			if CheckArg([Angle,XYOrigin]):
#				self.Angle = Angle
#				self.XYOrigin = XYOrigin
#				self._UpdateVersor()
#			else:
#				pass
#
#
#		#======================
#		#	 Angle
#		#======================
#		@property
#		def Angle(self):
#			return self._Angle
#		@Angle.setter
#		def Angle(self, Val):
#			if Val != None:
#				self._Angle= Val
#				self._m = np.tan(self._Angle)
#
#		#======================
#		#	 m
#		#======================
#		@property
#		def m(self):
#			return self._m
#		@m.setter
#		def  m(self, val):
#			if val!=None:
#				self._m = val
#				self._Angle= np.arctan(val)
#
#		#======================
#		#	 q
#		#======================
#		@property
#		def q(self):
#			return self._q
#		@q.setter
#		def q(self, val):
#			self._q = val
#
#
#		#======================
#		#	 XYOrigin
#		#======================
#		@property
#		def XYOrigin(self):
#			return self._XYOrigin
#		@XYOrigin.setter
#		def	XYOrigin(self,XY):
#			if XY== None : exit
#			self._XYOrigin = XY
#			self._q = XY[1] - self.m * XY[0]
#
#		#======================
#		#	 Draw
#		#======================
#		def Draw(self,L, N=100):
#			"""
#			Returns the x,y arrays of points which can be used to plot the ray.
#
#			Paramteres
#			-----------------
#			L : scalar
#				Length of the ray to plot
#			N : int
#				Number of samples
#
#			Returns
#			-----------------
#			x : 1darray
#				List of x points
#			y : 1darray
#				List of y points
#
#			"""
#
#			XYList = np.array([geom.StepAlongDirection(self.XYOrigin[0],
#									self.XYOrigin[1], L/i, self.Angle) for i in range(1,N+1)])
#			return XYList[:,0], XYList[:,1]
#
#	#================================
#    #  RayReflectFromLine
#    #================================
#	@staticmethod
#	def RayReflectFromLine(Ray_in = Ray(), Line_mirror = Line()):
#		'''
#		RayReflectFromLine(Ray_in = Ray(), Line_mirror = Line())
#
#		Calculates the reflection of an (oriented) ray onto a line.
#		Subscripts 0 refer to incident ray, 1 to reflecting line, 2 to reflected ray.
#
#		Parameters
#		----------
#		Ray_in : Ray object
#			ray defining the incident bea,
#		Line:mirrror : Line object
#			Line defining the reflectiong "surface"
#
#		Returns
#		-------
#		Ray_out : Ray object
#			Ray defining the reflected beam
#		XYIntersection : 1x2 array
#			Contains the x,y coordinates of the intersection betweeen the line containing the
#			ray and the mirror line. If the ray is oriented such that the optical intersection
#			really occurs, the Intersect output is True. Else, it it is set to false
#		Intersects : bool
#			Says whether the ray impinges on the mirror line or not.
#		More
#		-------
#		This is the basis for the reflection operations.
#		It does not include
#		- check over the physical extension of the mirror
#		- reflection from "mirror" more other than rect.
#		'''
#
#		v_in = Ray_in.v
#		v_mir = Line_mirror.v
#
#		n_mir = rm.RotVersor(v_mir, np.pi/2)
#
#		scalar_product = np.dot(v_in, n_mir)
#		v_out = v_in - 2 * n_mir * scalar_product
#		Angle_out = np.arctan2(v_out[1], v_out[0])
#		# intersection
#		(out_x0, out_y0) = geom.IntersectLine([Ray_in.m, Ray_in.q],
#											 [Line_mirror.m,Line_mirror.q])
#
#
#		Ray_out = geom.Ray(Angle = Angle_out, XYOrigin = [out_x0, out_y0])
#
#		#TODO:SERIOUS
#		Intersect = None
#		if ((out_x0 < np.sign(v_in[0])*Ray_in.XYOrigin[0]) or
#			(out_y0 < np.sign(v_in[1])*Ray_in.XYOrigin[1])):
#			Intersect = False
#		else:
#			Intersect = True
#		return Ray_out, out_x0, out_y0, Intersect
##----------------------------------------------------------


#==============================================================================
#	 CLASS: Line
#==============================================================================
class Line(object):
	'''
	Attributes
	-------------------------
	m : scalar
		slope
	q : scalar
		intercept
	Angle : scalar (rad)
		rotation angle, defined as Angle = arctan(m)
	Versor : 1x2 array
		Versor defining the direction of the line
	VersorN : 1x2 array
		Versor defining the normal diretion to the line

	'''
	def __init__(self, m= None, q = None, Angle=None):

		if CheckArg([m,q]):
			self.q = q
			self.m = m
			self._UpdateVersor()
		elif CheckArg([Angle,q]):
			self.q = q
			self.Angle= Angle
			self._UpdateVersor()
		else:
			pass
		#calculates the versor according to the rotation angle used

	#======================
	#	 Angle
	#======================
	@property
	def Angle(self):
		return self._Angle
	@Angle.setter
	def Angle(self, Val):
		self.Angle = Val
		self._m = np.tan(Val)

	#======================
	#	 m
	#======================
	@property
	def m(self):
		return self._m
	@m.setter
	def  m(self, val):
		self._m = val
		self._Angle = np.arctan(val)

	#======================
	#	 q
	#======================
	@property
	def q(self):
		return self._q
	@q.setter
	def q(self, val):
		self._q = val

	#======================
	#	 v
	#======================
	@property
	def v(self):
		'''
		Versor defining the direction along the Line
		'''
		return self._Versor
	#======================
	#	 vNorm
	#======================
	@property
	def vNorm(self):
		'''
		Versor defining the direction normal to the line
		'''
		return self._VersorN

	#======================
	#	 _UpdateVersor
	#======================
	def _UpdateVersor(self):
		'''

		'''
		self._Versor = RotVersor([1,0], self.Angle)
		self._VersorN = RotXY(self._Versor, np.pi/2)

	#======================
	#	 Draw
	#======================
	def Draw(self,xStart, xEnd, N=100):
		"""
		Returns the x,y arrays of points which can be used to plot the Line.

		Paramteres
		-----------------
		xStart : scalar
			Start x Value
		xEnd : scalar
			End x value

		N : int
			Number of samples

		Returns
		-----------------
		x : 1darray
			List of x points
		y : 1darray
			List of y points

		"""
		x = np.linspace(xStart, xEnd, N)
		y = self.m * x + self.q
		return x,y

#==============================================================================
#	 CLASS: Segment
#==============================================================================
class Segment(Line):

	#======================
	# FUN: __init__
	#======================
	def __init__(self, x0,y0,x1,y1):
		m,q = geom.PointsToLine(x0,y0,x1,y1)
		Line.__init__(self,m=m, q=q)
		self._XYStart = np.array([x0,y0])
		self._XYEnd = np.array([x1,y1])

	#======================
	# PROP:	 XYStart
	#======================
	@property
	def XYStart(self):
		return self._XYStart
	@XYStart.setter
	def XYStart(self,val):
		self._XYStart = val
		# "joins" the new XYStart with the stored XYEnd, and updates the other
		# variables
		m,q = geom.PointsToLine(self._XYStart[0], self._XYStart[1], 												self._XYEnd[0], self._XYEnd[1])

	#======================
	# PROP:	 XYEnd
	#======================
	@property
	def XYEnd(self):
		return self._XYEnd
	@XYEnd.setter
	def XYEnd(self,val):
		self._XYEnd = val
		# "joins" the stored XYStart with the NEW XYEnd, and updates the other
		# variables
		m,q = geom.PointsToLine(self._XYStart[0], self._XYStart[1], 												self._XYEnd[0], self._XYEnd[1])
		self.q = q
		self.m = m

	#======================
	# METHOD:	 __Draw
	#======================
	def __Draw(self,N=2):
#			return geom.DrawSegment(XYStart[0],XYStart[0], XYEnd[0],XYEnd[1])
		pass
#==============================================================================
#	 CLASS: Vector
#==============================================================================
class Vector(object):
	'''
	The unit vector is automatically normalized to unit norm, basing on the inputs
	parameters.

	Set of Parameters 1
	-------------------
	x : x component

	y : y component

	Set of Parameters 2
	-------------------
	Angle : Angle (radians)

	Set of Parameters 3
	-------------------
	V : a Vector object

	Set of Parameters 4
	-------------------
	v : a v = [vx,vy] type

	'''

	#================================
	# FUN: __init__
	#================================
	def __init__(self,
				vx = None, vy = None,
				v = None, # [vx,vy] array
				V = None, # a vector object
				Angle = None,
				XYOrigin = [0,0], Length = 1, IsUnitVector = False):

		self._IsUnitVector = IsUnitVector
		self.XYOrigin = XYOrigin         # Set it now, not later

		if CheckArg([vx,vy]):
			if (vx!=0 or vy !=0):
				self.v = [vx,vy] # _v is assigned
			else:
				self._ZeroLength() # _v is assigned
		elif CheckArg([v]):
			self.v = v          # _v is assigned

		elif CheckArg([Angle, Length]):
			if Length >0:
				self.v = RotVersor(np.array([1,0]) *Length, Angle)  # _v is assigned
			else:
				self._ZeroLength()    # _v is assigned
		else:
			print ('Vecor Init Wrong Argument set')



		if self.Length > 0:
			self._vNorm = UnitVectorNormal(self.v)
		else:
			self._vNorm = None

		if IsUnitVector == True:
			self.v = Normalize(self.v)


	#======================
	# FUN: __str__
	#======================
	def __str__(self):
		StrMsg = (' V = [%f,%f]\n Angle=%0.2f  deg\n XYOrigin=[%f,%f]' %
				(self.v[0], self.v[1], (self.Angle * 180/np.pi),
				self.XYOrigin[0], self.XYOrigin[1]))
		return StrMsg
	#======================
	# FUN: _ZeroLength
	#======================
	def _ZeroLength(self):
		'''
		The Vector is recognized to be degenerate; hence I set all the values accordingly.
		'''
		self._v = np.array([0,0])
		self.vAngle = 0
		self._vNorm = None
		self.XYEnd = self.XYOrigin

	#======================
	# PROP: v
	#======================
	'''
	v: is the numerical array containing the components
	'''
	@property
	def v(self):
		return self._v
	@v.setter
	def v(self, value):
		vx = value[0]
		vy = value[1]
		# Normalize to unity?
		L2 = 1 if self._IsUnitVector == False else 	 vx**2 + vy**2
		self._v = np.array([vx/L2, vy/L2])
		self._vAngle = np.arctan2(self._v[1],self._v[0])

	#======================
	# PROP: vAngle
	#======================
	@property
	def vAngle(self):
		return self._vAngle
	@vAngle.setter
	def vAngle(self, value):
		self._v = RotVersor(np.array([1,0]) *self.Length, value)  # don't use self.Lenght (it bases on ._v)
		self._vAngle = value

	#======================
	# PROP: Angle
	#======================
	@property
	def Angle(self):
		return self._vAngle
	@vAngle.setter
	def Angle(self, value):
		self._v = RotVersor([1,0], value)
		self._vAngle = value

	#======================
	# PROP: PolyCoeff
	#======================
	@property
	def PolyCoeff(self):
		'''
		Returns the coefficients of the 1st degree polynomial p =[m,q] (line equation)
		'''
		XYEnd = self.XYOrigin + self.v
		x = np.array([self.XYOrigin[0], XYEnd[0]])
		y = np.array([self.XYOrigin[1], XYEnd[1]])
		return np.polyfit(x,y,1)
	#======================
	# PROP: vNorm
	#======================
	@property
	def vNorm(self):
		return self._vNorm
	#======================
	# PROP: XYOrigin
	#======================
	@property
	def XYOrigin(self):
		return self._XYOrigin
	@XYOrigin.setter
	def XYOrigin(self, value):
		self._XYOrigin = np.array(value)

	#======================
	# PROP: XYEnd
	#======================
	@property
	def XYEnd(self):
		return self._XYOrigin + self._v
	@XYEnd.setter
	def XYEnd(self, value):
		self._Length = norm(value - self._XYOrigin)

	#======================
	# PROP: Length
	#======================
	@property
	def Length(self):
		try:
			 return np.linalg.norm(self._v)
		except:
			return 0
	#======================
	# METHOD: Rotate
	#======================
	def Rotate(self, Angle):
		'''
		Rotates the present Unit vector object by angle
		It is equivalent to the code

		>>> UnitVector.vAngle +=  Angle
		'''
		self.vAngle = self.vAngle + Angle


	#======================
	# PROP: VersorNor
	#======================
	@property
	def VersorNorm(self):
		''' Returns a UnitVector object which is normal to this objkect'''
		import copy
		_Versor = copy.deepcopy(self)
		_Versor.Rotate(+pi/2)
		return _Versor

	#======================
	# METHOD: GetNormal
	#======================
	def GetNormal(self):
		'''
		Returns another vector which is normal to the present one.
		It is equivalent to rotate of +pi/2

		>>> UnitVector.vAngle +=  Angle
		'''
		import copy
		_v = copy.deepcopy(self)
		_v.Rotate(+pi/2)
		return _v
	#======================
	# METHOD: Paint
	#======================
	def Paint(self, FigHandle = None,  Length = 0.3, ArrowWidth = 0.3,
		   Color = 'k', Shift = False):
		plt.figure(FigHandle)
		ax = plt.axes()
		ArrowLength = 1.5 * ArrowWidth
		XYEnd = self.XYOrigin +  self.v
		ShiftX = 0 if Shift == False else -np.cos(self.Angle)*(Length + ArrowLength)
		ShiftY = 0 if Shift == False else -np.sin(self.Angle)* (Length+ArrowLength)
		x0 = self.XYOrigin[0] + ShiftX
		y0 = self.XYOrigin[1] + ShiftY
		x1 = XYEnd[0] + ShiftX
		y1 = XYEnd[1] + ShiftY

		ArrowWidth = 0.5 * Length if ArrowWidth == None else ArrowWidth

		ax.arrow(x0,y0,Length*(x1-x0), Length*(y1-y0),
				   head_width = ArrowWidth, head_length= ArrowLength,
								   fc=Color, ec=Color)
#============================================================================
#	 CLASS: UnitVector
#==============================================================================
class UnitVector(Vector):
	def __init__(self,  vx = None, vy = None,
				v = None,
				V = None,
			   Angle = None, XYOrigin = [0,0]):
		Vector.__init__(self,  vx = vx, vy= vy, v = v, V = V ,
				  Angle = Angle, XYOrigin = XYOrigin,
				  IsUnitVector = True)

#============================================================================
#	 CLASS: Ray
#==============================================================================
class Ray(Vector):
	#======================
	# FUN: __init__
	#======================
	def __init__(self, x0 = None,y0 = None ,x1 = None ,y1 = None,
					XYOrigin = None, Angle = None, FocalLength = float('inf'), Length = 1,
					vx = None, vy = None	):
		'''
		Parameters Set
		---------------------------------

		'''

		# Parameter Set 1
		if CheckArg([x0,y0,x1,y1]):
			# Store input
			Vector.__init__(self, vx = x1-x0, vy = y1-y0, IsUnitVector = True )

		# Parameter Set 2
		elif CheckArg([XYOrigin, Angle]):
			# Store input
			Vector.__init__(self, Angle=Angle, XYOrigin = XYOrigin, IsUnitVector = True  )
			self.XYOrigin = XYOrigin
		elif CheckArg([vx, vy]):
			Vector.__init__(self, vx = vx, vy = vy, IsUnitVector = True )
		elif all([Arg == None for Arg in [x0,y0,x1,y1,XYOrigin, Angle,FocalLength]]):
#				print('Ray.__init__ : empty Ray was initialized')
#				raise ValueError('A very specific bad thing happened')
			pass
		else:
			print('Ray.__init__ : a wrong combination of arguments was used')
			raise ValueError('A very specific bad thing happened')
 			# Update further parameters (common procedure)

		#self.XYOrigin = [0,0] if XYOrigin == None else XYOrigin
		self.XYOrigin = [0,0] if XYOrigin is None else XYOrigin
		self.FocalLength = FocalLength

	#======================
	# PROP: UnitVectorAtOrigin
	#======================
	@property
	def UnitVectorAtOrigin(self):
		return UnitVector(v = self.v)


	#======================
	# PROP: Length
	#======================
	@property
	def Length(self):
		return norm(self.v)

	#======================
	# PROP: Norm
	#======================
	@property
	def Norm(self):
		return norm(self.v)
	#======================
	# PROP: XYEnd
	#======================
	@property
	def Norm(self):
		return norm(self.v)

	#======================
	# PROP: FocalLength
	#======================
	@property
	def FocalLength(self):
		return norm(self._FocalLength)
	@FocalLength.setter
	def FocalLength(self, value):
		value = float('inf') if value == None else value
		self._FocalLength = value
		self._XYFocus = self._XYOrigin + self._FocalLength * Normalize(self.v) if self._FocalLength < float('inf') else float('inf')

	#======================
	# METHOD: Paint
	#======================
	def Paint(self, FigHandle = None, Length = None, ArrowWidth = 0.3,
			   Color = 'k', Shift = False):

		UV = UnitVector(v = self.v, XYOrigin = self.XYOrigin)
		_Length = Length = Length if Length != None else self.Length
		UV.Paint(FigHandle, _Length,
					  ArrowWidth = ArrowWidth, Color = Color, Shift = Shift)

	#======================
	#	 Draw
	#======================
	def Draw(self,L, N=100):
		"""
		Returns the x,y arrays of points which can be used to plot the ray.

		Paramteres
		-----------------
		L : scalar
			Length of the ray to plot
		N : int
			Number of samples

		Returns
		-----------------
		x : 1darray
			List of x points
		y : 1darray
			List of y points

		"""

		XYList = np.array([geom.StepAlongDirection(self.XYOrigin[0],
								self.XYOrigin[1], L/i, self.Angle) for i in range(1,N+1)])
		return XYList[:,0], XYList[:,1]

#============================================================================
#	 CLASS: Ray
#==============================================================================
class Ray_seminuovo(object):
	''' Essentially, a Ray object contains the coeffcient of a line + info about
	Theta
	q, XYStart,
	Lenght
	XYEnd
	'''

	#======================
	# FUN: __init__
	#======================
	def __init__(self, x0 = None,y0 = None ,x1 = None ,y1 = None,
					XYOrigin = None, Angle = None, FocalLength = None):
		'''
		Parameters Set
		---------------------------------

		'''

		self.v = [1,0]
		self.vNorm =[0,1]

		# Parameter Set 1
		if CheckArg([x0,y0,x1,y1]):
			# Store input
			self.XYOrigin = np.array([x0,y0])
			self.XYEnd = np.array([x1,y1])

			# Update other parameters	(specific)
			dx = x1-x0
			dy = y1-y0
			L2 = dx**2 + dy**2
			self._v = np.array([dx/L2, dy/L2])
			self.m, self.q = geom.PointsToLine(0,0,self.v[0],self.v[1])
			self.Angle = np.arctan(self.m)

		# Parameter Set 2
		elif CheckArg([XYOrigin, Angle]):
			# Store input
			self.Angle = Angle
			self.XYOrigin = XYOrigin

			# Update other parameters (specific)
			self.v = RotVersor([1,0], Angle)
			self.m = self.v[1]/self.v[0]
			self.q = XYOrigin[1] - self.m * XYOrigin[0]
		elif all([Arg == None for Arg in [x0,y0,x1,y1,XYOrigin, Angle,FocalLength]]):
#				print('Ray.__init__ : empty Ray was initialized')
#				raise ValueError('A very specific bad thing happened')
			pass
		else:
			print('Ray.__init__ : a wrong combination of arguments was used')
			raise ValueError('A very specific bad thing happened')
 			# Update further parameters (common procedure)
		self._vNorm = UnitVectorNormal(self.v)

	#======================
	# PROP: Length
	#======================
	@property
	def Length(self):
		return norm(self.v)

	#======================
	# PROP: Norm
	#======================
	@property
	def Norm(self):
		return norm(self.v)
	#======================
	# PROP: XYEnd
	#======================
	@property
	def Norm(self):
		return norm(self.v)


	#======================
	# METHOD: Paint
	#======================
	def Paint(self, FigHandle = None, ArrowWidth = 0.3):
		V = UnitVector(Angle = self.Angle, XYOrigin = self.XYOrigin)
		V.Paint(FigHandle, Length = self.Length,  ArrowWidth = ArrowWidth)

	#======================
	#	 Draw
	#======================
	def Draw(self,L, N=100):
		"""
		Returns the x,y arrays of points which can be used to plot the ray.

		Paramteres
		-----------------
		L : scalar
			Length of the ray to plot
		N : int
			Number of samples

		Returns
		-----------------
		x : 1darray
			List of x points
		y : 1darray
			List of y points

		"""

		XYList = np.array([geom.StepAlongDirection(self.XYOrigin[0],
								self.XYOrigin[1], L/i, self.Angle) for i in range(1,N+1)])
		return XYList[:,0], XYList[:,1]

#	def DrawCircle(x,y,R, x0, y0)
#%%
#import matplotlib.pyplot as plt
#plt.close('all')
#plt.axis('equal')
#xc,yc = geom.DrawCircle(1)
#plt.plot(xc,yc)
#plt.xlim(-5,5)
#plt.ylim(-5,5)
#

#========================================================
#	FUN: FileIO
#========================================================
class FileIO:


	#========================================================
	#	FUN: ReadYFile
	#========================================================
	def ReadYFile(Path,  SkipLines = 0):
		'''
		Behavior:
		-----
		Reads the y data formatted as a column.

		where N is len(y)
		'''
		with open(Path) as file:
			Lines = file.readlines()[SkipLines :]
		N = len(Lines)
		y = np.zeros(N)

		# format lines
		for (iLine, Line) in enumerate(Lines):
			Line = Line.strip()
			if Line != '':
				y[iLine] = float(Line)

		return y

	#========================================================
	#	FUN: ReadXYFile
	#========================================================
	def ReadXYFile(Path, Delimiter = '\t', SkipLines = 2):
		'''
		Behavior:
		-----
		Reads the x,y data formatted as a column
		'''
		with open(Path) as file:
			Lines = file.readlines()[SkipLines :]
		N = len(Lines)
		x = np.zeros(N)
		y = np.zeros(N)
		for (iLine, Line) in enumerate(Lines):
			Line = Line.strip()
			if Line != '':
				Tokens = Line.split(Delimiter)
				x[iLine] = float(Tokens[0])
				y[iLine] = float(Tokens[1])

		return x,y

	#==============================================
	# FUN SaveToH5
	#==============================================
	def SaveToH5b(FileName='output.hdf5', GroupNames=None, values=None):
		"""
		Save to hdf5 file.

		len(group_names) must be equal to len(values).

		group_names is a Python list, containing strings describing the i-th value
		in values list.

		values is a Python list, containing values corresponding to the i-th
		group_name. The elements can be of any shape and type, as long as they fit
		into a Python list

		Parameters
		------------
		FileName : string
			filename of the hdf5 output
		group_names : list
			group names in hdf5
		values : list
			values corresponding to group_names
		"""
		# Ensures that the path exists
		PathCreate(FileName, True)

		import h5py # For hdf5 files

		DataFile = h5py.File(FileName, 'w')

		for i, GroupName in enumerate(GroupNames):
			DataFile.create_dataset(GroupName, data=values[i])

		DataFile.close()

		return None

	#==============================================
	# FUN SaveToH5t
	#==============================================
	def SaveToH5(FileName='output.hdf5', GroupValueTuples = None,
			   Attributes = None,
			   ExpandDataContainers = True,
			   Mode = 'w'):
		"""
		Save to hdf5 file. "i" stands for "tuples", which is the data input data type.

		This function supports the *DataContainer* class. This means that:
			- If a valid h5 type is passed, it is saved.
			- A DataContainer object is passed, it is processed looking for the valid
				h5 types. The behavior is commanded by the flag: TryToExpandDataClasses.


		len(group_names) must be equal to len(values).

		Parameters
		------------
		FileName : string
			filename of the hdf5 output

		PathValueTuples : list of tuples
			List of tuples in the form (String to path, value)

		TryToExpandDataClasses : bool
			If true, Values of type 'type' are treated as data containers and an
			additional search is performed through them. The final path is given by
			the specified path + the new found attribute.

			Example:
			Tuple = ('Temperature', TemperatureInfo)
			and
			*TemperatureInfo.T = 12*
			*TemperatureInfo.Location = Trieste*
			*TemperatureInfo.Units = Celsius*

			Then the entries stored in the h5 file will be
			'Temerature/TemperatureInfo/T'
			'Temerature/TemperatureInfo/Location'
			'Temerature/TemperatureInfo/Units'

			**What if** it happens to have one more nesting level? E.g. ? *TemperatureInfo.AnotherDataStructure*

			In principle the stuff shall go on the same way... but we have to work on that.

			**CAVEAT** Such an introspection mechanism only exports the following data types:
				- int
				- float
				- numpy.ndarray
				- str

		Dev Notes
		------------
		Linked to Scrubs.DataContainer object for the advanced functionality of DataCointainer
		expasion

		"""
		PathValueTuples  = GroupValueTuples
		from Scrubs import ListAttr, ListAttrRecursive
		from LibWiser.Scrubs import DataContainer # otherwise the type match does not work properly
		# Ensures that the path exists
		PathCreate(FileName, True)

		import h5py # For hdf5 files

		DataFile = h5py.File(FileName, mode = Mode)

		# loop on each tuple in the form: (Path, Value)
		# Path is actually referred to as 'group'
		for i, Tuple in enumerate(PathValueTuples):
			GroupName = Tuple[0]
			Value = Tuple[1]

			# Performs DataContainer expansion
			if type(Value) == DataContainer and ExpandDataContainers:
				SubItems = Value._GetSubItems(Preset = 'mathstr')

				# Digest each SubItem and prepare it for being attached to the H5 output
				for SubItem in SubItems:
						SubGroupName = GroupName + '/' + SubItem[0]
						SubValue = SubItem[1]
						DataFile.create_dataset(SubGroupName, data=SubValue)



			# Do normal operations
			else:
				# This try block handle the case you are trying to modify a field (group) that
				# already exists.
				try:
					del DataFile[GroupName]
				except:
					pass

				DataFile.create_dataset(GroupName, data=Value)

		if Attributes is not None:
			Items = list(Attributes.items())
			for Attr in Items:
				DataFile.attrs[Attr[0]] = Attr[1]
#		DataFile.attrs = Attributes
		DataFile.close()

		return None

	SaveToH5t = SaveToH5

class CommonPlots:

	#=============================================================#
	# FUN FigureError
	#=============================================================#
	def FigureError(OpticalElement, Index = 0,  LastUsed = False,FigureIndex = None, **kwargs ):
		return Metrology.PlotFigureError(OpticalElement, Index = 0,  LastUsed = False,FigureIndex = None, **kwargs )

	#=============================================================#
	# FUN FigureError
	#=============================================================#
	def FigureErrorUsed(OpticalElement, Index = 0,  FigureIndex = None, **kwargs ):
		return Metrology.PlotFigureError(OpticalElement, Index = 0,  LastUsed = True ,
								   FigureIndex = None,
								   AppendToTitle = ' (Used in computation)', **kwargs )

	#=============================================================#
	# FUN RadiationAtOpticalElement
	#=============================================================#
	def RadiationAtOpticalElement(OptElement,
							   XUnitPrefix = 'm' ,
							   Normalize = False ,
							   FigureIndex = None,
							   Type = 'f',
							   AppendToTitle = '',
							   **kwargs ):
		'''
		Helper function. Plots the Radiation (either Intensity or the absolute value
		of the field) at a given OpticalElement.
		The functions IntensityAtOpticalElement and FieldAtOpticalElement are also
		available as well.

		Parameters
		------
		Normalize : bool/str
			- max : divides by Max values
			- sum : divides by sum of the input array
			- False : does nothing

		Type: string ['f'|'i']
			- 'f' : plots the Field (absolute value)
			- 'i' : plots the Intensity

		kwargs are redirected to the plot command. So you can use the label
		parameter to assign plot names

		'''
		try:
			x = OptElement.Results.S

			plt.figure(FigureIndex, **kwargs)

			if XUnitPrefix is None:
				XUnitPrefix = Units.GetSiUnitScale(x)
			XUnitScale = Units.SiPrefixes[XUnitPrefix]


			x = OptElement.Results.S / XUnitScale
			A  = abs(OptElement.ComputationData.Field)
			I = A**2

			# Switch y (Observable to plot)
			#------------------------------------------------------------
			if Type.lower() == 'i':
				y = I
				Title = 'Intensity @'
				YLabel = 'I'
			else:
				y = A
				Title = 'Field @'
				YLabel = '|E|'

			# Normalization
			#------------------------------------------------------------
			if bool(Normalize == True) or str(Normalize).lower() == 'max':
				y = y/max(y)
			elif (str(Normalize).lower() == 'total') or str(Normalize).lower() == 'sum':
				y = y/ np.sum(y)

			else:
				y = y


			# --- plot x,y
			plt.plot(x,y)
			# --- layout
			plt.title(Title + OptElement.Name + ' ' + AppendToTitle)
			plt.xlabel(XUnitPrefix+'m')
			plt.ylabel(YLabel)
			plt.grid('on')

			if LegendOn:
				plt.legend()
		except:
			pass

	#=============================================================#
	# FUN IntensityAtOpticalElement
	#=============================================================#
	def IntensityAtOpticalElement(OptElement,
							   XUnitPrefix = 'm' ,
							   Normalize = True ,
							   FigureIndex = None,
							   AppendToTitle ='',
							   **kwargs ):
		'''
		Specialised version of RadiationAtOpticalElement
		'''
		return CommonPlots.RadiationAtOpticalElement(OptElement,
							   XUnitPrefix = XUnitPrefix ,
							   Normalize = Normalize,
							   FigureIndex = FigureIndex,
							   Type = 'i',
							   AppendToTitle = AppendToTitle,
							   **kwargs )
	#=============================================================#
	# FUN FieldAtOpticalElement
	#=============================================================#
	def FieldAtOpticalElement(OptElement,
							   XUnitPrefix = 'm' ,
							   Normalize = True ,
							   FigureIndex = None,
							   AppendToTitle = '',
							   LegendOn = False,
							   **kwargs ):
		'''
		Specialised version of RadiationAtOpticalElement
		'''
		return CommonPlots.RadiationAtOpticalElement(OptElement,
							   XUnitPrefix = XUnitPrefix ,
							   Normalize = Normalize,
							   FigureIndex = FigureIndex,
							   AppendToTitle = '',
							   Type = 'f',
							   **kwargs )



class Metrology:




	def AverageXYFiles(PathList, ReaderFunction, ReaderFunctionParams):
		'''
		Performs an average of X,Y files.

		X,Y shall be evenly sampled.

		'''
		pass



	#=============================================================#
	# FUN ReadLtpElettraJavaFileA
	#=============================================================#
	def ReadLtpLtpJavaFileA(PathFile : str,
						 Decimation = 1,
						 DecimationStart = 1,
						 Delimiter = ' ',
						 SkipLines = 0,
						 ReturnStep = False,
						 XScaling = 1e-3,
						 YScaling = 1,
						 **kwargs):
		'''
		Expects only a X and Y column, with no header, white space as delimiter.
		There may be sawtooth fluctuations in the source data, in this case use:
		"Undersampling" flag. For example:

		Parameter
		----
		DecimateEveryN : int
			Takes one point every N. Default is 1 (all the points). The final output
			has the same size of the original output, because linear resampling is performed.

		ReturnStep : bool
			If True, returns the tuple *x,h0,Step* where  ``Step = np.mean(np.diff(x))``.
			This becaouse it may happen that the separation recorded on the LTP files varies a little bit.

			'''

		#----Load Heights
		x,h0 = FileIO.ReadXYFile(PathFile, Delimiter, SkipLines)
		x = x * XScaling
		h0 = h0 * YScaling

		h0a = h0[1::2]
		xa  = x[1::2]
		f = scipy.interpolate.interp1d(xa,h0a, kind = 'linear', fill_value = 'extrapolate')
		h0b = f(x)
		if ReturnStep == False:
			return x ,h0b
		else:
			Step = np.mean(np.diff(x))
			return x, h0b, Step
	#=============================================================#
	# FUN RectangularGrating
	#=============================================================#
	def RectangularGrating(L0,L1 = None, N = 1e4, LinesPerMillimiter = 1000,
						GrooveHeight = 10e-9, HighDuty = 0.5,
						ReturnStep = True):
		'''
		Generates a square wave, mimiking the groove height profile of  a
		(reflection) grating.

		Parameters
		-----
		L0 : float
			total length of the mirror.

		L1 : float
			length of the grooved region. If None, it is assumed to be equal to L0

		N : int
			Sampling points

		LinesPerMillimiter : int
			Lines per millimiter

		GrooveHeight : scalar
			Groove heigth (default=10nm)

		HighDuty : float (0 to 1)
			Duty cycle of the high period

		Return
		-------
		GratingProfile : array like
			Height profile (m) of the grating.

		Step : scalar
			Lateral step, corresponding to L0/N (yep, it is not so interesting).


		'''

		from scipy.signal import square
		NumberOfPoints = N
		# square(t, duty=0.5)
#		L = L1
		# L in metres, convert LinesPerMillimiter to LinesPerMeter
		LinesPerMeter = LinesPerMillimiter * 1e3
		# Create x-axis, must be strictly positive for consistent result
		x = np.linspace(0., L0, num=NumberOfPoints)

		# Initialize grating parameter
		GratingParameter = 2. * np.pi * LinesPerMeter * x
		# Generate a grating
		GratingProfile = ((square(GratingParameter, duty = HighDuty) + 1.) / 2.) * GrooveHeight

		if L1 is not None and L1 < L0:
			xTemp = np.linspace(-L0 / 2., L0 / 2., num=NumberOfPoints)
			GratingProfile[np.abs(xTemp) >= L1 / 2.] = 0.
		if ReturnStep:
			Step = L0/N
			return GratingProfile, Step
		else:
			return GratingProfile

	#=============================================================#
	# FUN SlopeIntegrate
	#=============================================================#
	def SlopeIntegrate(Slope, dx = None, x = None, SubtractPoly1 = False):
		'''
		Integrate the slope to get a height profile.

		Slopes : *array like*
			Slope array to integrate

		dx : *scalar, optional* (alternative to x)
				The X step b|w the Slope values.

		x : *array, optional* (alternative to dx)
				The sample points corrisponding to the Slope values

		SubtractPoly1 : *boolean*
			If True, the final profile will be y = y0 - p1, where

			- *y0* is the result of the integration of *Slopes*
			- *p1* is  a line passing through the first N and the last N points of y0


		'''
		if CheckArg([dx]):
			x = np.linspace(0,len(Slope) * dx, len(Slope))
		elif CheckArg([x]):
			pass
		else:
			#FIX: Throw error
			pass

		#h = [np.trapz(Slope[0:i], dx ) for i in range(1,len(Slope))]
		h1 = np.cumsum(Slope) *  dx
		h1 = h1 - h1[0]
#		I have chosen y.
		return h1
	#=============================================================#
	# FUN ReadLtp2File
	#=============================================================#
	def ReadLtp2File(Path : str, ForceYScalingToUnity = True):
		'''
		#TODO: This function is very specific and should not stay here.
		Let's wait how the class is evolving...

		Parameters
		------
		Path : *string*
			Full path of the file, written in the Ltp2 format.
			Ltp2 format is the old format of the metrology lab of ELETTRA.
			For more info, you should really read the code of this function.


		ForceYScalingToUnity : *boolean*
			Ignores the *ZUnit* parameters (specified in the file). I introduced
			this because, apparently, the y(or z) data are always saved in S.I.
			units, whereas x data are not.


		Read an (old) Ltp2 file and returns
		- x,y data array in S.I units
		- a data structure containing various info on the file.

		Return
		=====
		x : x data. Position along the mirror.

		y : y data. Either height or slopes. See FileInfo.YUnit

		FileInfo: data structure (class), containing
			FileName XUnit YUnit XScale YScale XStep
			example: XStep = FileInfo.XStep
		'''
		FileInfo = namedtuple('FileInfo', 'FileName XUnit YUnit XScale YScale XStep Type')
		with open(Path, 'r') as f:
		    Lines = f.readlines()


		I_FILENAME = 6
		I_STEP_SIZE = 10
		I_DATA_TYPE = 9
		I_X_UNIT = 11
		I_Y_UNIT = 12
		I_DATA_START = 40

		# Get File Name
		FileInfo.FileName = Lines[I_FILENAME].strip()

		#Get Data Type (Slopes or height or else)
		FileInfo.Type = (Lines[I_DATA_TYPE].strip()).split(':')[1].lower()

		#Get X,Y Unit
		FileInfo.XUnit = (Lines[I_X_UNIT].strip()).split(':')[1]
		FileInfo.YUnit = (Lines[I_Y_UNIT].strip()).split(':')[1]

		#Get X,Y Scale
		FileInfo.XScale = Units.UnitString2UnitScale(FileInfo.XUnit)
		FileInfo.YScale = Units.UnitString2UnitScale(FileInfo.YUnit) if not ForceYScalingToUnity else 1

		# Get XStep
		FileInfo.XStep = float((Lines[I_STEP_SIZE].strip()).split(':')[1]) * FileInfo.XScale

		#Get X,Y Arrays
		N = len(Lines) -  I_DATA_START
		x = np.zeros([N])
		y = np.zeros([N])
		for (iLine, Line) in enumerate(Lines[I_DATA_START:]):
			Tokens = Line.split('\t')
			x[iLine] = float(Tokens[0])
			y[iLine] = float(Tokens[1])

		x = x * FileInfo.XScale
		y = y * FileInfo.YScale

		return (x,y, FileInfo)

	#=============================================================#
	# FUN PlotFigureError
	#=============================================================#
	def PlotFigureError(OpticalElement, Index = 0,  LastUsed = False,FigureIndex = None,
					 AppendToTitle = '', fmt = '-', **kwargs ):
		'''
		Type: Helper/Developer function
		-----

		Plots the Figure Error of OpticalElement.CoreOptics.
		This function should not really stay here, but it could be a good idea to
		be placed in the future CoreOptics.Metrology subclass

		'''
		#@todo Really:
#		We should catch the error so that the execution is not stopped, but a warning is written to the console.

		#Internal Reassignment
		Item = OpticalElement
		Tot = len(OpticalElement.CoreOptics.FigureErrors)
		if LastUsed == True:
			y = Item.CoreOptics.LastFigureErrorUsed
			Index = Item.CoreOptics.LastFigureErrorUsedIndex
			#FIXME:minor
			# There is not: LastFigureErrorStepUsed... or similar... so
			# the following lines are not rigorous
			dx = Item.CoreOptics.FigureErrorSteps[Index]
			x = np.linspace(0,len(y) * dx, len(y))
			TitleStr = 'Figure Error[%d/%d], Last Used' % (Index + 1,Tot)
		else:
			y = Item.CoreOptics.FigureErrors[Index]
			dx = Item.CoreOptics.FigureErrorSteps[Index]
			x = np.linspace(0,len(y) * dx, len(y))
			TitleStr = 'Figure Error[%d/%d]' % (Index + 1,Tot)  + AppendToTitle
		'''
		Notes: Index +1 => In order so that the maximum is e.h. 5/5 and min is 1/5
		'''

		PlotLabel  = '[%d/%d, L=%0.1f mm out of %0.1f mm]' % (Index + 1,Tot, x[-1] - x[0], OpticalElement.CoreOptics.L)
		plt.figure(FigureIndex, **kwargs)
		plot(x * 1e3,y * 1e9, '.-', label = PlotLabel)
		plt.xlabel('mm')
		plt.ylabel('nm')
		plt.title(Item.Name + TitleStr)
		plt.grid('on')
		plt.legend()
#		plt.legend('oe:'+ OpticalElement.Name)
		return None



#
#	def RectangularGrating(L, NumberOfPoints, LinesPerMillimiter, GrooveHeight, DutyCycle = 0.5, L0=0.):
#	    #square(t, duty=0.5)
#
#	    # L in metres, convert LinesPerMillimiter to LinesPerMeter
#		LinesPerMetereter = LinesPerMeterillimiter * 1e3
#	    # Create x-axis, must be strictly positive for consistent result
#	    x = np.linspace(0., L, num=NumberOfPoints)
#
#	    # Initialize grating parameter
#	    GratingParameter = 2. * np.pi * LinesPerMetereter * x
#	    # Generate a grating
#
#		 GratingProfile = ((square(GratingParameter) + 1.) / 2.) * GrooveHeight
#
#	    if L0 != 0:
#	        xTemp = np.linspace(-L/2., L/2., num=NumberOfPoints)
#	        GratingProfile[np.abs(xTemp)>=L0/2.] = 0.
#
#	    return GratingProfile

