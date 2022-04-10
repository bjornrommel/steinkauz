//
//  Bayes-style inversion of traveltimes for node location and node time drift.
//

// include headers
#include <iostream>
#include <pybind11/embed.h>  // py::scoped_interpreter
#include <pybind11/stl.h>    // bindings from C++ STL containers to Python types
#include "config.h"
#include "define.h"
#include "node.h"
#include "source.h"
#include "table.h"
#include "graphics.h"


int main() {

	// set up nodes
	Nodes nodes(NODEPARAM, NODELOCMOMENT, NODETIMEMOMENT);

	// set up sources
	Sources sources(SOURCEPARAM, SOURCELOCMOMENT, SOURCETIMEMOMENT);

	// set up pingers
	Nodes pingers(PINGERPARAM, PINGERLOCMOMENT, PINGERTIMEMOMENT);

	// invert
	Table table(sources, nodes, pingers);

	// plot
	Graphics graphics(nodes, NODEFIGURE, NODEOPTION);

	// return
	return EXIT_SUCCESS;

};