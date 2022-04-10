//
// Set up a time drift.
//


// include headers
#include <iostream>
#include "config.h"
#include "define.h"
#include "perturbation.h"
#include "drift.h"


// define constructor for Drift
Drift::Drift(MomentType driftmoment) {

	// generate randomized STD's for a time drift
	init_drift(driftmoment);   // outsource initialization of std

};


// initialize variable drift
void Drift::init_drift(MomentType driftmoment) {

	// get perturbation for STD's
	Perturbation perturbation;                      // dynamic re-sizing in case of higher-order STD's
	Eigen::VectorXd perturb =
		perturbation.get_perturb(driftmoment, 3);   // not a true vector, but works below

	// assign perturbations and construct drift
	std::vector<std::vector<double>> drift = {
		{0., 0., 0.},                           // nominal (to comply with NOM, ACT, EST notation)
		{perturb[0], perturb[1], perturb[2]},   // actual
		{0., 0., 0.}                            // estimated
	};

};


// get variable drift
std::vector<std::vector<double>> Drift::get_drift() {

	// return
	return drift;

};