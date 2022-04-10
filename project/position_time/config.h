//
// Define global constants.
//


// guard
#if !defined MY_CONFIG_H
#define MY_CONFIG_H


// include
#include <vector>
#include <string>


// --- do change below --- do change below --- do change below ---


// define node param globals
const int NODEFIGURE = 1;              // figure number
const std::string NODEOPTION = "ro";   // plot option
const int NODEMAXILINE = 2;            // maximal number of inline lines
const int NODEMAXXLINE = 2;            // maximal number of crossline lines
const double NODEX0 = 0.;              // inline origin
const double NODEY0 = 50.;             // crossline origin
const double NODEZ0 = 1000.;           // depth origin
const double NODEDX = 50.;             // inline spacing
const double NODEDY = 50.;             // crossline spacing
const double NODEMEANX = 0.;           // inline perturbation mean
const double NODEMEANY = 0.;           // crossline perturbation mean
const double NODEMEANZ = 0.;           // vertical perturbation mean
const double NODESTDX = 5.;            // inline perturbation standard deviation
const double NODESTDY = 5.;            // crossline perturbation standard deviation
const double NODESTDZ = 10.;           // vertical perturbation standard deviation
const double NODESTD0 = 5.;            // time drift 0. order standard deviation
const double NODESTD1 = 0.01;          // time drift 1. order standard deviation
const double NODESTD2 = 0.0005;        // time drift 2. order standard deviation


// define time globals
const double MAXTIME = 1000;        // record time
const double TIMESAMPRATE = 4.;     // sampling rate
const std::vector<double> TIMESTD   // standard deviation of coefficients
	= { 1., 0.000005, 0.000002 };


// define source param globals
const int SOURCEFIGURE = 1;              // figure number
const std::string SOURCEOPTION = "bo";   // plot option
const int SOURCEMAXILINE = 3;            // maximal number of inline lines
const int SOURCEMAXXLINE = 3;            // maximal number of crossline lines
const double SOURCEX0 = 10.;             // inline origin
const double SOURCEY0 = 5.;              // crossline origin
const double SOURCEZ0 = 3.;              // depth origin
const double SOURCEDX = 25.;             // inline spacing
const double SOURCEDY = 100.;            // crossline spacing
const double SOURCEMEANX = 0.;           // inline perturbation
const double SOURCEMEANY = 0.;           // crossline perturbation
const double SOURCEMEANZ = 0.;           // vertical perturbation
const double SOURCESTDX = 0.;            // inline perturbation
const double SOURCESTDY = 0.;            // crossline perturbation
const double SOURCESTDZ = 0.;            // vertical perturbation
const double SOURCEDT = 0.02;            // nominal shot time interval
const double SOURCESTD0 = 0.0001;        // source 0. order standard deviation (source time variation)
const double SOURCESTD1 = 0.;            // source 1. order mean (not typically applicable)
const double SOURCESTD2 = 0.;            // source 2. order standard deviation (not typically applicable)


// define param globals
const int PINGERFIGURE = 1;              // figure number
const std::string PINGEROPTION = "go";   // plot option
const int PINGERMAXILINE = 1;            // maximal number of inline lines
const int PINGERMAXXLINE = 1;            // maximal number of crossline lines
const double PINGERX0 = 0.;              // inline origin
const double PINGERY0 = 0.;              // crossline origin
const double PINGERZ0 = 1000.;           // depth origin
const double PINGERDX = 10.;             // inline spacing
const double PINGERDY = 150.;            // crossline spacing
const double PINGERMEANX = 0.;           // inline perturbation
const double PINGERMEANY = 0.;           // crossline perturbation
const double PINGERMEANZ = 0.;           // vertical perturbation
const double PINGERSTDX = 0.;            // inline perturbation
const double PINGERSTDY = 0.;            // crossline perturbation
const double PINGERSTDZ = 0.;            // vertical perturbation


// sound velocity
const double VEL = 1500;   // sound velocity


// define level of print
const bool PRINTFORWARD = false;        // print forward operator
const bool PRINTLOCATION = false;       // print location of devices
const std::vector<bool> PRINTTIME = {
	false,                              // print nominal time
	false,                              // print actual time
	false                               // print estimated time
};
const bool PRINTMEMBER = false;         // print layout
const bool PRINTSTATUS = false;         // print times

const bool PRINTUPDATE = true;          // progress in inversion
const bool PRINTITERATION = false;       // print iteration results


// inversion
const int EMERGENCY = 123;     // max number of iterations (emergency break)
const double RES = 0.000001;   // max residual time


// guard
#endif