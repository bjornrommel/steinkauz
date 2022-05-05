//
// Set up a table of distance and traveltime derivatives
// and invert for the actual position of nodes
//


// include headers
#include <iostream>
#include <iomanip>
#include <chrono>
#include <cmath>
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


InverseType* Table::get_act_time(Sources sources, Nodes nodes, int ni, int nx) {

	// get source, node and pinger profile
	ProfileType sou_profile = sources.get_parameter().profile;

	// define traveltime
	Eigen::VectorXd time = Eigen::VectorXd::Zero(sou_profile.maxil * sou_profile.maxxl);

	// loop over all sources calculating traveltimes
	auto lambda = [&time](Sources sources, int ni, int nx, Nodes nodes) {

		// define temp objecte
		ProfileType sou_profile = sources.get_parameter().profile;
		Eigen::Vector3d nodco{ (*nodes.get_layout())[ni][nx].loc[ACT] };     // node coordinate
		Eigen::VectorXd noddt{ (*nodes.get_layout())[ni][nx].drift[ACT] };   // node time drift

		// loop over all source points
		int row = 0;                                           // row counter
		for (int si = 0; si < sou_profile.maxil; si++) {       // inline loop
			for (int sx = 0; sx < sou_profile.maxxl; sx++) {   // crossline loop

				// calculate time
				time[row] =                                        // actual time
					(
						(*sources.get_layout())[si][sx].loc[ACT]   // ... differential vector
						-                                          // ... dito
						nodco                                      // ... dito
					).norm()                                       // ... now distance
					/                                              // ... divided by
					VEL;                                           // ... velocity
				if (DRIFT_INVERSION) {
					time[row] +=
						(noddt[2] * sources.get_shot()[si][sx] + noddt[1]) *
						sources.get_shot()[si][sx] + noddt[0];
				};

				row++;   // increment loop counter
			};
		};
	};

	// execute lambda
	// (lambda function faster than standard code)
	lambda(sources, ni, nx, nodes);

	// print
	if (PRINT_ITERATION) {
		Eigen::VectorXd nodco = (*nodes.get_layout())[ni][nx].loc[ACT];
		Eigen::VectorXd noddt = (*nodes.get_layout())[ni][nx].drift[ACT];
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout.precision(3);
		std::cout << "node location" << std::endl;
		std::cout
			<< "act.: "
			<< std::setw(8) << nodco[X] << ", "
			<< std::setw(8) << nodco[Y] << ", "
			<< std::setw(8) << nodco[Z] << std::endl;
		if (DRIFT_INVERSION) {
			std::cout.precision(9);
			std::cout << "drift parameter" << std::endl;
			std::cout
				<< "act.: "
				<< std::setw(12) << noddt[0] << ", "
				<< std::setw(12) << noddt[1] << ", "
				<< std::setw(12) << noddt[2] << std::endl;
		};
		std::cout << std::endl;
	};

	// return
	InverseType* parcel = new InverseType;
	*parcel = { time };
	return parcel;

};


// short cut the right side of forward
Eigen::MatrixXd Table::get_right_forward(Sources sources) {

	// get source, node and pinger profile
	ProfileType sou_profile = sources.get_parameter().profile;

	// define right side of forward
	Eigen::MatrixXd rforward(sou_profile.maxil * sou_profile.maxxl, DRIFT);

	// loop over all source points
	int row = 0;
	for (int si = 0; si < sou_profile.maxil; si++) {       // inline loop
		for (int sx = 0; sx < sou_profile.maxxl; sx++) {   // crossline loop

			// concatenate forward to the right right
			rforward.row(row) = -1. * Eigen::Vector3d{
				1,
				sources.get_shot()[si][sx],
				pow(sources.get_shot()[si][sx], 2),
			};

			// loop counter
			row++;
		};
	};

	// return
	return rforward;

};


