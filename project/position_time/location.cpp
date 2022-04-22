//
// Assign a location to any device.
//
// The index number consists of one block each for inline and crossline numbering. It is used for easy
// identification of a position.
//


// include headers
#include <iostream>
#include <iomanip>
#include <Dense>
#include "define.h"
#include "perturbation.h"
#include "location.h"


// define constructor for Location
Location::Location(
	ParameterType parameter, MomentType locmoment, int il, int xl, Normal normal, bool production) {

	// declare variables
	init_index(parameter, il, xl);                                     // outsource index number
	init_location(parameter, locmoment, il, xl, normal, production);   // outsource location

};


// assign index
void Location::init_index(ParameterType parameter, int il, int xl) {

	// number consisting of flag, inline, crossline
	ProfileType profile = parameter.profile;
	int ib = int(pow(10, ceil(log10(profile.maxil + 0.000001))));   // e.g. aaa for max 3-digit inline
	int xb = int(pow(10, ceil(log10(profile.maxxl + 0.000001))));   // e.g. bb for max 2-digit crossline
	index = parameter.flag * ib * xb + il * xb + xl;                // e.g, 1aaabb

};


// define function for init_loc
void Location::init_location(
	ParameterType parameter, MomentType locmoment, int il, int xl, Normal normal, bool production)
{

	// initialize location
	OriginType origin = parameter.coordinate.origin;
	SpacingType spacing = parameter.coordinate.spacing;
	Eigen::Vector3d row = { origin.x0 + il * spacing.dx, origin.y0 + xl * spacing.dy, origin.z0 };
	location = {
		row,   // will be nominal [NOM]
		row,   // will be actual [ACT]
		row    // will be estimated [EST]
	};

	// exclude when assigning memory
	if (production) {

		// get perturbation
		Perturbation perturbation;
		Eigen::Vector3d scatter = perturbation.get_perturbation(locmoment, SPACE, normal);

		// actual = summing location + perturbation
		location[ACT] += scatter;

		// print
		if (PRINT_LOCATION) {
			std::cout.setf(std::ios::fixed, std::ios::floatfield);
			std::cout.precision(3);
			std::cout << DEVICE[size_t(parameter.flag) - 1] << " (" << il << ", " << xl << ") no " << index
				<< std::endl;
			std::cout << "nom.: " << std::setw(8) << location[NOM][X]
				<< ", " << std::setw(8) << location[NOM][Y]
				<< ", " << std::setw(8) << location[NOM][Z] << std::endl;
			std::cout << "act.: " << std::setw(8) << location[ACT][X]
				<< ", " << std::setw(8) << location[ACT][Y]
				<< ", " << std::setw(8) << location[ACT][Z] << std::endl;
			std::cout << "est.: " << std::setw(8) << location[EST][X]
				<< ", " << std::setw(8) << location[EST][Y]
				<< ", " << std::setw(8) << location[EST][Z] << std::endl;
			std::cout << std::endl;
		};

	};

};