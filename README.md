# Steinkauz

Projekt Steinkauz: a series of notebooks on various topics of seismic data processing.
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bjornrommel/steinkauz/master)  

## Subsurface-Traveltime Ambiguity / Python

- [Subsurface-Traveltime Ambiguity](https://github.com/bjornrommel/steinkauz/tree/master/project/ambiguity):
Modifying the subsurface, and the velocity of a seismic wave travelling through the subsurface, in some specific way changes the traveltime of that wave very little. Here, a Python software simulates the propagation of two waves, the original and a modified one, and displays their wavefronts. A [paper](https://github.com/bjornrommel/steinkauz/tree/master/project/ambiguity/BjörnRommel.WeaklyAnellipticalTraveltimeAnalysis.pdf) "Weakly-Anelliptical Traveltime Analysis: Ambiguity between Subsurface and Elasticity" is under review with Geophysics. The corresponding [software](https://github.com/bjornrommel/steinkauz/tree/master/project/ambiguity/ambiguity-as_used_for_manuscript.py) written in Python is also available.

## Positioning and Timing of Nodes / C++

- [Positioning and Timing of Nodes](https://github.com/bjornrommel/steinkauz/tree/master/project/position_time)
Deploying nodes is not perfect: nodes are usually slightly mis-positioned. Furthermore, the clocks used in nodes tend to drift over time. Using source location, all available first breaks and later pinger time signals, however, the position of nodes and their time drifts can be determined.  

## Notebooks / Jupyter

- [AVO for Density](https://github.com/bjornrommel/steinkauz/tree/master/project/avo_for_density):
Often, density is said to be unobtainable by AVO inversion. However, a Bayesian-style AVO inversion based on a prior model, seismic data and a best estimate of their respective uncertainties is robust. It will invert for density, too, and its posterior uncertainty will be smaller. Also, from a philosophical point of view, we make optimal use of all available information.
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bjornrommel/steinkauz/master?labpath=%2Fproject%2Favo_for_density%2Favo_for_density.ipynb)

- [No DC Removal](https://github.com/bjornrommel/steinkauz/tree/master/project/no_dc_removal): 
Seismic instruments are calibrated by equating their null-line with the mean of a very large noise dataset. Nonetheless, individual seismic records, which are small in size, will show means fluctuating around the null-line. 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bjornrommel/steinkauz/master?filepath=project/no_dc_removal/no_dc_removal.ipynb)

- [Steinkauz Tutorial](https://github.com/bjornrommel/steinkauz/tree/master/project/steinkauz):
The Jupyter module steinkauz provides a line / cell magic rendering all LaTeX input.
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bjornrommel/steinkauz/HEAD?filepath=project%2Fsteinkauz%2Ftutorial.ipynb)

## Patent / Law

- [Time Drift Calibration:](https://github.com/bjornrommel/steinkauz/tree/master/project/time_drift_calibration)
Calibrate a time drift of a node during its deployment (in-situ). 

## Steinkauz / Jupyter module rendering LaTeX

- [Download Steinkauz:](https://github.com/bjornrommel/steinkauz/tree/master/project/steinkauz)
steinkauz.py is an iPython line/cell magics extension. It converts a LaTeX fragment, which it gets from a file or reads in from the notebook itself, into a PNG image. This PNG file will then be displayed inside the notebook. Key point being, that fragment can be updated in line with the results of computations made in that notebook. For details see the tutorial and download the source file.

## Blended Acquisition / Technical Marketing
- [Multiple Sources:](https://github.com/bjornrommel/steinkauz/tree/master/project/blended_acquisition)
An illustrative, but very technical introduction into the subject of blended acquisition including triple and penta sources.

## Collaboration and Support
 
You are invited to improve any notebook or even to donate one of your own making.

## Credit  

You can use the module and notebooks, but, please, give credit where credit is due.   

## Contact  

## Acknowledgements  

The Jupyter magic steinkauz has been inspired by Dan MacKinlay's latex_fragment (https://github.com/danmackinlay/latex_fragment)  
And, then, there are all the contributors to Jupyter Notebook!

