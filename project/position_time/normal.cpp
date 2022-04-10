//
// Set up a normal distribution.
// The normal distribution shall use standard mean = 0.0 and std = 1.0. Actual mean and standard deviation
// shall be implemented in perturbation.cpp, where random numbers are collected per vector or matrix.
// The default seed generator, generator.seed(unsigned int(time(NULL))), does not have sufficiently fine
//  granularity in time. Instead, use the method device().


// include header
#include <random>
#include "define.h"
#include "normal.h"


// define constructor for Normal, which seeds and defines the general properties of a normal distribution
Normal::Normal()
{

	// set seed and mean / std of a normal distribution
	std::random_device device;                                  // random device
	generator.seed(unsigned int(device()));                     // seed with random number from device()
	std::normal_distribution<double> distribution(MEAN, STD);   // call standard normal distribution

};