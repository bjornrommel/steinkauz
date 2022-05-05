//
// Set up a table of distance and traveltime derivatives
// and invert for the actual position of nodes
//


// guard
#if !defined MY_TABLE_H
#define MY_TABLE_H


// include headers
#include <Dense>
#include "define.h"


// typedef returned from computing traveltime and forward
typedef struct {
	Eigen::VectorXd time;
	Eigen::MatrixXd forward;
} InverseType;


// declare a class Table
class Table
{

private:
	std::vector<Eigen::Vector2d> time;   // travel times

public:
	Table(Sources, Nodes, Pingers);                        // construct
	Eigen::MatrixXd get_right_forward(Sources);            // get right-side forward
	InverseType* get_act_time(Sources, Nodes, int, int);   // get nominal traveltime
	InverseType* get_est_time_forward(
		Sources, Nodes, int, int, Eigen::MatrixXd);        // get traveltime and forward
	void init_table(Sources, Nodes, Pingers);              // set up forward

};


// guard
#endif
