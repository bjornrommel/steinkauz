//
// Set up the graphics for source, node and pinger layout
// !!! Do not use debug mode in VisualStudio !!!
//


// include headers
#include <string>
#include <pybind11/embed.h>  // py::scoped_interpreter
#include <pybind11/stl.h>    // bindings from C++ STL containers to Python types
#include "define.h"
#include "source.h"
#include "node.h"
#include "pinger.h"
#include "graphics.h"


// default name of pybind11
namespace py = pybind11;
using namespace py::literals;


// define default constructor for nodes
Graphics::Graphics(Sources sources, Nodes nodes, Pingers pingers) {

	// open
	open();

	// plot pingers
	plot_layout(pingers.get_layout(), pingers.get_parameter().profile, "blue");

	// plot sources
	plot_layout(sources.get_layout(), sources.get_parameter().profile, "red");

	// plot nodes
	plot_layout(nodes.get_layout(), nodes.get_parameter().profile, "green");

	// show
	plot_show();

	// close
	close();

};


// open Python
void Graphics::open() {

	// open Python interpreter
	py::initialize_interpreter();

};


void Graphics::plot_layout(std::shared_ptr<LayoutType> layout, ProfileType profile, std::string color) {

	// initialize vector for matplotlib-suitable coordinates
	std::vector<double> x1(profile.maxil * profile.maxxl);
	std::vector<double> x2(profile.maxil * profile.maxxl);
	std::vector<double> y1(profile.maxil * profile.maxxl);
	std::vector<double> y2(profile.maxil * profile.maxxl);

	// define coordinates for the foot[NOM] and head[ACT] points
	// (matplotlib works with ordinary std::vectors, not Eigen::Vector)
	for (int iline = 0; iline < profile.maxil; iline++) {       // inline loop
		for (int xline = 0; xline < profile.maxxl; xline++) {   // crossline loop
			int index = iline * profile.maxxl + xline;          // ppoint index
			x1[index] = (*layout)[iline][xline].loc[NOM][X];    // plot point x
			y1[index] = (*layout)[iline][xline].loc[NOM][Y];    // plot point y
			x2[index] = (*layout)[iline][xline].loc[ACT][X];    // plot point x
			y2[index] = (*layout)[iline][xline].loc[ACT][Y];    // plot point y
		};
	};

	// define locals for matplotlib
	py::dict locals = py::dict{
		"x"_a = x1,
		"y"_a = y1,
		"color"_a = color,
		"figure"_a = this->figure,
	};

	// execute Python code using the variables saved in locals
	py::exec(
		R"(
			import matplotlib.pyplot as plt
			plt.figure(figure)
			plt.plot(x, y, 'o', markerfacecolor='none', markeredgecolor=color)
		)",
		py::globals(), locals
	);

	// define locals for matplotlib
	locals = py::dict{
		"x"_a = x2,
		"y"_a = y2,
		"color"_a = color,
		"figure"_a = this->figure,
	};

	// execute Python code using the variables saved in locals
	py::exec(
		R"(
			import matplotlib.pyplot as plt
			plt.figure(figure)
			plt.plot(x, y, 'o',  markerfacecolor=color, markeredgecolor=color)
		)",
		py::globals(), locals
	);

	// define differential coordinates for the arrows from foot to head points
	// (preparing arrows from x1, y1 with length x2-x1, y2-y1)
	for (int iline = 0; iline < profile.maxil; iline++) {       // inline loop
		for (int xline = 0; xline < profile.maxxl; xline++) {   // crossline loop
			int index = iline * profile.maxxl + xline;          // row index
			x2[index] -= x1[index];                             // plot length dx
			y2[index] -= y1[index];                             // plot length dy

			// define locals for matplotlib
			locals = py::dict{
				"x1"_a = x1[index],
				"y1"_a = y1[index],
				"x2"_a = x2[index],
				"y2"_a = y2[index],
				"color"_a = color,
				"figure"_a = this->figure,
			};

			// execute Python code using the variables saved in locals
			py::exec(
				R"(
					import matplotlib.pyplot as plt
					plt.figure(figure)
					plt.arrow(x1, y1, x2, y2, length_includes_head='true', head_width=1.5)
				)",
				py::globals(), locals
			);

		};
	};

};


// show graphics
void Graphics::plot_show() {

	// save the necessary local variables in a Python dict
	py::dict locals = py::dict{
	};

	// execute Python code using the variables saved in locals
	// (add an option to print)
	py::exec(
		R"(
			import matplotlib.pyplot as plt
			plt.show()
		)",
		py::globals(), locals
	);

};


// close down
void Graphics::close() {

	// close Python interpreter
	py::finalize_interpreter();

};