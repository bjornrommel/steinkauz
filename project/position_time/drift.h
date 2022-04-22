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
	std::vector<std::vector<double>> drift;   // declare drift

public:
	Drift(ParameterType, MomentType, int, int, Normal, bool=true);            // construct
	std::vector<std::vector<double>> 
		init_drift(ParameterType, MomentType, int, int, Normal, bool=true);   // initialize drift
	inline std::vector<std::vector<double>> get_drift();                      // get drift

};


// get variable drift
inline std::vector<std::vector<double>> Drift::get_drift()
{

	// return
	return drift;

};


// guard
#endif