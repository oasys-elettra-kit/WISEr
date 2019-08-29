# -*- coding: utf-8 -*-
"""
Created on Wed Jun 08 14:06:01 2016
Huygens Fresnel Method Library
@authors:
Cose da sistemare
- capire come chiamare gli assi del fascio gaussiano RhoZ ?
- trovare denominazione comune xMir yMir, Mir_x MirX Mir_xy MirXY e salaminchia
"""
#%%
from numpy import sum, cos, sin, tan, pi, array, arange, size, polyval, polyfit, dot, exp, real, imag, sqrt, prod, zeros, floor, unravel_index, empty, linspace, ceil, amin, amax, diff, cumsum, append, deg2rad, column_stack, linalg, sort, complex, concatenate, nan, inf, ndarray
from LibWISEr.ToolLib import Debug
from numba import jit, prange
from numba import int64, float64, complex128
from numba import cuda

from scipy import ndimage
import multiprocessing

Amp = lambda x : abs(x) / max(abs(x))
Cyc = lambda x : real(x) / abs(x)

def ro_property(field):
    return property(lambda self : self.__dict__[field])


def GetCentre(N):
    '''
    %  Y = GetCentre(X)
    % Restituisce il centro del vettore X. Il centro è inteso come
    % il punto in cui compare la DC della trasformata di Fourier.
    % Ovviamente, il tutto è in base-1, compatibile con matlab.
    '''
    return int(floor(N / 2.))

def ArgMax (X = empty(0)):
    r, c = unravel_index(X.argmax(), X.shape)
    return r, c

def ArgMin (X = empty(0)):
    r, c = unravel_index(X.argmin(), X.shape)
    return r, c


def MakeScreenXY_1d(XY0, L, N, Theta = 0, Normal = False ):
    if Normal == True:
        Theta = Theta - pi / 2.

    if abs(Theta) == pi / 2.:
        Det_y0 = XY0[1] - L / 2.
        Det_y1 = XY0[1] + L / 2.
        y = linspace(Det_y0, Det_y1,N)
        x = 0*y + XY0[0]

    else:
        m = tan(Theta)
        q = XY0[1] - XY0[0] * m
        p = array([m,q])
        Det_x0 = XY0[0] - L / 2. * cos(Theta)
        Det_x1 = XY0[0] + L / 2. * cos(Theta)
        x = linspace(Det_x0, Det_x1, N)
        y = polyval(p, x)

    return x, y

def FastResample1d(*args):
    '''
        FastResample1d([x], [y], [n])
        Usage:
        yy = FastResample1d(y,1000)
        or
        xx,yy =FastResample1d(x,y,1000)
    '''
    from scipy import interpolate as interpolate
    # input: y,N
    if len(args) == 2:
        y = args[0]
        N0 = len(y)
        N = args[1]
        if N == N0:
            return y

        x = arange(0, N0)
        f = interpolate.interp1d(x, y)
        xNew = linspace(0,N0-1,N)
        yNew = f(xNew)
        return  yNew
    #input: x,y,N
    elif len(args) == 3:
        x = args[0]
        y = args[1]
        N = args[2]
        N0 = len(x)
        xNew = linspace(amin(x), amax(x),N)
        fy = interpolate.interp1d(x, y)
        yNew = fy(xNew)
        return xNew, yNew
    else:
        raise  ValueError('Wrong argument number in calling FastResample1d')
        return None



