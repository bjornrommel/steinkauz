//
// Set up a source. 
// The calculation of shot times is simply hardwired. Needs improvement!
//


// include headers
#include <iostream>
#include "define.h"
#include "source.h"


// define constructor for Nodes
Sources::Sources(ParamType param, MomentType locmoment, MomentType timemoment) :
	Param(param),                           // source param
	Layout(param, locmoment, timemoment),   // source location and timemoment drift
	Shot(param)                             // source shot times
{

};
