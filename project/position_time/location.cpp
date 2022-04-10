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
#include "param.h"
#include "perturbation.h"
#include "location.h"


// define constructor for Location
Location::Location(ParamType param, MomentType locmoment, int il, int xl)
{

	// declare variables
	init_index(param, il, xl);            // outsource index number
	init_loc(param, locmoment, il, xl);   // outsource initialization of location

};


// assign unique number
void Location::init_index(ParamType param, int il, int xl) {

	// number consisting of flag, inline, crossline
	ProfileType profile = param.profile;
	int ib = int(pow(10, ceil(log10(profile.maxil + 0.000001))));   // e.g. aaa for max 3-digit inline
	int xb = int(pow(10, ceil(log10(profile.maxxl + 0.000001))));   // e.g. bb for max 2-digit crossline
	index = param.flag * ib * xb + il * xb + xl;                    // e.g, 1aaabb

};


// define function for init_loc
void Location::init_loc(ParamType param, MomentType locmoment, int il, int xl)
{

	// initialize location
	OriginType origin = param.coordinate.origin;
	SpacingType spacing = param.coordinate.spacing;
	Eigen::Vector3d row = { origin.x0 + il * spacing.dx, origin.y0 + xl * spacing.dy, origin.z0 };
	loc = {
		row,   // will be nominal [NOM]
		row,   // will be actual [ACT]
		row    // will be estimated [EST]
	};

	// get perturbation
	Perturbation perturbation;
	Eigen::Vector3d scatter = perturbation.get_perturb(locmoment, SPACE);

	// actual = summing location + perturbation
	loc[ACT] += scatter;

	// print
	if (PRINTLOCATION) {
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout.precision(3);
		std::cout << DEVICE[size_t(param.flag)-1] << " (" << il << ", " << xl << ") no " << index
			<< std::endl;
		std::cout << "nom.: " << std::setw(8) << loc[NOM][X] << ", " << std::setw(8) << loc[NOM][Y]
			<< ", " << std::setw(8) << loc[NOM][Z] << std::endl;
		std::cout << "act.: " << std::setw(8) << loc[ACT][X] << ", " << std::setw(8) << loc[ACT][Y]
			<< ", " << std::setw(8) << loc[ACT][Z] << std::endl;
		std::cout << std::endl;
	};

};


std::vector<Eigen::Vector3d> Location::get_loc()
{

	// return loc
	return loc;

};