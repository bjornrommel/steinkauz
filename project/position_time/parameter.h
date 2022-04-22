//
// PRESIDUALerve the source / node / PINGER_ parameters.
//


// guard
#if !defined MY_PARAMS_H
#define MY_PARAMS_H


// include headers
#include "define.h"


// declare class Nodes
class Parameter {

private:
	ParameterType parameter;   // declare parameter

public:
	Parameter(ParameterType);                     // construct
	inline ParameterType get_parameter() const;   // get entire parameter

};


// get entire parameters
inline ParameterType Parameter::get_parameter() const
{

	// return
	return parameter;

};


// guard
#endif