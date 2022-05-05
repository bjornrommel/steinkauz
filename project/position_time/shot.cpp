//
// Create shot times
//


// include headers
#include<iostream>
#include "define.h"
#include "shot.h"


Shot::Shot(ParameterType parameter) :
	shot(init_shot(parameter)) {   // outsource initialization
};

// define function set_time
std::vector<std::vector<double>> Shot::init_shot(ParameterType parameter) {

	// extract layout
	ProfileType profile = parameter.profile;

	// assign memory
	std::vector<std::vector<double>> shot(profile.maxil, std::vector<double>(profile.maxxl));

	// initialize shot times
	for (int si = 0; si < profile.maxil; si++) {
		for (int sx = 0; sx < profile.maxxl; sx++) {
			shot[si][sx] = (sx + si * profile.maxxl) * SOURCE_DT;   // shot time interval
		};
	};

	// return
	return shot;

};