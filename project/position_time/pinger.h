//
// Set up nodes.
//


// guard
#if !defined MY_PINGER_H
#define MY_PINGER_H


// include headers
#include "define.h"
#include "parameter.h"
#include "layout.h"


// declare class Pingers
class Pingers :
	public Parameter, public Layout {

private:
	// parameter to be declared in the inherited class Parameter
	// layout to be declared in the inherited class Layout

public:
	Pingers(ParameterType, MomentType, MomentType);   // construct

};


// guard
#endif