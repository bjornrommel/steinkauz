//
// Set up a normal distribution.
//


// guard
#if !defined MY_NORMAL_H
#define MY_NORMAL_H


// include headers
#include <random>
#include "define.h"


// declare a class normal for normal distribution
class Normal
{

public:
	Normal();              // constructor
	double get_normal();   // provide normal distribution

private:
	std::default_random_engine generator;            // seed generator
	std::normal_distribution<double> distribution;   // normal distribution

};


// define get_normal inline
inline double Normal::get_normal()
{

	// return one random number: distribution is set to normal, generator contains seed
	return distribution(generator);

};


// guard
#endif