def HalfEnergyWidth_1d(X,  UseCentreOfMass = True, Step = 1,  TotalEnergy = None,
                        AlgorithmType = 0):
    '''
        Parameters
        ------------
        X : 1d array
        UseCentreOfMass : if False, computes the HEW respect with the maximum
        TotalEnergy : if None, uses TotalEnergy = sum(X).
        Returns
        ------------
        Hew : the Half width energy of the array X (1d)
        Centre : the centre of mass or the maximum value of X
        Uses interpolation for sub-pixel accuracy: NO (not yet)
    '''

    ''' Stupid remarks
    The Hew of a Gaussian is 0.675
    '''

    TotalEnergy = sum(X) if TotalEnergy==None else TotalEnergy
    HalfEnergy = 0.5 * TotalEnergy ;

    if UseCentreOfMass == True:
        iCentre = int(floor(ndimage.measurements.center_of_mass(X)))
    else:	# uses max value. May be issues if many equal values are found
        iCentre = X.argmax()

    if AlgorithmType ==1:
        #================================================
        # Algoritmo binario
        #================================================
        RHi = floor(len(X) / 2)
        RLow = 1

        # algoritmo intelligente, ma che non funziona
        myR = int(floor(ceil(RHi + RLow) / 2))
        DeltaR = RHi - RLow # variabile di controllo
        NIterations = 0
        while DeltaR > 1:
            NIterations = NIterations + 1
            iStart = int(round(iCentre - myR))
            iEnd = int(round(iCentre + myR))+1
            if sum(X[iStart:iEnd]) < HalfEnergy:
                RLow = myR
            else:
                RHi = myR
            myR = ceil(RLow + RHi) / 2
            DeltaR = RHi-RLow
    elif AlgorithmType == 0:
        #================================================
        # Algoritmo stupido
        #================================================
        myEnergy = 0
        iR = 1
        while myEnergy < HalfEnergy:
            myEnergy = sum(X[iCentre - iR : iCentre + iR])
            iR = iR + 1
        myR = iR
    Diameter = 2. * myR
    return Diameter * Step, iCentre * Step




def Gauss1d(N, Sigma):
    x = arange(0, N) - GetCentre(N)
    y = exp(-0.5 * x**2 / Sigma**2)
    return y



'''
def GaussNoise(N,Sigma):
    Sigma = N/Sigma
    y = Gauss1d(N,Sigma)
    y = np.fft.fftshift(y)
    r = 2*pi * np.random.rand(N)
    f = np.fft.ifft(y * exp(1j*r))
    return real(f)
'''

#______________________________________________________________________________
# 	xy2xyList
#______________________________________________________________________________
def xy2v(x,y):
    return [[xi,yi] for xi in x for yi in y]

def v2xy(v):
    return []




##================================================================
##  RMat
##================================================================
#def RMat(Theta):
#	'''
#	Returns the rotation matrix for an angle Theta.
#	'''
#	return [[cos(Theta), -sin(Theta)],
#				[sin(Theta), cos(Theta)]]


#================================================================
#  XY_to_L
#================================================================
def XY_to_L(x,y):
    '''
    Dato un segmento di coordinate x,y, calcola la coordinata propria (solidale al segmento).
    L'origine della nuova coordinata L viene assunta a metà della lunghezza degli array di ingresso (che ha senso finché x,y definiscono un segmento di retta).
    '''
    N2 = int(floor(len(x) / 2))
    L = 0*x
    L[0:N2] = -1 * sqrt((x[0:N2] - x[N2])**2 + (y[0:N2] - y[N2])**2)
    L[N2:] = 1 * sqrt((x[N2:] - x[N2])**2 + (y[N2:] - y[N2])**2)
    return L
#================================================================
#  xy_to_s
#================================================================
def xy_to_s(x,y):
    '''
    For two arrays x,y computes the array of displacements s defined as
                s_i = sqrt( dx_i^2 + dy_i^2)
    where
                dx_i = x_i - x_(i-1)   and similarly for dy_i
    Essentially, s is the proper coordinate axis of the curve described by x,y.
    '''

    if (x is None) or (y is None):
        return None

    N2 = int(floor(len(x) / 2))
    s0 = len(x) / 2
    Steps = sqrt(diff(x)**2 + diff(y)**2)
    s = cumsum(Steps)
    s = append(0, s) - s[int(len(s) / 2)]
    return s

