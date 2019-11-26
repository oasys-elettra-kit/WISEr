# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 18:51:10 2016

@author: Mic
"""

#%%
import Rayman5 as rm
import Noise as Noise
from must import *
from scipy import interpolate
log=np.log
fft = np.fft.fft
fftshift = np.fft.fftshift

reload(Noise)



#%%
PathPsd = "..\\Data\psd_00settete.dat"
RMak= Noise.RoughnessMaker()
RMak.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW = False
RMak.NumericPsdLoadXY(PathPsd,xScaling = 1, yScaling = 1, xIsSpatialFreq = False)

N = int(10000) # points of the mirror
N2 =int( N//2)
L =300 # (mm) material length of the mirror
L_um = L*1e3
L_nm = L*1e6

fMin = 1/L_um #minimum spatial frequency

ff,yy = RMak.NumericPsdGetXY()

fSpline = (np.array(range(N2))+1)/L_um # um^-1

fun = interpolate.splrep(log(ff), log(yy), s=1)
yPsd_log = interpolate.splev(log(fSpline), fun)
ySpline = exp(yPsd_log)
yPsd = ySpline

# tolgo
yPsd[fSpline<ff[0]] = 200
n = len(yPsd)


plot(fSpline, yPsd,'-')
plot(ff, yy,'x')
plt.legend(['ySpline','Data'])
ax = plt.axes()
#ax.set_yscale('log')
#ax.set_xscale('log')

#%% controllo RMS integrando la yPsd
import scipy.integrate as integrate

RMS = sqrt(integrate.trapz(yPsd, fSpline/1000))

#%%  Modo Manfredda style

#yPsdNorm = sqrt(yPsd/L_um/1000)
#yPsdNorm_reverse = yPsdNorm[::-1]
yPsd_reverse = yPsd[::-1]
ell= 1/(fSpline[1] - fSpline[0])

yPsd2 = np.hstack((yPsd_reverse ,0,yPsd[0:-1]))
yPsd2Norm = sqrt(yPsd2/ell/1000/2)

n_ = len(yPsd2)
print('len(yPsd2) = %0.2d' % len(yPsd2Norm))
phi = 2*pi * np.random.rand(n_)
r = exp(1j*phi)

yPsd2Norm_ = fftshift(yPsd2Norm)
#yPsd2Norm_[len(yPsd2Norm_)//2] = 0

yRaf = np.fft.fft(r*yPsd2Norm_)
yRaf = real(yRaf)
print('Rms = %0.2e nm' % np.std(yRaf))

plot(yPsd2Norm_)

print('max yPsd_ = %d nm' % max(yPsd2))
print('max yPsd2Norm = %0.4f nm' % max(yPsd2Norm))
print('Rms yRaf = %0.2e nm' % np.std(yRaf))


yRaf2 = Noise.PsdArray2Noise_1d_v2(ff,yy,L,N)
print('Rms yRaf2 = %0.2e nm' % np.std(yRaf2))
