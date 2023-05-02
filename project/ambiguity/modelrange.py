# -*- coding: utf-8 -*-
"""
Preparing a picture showing a range of elasticity models.
See publication: modelrange.eps

Date: 1.5.2023

@author: Björn Rommel (rommel@seisrock.com)
"""


import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from IPython import get_ipython


# pylint:disable=invalid-name                 # r2, r4 and g see paper
# pylint:disable=too-few-public-methods       # yeah, over the top here for now


# user-defined parameters # user-defined parameters # user-defined parameters #
VEL = 1000             # original reference velocity
R2 = 0.2               # original anisotropy coefficient r2
R4 = 0.2               # original anisotropy coefficient r4
GMIN = -0.1            # minimum stretch parameter
GMAX = +0.3            # maximum stretch parameter
GSTEP = 0.05           # stretch parameter increment
FILENAME = "modelrange.eps"   # filename
PUBLICWIN = True       # True / False on windonws / non-Windows platform
PUBLICWIDTH = 5.0754   # 0.7 x the width of an SEG article
PUBLICHEIGHT = 1234    # anything ridiculously large
FIGSIZE = (PUBLICWIN, PUBLICWIDTH)
DEBUG = True           # debugs failure in updating bounding box
MULT = 100             # ratio of plotted points versus marked points
# change for Dog Creek Shale
VEL = 1875
R2 = 0.2000000
R4 = 0.3120401

# Note, for some unknown reason matplotlib does not scale the graphics more or
# less proportional to the desired figure width. So, while trying to find the
# requested figure width that generates the actually desired figure width the
# iterative algorithm might simply bail out. Well, at least, we are somewhat
# close.


class Var():
    """
    Set the user-defined parameters from above.

    Can be extended to a non-symmetric phase velocity of arbitrarily many
    coefficients.

    """

    def __init__(self):
        """
        Initialize user-given input.

        Returns
        -------
        None.

        """
        self.vel = VEL   # reference velocity
        self.r2 = R2     # second anisotropy coefficient
        self.r4 = R4     # fourth anisotropy coefficient


class GGG():
    """
    Set all stretch-related parameters.

    """

    def __init__(self):
        """
        Initialize all stretch related parameters.

        """
        # get user-defined parameters
        self.min = GMIN     # minimum stretch parameter
        self.max = GMAX     # maximum stretch parameter
        self.step = GSTEP   # increment stretch parameter
        # correct step size to plot MULT-times more points
        self.step /= MULT   # calculated increment of stretch parameter
        # get number of points
        self.nos = int(np.round((self.max - self.min) / self.step)) + 1
        # adjust maximum stretch parameter
        self.max = self.min + (self.nos - 1) * self.step
        # get list of stretch parameters
        self.arr = \
            np.array([self.min + iii * self.step for iii in range(self.nos)])
        # compute list of stretch terms sqrt(1+g)
        self.term = np.sqrt(1 + self.arr)


class Data():
    """
    Compute all data needed for plotting.

    """

    def __init__(self, var=None, g=None):
        """
        Initialize computing all data needed for plotting.

        Parameters
        ----------
        var : Var
            user-defined parameters
        g : GGG
            stretch-related parameters

        Returns
        -------
        none

        """
        self.vel = var.vel * (1 + g.arr)       # stretched velocity
        self.r2 = (var.r2 - g.arr) / g.term    # stretched second aniso. para.
        self.r4 = var.r4 / (g.term * g.term)   # stretched fourth aniso. para.
        self.nos = g.nos                       # number