def PathLength(x,y):
    return sum(sqrt(diff(x)**2 + diff(y)**2))


#================================================================
#  CartT
#================================================================
def CartT(Vxy, NewOrigin = array([0,0]), Theta = 0 ):
    Vxy = array(Vxy)
    NewOrigin = array(NewOrigin)
    return  dot(Vxy - NewOrigin, RMat(Theta))

#================================================================
#  CartChange
#================================================================
def CartChange(x,y, NewOrigin = array([0,0]), Angle = 0, Deg = False):
    '''
    Simple function for cartesian change of coordinates.
    Parameters
    ----------------------
    x : 1d array
        x coordinates
    y : 1d array
        y coordinates
    NewOrigin : 1x2 array
        [x,y] coordinates of the NewOrigin (expressed in the old system)
    Angle : scalar (rad)
        Rotation angle
    Deg : boolean (=false)
        Says if Angle is in degrees or radians (default)
    '''
    # degrees => radians conversion (if necessary)
    if (Angle !=0) and (Deg == True):
        Angle = deg2rad(Angle)

    Vxy = column_stack((x,y))
    U = CartT(Vxy, NewOrigin, Angle)
    return (U[:,0], U[:,1])


#================================================================
#  CartChange_XY
#================================================================
def CartChange_XY(XY, NewOrigin = array([0,0]), Angle = 0, Deg = False):
    '''
        Alternate version of CartChange, uses XY array instead of separate
        x and y.
    '''
    x = XY[0]
    y = XY[1]

    return CartChange(x,y, NewOrigin, Angle, Deg)

#================================================================
#  CartChange_Poly
#================================================================
def CartChange_Poly(P, NewOrigin = array([0,0]), Angle = 0, Deg = False):
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
    P = array(P)
    N =   len(P)-1 # degree of the polynomial

    if N <1:
        print('Errror: Polynomial order too low (<1), finding coefficient is useles...')
        return None

    x = linspace(0,N, N+1)
    y = polyval(P,x)

    x_new, y_new = CartChange(x,y,NewOrigin, Angle, Deg)

    # Polynomial fit

    P_new = polyfit(x_new, y_new, N)
    P_new2 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
#	P_new3 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
    return P_new2

