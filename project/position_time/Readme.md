# Positioning and Timing of Nodes

## Installation

The software is written in C++ according to the ISO C++20 Standard. It require the [Eigen](https://eigen.tuxfamily.org) and [pybind11](https://github.com/pybind/pybind11) libraries as well as a [Python 3.10](https://www.python.org) installation with the [matplotlib](https://matplotlib.org/) library.  

This software is work in progress. Specifically, the use of pingers is not yet fully implemented.

Specifically, do not use "debug" mode with VisualStudio: pybind11 calling matplotlib fails when closing the interpreter.