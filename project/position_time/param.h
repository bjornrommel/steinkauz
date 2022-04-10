//
// Preserve the source / node / pinger param.
//


// guard
#if !defined MY_PARAMS_H
#define MY_PARAMS_H


// include headers
#include "define.h"


// declare class Nodes
class Param {

private:
	ParamType param;   // declare param with ParamType declared in define.h

public:
	Param(ParamType);        // construct
	ParamType get_param();   // get entire param

};


// guard
#endif