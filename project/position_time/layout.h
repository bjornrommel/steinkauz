//
// Set up a layout of node, source or pinger.
//


// guard
#if !defined MY_LAYOUT_H
#define MY_LAYOUT_H


// include headers
#include <vector>
#include "define.h"


// declare class Layout
class Layout
{

private:
	LayoutType layout;   // declare layout

public:
	Layout(ParamType, MomentType, MomentType);                   // construct
	LayoutType init_layout(ParamType, MomentType, MomentType);   // set up the layout
	LayoutType get_layout();                                     // get the (entire) layout
	void set_layout(LayoutType);                                 // set the (entire) layout
	std::vector<Eigen::Vector3d> get_loc(int, int);              // get the location for one layout point
	void set_coord(int, int, int, Eigen::Vector3d);

};


// guard
#endif