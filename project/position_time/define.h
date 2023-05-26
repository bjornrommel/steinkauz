//
// Define global constants and types.
//


// guard
#if !defined MY_DEFINE_H
#define MY_DEFINE_H


// include
#include <Dense>
#include <random>
#include <list>  
#include "config.h"


// define names for devices
const int NODE_FLAG{ 1 };
const int SOURCE_FLAG{ 2 };
const int PINGER_FLAG{ 3 };
const std::vector<std::string> DEVICE = { "node:", "source:", "pinger:" };


// define drift globals
const int DRIFT = 3;


// define location globals
const int STATE = 3;                               // number of states (as listed below)
const int NOM = 0;                                 // nominal
const int ACT = 1;                                 // actual
const int EST = 2;                                 // estimated
const std::list<int> STATES = { NOM, ACT, EST };


// define node / source / PINGER_ coordinate origin
typedef struct OriginStruct {
	double x0{ 0. };
	double y0{ 0. };
	double z0{ 0. };
} OriginType;
const OriginType NODE_ORIGIN = { NODE_X0, NODE_Y0, NODE_Z0 };
const OriginType SOURCE_ORIGIN = { SOURCE_X0, SOURCE_Y0, SOURCE_Z0 };
const OriginType PINGER_ORIGIN = { PINGER_X0, PINGER_Y0, PINGER_Z0 };


// define node / source / PINGER_ spacing
typedef struct SpacingStruct {
	double dx{ 0. };
	double dy{ 0. };
} SpacingType;
const SpacingType NODE_SPACING = { NODE_DX, NODE_DY };
const SpacingType SOURCE_SPACING = { SOURCE_DX, SOURCE_DY };
const SpacingType PINGER_SPACING = { PINGER_DX, PINGER_DY };


// define node / source / PINGER_ coordinates by combining origin and spacing
typedef struct CoordinateStruct {
	OriginType origin;
	SpacingType spacing;
} CoordinateType;
const CoordinateType NODE_COORDINATE = { NODE_ORIGIN, NODE_SPACING };
const CoordinateType SOURCE_COORDINATE = { SOURCE_ORIGIN, SOURCE_SPACING };
const CoordinateType PINGER_COORDINATE = { PINGER_ORIGIN, PINGER_SPACING };


// define node / source / PINGER_ layout
typedef struct ProfileStruct {
	int maxil{ 0 };   // max inline number
	int maxxl{ 0 };   // max crossline number
} ProfileType;
const ProfileType NODE_PROFILE = { NODE_MAX_INLINE, NODE_MAX_XLINE };
const ProfileType SOURCE_PROFILE = { SOURCE_MAX_INLINE, SOURCE_MAX_XLINE };
const ProfileType PINGER_PROFILE = { PINGER_MAX_INLINE, PINGER_MAX_XLINE };


// define all-encompassing parameter
typedef struct ParamStruct {
	int flag{ 0 };
	CoordinateType coordinate;
	ProfileType profile;
} ParameterType;
const ParameterType NODE_PARAMETER = { NODE_FLAG, NODE_COORDINATE, NODE_PROFILE };
const ParameterType SOURCE_PARAMETER = { SOURCE_FLAG, SOURCE_COORDINATE, SOURCE_PROFILE };
const ParameterType PINGER_PARAMETER = { PINGER_FLAG, PINGER_COORDINATE, PINGER_PROFILE };


// define location
// std::array [NOM / ACT / EST] of Eigen::Vector3d [X, Y, Z]
typedef std::array<Eigen::Vector3d, STATE> LocationType;   // state-many sets of coordinates per grid point
typedef std::array<Eigen::VectorXd, DRIFT> DriftType;      // drift-many sets of time drifts per grid point
typedef struct GridStruct {
	LocationType loc;                                      // location of layout (inline, crossline)
	DriftType drift;                                       // time drift of nodes
} GridType;


// define layout
typedef std::vector<std::vector<GridType>> LayoutType;   // 2-dimensional grid


// define node / source / pinger perturbation
typedef struct MomentStruct {
	Eigen::Vector3d mean;
	Eigen::Vector3d std;
} MomentType;
// define location scattering
const MomentType NODE_LOCATION_PARAMETER = {
	{NODE_MEANX, NODE_MEANY, NODE_MEANZ}, {NODE_STDX, NODE_STDY, NODE_STDZ}
};
const MomentType SOURCE_LOCATION_PARAMETER = {
	{SOURCE_MEANX, SOURCE_MEANY, SOURCE_MEANZ}, {SOURCE_STDX, SOURCE_STDY, SOURCE_STDZ}
};
const MomentType PINGER_LOCATION_MOMENT = {
	{PINGER_MEANX, PINGER_MEANY, PINGER_MEANZ}, {PINGER_STDX, PINGER_STDY, PINGER_STDZ}
};


// define node / source time drift
const MomentType NODE_TIME_MOMENT = {
	{0., 0., 0.}, {NODE_STD0, NODE_STD1, NODE_STD2}
};
const MomentType SOURCE_TIME_MOMENT = {
	{0., 0., 0.}, {SOURCE_STD0, SOURCE_STD1, SOURCE_STD2}
};
const MomentType PINGER_TIME_MOMENT = {
	{0., 0., 0.}, {0., 0., 0.}
};


// define default globals
const int NOINT = 0;               // default definition for int
const int NOFIGURE = 0;            // default definition for a figure number
const std::string NOOPTION = "";   // default definition for graphics option


// define coordinate globals
const int SPACE = 3;                      // spatial dimension
const int X = 0;                          // x coordinate
const int Y = 1;                          // y coordinate
const int Z = 2;                          // z coordinate
const std::list<int> CPT = { X, Y, Z };


// set default values for a normal distribution
const double MEAN = 0.0;
const double STD = 1.0;


// guard
#endif