# WISER, explained	



WISER is a Physical optics computation package created to simulate the focal spot produced by Hard and Soft X-Ray mirrors, such as those used in [X-ray telescopes](https://en.wikipedia.org/wiki/X-ray_telescope) or in [Synchrotrons](https://en.wikipedia.org/wiki/Synchrotron) and [Free Electorn Lasers](https://en.wikipedia.org/wiki/Free-electron_laser) . 

It is specialized in the wave propagation at *tangential reflections,* representing the optical elements by means of linear support geometric entities, such as ellipse-arc, segments, circle-arc, etc. 

|                       **OASYS-WISER**                        |                           WiseLib                            |
| :----------------------------------------------------------: | :----------------------------------------------------------: |
| the visual interface within the OASYS canvas<br />to get fast results in an intuitive way | The core Python library,<br />to unleash the full power of WISER |



## How do I use WISER?

WISER can be used in two forms: 

**In OASYS, with a visual interface**

<u>Use the OASYS if you belong to the 99% of people who are out of time and are thinking "I just want to see if this software get my job done!</u>!" 

OASYS is better suited for simple simulations.

**In a Python script, as a library** 

```
form LibWiser import Wiser

Beamline = Wiser.Example.GetExampleBeamline()
print(Beamline)
Beamline.ComputeFields()
```

<u>Use the library if you belong to the 1% of people that craves for unleashing the full power of WISER.</u>

LibWiser is better suited for sophisticated simulations, with batch operations, scans over distinct physical variables, tailored control of focus-search algorithms, etc.





# 