#================================================================
#  RotXY
#================================================================
def RotXY(x,y, Theta = 0, CentreOfRotation = array([0,0])):
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
    >>> RotXY(0,1,45 * pi / 180.)
    >>> Out[12]: (array([-0.70710678]), array([ 0.70710678]))
    '''
    if Theta == 0:
        return (array(x), array(y))
    Theta = -Theta # non so perché il -1, odio le matrici di rotazione.
    Vxy = column_stack((x,y))
    U  = dot(Vxy - CentreOfRotation, RMat(Theta)) + CentreOfRotation
    return (U[:,0], U[:,1])

#================================================================
#  RotPoly
#================================================================
def RotPoly(P, NewOrigin = array([0,0]), Angle = 0, Deg = False):
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
    P = array(P)
    N =   len(P)-1 # degree of the polynomial
    if N <1:
        print('Errror: Polynomial order too low (<1), finding coefficient is useles...')
        return None

    x = linspace(0,N, N+1)
    y = polyval(P,x)

    x_new, y_new = RotXY(x,y, Angle ,NewOrigin)

    # Polynomial fit
    P_new = polyfit(x_new, y_new, N)
    P_new2 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
#	P_new3 = [Val if 1e-15 < abs(Val) else 0 for Val in P_new]
    return P_new2

#================================================================
#  RotPoint
#================================================================
def RotPoint(XY, Theta = 0, CentreOfRotation = array([0,0])):
    '''
    The same as RotXY, but with input (x1, y1) intead of
    [x1...xn] , [y1 ... yn]
    '''
    (x,y) =  RotXY(XY[0], XY[1], Theta = Theta, CentreOfRotation = CentreOfRotation)
    return array([x, y])

#================================================================
#  RotVersor
#================================================================
def RotVersor(V, Angle, Deg = False):
    '''
    Rotate the versor V = (Vx, Vy)
    '''
    if Deg== True:
        Angle = Angle * pi / 180.

    if (Angle == 0) or linalg.norm(V) == 0:
        return V
    else:
        U = RotXY(V[0], V[1], Angle)
        return array([U[0][0], U[1][0] ])

#______________________________________________________________________________
# 	Range
#______________________________________________________________________________
def Range(Start, End, Step):
    return arange(Start, End+Step, Step)


#==============================================================================
# 	CLASS: SphericalWave_2d
#==============================================================================
class SphericalWave_1d(object):
    #================================================
    # 	__init__
    #================================================
    def __init__(self, Lambda, OriginZ = 0, OriginY = 0):
        self.Lambda = Lambda
        self.OriginZY = array([OriginZ, OriginY])

    #================================================
    # 	EvalPhase
    #================================================
    def EvalPhase(self,z,y):
        k = 2 * pi / self.Lambda
        (z,y) = _MatchArrayLengths(z,y)
        return k * sqrt((y - self.OriginZY[1])**2 + (z - self.OriginZY[0])**2)


    #================================================
    # 	EvalCycles
    #================================================
    def EvalCycles(self,z = array(None) , y = array(None)):
        (z,y) = _MatchArrayLengths(z,y)
        return cos(self.EvalPhase(z,y))

    #================================================
    # 	EvalField
    #================================================
    def EvalField(self, z = array(None), y = array(None) ):
        (z,y) = _MatchArrayLengths(z,y)
        R = sqrt((y - self.OriginZY[1])**2 + (z - self.OriginZY[0])**2)
        return 1 / R * exp(1j*self.EvalPhase(z, y))
'''
    #================================================
    # 	Eval
    #================================================
    def Eval(self, z = np.array(None) , y = np.array(None)):
        return self.Field(z,y)
