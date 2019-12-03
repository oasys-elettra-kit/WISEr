
#%%
import importlib
from LibWISEr import WiserImport as wr
importlib.reload(wr)

wr.tl.Metrology.RectangularGrating()


#%%
# PRESTO spectrometer parameter
# Grazing angle: 2.5 deg
L0 = 250e-3 	# 	Total length
L1 = 60e-3 	#	groove length
N = 1000
LinesPerMillimiter = 3750
GrooveHeigth = 9.5
DutyCycle = 0

x = np.linspace(-L/2., L/2., num=noPts)
grating = RectangularGrating(L, noPts, linesPerMm, grooveHeight, L0=0.2)

print('Number of grooves = {}'.format(0.4*1e3 * linesPerMm))

plt.plot(x, grating)
plt.show()