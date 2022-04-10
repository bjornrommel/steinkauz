//
// Create shot times
//


// include headers
#include "define.h"
#include "shot.h"


Shot::Shot(ParamType param)
{
	init_shot(param);

};


// define function set_time
void Shot::init_shot(ParamType param) {

	// extract layout
	ProfileType profile = param.profile;

	// initialize and assign memory
	std::vector<std::vector<double>> shot(profile.maxil, std::vector<double>(profile.maxxl));

	for (int si = 0; si < profile.maxil; si++) {
		for (int sx = 0; sx < profile.maxxl; sx++) {
			shot[si][sx] = (si + sx * profile.maxil) * SOURCEDT;   // shot time interval hard-wired here 
		};
	};

};


std::vector<std::vector<double>> Shot::get_shot() {

	// return
	return shot;

};