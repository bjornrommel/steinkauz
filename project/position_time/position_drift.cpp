//
//  Bayes-style inversion of traveltimes for the location and time drift of nodes.
//

// include headers
#include <iostream>
#include "config.h"
#include "define.h"
#include "normal.h"
#include "source.h"
#include "node.h"
#include "pinger.h"
#include "table.h"
#include "graphics.h"



int main() {

	// normal distribution
	Normal normal;

	// set up sources
	Sources sources(SOURCE_PARAMETER, SOURCE_LOCATION_PARAMETER, SOURCE_TIME_MOMENT, normal);

	// set up nodes
	Nodes nodes(NODE_PARAMETER, NODE_LOCATION_PARAMETER, NODE_TIME_MOMENT, normal);

	// set up pingers
	Pingers pingers(PINGER_PARAMETER, PINGER_LOCATION_MOMENT, PINGER_TIME_MOMENT, normal);

	// invert
	Table table(sources, nodes, pingers);

	// plot
	Graphics graphics(sources, nodes, pingers);

	// return
	return EXIT_SUCCESS;

};