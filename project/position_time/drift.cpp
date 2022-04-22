//
// Set up a time drift.
//


// include headers
#include <iostream>
#include <iomanip>
#include "define.h"
#include "perturbation.h"
#include "drift.h"


// define constructor for Drift
Drift::Drift(
	ParameterType parameter, MomentType driftmoment, int il, int xl, Normal normal, bool production) :
	drift(init_drift(parameter, driftmoment, il, xl, normal, production)) {
};


// initialize variable drift
std::vector<std::vector<double>>
	Drift::init_drift(
		ParameterType parameter, MomentType driftmoment, int il, int xl, Normal normal, bool production)
{

	// get perturbation for STD's
	Perturbation perturbation;
	Eigen::VectorXd scatter =
		perturbation.get_perturbation(driftmoment, 3, normal);   // not a true vector, but works below

	// assign perturbations and construct drift
	std::vector<std::vector<double>> drift = {
		{0., 0., 0.},                            // nominal (to comply with NOM, ACT, EST notation)
		{scatter[0], scatter[1], scatter[2]},    // actual
		{0., 0., 0.}                             // estimated
	};

	// exclude memory assignment only
	if (production) {

		// printout
		if (PRINT_DRIFT) {
			std::cout.setf(std::ios::fixed, std::ios::floatfield);
			std::cout.precision(6);
			std::cout
				<< DEVICE[size_t(parameter.flag) - 1] << " (" << il << ", " << xl << ") time drift"
				<< std::endl;
			std::cout.setf(std::ios::showpos);
			std::cout
				<< "nom.: "
				<< std::setw(8) << drift[NOM][X] << ", "
				<< std::setw(8) << drift[NOM][Y] << ", "
				<< std::setw(8) << drift[NOM][Z] << std::endl;
			std::cout
				<< "act.: "
				<< std::setw(8) << drift[ACT][X] << ", "
				<< std::setw(8) << drift[ACT][Y] << ", "
				<< std::setw(8) << drift[ACT][Z] << std::endl;
			std::cout << std::endl;
			std::cout.unsetf(std::ios::showpos);
		};

	};

	// return
	return drift;

};