InverseType* Table::get_est_time_forward(
	Sources sources, Nodes nodes, int ni, int nx, Eigen::MatrixXd rforward) {

	// get source, node and pinger profile
	ProfileType sou_profile = sources.get_parameter().profile;

	// define traveltime
	Eigen::VectorXd time(sou_profile.maxil * sou_profile.maxxl);

	// define forward operator
	int dim = SPACE;         // inversion for node location
	if (DRIFT_INVERSION) {   // extend if inversion for time drift
		dim += DRIFT;
	};
	Eigen::MatrixXd forward(sou_profile.maxil * sou_profile.maxxl, dim);

	/*
	// start time taking
	auto start = std::chrono::high_resolution_clock::now();
	*/

	// loop over all sources calculating estimated traveltimes and forward operator
	// (lambda saving CPU time!)
	auto lambda =
		[&forward, &time](
			Sources sources, Eigen::MatrixXd rforward, int ni, int nx, Nodes nodes) {

		// define temp object
		ProfileType sou_profile = sources.get_parameter().profile;
		Eigen::Vector3d nodco{ (*nodes.get_layout())[ni][nx].loc[EST] };     // node coordinate
		Eigen::VectorXd noddt{ (*nodes.get_layout())[ni][nx].drift[EST] };   // node time drift

		// loop over all source points
		int row = 0;
		for (int si = 0; si < sou_profile.maxil; si++) {       // inline loop
			for (int sx = 0; sx < sou_profile.maxxl; sx++) {   // crossline loop

				// calculate time and forward
				forward(row, Eigen::seq(0,2)) =                // differential location = ...
					(*sources.get_layout())[si][sx].loc[EST]   // forward operator times velocity
					-
					nodco;
				time[row] =
					forward(row, Eigen::seq(0, 2)).norm();     // actually distance
				forward.row(row) /= time[row];                 // diff. location / distance

				// loop counter
				row++;
			};
		};
		forward /= VEL;                                        // final forward operator
		time /= VEL;                                           // final estimated time

		// check for inversion of node time drift
		if (DRIFT_INVERSION) {

			// loop over all source points
			int row = 0;
			for (int si = 0; si < sou_profile.maxil; si++) {       // inline loop
				for (int sx = 0; sx < sou_profile.maxxl; sx++) {   // crossline loop

					// add to traveltime
					time[row] +=
						(noddt[2] * sources.get_shot()[si][sx] + noddt[1]) *
						sources.get_shot()[si][sx] + noddt[0];

					// loop counter
					row++;
				};
			};

			// overwrite right side of forward
			forward(Eigen::all, Eigen::seq(3, 5)) = rforward;

		};

	};

	// execute lambda
	lambda(sources, rforward, ni, nx, nodes);   // execute lambda

	/*
	// stop time taking
	auto end = std::chrono::high_resolution_clock::now();
	double duration =
		std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
	duration *= 1e-9;
	std::cout
		<< "Time used : "
		<< std::fixed << std::setprecision(9) << duration << " sec"
		<< std::endl;
	*/

	// print
	if (PRINT_ITERATION) {
		Eigen::VectorXd nodco = (*nodes.get_layout())[ni][nx].loc[EST];
		Eigen::VectorXd noddt = (*nodes.get_layout())[ni][nx].drift[EST];
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout << "node location" << std::endl;
		std::cout.precision(3);
		std::cout
			<< "est.: "
			<< std::setw(8) << nodco[X] << ", "
			<< std::setw(8) << nodco[Y] << ", "
			<< std::setw(8) << nodco[Z] << std::endl;
		if (DRIFT_INVERSION) {
			std::cout.precision(9);
			std::cout << "drift parameter" << std::endl;
			std::cout
				<< "est.: "
				<< std::setw(12) << noddt[0] << ", "
				<< std::setw(12) << noddt[1] << ", "
				<< std::setw(12) << noddt[2] << std::endl;
		};
		std::cout << std::endl;
	};

	// return
	InverseType* parcel = new InverseType;
	*parcel = { time, forward };
	return parcel;

};


void Table::init_table(Sources sources, Nodes nodes, Pingers pingers) {

	// define auxiliary variables
	double res = DBL_MAX;   // traveltime residual
	int emergency = 0;      // emergency break

	// get right-side forward (dependent on shot times only)
	Eigen::MatrixXd rforward = get_right_forward(sources);

	// get source, node and pinger profile
	ProfileType nod_profile = nodes.get_parameter().profile;

	// loop over all nodes
	for (int ni = 0; ni < nod_profile.maxil; ni++) {       // inline loop
		for (int nx = 0; nx < nod_profile.maxxl; nx++) {   // crossline loop

			// get the data = actual traveltimes one node at a time
			InverseType* act = get_act_time(sources, nodes, ni, nx);   // actual traveltime

			// initialize inversion loop
			res = DBL_MAX;   // largest residual set to infinity
			emergency = 0;   // emergency break zeroed

			// control inversion loop
			while (
				(res > RESIDUAL_TIME)        // largest residual > user-defined threshold
				&&
				(emergency < EMERGENCY)) {   // emergency counter < user-defined maximum

				/*
				// time checking
				auto start = std::chrono::high_resolution_clock::now();
				*/

				// get the currently estimated traveltime and forward
				InverseType* est =
					get_est_time_forward(sources, nodes, ni, nx, rforward);   // forward and estimated time

				/*
				// time checking
				auto end = std::chrono::high_resolution_clock::now();
				double duration =
					std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
				duration *= 1e-9;
				std::cout
					<< "Time used : "
					<< std::fixed << std::setprecision(9) << duration << " sec"
					<< std::endl;
				*/

				// Eigen::MatrixXd forward = test->forward;
				// current residual = (estimated - actual) traveltimes
				res = (est->time - act->time).cwiseAbs().maxCoeff();   // element-wise
				if (PRINT_ITERATION) {
					std::cout.setf(std::ios::fixed, std::ios::floatfield);
					std::cout.precision(9);
					std::cout << "residual: " << res << std::endl << std::endl;
				};

				// grand inversion
				Eigen::VectorXd nod_up =
					(est->forward.transpose() * est->forward).ldlt().solve(
						est->forward.transpose() * (est->time - act->time));

				// update node layout
				(*nodes.get_layout())[ni][nx].loc[EST] += nod_up(Eigen::seq(0, 2));
				if (DRIFT_INVERSION) {
					(*nodes.get_layout())[ni][nx].drift[EST] += nod_up(Eigen::seq(3, 5));

				};

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