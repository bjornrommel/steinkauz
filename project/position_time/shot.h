// guard
#if !defined MY_SHOT_H
#define MY_SHOT_H


// include headers
#include <vector>
#include "define.h"


// declare class Shot
class Shot {

private:
	std::vector<std::vector<double>> shot;   // declare shot times
	void init_shot(ParameterType);           // create shot times

public:
	Shot(ParameterType);                           // construct
	std::vector<std::vector<double>> get_shot();   // return shot times

};

// guard
#endif