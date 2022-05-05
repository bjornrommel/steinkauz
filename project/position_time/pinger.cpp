//
// Set up nodes.
// Parameters are copied into the variable parameter of class Parameter.
// Node locations are computed and stored in the variable layout of class Layout.
//


// include headers
#include "define.h"
#include "pinger.h"


// define constructor for Pingers
Pingers::Pingers
	(ParameterType parameter, MomentType locmoment, MomentType driftmoment) :
	Parameter(parameter),                         // parameters
	Layout(parameter, locmoment, driftmoment) {   // location and clock drift
};