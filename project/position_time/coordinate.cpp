//
// Coordinates of any one node or source.
//

// include header
#include "coordinate.h"

// define constructor for Coordinate
Coordinate::Coordinate(double inx, double iny, double inz) {
	loc = Eigen::Vector3d(inx, iny, inz);
};