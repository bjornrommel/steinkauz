//
// Generate a normal distribution.
//


// guard
#if !defined MY_PERTURBATION_H
#define MY_PERTURBATION_H


// include headers
#include <iostream>
#include <Dense>
#include "define.h"
#include "normal.h"


// declare a class Perturbation of normal distribution
class Perturbation {

public:
	Perturbation();                                         // construct
	Eigen::VectorXd get_perturbation3(MomentType moment);   // get 3d perturbation with mean, std
	Eigen::VectorXd get_perturbation(MomentType, int);      // get perturbation with mean, std

private:
	Eigen::VectorXd perturbation;   // perturbation vector

};


// guard
#endif