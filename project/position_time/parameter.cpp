//
// PRESIDUALerve source / node / PINGER_ parameter.
// The user-defined parameters shall be checked and pRESIDUALerved inside a variable parameter of type ParameterType.
//


// include headers
#include <cassert>
#include "define.h"
#include "parameter.h"


// define constructor for Parameter
Parameter::Parameter(ParameterType parameter) :
	parameter(parameter) {                         // copy parameter

	// sanity check flag
	int flag = parameter.flag;
	assert((flag == NODE_FLAG) || (flag == SOURCE_FLAG) || (flag == PINGER_FLAG));

	// sanity check profile
	ProfileType profile = parameter.profile;
	assert(profile.maxil > 0);                 // at least one inline
	assert(profile.maxxl > 0);                 // at least one crossline

	// sanity check spacing
	SpacingType spacing = parameter.coordinate.spacing;
	assert(spacing.dx > 0.);                              // positive spacing; start lower left corner
	assert(spacing.dy > 0.);                              // dito

};