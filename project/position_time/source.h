//
// Set up a source.
//


// guard
#if !defined MY_SOURCE_H
#define MY_SOURCE_H


// include headers
#include <vector>
#include "define.h"
#include "parameter.h"
#include "layout.h"
#include "shot.h"
#include "normal.h"


// declare class Nodes
class Sources : public Parameter, public Layout, public Shot {

private:
	// param to be declared in the inherited class Param
	// layout to be declared in the inherited class Layout
	// shot to be declared in the inherited class Shot

public:
	Sources(ParameterType, MomentType, MomentType, Normal);   // construct

};


// guard
#endif