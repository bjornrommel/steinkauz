# -*- coding: utf-8 -*-
"""
Subject:
correct_figure_size.py

Summary
Adjust a figures width and height until the width matches the requested width.

Provided function:
adjust_size(fig=None, width=None, ghostcmd=None, postcmd=None)
where
fig: matplotlib.pyplot.figure(..)
    a Matplotlib figure, see Matplotlib for accepted identifiers
width: float
    requested width in inches
    default width: COLUMNWIDTH: width of 1 column in Geophysics
    alternative width: PAGEWIDTH: width of 2 columns = page in Geophysics
    user-defined width: any
ghostcmd: char
    ghostscript commands used to extract bounding box
    default: "gswin64c -dBATCH -dNOPAUSE -q -sDEVICE=bbox "
postcmd: dict
    postscript commands used to save figure
    default: POSTCMD = {
        'pad_inches': 0, bbox_inches': 'tight', 'facecolor': 'xkcd:mint green'}

@author: Björn Rommel
@email: info@seisrock.com
@version: 1.1.0
@date: 10.9.2024
"""


# import modules
import tempfile as tf
import subprocess as sp
import sys
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt


# SEG figure widths in inch
PC2IN = 20. / 72.           # conversion pica to inch
COLUMNWIDTH = 20. * PC2IN   # column width 20pc
PAGEWIDTH = 42. * PC2IN     # two-column width incl. gap 42pc

# conversion postscript points to matplotlib inches
PT2IN = 1. / 72.

# max width residual
MAXERROR = 1.0e-3   # in inch


# --- user-defined commands ---------------------------------------------------


# ghostscript command to extract bounding box
GHOSTCMD = "gswin64c -dBATCH -dNOPAUSE -q -sDEVICE=bbox "

# additional postscript commands
POSTCMD = {                           # as dict
    'pad_inches': 0,                  # no padding
    'bbox_inches': 'tight',           # tight layout
    'facecolor': 'xkcd:mint green'}   # background showing figure box

# additional information
PRINT = 2   # 0 show figure, 1 print final size, 2 print intermediate size


# -----------------------------------------------------------------------------


# pylint:disable=invalid-name


# matplotlib
mpl.set_loglevel("error")   # suppress warning about transparency, etc


def adjust_size(
        fig=None, width=COLUMNWIDTH, ghostcmd=GHOSTCMD, postcmd=POSTCMD):
    """
    Modifying the figure size until it matches a requested width.

    Parameters
    ----------
    fig : pyplot figure
        figure identifier
    width : float
        requested width in inches
    ghostcmd : char
        ghostscript commands
    postcmd : dict
        postscript commands

    Returns
    -------
    new : Size
        figure width and height

    """
    # print
    if PRINT > 0:
        print(f"requested figure size:    {width}")
    # init parameter
    para = Para(width=width)
    # open a named temporary file
    with tf.NamedTemporaryFile(mode="w+") as fp:   # suffix=".eps" fails later
        # add postfix (for some reasons needed to save in 'eps' format)
        fp.name += ".eps"
        # check first figure size
        old = Size(fig=fig).check(
            fp=fp, para=para, ghostcmd=ghostcmd, postcmd=postcmd)
        while np.abs(para.err) > MAXERROR:   # loop until residual error small
            # check next figure size
            para.wd += para.sp
            new = Size(fig=fig).check(
                fp=fp, para=para, ghostcmd=ghostcmd, postcmd=postcmd)
            # check residual error
            para.error(width=width, new=new)
            if para.stop:
                break
            # update figure size
            para.update(old=old, new=new)
            # prepare next iteration
            old.advance(new=new)
    # print
    if PRINT > 0:
        print(f"final figure size:        {new.wd}, {new.ht}")
    # return
    return new.wd, new.ht


class Para():
    """
    Handle parameters controlling this module.

    """

    def __init__(self, width=COLUMNWIDTH):
        """
        Initialize parameters controlling the working of this module.

        Parameters
        ----------
        width : float
            requested width, with COLUMNWIDTH as default

        """
        self.wd = width / 2.            # init figure width
        self.sp = width                 # init stepsize
        self.err = sys.float_info.max   # init error (such as to enter loop)
        self.stop = False               # emergency stop division by zero

    def error(self, width=None, new=None):
        """
        Compute residual error between requested and current figure width.

        Parameters
        ----------
        width : float
            requested width
        new : Size
            current figure width and height

        Returns
        -------
        none

        """
        # define error
        self.err = width - new.wd

    def update(self, old=None, new=None):
        """
        Update the step size from current to next figure width.

        Parameters
        ----------
        old : Size
            previous figure width and height
        new : Size
            current figure width and height

        Returns
        -------
        None.

        """
        # check residual error
        if 1. / sys.float_info.max > np.abs(new.wd - old.wd):
            self.sp = None
            self.stop = True                                   # exit loop
        else:
            self.sp = self.err / (new.wd - old.wd) * self.sp   # update spacing
            self.stop = False


