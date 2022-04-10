//
// Set up a grid of node, source or pinger.
// grid.loc contains the location of all devices within the given in- and crosslines.
//


// include headers
#include<iostream>
#include "define.h"
#include "layout.h"
#include "location.h"
#include "drift.h"


// define constructor for Layout
Layout::Layout(ParamType param, MomentType locmoment, MomentType timemoment)
{

	// initialize grid
	layout = init_layout(param, locmoment, timemoment);   // outsource

};


// define function for init_layout
LayoutType Layout::init_layout(ParamType param, MomentType locmoment, MomentType timemoment)
{

	// initialize and assign memory
	Location loc(param, locmoment, 0, 0);
	Drift drift(timemoment);
	LayoutType
		layout(
			param.profile.maxil,
			std::vector<GridType>(param.profile.maxxl, { loc.get_loc(), drift.get_drift() }));

	// initialize grid with correct node location and timemoment STD's
	for (int il = 0; il < param.profile.maxil; il++) {       // inline loop
		for (int xl = 0; xl < param.profile.maxxl; xl++) {   // crossline loop
			Location loc(param, locmoment, il, xl);          // node location
			layout[il][xl].loc = loc.get_loc();                // assign to grid
			Drift drift(timemoment);                         // clock time
			layout[il][xl].drift = drift.get_drift();          // assign to grid
		};
	};

	// return
	return layout;
};


// define function for get_layout
LayoutType Layout::get_layout() {

	// return layout
	return layout;

};


// define function for put_layout
void Layout::set_layout(LayoutType layout1) {

	// overwrite layout
	layout = layout1;

};


// define function for get_loc
std::vector<Eigen::Vector3d> Layout::get_loc(int ni, int nx) {

	// return loc
	return layout[ni][nx].loc;

};


// define function for set_coord
void Layout::set_coord(int ni, int nx, int state, Eigen::Vector3d coord) {

	// assign loc to a point in layout
	layout[ni][nx].loc[state] = coord;

};
