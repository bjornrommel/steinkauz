//
// Set up a table of distance and traveltime derivatives.
//


// guard
#if !defined MY_TABLE_H
#define MY_TABLE_H


// include headers
#include <Dense>
#include "define.h"
#include "node.h"
#include "source.h"


// declare a class Table
class Table {

private:
	std::vector<Eigen::Vector2d> time;   // travel times

public:
	Table(Sources, Nodes, Nodes);                             // construct

	Eigen::VectorXd get_act_time(Sources, Nodes, int, int);   // get nominal time
	auto get_est_time_forward(Sources, Nodes, int, int);
	void init_table(Sources, Nodes, Nodes);                   // set up a forward operator

};


// guard
#endif
