//
// Set up nodes.
// Parameters are copied into the variable param by the class Param.
// Node locations are computed in the class Layout and stored in the variable layout.
//


// include headers
#include "define.h"
#include "node.h"


// define constructor for Nodes
Nodes::Nodes(ParamType param, MomentType locmoment, MomentType timemoment) :
	Param(param),                          // node param
	Layout(param, locmoment, timemoment)   // node location and timemoment drift
{

};


// define function for set_coord
void Nodes::set_coord(int ni, int nx, int state, Eigen::Vector3d coord) {

	// assign loc to a point in layout
	

};