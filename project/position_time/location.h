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


// declare an abstract class Location
class Location
{

private:
	int index;               // index number per node
	LocationType location;   // location of node (x, y, z)

public:
	Location(ParameterType, MomentType, int, int, bool = true);           // construct
	void init_index(ParameterType, int, int);                             // assign index number
	void init_location(ParameterType, MomentType, int, int, bool=true);   // assign location
	inline LocationType get_location() const;                             // get location

};


inline LocationType Location::get_location() const {

	// return loc
	return location;

};


// guard
#endif