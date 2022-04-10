//
// Set up nodes.
//


// guard
#if !defined MY_NODE_H
#define MY_NODE_H


// include headers
#include <vector>
#include "define.h"
#include "param.h"
#include "layout.h"


// declare class Nodes
class Nodes : public Param, public Layout
{

private:
	// param to be declared in the inherited class Param
	// layout to be declared in the inherited class Layout

public:
	Nodes(ParamType, MomentType, MomentType);   // construct
	void set_coord(int ni, int nx, int state, Eigen::Vector3d coord);

};


// guard
#endif