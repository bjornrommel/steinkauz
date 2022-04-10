//
// Generate a normal distribution.
//


// include personal headers
#include "define.h"
#include "perturbation.h"
#include "normal.h"


// define constructor for Perturbation
Perturbation::Perturbation() :
	normal()                     // initialize a normal distribution
{

};


// define function for Perturbation
Eigen::VectorXd Perturbation::get_perturb(MomentType locmoment, int dim)
{

	// generate perturbation vector of the same length as locmoment
	Eigen::VectorXd perturb(dim);                                            // define perturbation vector
	for (int i = 0; i < dim; ++i) {                                          // loop over vector dimension
		perturb(i) = locmoment.mean[i] + locmoment.std[i] * normal.get_normal();   // modify mean, std
	};

	// return
	return perturb;

};