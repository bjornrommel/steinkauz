//
// Set up nodes.
//


// guard
#if !defined MY_NODE_H
#define MY_NODE_H


// include headers
#include "define.h"
#include "parameter.h"
#include "layout.h"


// declare class Nodes
class Nodes :
	public Parameter, public Layout {

private:
	// parameter to be declared in the inherited class Parameter
	// layout to be declared in the inherited class Layout

public:
	Nodes(ParameterType, MomentType, MomentType);   // construct

};


// guard
#endif