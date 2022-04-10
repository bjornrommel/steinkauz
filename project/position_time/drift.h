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
class Drift {

private:
	std::vector<std::vector<double>> drift;   // declare drift

public:
	Drift(MomentType);                              // construct
	void init_drift(MomentType);                    // initialize drift
	std::vector<std::vector<double>> get_drift();   // get drift

};


// guard
#endif