'''

#	def ChirpCyclesInParaxialApproximation







class SourceType():
    POINT = 0
    GAUSSIAN_TEM00 = 1


#==============================================================================
# 	FUN: HuygensIntegral_1d_Kernel
#==============================================================================

#import yaml

@jit('complex128[:](float64, complex128[:], float64[:], float64[:], float64[:], float64[:])', nopython=True, nogil=True, parallel=True, cache=True)
def HuygensIntegral_1d_Kernel(wl, Ea, xa, ya, xb, yb):
    """
    Parameters
    --------------------
    wl : float
        Wavelength (m)
    Ea : 1d complex array
        Electromagnetic Field
    xa, ya : 1d array float
        Coordinates of the start plane
    xb, yb : 1d array float
        Coordinates of the final plane
    bStart : int
        Start index on the start plane
    bEnd : int
        End index on the final plane
    The computation is performed on the elements
    xb(bStart) --> xb(bEnd) and yb(bStart) --> yb(bEnd)
    """

    k = 2. * pi / wl

    bStart = 0
    bEnd = prod(int64(xb.shape))
    EbTokN = xb.shape[0]

    EbTokN = bEnd - bStart
    EbTok = zeros(EbTokN, dtype=complex128)
    RList = zeros(EbTokN, dtype=float64)

    # loop on items within the segment of B
    assert(EbTok.shape == RList.shape)
    assert(RList.shape == xa.shape)
    assert(RList.shape == ya.shape)

    for i in prange(0, EbTokN):
        xbi = xb[i + bStart]
        ybi = yb[i + bStart]
        xbi = xb[i]
        ybi = yb[i]
        # Preliminary normalisation
        # 17/01/2017
        # Normalization = self.L * self.(Alpha)/(Lambda * )
        # R = np.array((sqrt((xa - xbi)**2 + (ya - ybi)**2)))

        RList = sqrt((xa - xbi)**2 + (ya - ybi)**2)

        EbTok[i] = 1. / sqrt(wl) * sum(Ea / RList * exp(-1j * k * RList))
        EbTok[i] = sum(Ea / RList * exp(-1j * k * RList))

    EbTok = 1. / sqrt(wl) * EbTok

    return EbTok


# # Fully vectorized implementation of the HuygensIntegral_1d_Kernel using Numpy linalg functions
# #@jit(nopython=True, nogil=True, parallel=True)
# def HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, bStart=np.int64(-1), bEnd=np.int64(0)):
#     k = 2. * pi / Lambda
#
#     if bStart == -1:
#         bStart = 0
#         bEnd = prod(np.int64(xb.shape))
#
#     EbTokN = bEnd - bStart
#
#     vec_Rlist = zeros((EbTokN, EbTokN), dtype=np.float64)
#
#     vec_Rlist = sqrt((xa - xb[bStart:bEnd, None])**2 + (ya - yb[bStart:bEnd, None])**2, dtype=np.float64)
#     vec_EbTok = 1. / sqrt(Lambda) * sum(Ea / vec_Rlist * exp(-1j * k * vec_Rlist), axis=1, dtype=np.complex128)
#
#     return vec_EbTok



def _MatchArrayLengths (x,y):
    '''
        If x(or y) is a Mx1 array and y(or x) is a scalar, then y (or x) is a Mx1 	array filled with replica of the single value of input y
    '''
    IsArray = lambda t : True if type(t) == ndarray else False

    if IsArray(x) and not IsArray(y):
        y = array(x) * 0. + y
        return (x,y)
    elif IsArray(y) and not IsArray(x):
        x = array(y) * 0. + x
        return (x,y)
    else:
        return (x,y)

#==============================================================================
# 	WRAPPER
#==============================================================================
def _wrapper_HuygensIntegral_1d_Kernel(parameters):

    # Unpack the parameters
    Lambda, Ea, xa, ya, xb, yb, bStart, bEnd = parameters

    # Convert to float
    Lambda = float64(Lambda)
    Ea = complex128(Ea)
    xa = float64(xa)
    ya = float64(ya)
    xb = float64(xb)
    yb = float64(yb)

    # Convert to int
    bStart = int64(bStart)
    bEnd = int64(bEnd)

    return HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, bStart, bEnd)

#==============================================================================
# 	WRAPPER ARGUMENTS
#==============================================================================
def _wrapper_args_HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, NPools):
    N = size(xb)
    r = linspace(0,N, NPools+1) ; r = array([floor(ri) for ri in r]) ;
    #args_StartStop = list(zip([x for x in r], r[1:]))
    args_StartStop = list(zip(r[0:], r[1:]))
    #args_StartStop  = (len(r)-1) * [(r[0], r[1])] # toglier
    args =  [[Lambda, Ea, xa, ya, xb, yb] + list(myArg) for myArg in args_StartStop]
    return (args, args_StartStop)

#==============================================================================
# 	FUN: HuygensIntegral_1d_MultiPool
#==============================================================================
def HuygensIntegral_1d_MultiPool(Lambda, Ea, xa, ya, xb, yb, NPools = 1, Verbose = True):

    (xa, ya) = _MatchArrayLengths(xa,ya)
    (xb, yb) = _MatchArrayLengths(xb,yb)
    # Convert to float
    Lambda = float64(Lambda)
    Ea = complex128(Ea)
    xa = float64(xa)
    ya = float64(ya)
    xb = float64(xb)
    yb = float64(yb)

    if Verbose:
        # multi pool
        print(30 * '=-.');
        print('\n')
        print('HuygensIntegral_1d_MultiPool')
        print('N0:=%d' % len(xa))
        print('N1:=%d' % len(xb))
        print('NPools = %d' % NPools)
        # print('--------------------------------')
        # print('Lambda', type(Lambda), np.shape(Lambda))
        # print('Ea', type(Ea), np.shape(Ea))
        # print('xa', type(xa), np.shape(xa))
        # print(xa)
        # print('ya', type(ya), np.shape(ya))
        # print(ya)
        # print('xb', type(xb), np.shape(xb))
        # print(xb)
        # print('yb', type(yb), np.shape(yb))
        # print(yb)

    if NPools > 1:
        p = multiprocessing.Pool(NPools)
        (args, argsStartStop) = _wrapper_args_HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, NPools)
        res = p.map(_wrapper_HuygensIntegral_1d_Kernel, args)
        p.close()
#		return argsStartStop # toglire
        if size(res) > 1:
            return concatenate(res)
        else:
            return res
    else: #single thread
        return HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb)

#==============================================================================
# 	FUN: HuygensIntegral_1d
#==============================================================================
HuygensIntegral_1d = HuygensIntegral_1d_MultiPool

def SamplingGoodness_QuadraticPhase(MatrixN, dPix, Lambda, z, R=inf, Verbose = True):
    '''
    [iqLim, TextOutput, OUT] =
    '''
    class strucOUT:
        zMin = nan
        NOsc = nan
        alpha = nan
        alphaMax = nan
        alphaRatio = nan
        iLim = nan
        Text = 'text'

    OUT  = strucOUT()
    #% SamplingGoodness(MatrixN, PixelPhysicalSize, Lambda, z)
    k = 2. * pi / Lambda
    N = MatrixN
    L = N * dPix/2 # assume l'onda piana centrata nella matrice

    zMin = (Lambda/dPix/L + 1/R)**-1  # z minimum
    alpha = k/2 * (1/z + 1/R)
    alphaMax = pi/2/dPix/L
    NOsc = alpha*L**2/2/pi

    OUT.zMin = zMin
    OUT.NOsc = NOsc
    OUT.alpha = alpha
    OUT.alphaMax = alphaMax
    OUT.alphaRatio = alpha/alphaMax
#	OUT.iqLim = iqLim ;
    OUT.Text = 'No aliasing for z < %0.1e m \n N Oscillations =\t%0.1f\n MagicRatio =\t%0.2f\n iqLim =\t%0.2f (N/2=%d)' %(zMin, NOsc, OUT.alphaRatio , OUT.iLim, N/2)
    if Verbose == True:
        print(OUT.Text)
    return OUT



#	#==============================================================================
#	# 	CLASS: Ellipse:Simulation
#	#==============================================================================
#	class Simulation(object):
#
#		#=======================================================================
#		# 	SMALL CLASS: SimulationSettings
#		#=======================================================================
#		class SimulationSettings(object):
#			def __init__(self):
#				self.Lambda = 10e-9
#				self.DetectorSize = 50e-6
#				self.Defocus = 0
#				self.NPools = 6
#				self.SourceGaussianWaist = 10e-3
#				self.AnalyticSourceType = SourceType.POINT
#
#			#=======================================================================
#			# 	Simulation:__init__
#			#=======================================================================
#			def __init__(self, ParentEllipse = None):
#				self.Ellipse = ParentEllipse
#				self.Settings = SimulationSettings()
#
#
#
#			#=======================================================================
#			# 	Simulation:AnalyticSource_EvalFieldAtFocalPlane
#			#=======================================================================
#			def FieldAtFocalPlane(self, Source,																								DetectorSize = self.Settings.DetectorSize,
#									Defocus = self.Settings.Defocus,
#									NPools = self.Settings.NPools,
#									):
#				'''
#				Computes the Electromagnetic field around the focal plane (F2) of the
#				ellipse object. The detector plane is normal to the ellipse axis.
#
#
#				Return: Field (complex), displacement array (float)
#				'''
#				Det_Size = DetectorSize
#				Kb = self.Ellipse
#				# Auto Sampling (easy way)
#				NAuto = int(10 * self.L * Det_Size  * cos(Kb.pTan_Angle - arctan(-1/Kb.p2[0])) /Lambda/Bb.f2)
#				# Plane 0
#				[Mir_x, Mir_y] = Kb.GetXY_MeasuredMirror(NAuto,0)
#				# E0
#				Mir_E = Source.EvalField_XYLab(Mir_x, Mir_y)
#	#			Source.
#				# Plane 1
#				Det_x, Det_y = kbv.GetXY_TransversePlaneAtF2(Det_Size, NAuto, Defocus )
#				Det_ds = np.sqrt((Det_x[0] - Det_x[-1])**2 + (Det_y[0] - Det_y[-1])**2)
#				# E1
#				E1[i,:] = HuygensIntegral_1d_MultiPool(Lambda,
#														Mir_E,Mir_x, Mir_y, Det_x, Det_y, NPools)
#
#				Det_s = xy_to_s(Det_x, Det_y)
#				return E1, Det_s
#'''

