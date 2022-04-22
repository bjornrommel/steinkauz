//
// Generate a normal distribution.
//


// include personal headers
#include "define.h"
#include "perturbation.h"
#include "normal.h"


// define constructor for Perturbation
Perturbation::Perturbation() {
};


// define function for Perturbation
Eigen::VectorXd Perturbation::get_perturbation(MomentType moment, int dim, Normal normal) {

	// generate perturbation of the same length as moment
	Eigen::VectorXd perturbation(dim);                                            // define perturbation
	for (int i = 0; i < dim; ++i) {                                               // loop over vector dimension
		perturbation(i) = moment.mean[i] + moment.std[i] * normal.get_normal();   // modify mean, std
	};

	// return
	return perturbation;

};