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

N = 1000 # punti dello specchio
N2 = N//2
L = 400 # (mm)
L_um = L*1e3
df_um = 1/L_um
ff,yy = RMak.NumericPsdGetXY()


#%% interp lineare

fun = interp1d(ff,yy)
yNew = fun(ff)

plot(log(ff), log(yNew),'r')
plot(log(ff), log(yy),'.')



#%% con spline
fun = interpolate.splrep(log(ff), log(yy), s=2)
yNew2_log = interpolate.splev(log(ff),fun)
yNew2 = exp(yNew2_log)
plot(log(ff), log(yNew2),'r')
plot(log(ff), log(yy),'.')



#%%

N = len(f)
plt.figure(1)
plot(np.log(ff), np.log(yy),'.r')
plot(fSpline,ySpline,'g')
plt.xlabel('f (m^-1)')
#%%



df = np.mean(np.diff(ff))

# qui f e y avranno N elementi





P = FftAlign2(Psd, 2*N)
P = P/2.0; #necessario per ripartire la potenza spettrale fra freq + e -
  np = n_elements(fx)

L = 1/(fx[1]-fx[0])
  x_line = double(findgen(NP)*float(L)/float(NP) - L/2)
  tr_four = dcomplexarr(NP)
  seed = (double(systime(/seconds))-long(systime(/seconds)))*1e+6
  num =randomu(seed, NP/2-1)
  for i =long(1), NP/2-1 do tr_four[i] = double(sqrt(P[i+NP/2-1]/(L*1000))) *dcomplex(cos(2*!pi*num[i-1]), sin(2*!pi*num[i-1])) ;nm^2
  for i =long(0), NP/2-1 do begin
    tr_four[i+NP/2]=conj(tr_four[NP/2-i])
  endfor
  num =0
  line =fft(tr_four, /inverse); nm
  x = x_line
  res = double(line)
  resid = imaginary(line)
  return, res
end