'''
NOT NEEDED ANYMORE, BUT STILL KEPT HERE!
#==============================================================================
# 	FUN: HuygensIntegral_1d_MultiPool
#==============================================================================
def HuygensIntegral_1d_MultiPool(Lambda, Ea, xa, ya, xb, yb, NPools = 1, Verbose = True):

    (xa, ya) = _MatchArrayLengths(xa,ya)
    (xb, yb) = _MatchArrayLengths(xb,yb)
    # Convert to float
    Lambda = float64(Lambda)
    Ea = complex128(Ea)
    xa = float64(xa)
    ya = float64(ya)
    xb = float64(xb)
    yb = float64(yb)

    if Verbose:
        # multi pool
        print(30 * '=-.');
        print('\n')
        print('HuygensIntegral_1d_MultiPool')
        print('N0:=%d' % len(xa))
        print('N1:=%d' % len(xb))
        print('NPools = %d' % NPools)
        # print('--------------------------------')
        # print('Lambda', type(Lambda), np.shape(Lambda))
        # print('Ea', type(Ea), np.shape(Ea))
        # print('xa', type(xa), np.shape(xa))
        # print(xa)
        # print('ya', type(ya), np.shape(ya))
        # print(ya)
        # print('xb', type(xb), np.shape(xb))
        # print(xb)
        # print('yb', type(yb), np.shape(yb))
        # print(yb)

    if NPools > 1:
        p = multiprocessing.Pool(NPools)
        (args, argsStartStop) = _wrapper_args_HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, NPools)
        res = p.map(_wrapper_HuygensIntegral_1d_Kernel, args)
        p.close()
#		return argsStartStop # toglire
        if size(res) > 1:
            return concatenate(res)
        else:
            return res
    else: #single thread
        return HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb)

#==============================================================================
# 	WRAPPER
#==============================================================================
def _wrapper_HuygensIntegral_1d_Kernel(parameters):

    # Unpack the parameters
    Lambda, Ea, xa, ya, xb, yb, bStart, bEnd = parameters

    # Convert to float
    Lambda = float64(Lambda)
    Ea = complex128(Ea)
    xa = float64(xa)
    ya = float64(ya)
    xb = float64(xb)
    yb = float64(yb)

    # Convert to int
    bStart = int64(bStart)
    bEnd = int64(bEnd)

    return HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, bStart, bEnd)

#==============================================================================
# 	WRAPPER ARGUMENTS
#==============================================================================
def _wrapper_args_HuygensIntegral_1d_Kernel(Lambda, Ea, xa, ya, xb, yb, NPools):
    N = size(xb)
    r = linspace(0,N, NPools+1) ; r = array([floor(ri) for ri in r]) ;
    #args_StartStop = list(zip([x for x in r], r[1:]))
    args_StartStop = list(zip(r[0:], r[1:]))
    #args_StartStop  = (len(r)-1) * [(r[0], r[1])] # toglier
    args =  [[Lambda, Ea, xa, ya, xb, yb] + list(myArg) for myArg in args_StartStop]
    return (args, args_StartStop)

'''
