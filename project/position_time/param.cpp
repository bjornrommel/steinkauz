//
// Preserve source / node / pinger param.
// The user-defined param shall be checked and preserved inside.
//


// include headers
#include <cassert>
#include "define.h"
#include "param.h"


// define constructor for Param
Param::Param(ParamType param) :
	param(param)   // copy param
{

	// sanity check
	assert(param.profile.maxil > 0);   // at least one inline
	assert(param.profile.maxxl > 0);   // at least one crossline

};


// get entire parameters
ParamType Param::get_param() {

	// return
	return param;

};