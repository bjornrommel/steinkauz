# Positioning and Timing of Nodes

## Installation

The software is written in C++ according to the ISO C++20 Standard. It requires the [Eigen](https://eigen.tuxfamily.org) and [pybind11](https://github.com/pybind/pybind11) libraries as well as a [Python 3.10](https://www.python.org) installation with the [matplotlib](https://matplotlib.org/) library.  

This software is work in progress. Specifically, the use of pingers is not yet fully implemented.

The user-definable parameters are located in config.h. For both sources and nodes,
XO, YO, Z0 denote the coordinte origin, that is the left bottom grid point, of their respective layout,
DX, DY the spacing of the grid points of their respective layout,
MEANX, MEANY, MEANZ the mean of the actual off-grid point placing (typically 0. as we do not typically have systematic errors),
STDX, STDY, STDZ the standard deviation of the actual off-grid point placing (typically around 1m or so for nodes, less for sources),
STD0, STD1, STD2 the standard deviations of a constant, linear and quadratic time drift, respectively
The time drift is not yet implemented. Idea being, each node will be assigned a set of std0, std1, std2 parameters, randomally selected from the normal distribution STD0, STD1, STD2 valid across all nodes; hence, each node will show their unique time drift. 

Specifically, do not use "debug" mode with VisualStudio: pybind11 calling matplotlib fails when closing the interpreter.