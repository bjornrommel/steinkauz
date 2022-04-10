//
// Coordinates of nodes or sources.
//

// pragma
#pragma once

// include system libraries
#include <vector>

// include eigen-3.4.0 libraries
#include <Dense>

// declare a coordinate class
class Coordinate {
public:
	Coordinate(double, double, double);   // constructor
private:
	Eigen::Vector3d loc;
};
