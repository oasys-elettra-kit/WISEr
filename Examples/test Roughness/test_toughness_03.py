# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 18:51:10 2016

@author: Mic
"""

#%%
import Rayman5 as rm
import Noise2 as Noise
from must import *
from scipy import interpolate
log=np.log
reload(Noise)
fft = np.fft.fft

fftshift = np.fft.fftshift
def FftAlign2(xHalf,N):

	x = np.hstack((xHalf[::-1], xHalf[1:]))
	idelta = len(x) - N
	if idelta == 1:# piu lungo
		x = x[0:-1] # uguale
	elif idelta == 0:
		pass
	else:
		print('Error!  len(x) - N = %0d - %0d = %0d' % (len(x), N, idelta))

	return x



#%%

PathPsd = "D:\Topics\Simulatore WISE\data\psd_00settete.dat"
RMak= Noise.RoughnessMaker()
RMak.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW = False
RMak.NumericPsdLoadXY(PathPsd,xScaling = 1, yScaling = 1, xIsSpatialFreq = False)

N = int(1e4) # punti dello specchio
N2 = N//2
L = 150 # (mm)
L_um = L*1e3

fMin = 1/L_um

ff,yy = RMak.NumericPsdGetXY()

fSpline = (np.array(range(N2))+1)*fMin

fun = interpolate.splrep(log(ff), log(yy), s=2)
yPsd_log = interpolate.splev(log(fSpline), fun)
ySpline = exp(yPsd_log)
yPsd = ySpline

# tolgo
yPsd[fSpline<ff[0]] = 0
n = len(yPsd)


plot(fSpline, yPsd,'-r')
plot(ff, yy,'.')
plt.legend(['ySpline','Data'])
ax = plt.axes()
ax.set_yscale('log')
#ax.set_xscale('log')

#%% controllo RMS integrando la yPsd
import scipy.integrate as integrate

RMS = sqrt(integrate.trapz(yPsd, fSpline/1000))



#%% DA IDL

#P = FftAlign2(yPsd, 2*N) # così P è lunga 2*N
# yPsd non ha la componente DC

yPsd_reversed = yPsd[::-1]
P = np.hstack((yPsd_reversed[:-1], 0, yPsd))
P = P/2.0; #necessario per ripartire la potenza spettrale fra freq + e -
#P = P[::-1]
n = len(P)
ell = 1/(fSpline[2] - fSpline[1])
P = sqrt(P)/ell*1000
#P = np.fft.fftshift(P)

plt.figure(100)
plot(abs(P))

yPsdNorm = yPsd /ell*1000
a = sqrt(yPsdNorm[:-1])
r = np.random.rand(len(a))
ar = a*exp(1j*r)
br = a[::-1]
trFour = np.hstack((0,ar, 0,np.conj(br)))


yRaf = np.fft.ifft(trFour)
yRaf = real(yRaf)

#r = 2*pi * np.random.rand(len(P))
#yRaf = np.fft.ifft(P * exp(1j*r))
#yRaf = real(yRaf)

print('Rms = %0.2e nm' % np.std(yRaf))


#%%
