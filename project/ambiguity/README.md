# Steinkauz

## Subsurface-Traveltime Ambiguity

Traveltime analysis over an anisotropic subsurface is inherently ambiguous. I can modify the subsurface and the   (linearized) velocity of a seismic wave travelling through that subsurface, in some specific way, yet the traveltimes observed at the surface show only "small" changes.  
![two different subsurface-wavefronts models](SubsurfaceModel.png?raw=true)
- A [paper](https://github.com/bjornrommel/steinkauz/tree/master/project/ambiguity/BjörnRommel.WeaklyAnellipticalTraveltimeAnalysis.pdf) "Weakly-Anelliptical Traveltime Analysis: Ambiguity between Subsurface and Elasticity" is under review with Geophysics. 
- A [Python software](https://github.com/bjornrommel/steinkauz/blob/master/project/ambiguity/ambiguity-as_used_for_manuscript.py) simulates the propagation of two waves, the original and a modified one, and displays their wavefronts. It is to be used within the jupyter environment.

