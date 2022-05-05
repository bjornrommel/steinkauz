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
	ParameterType parameter, MomentType locmoment, MomentType timemoment) :
	Parameter(parameter),                       // parameter
	Layout(parameter, locmoment, timemoment),   // location and time drift
	Shot(parameter) {                           // shot times
};