class Graph():
    """
    Prepare the graphics.

    """

    # pylint:disable=too-many-instance-attributes   # yeah, I know, non-elegant

    def __init__(self):
        """
        Initialize the graphics variables.

        Returns
        -------
        none

        """
        self.fig = None      # figure identifier
        self.axes = None     # subfigure identifier
        self.minvel = None   # minimum velocity
        self.maxvel = None   # maximum velocity
        self.minr2 = None    # minimum second anisotropy parameter
        self.maxr2 = None    # maximum second anisotropy parameter
        self.minr4 = None    # minimum fourth anisotropy parameter
        self.maxr4 = None    # maximum fourth anisotropy parameter

    def init(self):
        """
        Set up the graphics figure.

        Returns
        -------
        self : Graphi
            fig : plt.figure
                figure identifier
            axes : plt.figure.add_subplot
                subfigure identifier

        """
        # create a separate graphics window
        get_ipython().run_line_magic('matplotlib', 'qt')
        # set up figure
        self.fig = plt.figure(figsize=FIGSIZE, constrained_layout=True)
        # set up subfigure
        self.axes = self.fig.add_subplot(projection='3d')
        # return
        return self

    def limits(self, data=None):
        """
        Compute axis limits.

        Note, the floats in this function are used to generate multiples of the
        desired step size.

        Parameters
        ----------
        data : Data
            all data needed for plotting

        Returns
        -------
        self : Graph
            minr2, maxr2, minr4, maxr4, minvel, maxvel
                minimum / maximum second and fourth anisotropy coefficient and
                velocity

        """
        # calculate
        self.minr2 = np.floor(np.amin(data.r2) * 10.) / 10.
        self.maxr2 = np.ceil(np.amax(data.r2) * 10.) / 10.
        self.minr4 = np.floor(np.amin(data.r4) * 10.) / 10.
        self.maxr4 = np.ceil(np.amax(data.r4) * 10.) / 10.
        self.minvel = np.floor(np.amin(data.vel) / 100.) * 100.
        self.maxvel = np.ceil(np.amax(data.vel) / 100.) * 100.
        # return
        return self

    def plot(self, data=None):
        """
        Plot the curve and scatter points.

        Parameters
        ----------
        data : Data
            all data needed for plotting

        Returns
        -------
        self : Graph
            unmodified

        """
        # plot the continuous line
        self.axes.plot(data.r4, data.r2, data.vel, label='model curve')
        # plot the marker points along the continuous line
        self.axes.scatter3D(
            data.r4[0::MULT], data.r2[0::MULT], data.vel[0::MULT], alpha=1)
        # plot the projections
        self.axes.scatter(
            data.r4[0::MULT], data.r2[0::MULT], zdir='z', zs=self.minvel,
            alpha=1, label='points in (r2, r4)')
        self.axes.scatter(
            data.r4[0::MULT], data.vel[0::MULT], zdir='y', zs=self.maxr2,
            alpha=1, label='points in (v, r4)')
        self.axes.scatter(
            data.r2[0::MULT], data.vel[0::MULT], zdir='-x', zs=self.minr4,
            alpha=1, label='points in (v, r2)')
        # return
        return self

    def view(self, data=None, g=None):
        """
        Set up the graphics window axes.

        Parameters
        ----------
        data : Data
            all data needed for plotting
        g : GGG
            all stretch-related parameters

        Returns
        -------
        self : Graph
            unmodified

        """

        def _imax(in1, in2, fac):
            """
            Calculate the number of desired ticks along the axes.

            Parameters
            ----------
            in1 : float
                minimum value
            in2 : float
                maximum value
            fac : float
                desired step size between ticks

            Returns
            -------
            imax : int
                max number of indices

            """
            # compute the number of indices
            in1 = int(np.round(in1 / fac))
            in2 = int(np.round(in2 / fac))
            imax = in2 - in1 + 1
            # return
            return imax

        # define the viewpoint in 3D
        self.axes.view_init(elev=20., azim=-35, roll=0)
        # make legend
        # ### self.axes.legend()
        # set axes limits
        self.axes.set_zlim(self.minvel, self.maxvel)
        self.axes.set_ylim(self.minr2, self.maxr2)
        self.axes.set_xlim(self.minr4, self.maxr4)
        # set ticks
        imax = _imax(self.minvel, self.maxvel, 100)
        self.axes.set_zticks([self.minvel + iii * 100 for iii in range(imax)])
        imax = _imax(self.minr2, self.maxr2, 0.1)
        self.axes.set_yticks([self.minr2 + iii * 0.1 for iii in range(imax)])
        imax = _imax(self.minr4, self.maxr4, 0.1)
        self.axes.set_xticks([self.minr4 + iii * 0.1 for iii in range(imax)])
        # set aspect ratio
        self.axes.set_box_aspect((0.333, 1., 0.8))
        for iii in range(0, data.nos, MULT):
            text = f'{g.arr[iii]:+5.2f}'
            self.axes.text(data.r4[iii], data.r2[iii], data.vel[iii], text)
        # set label
        self.axes.set_zlabel('v   ')
        self.axes.set_ylabel('r2')
        self.axes.set_xlabel('r4')
        # show
        plt.show()
        # return
        return self

    def save(self):
        """
        Save the figure in EPS format.

        Returns
        -------
        self : Graph
            unmodified

        """

        def _getsize():
            """
            Get the bounding box of an EPS file.

            Returns
            -------
            width : float
                width of bounding box
            height : float
                height of bounding box

            """
            # define ghostscript command to extract bounding box
            command = "gswin64c -dBATCH -dNOPAUSE -q -sDEVICE=bbox "
            command += FILENAME
            # run above ghostscript command and store in result
            result = subprocess.run(command, check=True, capture_output=True)
            # extract bounding box, discard high-resolution bounding box
            result = result.stderr.decode("utf-8")
            result = result.split("\n")
            if DEBUG:
                print(f"\nreplace bounding box in {FILENAME}")
                print(result[0])
            # extract width and height of image
            result = result[1].split()
            width = (float(result[3]) - float(result[1])) / 72
            height = (float(result[4]) - float(result[2])) / 72
            # return width and height
            return width, height

        def _publicwin(step=0.2, errmax=1.e-3):
            """
            Adjust figure width to match required width of the bounding box.

            Parameters
            ----------
            step : float
                step size of input width; default arbitrary, but > 0
            errmax : float
                max error of figure width; default > 0, but small

            Returns
            -------
            none

            """
            # check switch
            # note, works only on Windows machine with ghostscript installed
            if PUBLICWIN:
                # initialize
                width = PUBLICWIDTH   # set above when initializing graphics
                # extract old width of figure; discard height
                oldwidth, _ = _getsize()
                # loop
                error = sys.float_info.max
                while np.abs(error) > errmax:
                    # try another input width
                    # note, input width not identical with output width!
                    width += step
                    self.fig.set_figwidth(width)
                    plt.savefig(
                        FILENAME, format='eps', bbox_inches='tight',
                        pad_inches=0, transparent=True)
                    # extract new width of figure
                    newwidth, _ = _getsize()
                    if DEBUG:
                        text = f"\nrequested width: {width}in = {width * 72}pt"
                        text += "\ncurrent width:   "
                        text += f"{newwidth}in = {newwidth * 72}pt"
                        print(text)
                    # slope of output width over input width
                    slope = (newwidth - oldwidth) / np.abs(step)
                    # current error
                    # note, desired PUBLICWIDTH - current output width
                    error = PUBLICWIDTH - newwidth
                    # preserve old current output width
                    oldwidth = newwidth
                    # calculate next input width
                    with np.errstate(
                            invalid='raise', divide='raise', over='raise'):
                        try:
                            step = error / slope
                        except RuntimeWarning as runtime:
                            print("\n" + runtime)
                            sys.exit()
                        except FloatingPointError as floating:
                            text = f"current width: {newwidth}in"
                            print("\n" + str(text))
                            print("no further update of bounding box!!!")
                            print("\n" + str(floating))
                            sys.exit()
                # final output
                # ### self.fig.set_figwidth(width)
                # ### plt.savefig(
                # ###    FILENAME, format='eps', bbox_inches='tight',
                # ###    pad_inches=0, transparent=True)

        # save EPS format
        plt.savefig(
            FILENAME, format='eps', bbox_inches='tight', pad_inches=0)
        _publicwin()
        # return
        return self


def main():
    """
    Run and control the program modelrange.

    Returns
    -------
    data : Data
        data computed from user input
    graph : Graph
        all graphics

    """
    var = Var()                   # get user-defined parameters
    g = GGG()                     # set stretch-related parameters
    data = Data(var=var, g=g)     # compute all internally used data from input
    graph = \
        Graph(). \
        init(). \
        limits(data=data). \
        plot(data=data). \
        view(data=data, g=g). \
        save()                    # prepare the graphics
    # return
    return data, graph


if __name__ == "__main__":
    main()
