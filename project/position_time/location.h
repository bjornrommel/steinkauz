//
// Assign a location to any device.
//


// guard
#if !defined MY_LOCATION_H
#define MY_LOCATION_H


// include headers
#include <Dense>
#include "config.h"
#include "define.h"
#include "param.h"


// declare an abstract class Device
class Location 
{

private:
	int index;          // index number per node
	LocationType loc;   // location of node (x, y, z)

public:
	Location(ParamType, MomentType, int, int);        // construct
	void init_index(ParamType, int, int);                     // assign index number
	void init_loc(ParamType, MomentType, int, int);   // assign location
	std::vector<Eigen::Vector3d> get_loc();                      // get location

};


// guard
#endif