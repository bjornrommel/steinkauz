//
// Set up a source.
// The calculation of shot times is simply hardwired. Needs improvement!
//


// include headers
#include <iostream>
#include "define.h"
#include "source.h"


// define constructor for Nodes
Sources::Sources(
	ParameterType parameter, MomentType locmoment, MomentType timemoment, Normal normal) :
	Parameter(parameter),                                                     // parameter
	Layout(parameter, locmoment, timemoment, normal),                         // location and time drift
	Shot(parameter) {                                                         // shot times
};
