//
// Set up a table of distance and traveltime derivatives
// and invert for the actual position of nodes
//


// include headers
#include <iostream>
#include <iomanip>
#include <Dense>
#include "define.h"
#include "source.h"
#include "node.h"
#include "pinger.h"
#include "table.h"


Table::Table(Sources sources, Nodes nodes, Pingers pingers) {

	// set up a grand table of available data
	init_table(sources, nodes, pingers);

};


Eigen::VectorXd Table::get_act_time(Sources sources, Nodes nodes, int ni, int nx) {

	// get source, node and pinger profile
	ProfileType sou_profile = sources.get_parameter().profile;

	// auxiliary variable
	int row = 0;
	double dist = 0.;

	Eigen::VectorXd sou_loc = Eigen::VectorXd::Zero(3);

	// define traveltime
	Eigen::VectorXd time = Eigen::VectorXd::Zero(sou_profile.maxil * sou_profile.maxxl);

	// current actual node location
	Eigen::VectorXd nod_loc = (*nodes.get_layout())[ni][nx].loc[ACT];

	// loop over all sources calculating traveltimes
	row = 0;
	for (int si = 0; si < sou_profile.maxil; si++) {        // inline loop
		for (int sx = 0; sx < sou_profile.maxxl; sx++) {    // crossline loop
			sou_loc =
				(*sources.get_layout())[si][sx].loc[ACT];   // extract actual source location
			dist =                                          // distance source->node
				pow(
					pow(sou_loc[X] - nod_loc[X], 2) +
					pow(sou_loc[Y] - nod_loc[Y], 2) +
					pow(sou_loc[Z] - nod_loc[Z], 2),
					0.5);
			time[row] = dist / VEL;                         // actual traveltime
			row++;                                          // increment source loop counter
		};
	};
	row--;                                                  // decrement source loop counter

	// print
	if (PRINT_ITERATION) {
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout.precision(3);
		std::cout << "node location" << std::endl;
		std::cout
			<< "act.: "
			<< std::setw(8) << nod_loc[X] << ", "
			<< std::setw(8) << nod_loc[Y] << ", "
			<< std::setw(8) << nod_loc[Z] << std::endl;
	};

	// return
	return time;

};


auto Table::get_est_time_forward(Sources sources, Nodes nodes, int ni, int nx) {

	// get source, node and pinger profile
	ProfileType sou_profile = sources.get_parameter().profile;

	// auxiliary variable
	int row = 0;
	double dist = 0.;

	// define actual source location
	Eigen::VectorXd sou_loc = Eigen::VectorXd::Zero(SPACE);

	// define traveltime
	Eigen::VectorXd time = Eigen::VectorXd::Zero(sou_profile.maxil * sou_profile.maxxl);

	// define forward operator
	Eigen::MatrixXd forward(sou_profile.maxil * sou_profile.maxxl, SPACE);

	// current estimated node location
	Eigen::VectorXd nod_loc = (*nodes.get_layout())[ni][nx].loc[EST];

	// loop over all sources calculating estimated traveltimes and forward operator
	for (int si = 0; si < sou_profile.maxil; si++) {              // inline loop
		for (int sx = 0; sx < sou_profile.maxxl; sx++) {          // crossline loop
			sou_loc = (*sources.get_layout())[si][sx].loc[EST];   // extract estimated source location
			dist =                                                // distance
				pow(
					pow(sou_loc[X] - nod_loc[X], 2) +
					pow(sou_loc[Y] - nod_loc[Y], 2) +
					pow(sou_loc[Z] - nod_loc[Z], 2),
					0.5);
			forward.row(row) = Eigen::Vector3d(                   // forward operator
				sou_loc[X] - nod_loc[X],
				sou_loc[Y] - nod_loc[Y],
				sou_loc[Z] - nod_loc[Z]
			);
			forward.row(row) /= (dist * VEL);
			time[row] = dist / VEL;                               // estimated traveltime
			row++;
		};
	};
	row--;

	// print
	if (PRINT_ITERATION) {
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout.precision(3);
		std::cout
			<< "est.: "
			<< std::setw(8) << nod_loc[X] << ", "
			<< std::setw(8) << nod_loc[Y] << ", "
			<< std::setw(8) << nod_loc[Z] << std::endl;
	};

	// return
	struct est_time_forward {      // return structure
		Eigen::VectorXd time;
		Eigen::MatrixXd forward;
	};
	return est_time_forward{ time, forward };

};


void Table::init_table(Sources sources, Nodes nodes, Pingers pingers) {

	// define auxiliary variables
	double res = DBL_MAX;   // traveltime residual
	int emergency = 0;      // emergency break

	// get source, node and pinger profile
	ProfileType sou_profile = sources.get_parameter().profile;
	ProfileType nod_profile = nodes.get_parameter().profile;
	ProfileType pin_profile = pingers.get_parameter().profile;

	// define various lengths
	int sou_rows = sou_profile.maxil * sou_profile.maxxl;   // number of sources
	int nod_rows = nod_profile.maxil * nod_profile.maxxl;   // number of nodes

	// define traveltime
	Eigen::VectorXd empty = Eigen::VectorXd::Zero(sou_rows);   // combining all sources, one node
	std::vector<Eigen::VectorXd> time(STATE_DIM, empty);       // zero for each time state

	// loop over all nodes
	for (int ni = 0; ni < nod_profile.maxil; ni++) {       // inline loop
		for (int nx = 0; nx < nod_profile.maxxl; nx++) {   // crossline loop

			// get the data = actual traveltimes one node at a time
			time[ACT] = get_act_time(sources, nodes, ni, nx);   // actual traveltime

			// initialize inversion loop
			res = DBL_MAX;   // largest residual set to infinity
			emergency = 0;   // emergency break zeroed

			// control inversion loop
			while (
				(res > RESIDUAL_TIME)        // largest residual > user-defined threshold
				&&
				(emergency < EMERGENCY)) {   // emergency counter < user-defined maximum

				// get the currently estimated traveltime and forward
				auto [time1, forward] =                              // compute and
					get_est_time_forward(sources, nodes, ni, nx);    // return to structure
				time[EST] = time1;                                   // re-assign properly

				// current residual = (estimated - actual) traveltimes
				res = (time[EST] - time[ACT]).cwiseAbs().maxCoeff();   // element-wise

				// grand inversion
				Eigen::VectorXd nod_up =
					(forward.transpose() * forward).ldlt().solve(forward.transpose() *
						(time[EST] - time[ACT]));

				// update node layout
				(*nodes.get_layout())[ni][nx].loc[EST] += nod_up;

				// emergency counter
				emergency++;

			};

		};

	};

	// message
	if (PRINT_ITERATION) {
		std::cout << "iteration completed!" << std::endl;
	};

};