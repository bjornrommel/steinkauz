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


// declare a class Table
class Table
{

private:
	std::vector<Eigen::Vector2d> time;   // travel times

public:
	Table(Sources, Nodes, Pingers);                           // construct
	Eigen::VectorXd get_act_time(Sources, Nodes, int, int);   // get nominal time
	auto get_est_time_forward(Sources, Nodes, int, int);
	void init_table(Sources, Nodes, Pingers);                 // set up a forward operator

};


// guard
#endif
