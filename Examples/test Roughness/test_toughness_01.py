# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 18:51:10 2016

@author: Mic
"""

#%%
import Rayman5 as rm
import Noise2 as Noise
from must import *
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
		print('Error!  len(x) - N = %0d' % idelta)

	return x



#%%

PathPsd = "D:\Topics\Simulatore WISE\data\psd_00settete.dat"
RMak= Noise.RoughnessMaker()

RMak.NumericPsdLoadXY(PathPsd,xScaling = 1e-6, yScaling = 1, xIsSpatialFreq = False)

ff,yy = RMak.NumericPsdGetXY()

plt.figure(1)
plot(np.log10(ff), yy,'.r')
plt.xlabel('f (m^-1)')



#%%
RMak.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW = False
L = 0.4
N = 2e3
df  = 1/L ;
fMax = df* N/2
fMin = df
f = np.linspace(fMin, fMax,N)

RMak.NumericPsdCheck(N,L)


#%% generazione rumore a mano
fPsdHalf, yPsdHalf = RMak.PsdEval(N//2+1, df)
yPsd = FftAlign2(yPsdHalf,N)
yPsd = yPsd/2


yPsd[int(N//2)] = 0
y = np.fft.fftshift(yPsd)
r = 2*pi * np.random.rand(len(yPsd))

yRaf = np.fft.ifft(y * exp(1j*r))
yRaf = imag(yRaf)

print('Rms = %0.2e' % np.std(yRaf))

#%% Controllo correlazione
'''
ftRaf = np.fft.fft(yRaf)
acRaf = np.real(np.fft.ifft(ftRaf * np.conj(ftRaf)))
acRaf_ = np.correlate(yRaf, yRaf,'same')
'''
