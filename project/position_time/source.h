//
// Set up a source.
//


// guard
#if !defined MY_SOURCE_H
#define MY_SOURCE_H


// include headers
#include <vector>
#include "config.h"
#include "define.h"
#include "param.h"
#include "layout.h"
#include "shot.h"


// declare class Nodes
class Sources : public Param, public Layout, public Shot
{

private:
	// param to be declared in the inherited class Param
	// layout to be declared in the inherited class Layout
	// shot to be declared in the inherited class Shot

public:
	Sources(ParamType, MomentType, MomentType);   // construct

};


// guard
#endif