//
// Set up the graphics for source and node ProfileType.
//


// include headers
#include <string>
#include <pybind11/embed.h>  // py::scoped_interpreter
#include <pybind11/stl.h>    // bindings from C++ STL containers to Python types
#include "define.h"
#include "graphics.h"


// default name of pybind11
namespace py = pybind11;
using namespace py::literals;


// define default constructor for nodes
Graphics::Graphics(Nodes nodes, int figure, std::string option) :
	figure(figure), option(option) {                   // default define figure, option

	LayoutType nod_layout = nodes.get_layout();
	ProfileType nod_profile = nodes.get_param().profile;

	Graphics graphics(nod_layout, nod_profile, figure, option);

};


// define default constructor for layouts
Graphics::Graphics(LayoutType layout, ProfileType profile, int figure, std::string option) :
	figure(figure), option(option) {   // default define figure, option

	// open
	open();

	// plot layout
	plot_layout(layout, profile);

	// show
	plot_show();

	// close
	close();

};


// open
void Graphics::open() {

	// open Python interpreter
	py::initialize_interpreter();

};


void Graphics::plot_layout(LayoutType layout, ProfileType profile) {

	// initialize vector for matplotlib-suitable coordinates
	std::vector<double> x1(profile.maxil * profile.maxxl);
	std::vector<double> x2(profile.maxil * profile.maxxl);
	std::vector<double> y1(profile.maxil * profile.maxxl);
	std::vector<double> y2(profile.maxil * profile.maxxl);

	// define coordinates for use with matplotlib
	for (int iline = 0; iline < profile.maxil; iline++) {       // inline loop
		for (int xline = 0; xline < profile.maxxl; xline++) {   // crossline loop
			int index = iline * profile.maxxl + xline;          // ppoint index
			x1[index] = layout[iline][xline].loc[NOM][X];        // plot point x
			y1[index] = layout[iline][xline].loc[NOM][Y];        // plot point y
		};
	};

	// define locals for matplotlib
	py::dict locals = py::dict{
		"x"_a = x1,
		"y"_a = y1,
		"option"_a = option,
		"figure"_a = figure,
	};

	// execute Python code, using the variables saved in `locals`
	py::exec(
		R"(
			import matplotlib.pyplot as plt
			plt.figure(figure)
			scatter = plt.plot(x, y, 'o')
			plt.setp(scatter, marker='o', markerfacecolor='none', markeredgecolor='red')
		)",
		py::globals(), locals
	);

	// define coordinates for use with matplotlib
	for (int iline = 0; iline < profile.maxil; iline++) {       // inline loop
		for (int xline = 0; xline < profile.maxxl; xline++) {   // crossline loop
			int index = iline * profile.maxxl + xline;          // ppoint index
			x2[index] = layout[iline][xline].loc[ACT][X];        // plot point x
			y2[index] = layout[iline][xline].loc[ACT][Y];        // plot point y
		};
	};

	// define locals for matplotlib
	locals = py::dict{
		"x"_a = x2,
		"y"_a = y2,
		"option"_a = option,
		"figure"_a = figure,
	};

	// execute Python code, using the variables saved in `locals`
	py::exec(
		R"(
				import matplotlib.pyplot as plt
				plt.figure(figure)
				scatter = plt.plot(x, y, 'o')
				plt.setp(scatter, marker='o', markerfacecolor='red', markeredgecolor='red')
			)",
		py::globals(), locals
	);

	// define coordinates for use with matplotlib
	for (int iline = 0; iline < profile.maxil; iline++) {       // inline loop
		for (int xline = 0; xline < profile.maxxl; xline++) {   // crossline loop
			int index = iline * profile.maxxl + xline;          // ppoint index
			x2[index] -= x1[index];        // plot point x
			y2[index] -= y1[index];        // plot point y

			// define locals for matplotlib
			locals = py::dict{
				"x1"_a = x1[index],
				"y1"_a = y1[index],
				"x2"_a = x2[index],
				"y2"_a = y2[index],
				"option"_a = option,
				"figure"_a = figure,
			};

			// execute Python code, using the variables saved in `locals`
			py::exec(
				R"(
						import matplotlib.pyplot as plt
						plt.figure(figure)
						scatter = plt.arrow(x1, y1, x2, y2, length_includes_head='true', head_width=1.5)
						plt.setp(scatter)
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

	// execute Python code, using the variables saved in `locals`
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