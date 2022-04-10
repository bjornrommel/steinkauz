//
// Set up the graphics for node and source layout.
//


// guard
#if !defined MY_GRAPHICS_H
#define MY_GRAPHICS_H


// include headers
#include <string>
#include "define.h"
#include "node.h"


// declare class Graphics
class Graphics {

private:
	int figure;           // figure number
	std::string option;   // line option

public:
	Graphics(Nodes, int figure=NOFIGURE, std::string option=NOOPTION);   // construct
	Graphics(LayoutType, ProfileType, int, std::string);
	void open();
	void plot_layout(LayoutType, ProfileType);
	void plot_show();                                               // show figure
	void close();
};


// guard
#endif