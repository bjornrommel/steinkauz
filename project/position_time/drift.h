//
// Set up a time drift.
// Converts the statistical known distributions of STD's for a drift into actual randomized STD's
// for each individual drift.
//


// guard
#if !defined MY_DRIFT_H
#define MY_DRIFT_H


// include headers
#include <vector>
#include "location.h"
#include "config.h"


// declare class Drift
class Drift
{

private:
	DriftType drift;   // declare drift

public:
	Drift(ParameterType, MomentType, int, int, bool=true);                  // construct
	DriftType init_drift(ParameterType, MomentType, int, int, bool=true);   // initialize drift
	inline DriftType get_drift() const;                                     // get drift

};


// get variable drift
inline DriftType Drift::get_drift() const {

	// return
	return drift;

};


// guard
#endif