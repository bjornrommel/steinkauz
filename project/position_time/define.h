//
// Define global constants and types.
//


// guard
#if !defined MY_DEFINE_H
#define MY_DEFINE_H


// include
#include <Dense>
#include "config.h"


// define names for devices
const int NODEFLAG = 1;
const int SOURCEFLAG = 2;
const int PINGERFLAG = 3;
const std::vector<std::string> DEVICE = { "node:", "source:", "pinger:" };


// define node / source / pinger coordinate origin
typedef struct {
	double x0;
	double y0;
	double z0;
} OriginType;
const OriginType NODEORIGIN = { NODEX0, NODEY0, NODEZ0 };
const OriginType SOURCEORIGIN = { SOURCEX0, SOURCEY0, SOURCEZ0 };
const OriginType PINGERORIGIN = { PINGERX0, PINGERY0, PINGERZ0 };


// define node / source / pinger spacing
typedef struct {
	double dx;
	double dy;
} SpacingType;
const SpacingType NODESPACING = { NODEDX, NODEDY };
const SpacingType SOURCESPACING = { SOURCEDX, SOURCEDY };
const SpacingType PINGERSPACING = { PINGERDX, PINGERDY };


// define node / source / pinger coordinates by combining origin and spacing
typedef struct {
	OriginType origin;
	SpacingType spacing;
} CoordinateType;
const CoordinateType NODECOORDINATE = { NODEORIGIN, NODESPACING };
const CoordinateType SOURCECOORDINATE = { SOURCEORIGIN, SOURCESPACING };
const CoordinateType PINGERCOORDINATE = { PINGERORIGIN, PINGERSPACING };


// define node / source / pinger layout
typedef struct {
	int maxil;   // max inline number
	int maxxl;   // max crossline number
} ProfileType;
const ProfileType NODEPROFILE = { NODEMAXILINE, NODEMAXXLINE };
const ProfileType SOURCEPROFILE = { SOURCEMAXILINE, SOURCEMAXXLINE };
const ProfileType PINGERPROFILE = { PINGERMAXILINE, PINGERMAXXLINE };


// define all-encompassing parameter
typedef struct {
	int flag;
	CoordinateType coordinate;
	ProfileType profile;
} ParamType;
const ParamType NODEPARAM = { NODEFLAG, NODECOORDINATE, NODEPROFILE };
const ParamType SOURCEPARAM = { SOURCEFLAG, SOURCECOORDINATE, SOURCEPROFILE };
const ParamType PINGERPARAM = { PINGERFLAG, PINGERCOORDINATE, PINGERPROFILE };


// define location
// std::vector [NOM / ACT / EST] of Eigen::Vector3d [X, Y, Z]
typedef std::vector<Eigen::Vector3d> LocationType;
typedef std::vector<std::vector<double>> DriftType;
typedef struct {
	LocationType loc;   // location of layout (inline, crossline)
	DriftType drift;    // standard deviations of that layout's timemoment
} GridType;
typedef std::vector<std::vector<GridType>> LayoutType;


// define node / source / pinger perturbation
typedef struct {
	Eigen::Vector3d mean;
	Eigen::Vector3d std;
} MomentType;
// define location scattering
const MomentType NODELOCMOMENT = {
	{NODEMEANX, NODEMEANY, NODEMEANZ}, {NODESTDX, NODESTDY, NODESTDZ}
};
const MomentType SOURCELOCMOMENT = {
	{SOURCEMEANX, SOURCEMEANY, SOURCEMEANZ}, {SOURCESTDX, SOURCESTDY, SOURCESTDZ}
};
const MomentType PINGERLOCMOMENT = {
	{PINGERMEANX, PINGERMEANY, PINGERMEANZ}, {PINGERSTDX, PINGERSTDY, PINGERSTDZ}
};
// define node / source time drift
const MomentType NODETIMEMOMENT = {
	{0., 0., 0.}, {NODESTD0, NODESTD1, NODESTD2}   // not strictly a true vector, but works
};
const MomentType SOURCETIMEMOMENT = {
	{0., 0., 0.}, {SOURCESTD0, SOURCESTD1, SOURCESTD2}   // not strictly a true vector, but works
};
const MomentType PINGERTIMEMOMENT = {
	{0., 0., 0.}, {0., 0., 0.}   // not strictly a true vector, but works
};


// define default globals
const int NOINT = 0;               // default definition for int
const int NOFIGURE = 0;            // default definition for a figure number
const std::string NOOPTION = "";   // default definition for graphics option


// define coordinate globals
const int SPACE = 3;   // spatial dimension
const int X = 0;       // x coordinate
const int Y = 1;       // y coordinate
const int Z = 2;       // z coordinate
const std::list<int> CPT = { X, Y, Z };


// define location globals
const int STATE = 3;   // number of states (as listed below)
const int NOM = 0;
const int ACT = 1;
const int EST = 2;
const int DEL = 3;
const std::list<int> STATES = { NOM, ACT, EST };


// set default values for a normal distribution
const double MEAN = 0.0;
const double STD = 1.0;


// guard
#endif