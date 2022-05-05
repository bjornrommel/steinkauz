//
// Set up a grid of node, source or PINGER_.
// grid.loc contains the location of all devices within the given in- and crosslines.
//


// include headers
#include <iostream>
#include <iomanip>
#include "define.h"
#include "layout.h"
#include "location.h"
#include "drift.h"


// define constructor for Layout
Layout::Layout(ParameterType parameter, MomentType locmoment, MomentType driftmoment) :
	playout(init_layout(parameter, locmoment, driftmoment)) {
};


// define function for init_layout
std::shared_ptr<LayoutType>
	Layout::init_layout(
		ParameterType parameter, MomentType locmoment, MomentType driftmoment) {

	// initialize and assign memory
	ProfileType profile = parameter.profile;
	Location location(parameter, locmoment, 0, 0, false);   // location
	Drift drift(parameter, driftmoment, 0, 0, false);       // time drift
	std::shared_ptr<LayoutType> playout{
		std::make_shared <LayoutType>(
			LayoutType{
				static_cast<unsigned int> (profile.maxil),
				std::vector<GridType>(
					static_cast<unsigned int> (profile.maxxl), {
						location.get_location(),                    // get location
						drift.get_drift()                           // get time drift
					}
				)
			}
		)
	};


	// initialize grid with correct node location and clock drift STD's
	for (int il = 0; il < profile.maxil; il++) {                // inline loop
		for (int xl = 0; xl < profile.maxxl; xl++) {            // crossline loop
			Location location(parameter, locmoment, il, xl);    // node location
			(*playout)[il][xl].loc = location.get_location();   // to pointer to layout of grid
			Drift drift(parameter, driftmoment, il, xl);        // clock time
			(*playout)[il][xl].drift = drift.get_drift();       // to pointer of layout of grid
		};
	};
	// return
	return playout;

};