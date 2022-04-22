//
// Set up the graphics for source, node and pinger layout, before and after optimal positioning
//


// guard
#if !defined MY_GRAPHICS_H
#define MY_GRAPHICS_H


// include headers
#include <string>
#include "define.h"
#include "source.h"
#include "node.h"
#include "pinger.h"


// declare class Graphics
class Graphics {

private:
	int figure{ 0 };   // figure number

public:
	Graphics(Sources, Nodes, Pingers);                        // construct
	void open();                                              // open figure
	void plot_layout(std::shared_ptr<LayoutType>, ProfileType, std::string);   // plot graphics
	void plot_show();                                         // show figure
	void close();                                             // close figure
};


// guard
#endif