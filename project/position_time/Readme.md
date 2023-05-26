# Positioning and Timing of Nodes

Deploying nodes is not perfect: nodes are usually slightly mis-positioned. Furthermore, the clocks used in nodes tend to drift over time. Using source location, all available first breaks and later pinger time signals, however, the position of nodes and their time drifts can be determined.

[Source and Receive Positioning](SubsurfaceModel.png?raw=true) shows the source and receiver points in red and green, respectively, and before and after re-positioning as open and filled circles, respectively. Since the source positioning is very accurate to begin with, source points are virtually unchanged.

## Installation

The software is written in C++ according to the ISO C++20 Standard, with the graphics written in Python 3. So, obviously, it requires a working C++ and [Python 3](https://www.python.org) environment. Furthermore, it specifically requires the [Eigen directory](https://eigen.tuxfamily.org) as well as the [matplotlib](https://matplotlib.org/) and [pybind11](https://github.com/pybind/pybind11) modules. And it is tested with VisualStudio 2022 only; however, do not use "debug" mode with VisualStudio: pybind11 calling matplotlib fails when closing the interpreter.

Admittedly, this software is work in progress. Specifically, the use of pingers is not yet implemented.

The user-definable parameters are located in config.h. For both sources and nodes,
XO, YO, Z0 denote the coordinte origin, that is the left bottom grid point, of their respective layout,
DX, DY the spacing of the grid points of their respective layout,
MEANX, MEANY, MEANZ the mean of the actual off-grid point placing (typically 0. as we do not typically have systematic errors),
STDX, STDY, STDZ the standard deviation of the actual off-grid point placing (typically around 1m or so for nodes, less for sources),
STD0, STD1, STD2 the standard deviations of a constant, linear and quadratic time drift, respectively
The time drift is not yet implemented. Idea being, each node will be assigned a set of std0, std1, std2 parameters, randomally selected from the normal distribution STD0, STD1, STD2 valid across all nodes; hence, each node will show their unique time drift. 

## C++ Specifics 
An example of a smart pointer is implemented in the module location.cpp. This modules assign nominal, actual and estimated coordinates to a grid point within the layout of any device. So, 3 coordinates per grid point times the number of inlines and xlines makes up a very large variable, furthermore one that is passed around.