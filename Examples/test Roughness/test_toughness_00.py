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

def FourierAlign2(xHalf,N):

	x = np.hstack((xHalf[::-1], xHalf[1:]))
	idelta = len(x) - N
	if idelta == 1:# piu lungo
		x = x[0:-1] # uguale
	elif idelta == 0:
		pass
	else:
		print('Error!  len(x) - N = %0d' % idelta)

	return x

x = np.linspace(0,5,6)
y = x
a = np.array([0,1,2,3,4,5])
n=10
b = FourierAlign2(a,n)

#%%

PathPsd = "D:\Topics\Simulatore WISE\data\psd_00settete.dat"
RMak= Noise.RoughnessMaker()

RMak.NumericPsdLoadXY(PathPsd,xScaling = 1e-6, yScaling = 1e-27, xIsSpatialFreq = False)




s = np.loadtxt(PathPsd)
x = s[:,0]
y = s[:,1]
x=x*1e-6
y = y*1e-27

f = 1/x

i = np.argsort(f)
f = f[i]
y = y[i]


ff,yy = RMak.NumericPsdGetXY()

f = np.array(f)
plt.figure(1)
plot(np.log10(f), y,'ob')
plot(np.log10(ff), yy,'.r')
plt.xlabel('f (m^-1)')


'''
ok, la classe legge bene il file, come me lo aspetto

'''

#%%
RMak.Options.FIT_NUMERIC_DATA_WITH_POWER_LAW = False
L = 0.6
N = 2e4
df  = 1/L ;
fMax = df* N/2
fMin = df
f = np.linspace(fMin, fMax,N)

#RMak.NumericPsdCheck(N,L)
_max = np.max(ff)
_min = np.min(ff)

print('fMax cercato  = %0.1e m^-1' % fMax )
print('fMax misurato = %0.1e m^-1 = %0.2e nm^-1' % (_max, (_max * 1e9) ))
print('fMin cercato  = %0.1e m^-1' % fMin )
print('fMin misurato = %0.1e m^-1 = %0.2e nm^-1' % (_min, (_min * 1e9) ))

fPsd, yPsd = RMak.PsdEval(N, df)
#% Plot che fa capire quanto della PSF viene utilizzato effettivamente nella simulazione

#plot(f, np.log10(yPsd),'x')
#plot(ff, np.log10(yy),'.r')

RMak.NumericPsdCheck(N,L)

#%generazione rumore auto

yRaf = RMak.MakeProfile(N,df)
plot(f, yRaf)


#%% generazione rumore a mano
fPsdHalf, yPsdHalf = RMak.PsdEval(N//2+1, df)

PsdArrayNew = np.hstack((yPsdHalf[::-1], yPsdHalf[1:]))
idelta = len(PsdArrayNew) - N
if idelta == 1:# piu lungo
	PsdArrayNew = PsdArrayNew[0:-1] # uguale
elif idelta == 0:
	pass
else:
	print('Error!  len(PsdArrayNew) - len(PsdArray) = %0d' % idelta)

print('len(PsdArrayNew) = %0d' % len(PsdArrayNew))

#%%

#genero rumore
PsdArrayNew[int(N//2)] = 2e-22

y = np.fft.fftshift(PsdArrayNew)
r = 2*pi * np.random.rand(len(PsdArrayNew))

yRaf = np.fft.ifft(y * exp(1j*r))
#yRaf = abs(yRaf)


#% Controllo correlazione
ftRaf = np.fft.fft(yRaf)
acRaf = np.real(np.fft.ifft(ftRaf * np.conj(ftRaf)))
acRaf_ = np.correlate(yRaf, yRaf,'same')
#%%
plot(acRaf_)

#%% COMMENTI
'''
test non completato ancora

'''