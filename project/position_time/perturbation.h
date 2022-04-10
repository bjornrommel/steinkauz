//
// Generate a normal distribution.
//


// guard
#if !defined MY_PERTURBATION_H
#define MY_PERTURBATION_H


// include headers
#include <Dense>
#include "define.h"
#include "normal.h"


// declare a class Perturbation of normal distribution
class Perturbation
{

public:
	Perturbation();                                 // construct
	Eigen::VectorXd get_perturb(MomentType, int);   // get perturbation with mean, std

private:
	Normal normal;             // contain properties of a normal distribution
	Eigen::VectorXd perturb;   // perturbation vector

};


// guard
#endif