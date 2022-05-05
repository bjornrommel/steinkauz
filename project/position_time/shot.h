// guard
#if !defined MY_SHOT_H
#define MY_SHOT_H


// include headers
#include <vector>
#include "define.h"


// declare class Shot
class Shot {

private:
	std::vector<std::vector<double>> shot;                       // declare shot times
	std::vector<std::vector<double>> init_shot(ParameterType);   // create shot times

public:
	Shot(ParameterType);                                        // construct
	inline std::vector<std::vector<double>> const get_shot();   // return shot times

};


// get shot
inline std::vector<std::vector<double>> const Shot::get_shot() {

	// return
	return shot;

};


// guard
#endif