# WISER
WISER: Wavefront sImulation codE libRary 

WISER is a physical optics package, currently based on Huygens-Fresnel propagation integral, conceived for simulating the optical performances of X-Ray Mirrors. 

Features
----
- It is 2D 
- Optical elements are segments, curves, elliptic arc sections, circle arc setions, etc.
- Various sorces
- Various optical elements
- Accounts for error surface defects
  - Figure error (as profile)
  - Roughness (as statistical Power Density)
- Uses Huygens-Fresnel integral (monochromatic light, spatially coherent)


Light Sources
----
- Gaussian (TEM00)
- Gaussian-Laguerre
- Point Source (Spherical wave)
- Plane Wave
- Arbitrary (passed as 1d complex field at given wavelength)
-
Optics element
----
- Plane Mirror
- Elliptic Mirror
- Spherical Mirror
- Slit
- Detector
- Grating

Common Tasks
----
