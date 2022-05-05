//
// Define global constants.
//


// guard
#if !defined MY_CONFIG_H
#define MY_CONFIG_H


// include
#include <vector>


// --- do change below --- do change below --- do change below ---


// define node globals
const int NODE_MAX_INLINE = 3;      // maximal number of inline lines
const int NODE_MAX_XLINE = 3;       // maximal number of crossline lines
const double NODE_X0 = 50.;         // inline origin
const double NODE_Y0 = 50.;         // crossline origin
const double NODE_Z0 = 1000.;       // depth origin
const double NODE_DX = 50.;         // inline spacing
const double NODE_DY = 50.;         // crossline spacing
const double NODE_MEANX = 0.;       // inline perturbation mean
const double NODE_MEANY = 0.;       // crossline perturbation mean
const double NODE_MEANZ = 0.;       // vertical perturbation mean
const double NODE_STDX = 10.;       // inline perturbation standard deviation
const double NODE_STDY = 10.;       // crossline perturbation standard deviation
const double NODE_STDZ = 5.;        // vertical perturbation standard deviation
const double NODE_STD0 = 0.001;     // time drift 0. order standard deviation
const double NODE_STD1 = 0.0001;    // time drift 1. order standard deviation
const double NODE_STD2 = 0.00001;   // time drift 2. order standard deviation


// define time globals
const double MAX_TIME = 1000;       // record time
const double TIME_SAMP_RATE = 4.;   // sampling rate


// define source globals
const int SOURCE_MAX_INLINE = 3;    // maximal number of inline lines
const int SOURCE_MAX_XLINE = 3;     // maximal number of crossline lines
const double SOURCE_X0 = 0.;        // inline origin
const double SOURCE_Y0 = 0.;        // crossline origin
const double SOURCE_Z0 = 0.;        // depth origin
const double SOURCE_DX = 100.;      // inline spacing
const double SOURCE_DY = 100.;      // crossline spacing
const double SOURCE_MEANX = 0.;     // inline perturbation
const double SOURCE_MEANY = 0.;     // crossline perturbation
const double SOURCE_MEANZ = 0.;     // vertical perturbation
const double SOURCE_STDX = 0.;      // inline perturbation
const double SOURCE_STDY = 0.;      // crossline perturbation
const double SOURCE_STDZ = 0.;      // vertical perturbation
const double SOURCE_DT = 20.;       // nominal shot time interval
const double SOURCE_STD0 = 0.001;   // source 0. order standard deviation (source time variation)
const double SOURCE_STD1 = 0.;      // source 1. order standard deviation
const double SOURCE_STD2 = 0.;      // source 2. order standard deviation 


// define globals
const int PINGER_MAX_INLINE = 3;   // maximal number of inline lines
const int PINGER_MAX_XLINE = 3;    // maximal number of crossline lines
const double PINGER_X0 = 0.;       // inline origin
const double PINGER_Y0 = 0.;       // crossline origin
const double PINGER_Z0 = 1000.;    // depth origin
const double PINGER_DX = 10.;      // inline spacing
const double PINGER_DY = 150.;     // crossline spacing
const double PINGER_MEANX = 0.;    // inline perturbation
const double PINGER_MEANY = 0.;    // crossline perturbation
const double PINGER_MEANZ = 0.;    // vertical perturbation
const double PINGER_STDX = 0.;     // inline perturbation
const double PINGER_STDY = 0.;     // crossline perturbation
const double PINGER_STDZ = 0.;     // vertical perturbation


// sound velocity
const double VEL = 1500;   // sound velocity


// printouts
const bool PRINT_ITERATION = true;   // print iteration results
const bool PRINT_LOCATION = true;    // print location of devices
const bool PRINT_DRIFT = true;       // print clock drift parameters pf devices


// inversion
const bool DRIFT_INVERSION = true;       // inversion of node time drift
const int EMERGENCY = 123;               // max number of iterations (emergency break)
const double RESIDUAL_TIME = 0.000001;   // max residual time


// guard
#endif