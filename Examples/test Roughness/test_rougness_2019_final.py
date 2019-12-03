# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:07:13 2019

@author: Mike
"""
#%%
import LibWISEr.WiserImport as wr
import LibWISEr.Noise as Noise
import numpy as np
from LibWISEr.must import*
import LibWISEr.ToolLib as tl
from LibWISEr.must import *

if 1==1:
	a = 11.2
	b = -1.482

	N = 1000
	L = 1

	PsdArgs = [a,b]
	PsdFun = wr.Noise.PsdFuns.PowerLaw

	qAxis  = wr.Noise.MakeFrequencies(L,N, False)
	qAxis_Inm = qAxis * 1e9
	plot(qAxis_Inm )
	s, PS = wr.Noise.PsdAnalytic2Noise(L = L, N = N,
								PsdFun = wr.Noise.PsdFuns.PowerLaw,
								   PsdArgs = PsdArgs)

	PSOut = tl.PowerSpectrum(s)
	PSOutHB = abs(PSOut[0:N//2+1]) # HalfBandwidth Power Spectrum
	#----
	plt.figure(1)
	#---- PLOT Numeric PS
	plot(qAxis*1e-9, PSOutHB) # positive bandwidth
	#---- PLOT Analytic PS
	plot(qAxis*1e-9, PS)
	plt.legend(['Numeric PS', 'Analytic PS'])
	plt.loglog()
	plt.xlabel('1/nm')
	plt.ylabel('PS')
	plt.grid('on')
#%%


#%% Protorype of the code (before merging in the two functions)
L = 1
s = wr.Noise.PsdAnalytic2Noise(L = L, N = 1000, PsdFun = wr.Noise.PsdFuns.PowerLaw,
						   PsdArgs =    (a,  b))
#%%
a = 11.2
b = -1.482

if 1==1:
	N = 1000
	L = 1

	PsdArgs = [a,b]
	PsdFun = wr.Noise.PsdFuns.PowerLaw
	df = 2*np.pi / L # minimum max-wavelength <=> min frequency
	fRange = df * np.arange(0,N//2+1)
	yHalf = PsdFun(fRange, *PsdArgs)
	ZeroDC = True
	if ZeroDC:
		yHalf[0] = 0
	sum(yHalf == np.inf)
	plot(fRange, yHalf)
	plt.loglog()

	PsdArray = yHalf
	N = len(PsdArray)
	IsHalfBandwidth = True
	if IsHalfBandwidth == True:
		PsdArrayNew = np.hstack(( PsdArray[-1:0:-1], PsdArray))
		PsdArrayNew = tl.MirrorArray(PsdArray)
	else:
		PsdArrayNew = PsdArray
	sum(PsdArrayNew == np.inf)
	N = len(PsdArrayNew)
	plt.figure(3)
	plot(PsdArrayNew)



	PsdArrayNew = np.fft.fftshift(PsdArrayNew) # Power Spectrum (shifted)
	plot(PsdArrayNew)
	sum(PsdArrayNew==np.inf)

	N = len(PsdArrayNew)
	Phi = 2*np.pi * np.random.rand(N) # random phases

	# The noise signal is proportional to the Spectrum, i.e. to sqrt(PS)
	# N**2 => normalization
	sum(PsdArrayNew==np.inf)
	S = np.sqrt(PsdArrayNew) *   np.exp(1j*Phi)
	s =   np.fft.ifft(S)
	sr = np.real(s) * np.sqrt(2)

	PSOut = abs(np.fft.fft(sr))**2
	PSOutRx = abs(PSOut[N//2:-1]) # take the positive bandwidth (and force >0)
	PSOutHB = abs(PSOut[0:N//2])
	#----
	plt.figure(2)
	#---- PLOT Numeric PS
	plot(PSOutHB) # positive bandwidth
	#---- PLOT Analytic PS
	plot(PsdArray)
	plt.loglog()
	plt.legend(['Numeric PS', 'Analytic PS'])


#%% gaussian
sigma_f = 1000

if 1==1:
	N = 1000
	L = 1

	PsdArgs = [sigma_f]
	PsdFun = wr.Noise.PsdFuns.Gaussian
	df = 2*np.pi / L # minimum max-wavelength <=> min frequency
	fRange = df * np.arange(0,N//2+1)
	yHalf = PsdFun(fRange, *PsdArgs)
	ZeroDC = True
	if ZeroDC:
		yHalf[0] = 0
	sum(yHalf == np.inf)

	PsdArray = yHalf
	N = len(PsdArray)
	IsHalfBandwidth = True
	if IsHalfBandwidth == True:
		PsdArrayNew = tl.MirrorArray(PsdArray)
	else:
		PsdArrayNew = PsdArray
	sum(PsdArrayNew == np.inf)
	N = len(PsdArrayNew)

	plt.figure(3)
	plot(PsdArrayNew)

	PsdArrayNew = np.fft.fftshift(PsdArrayNew) # Power Spectrum (shifted)
	plot(PsdArrayNew)
	sum(PsdArrayNew==np.inf)

	N = len(PsdArrayNew)
	Phi = 2*np.pi * np.random.rand(N) # random phases

	# The noise signal is proportional to the Spectrum, i.e. to sqrt(PS)
	# N**2 => normalization
	sum(PsdArrayNew==np.inf)
	S = np.sqrt(PsdArrayNew) *   np.exp(1j*Phi)
	s =   np.fft.ifft(S, norm = 'ortho')
	sr = sr

	PSOut = abs(np.fft.fft(sr, norm = 'ortho'))**2
	PSOutHB = abs(PSOut[0:N//2])
	#----
	plt.figure(2)
	#---- PLOT Numeric PS
	plot(PSOutHB) # positive bandwidth
	#---- PLOT Analytic PS
	plot(PsdArray)
	plt.legend(['Numeric PS', 'Analytic PS'])


#%%

x = np.array([0,1,2,3,4])
xx  = np.hstack(( x[-1:0:-1], x[:-1]))

xxs = np.fft.fftshift(xx)

S = np.fft.fft(xxs)

#%%
#%% power law
a = 11.2
b = -1.482

if 1==1:
	N = 1000
	L = 1

	PsdArgs = [a,b]
	PsdFun = wr.Noise.PsdFuns.PowerLaw
	df = 2*np.pi / L # minimum max-wavelength <=> min frequency
	fRange = df * np.arange(0,N//2+1)
	yHalf = PsdFun(fRange, *PsdArgs)
	ZeroDC = True
	if ZeroDC:
		yHalf[0] = 0
	sum(yHalf == np.inf)

	PsdArray = yHalf
	N = len(PsdArray)
	IsHalfBandwidth = True
	if IsHalfBandwidth == True:
		PsdArrayNew = tl.MirrorArray(PsdArray)
	else:
		PsdArrayNew = PsdArray
	sum(PsdArrayNew == np.inf)
	N = len(PsdArrayNew)

	plt.figure(3)
	plot(PsdArrayNew)

	PsdArrayNew = np.fft.fftshift(PsdArrayNew) # Power Spectrum (shifted)
	plot(PsdArrayNew)
	sum(PsdArrayNew==np.inf)

	N = len(PsdArrayNew)
	Phi = 2*np.pi * np.random.rand(N) # random phases

	# The noise signal is proportional to the Spectrum, i.e. to sqrt(PS)
	# N**2 => normalization
	sum(PsdArrayNew==np.inf)
	S = np.sqrt(PsdArrayNew) *   np.exp(1j*Phi)
	s =   np.fft.ifft(S, norm = 'ortho')
	sr = s

	PSOut = abs(np.fft.fft(sr, norm = 'ortho'))**2
	PSOutHB = abs(PSOut[0:N//2])
	#----
	plt.figure(2)
	#---- PLOT Numeric PS
	plot(PSOutHB) # positive bandwidth
	#---- PLOT Analytic PS
	plot(PsdArray)
	plt.legend(['Numeric PS', 'Analytic PS'])
	plt.loglog()

#%% power law
a = 11.2
b = -1.482

if 1==1:
	N = 1000
	L = 1

	PsdArgs = [a,b]
	PsdFun = wr.Noise.PsdFuns.PowerLaw

	s, PS = wr.Noise.PsdAnalytic2Noise(L = L, N = N,
								PsdFun = wr.Noise.PsdFuns.PowerLaw,
								   PsdArgs = PsdArgs)

	PSOut = tl.PowerSpectrum(s)
	PSOutHB = abs(PSOut[0:N//2])
	#----
	plt.figure(2)
	#---- PLOT Numeric PS
	plot(PSOutHB) # positive bandwidth
	#---- PLOT Analytic PS
	plot(PS)
	plt.legend(['Numeric PS', 'Analytic PS'])
	plt.loglog()

#%% TEST HEW SCATTERING

def HewScatteringContribution (Lambda, GrazingAngle, Kn,n):
	return (Kn/(n-1)) **(1/(n-1)) * (np.sin(GrazingAngle)/Lambda) **(3-n)/(n-1)

Kn = 0.233 # m^3
n = 2.122 #
Lambda_nm = np.linspace(0.5,20,1000)
Lambda = Lambda_nm * 1e-9

GrazingAngle = np.deg2rad(2.5)
Hew = HewScatteringContribution(Lambda, GrazingAngle, Kn,n)
Hew_um = Hew * 1e6
plt.plot(Lambda_nm, Hew_um)
plt.xlabel('lambda nm')
plt.ylabel('um')


