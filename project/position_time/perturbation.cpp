//
// Generate a normal distribution.
//


// include personal headers
#include <iostream>
#include "define.h"
#include "perturbation.h"
#include "normal.h"


// define constructor for Perturbation
Perturbation::Perturbation() {
};


// define function for Perturbation
Eigen::VectorXd Perturbation::get_perturbation(MomentType moment, int dim) {

	// generate perturbation of the same length as moment
	// (lambda "for loop" faster than standard one)
	// (vectorization doesn't improve further, though)
	Eigen::VectorXd perturbation(dim);                                  // define perturbation
	Normal normal;
	auto lambda = [moment, dim, &perturbation](Normal normal) {         // lambda
		for (int i = 0; i < dim; ++i) {                                 // loop dimension
			perturbation[i] =
				moment.mean[i] + moment.std[i] * normal.get_normal();   // modify mean, std
		};
	};
	lambda(normal);                                                     // call lambda

	// return
	return perturbation;

};


// define function for 3-dimensional Perturbation
Eigen::VectorXd Perturbation::get_perturbation3(MomentType moment) {

	// generate 3-dimensional perturbation
	Normal normal;
	Eigen::Vector3d scatter{ normal.get_normal(), normal.get_normal(), normal.get_normal() };
	Eigen::Vector3d perturbation{ moment.mean + (moment.std.array() * scatter.array()).matrix() };

	// return
	return perturbation;

};