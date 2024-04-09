# Steinkauz

## Subsurface-Velocity Ambiguity

Traveltime analysis over an anisotropic subsurface is inherently ambiguous. I can modify the subsurface and the exact or linearized velocity of a seismic wave travelling through that subsurface, in some specific way, yet the traveltimes observed at the surface show no or only "small" changes, respectively.  
![two different subsurface-wavefronts models](SubsurfaceModel.png?raw=true)
- The paper "Weakly-Anelliptical Traveltime Analysis: Ambiguity between Subsurface and Elasticity" is under review with Geophysics. 
- A [Python software called "ambiguity"](https://github.com/bjornrommel/steinkauz/blob/master/project/ambiguity/ambiguity-as_used_for_manuscript.py) simulates the propagation of two waves, the original and a modified one, and displays their wavefronts. 
- A [Python package called "ttwean"](https://github.com/bjornrommel/steinkauz/blob/master/project/ambiguity/ttwean) analysizes the velocity-subsurface ambiguity in detail: exact / linearized phase and energy velocity under stretch and offset-traveltime curves over a single layer. Install with 'pip install ttwean-3.0.1-py3-none-any.whl' or fall back on the source code 'ttwean-3.0.1.tar.gz'.
- A [subset of the above Python package called "ttwean_for_ttcrpy"](https://github.com/bjornrommel/steinkauz/blob/master/project/ambiguity/ttwean_for_ttcrpy) is designed specifically for use with the [ray-tracing software ttcrpy](https://github.com/groupeLIAMG/ttcr).

