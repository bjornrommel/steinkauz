//
// Set up a layout of node, source or PINGER_.
//


// guard
#if !defined MY_LAYOUT_H
#define MY_LAYOUT_H


// include headers
#include <iostream>
#include <vector>
#include "define.h"
#include "normal.h"


// declare class Layout
class Layout {

private:
	std::shared_ptr<LayoutType> playout;   // pointer to layout

public:
	Layout(ParameterType, MomentType, MomentType, Normal);            // construct
	std::shared_ptr<LayoutType>
		init_layout(ParameterType, MomentType, MomentType, Normal);   // set up the layout
	inline std::shared_ptr<LayoutType> get_layout() const;            // get the (entire) layout
	inline std::shared_ptr<LayoutType>
		set_layout(std::shared_ptr<LayoutType> playout);              // get the (entire) layout

};


// define function for get_layout
inline std::shared_ptr<LayoutType> Layout::get_layout() const {

	// return layout
	return playout;

};


// define function for get_layout
inline std::shared_ptr<LayoutType> Layout::set_layout(std::shared_ptr<LayoutType> playout1) {

	// return layout
	playout = playout1;

};


// guard
#endif