class Size():
    """
    Handle figure width and height.

    """

    def __init__(self, fig=None):
        self.fig = fig     # figure
        self.wd = np.nan   # width
        self.ht = np.nan   # height

    def _getsize(self, fp=None, ghostcmd=None):
        """
        Extract the actual size of a figure.

        Parameters
        ----------
        fp : File
            file pointer
        ghostcmd : char
            ghostscript command

        Returns
        -------
        self :
            actual width and height of the figure

        """
        # define ghostscript command to extract bounding box
        cmd = ghostcmd + fp.name
        # run above ghostscript command
        result = sp.run(cmd, check=True, capture_output=True)
        # extract bounding box and high-resolution bounding box
        result = result.stderr.decode("utf-8")
        result = result.split("\n")
        # extract high-resolution bounding box
        result = result[1]
        # extract width and height
        result = result.split()
        self.wd = (float(result[3]) - float(result[1])) * PT2IN
        self.ht = (float(result[4]) - float(result[2])) * PT2IN
        # print
        if PRINT > 1:
            print(f"intermediate figure size: {self.wd}, {self.ht}")
        # return
        return self

    def _savefigure(self, fp=None, para=None, postcmd=None):
        """
        Save matplotlib figure in eps format in a file.

        Parameters
        ----------
        fp : File
            file pointer
        para : Para
            parameter controlling this module
        postcmd : dict
            postscript command

        Returns
        -------
        self :

        """
        # set figure width
        self.fig.patch.set_facecolor('xkcd:mint green')   # just optical effect
        self.fig.set_figwidth(para.wd)                    # set new fig width
        plt.tight_layout(pad=0.0)                         # tight, zero pad
        # save figure at set width
        plt.savefig(fp.name, format='eps', **postcmd)
        # return
        return self

    def check(self, fp=None, para=None, ghostcmd=None, postcmd=None):
        """
        Save figure and check its width and height.

        Parameters
        ----------
        fp :
            file pointer
        para : Para
            parameter controlling this module
        ghostcmd : char
            ghostscript command
        postcmd : dict
            postscript command

        """
        # save figure
        self._savefigure(fp=fp, para=para, postcmd=postcmd)
        # extract width and height
        self._getsize(fp=fp, ghostcmd=ghostcmd)
        # return
        return self

    def advance(self, new=None):
        """
        Copy current figure width and height over the previous one.

        Parameters
        ----------
        new : Size
            current figure width and height

        Returns
        -------
        none

        """
        # copy old over new
        self.wd = new.wd
        self.ht = new.ht
        self.fig = new.fig


# -----------------------------------------------------------------------------


def main():
    """
    Test the module.

    Returns
    -------
    none

    """
    # pylint:disable=unused-variable
    # generate an example figure
    fig = figure()
    # use module
    wd, ht = (
        adjust_size(
            fig=fig, width=COLUMNWIDTH, ghostcmd=GHOSTCMD, postcmd=POSTCMD))


def figure():
    """
    Generate any example figure to test the routine.

    Copied from
    https://matplotlib.org/stable/gallery/lines_bars_and_markers/errorbar_limits_simple.html#sphx-glr-gallery-lines-bars-and-markers-errorbar-limits-simple-py

    Returns
    -------
    fig : pyplot.figure
        an example figure

    """
    # define figure
    fig = plt.figure()
    # define variables
    x = np.arange(10)
    y = 2.5 * np.sin(x / 20 * np.pi)
    yerr = np.linspace(0.05, 0.2, 10)
    # plot error bars
    plt.errorbar(x, y + 3, yerr=yerr, label='both limits (default)')
    plt.errorbar(x, y + 2, yerr=yerr, uplims=True, label='uplims=True')
    plt.errorbar(
        x, y + 1, yerr=yerr, uplims=True, lolims=True,
        label='uplims=True, lolims=True')
    upperlimits = [True, False] * 5
    lowerlimits = [False, True] * 5
    plt.errorbar(
        x, y, yerr=yerr, uplims=upperlimits, lolims=lowerlimits,
        label='subsets of uplims and lolims')
    # plot legend
    plt.legend(loc='lower right')
    # show figure
    fig.tight_layout()
    plt.draw()
    # return
    return fig


if __name__ == '__main__':
    main()
