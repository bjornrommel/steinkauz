# -*- coding: utf-8 -*-
"""


                            MYSEGY

Provide functions to prepare figures for publication with the SEG.


                            adjust_size

Adjust a figures width and height until the width matches the requested width.
Use the final figure width when finally saving your figure.

adjust_size(fig=None, width=COLUMNWIDTH, ghostcmd=GHOSTCMD, postcmd=POSTCMD),
where
    fig: matplotlib.pyplot.figure(..)
        Matplotlib figure, see Matplotlib for accepted identifiers.
    width: float
        Requested width in inches.
        Default width: COLUMNWIDTH, width of 1 column in Geophysics.
        Alternative width: PAGEWIDTH, width of 2 columns = page in Geophysics.
        User-defined width: any.
    ghostcmd: char
        Ghostscript commands used to extract bounding box.
        Default: GHOSTCMD = "gswin64c -dBATCH -dNOPAUSE -q -sDEVICE=bbox ".
        Change the executable gswin64c to whatever ghostscript you have, but
        keep the other options!
    postcmd: dict
        Postscript commands used to save figure.
        Default: POSTCMD = {'pad_inches': 0, bbox_inches': 'tight',
        'facecolor': 'xkcd:mint green'}
        The no-padding and tight-box options remove any extra margin around the
        actual figure area, whereas the facecolor, whatever it is, only
        visualizes it.

Typical use case is
    from matplotlib import pyplot as plt     # import pyplot
    myfig = plt.figure()                     # init a figure
    width, height = adjust_size(fig=myfig)   # extract the nominal width
    myfig.fig.set_figwidth(width)            # set nominal figure width
    plt.tight_layout(pad=0.0)                # tighten bounding box, zero pad
    plt.savefig(                             # save figure
        <filename>, format='eps', 'pad_inches'=0, bbox_inches'='tight')
to obtain the nominal figure width and, then, create a tight figure of exactly
1-column width.


                            set_style

Set a Matplotlib figure to a specific style.

set_style(style=STYLESHEET)
where
    style: file
        A file containing a style sheet. See
        https://matplotlib.org/stable/users/explain/customizing.html

Typical use case is simply
    set_style()
to apply a style conforming to SEG's requirements.


                            set_font

Set fonts in a Matplotlib figure to specific values.

set_font()

Typical use case is simply
    set_font()
to set fonts conforming to SEG's requirements.


@author: Björn Rommel
@email: info@seisrock.com
@version: 2.0.0
@date: 11.9.2024
"""


# import modules
import tempfile as tf
import subprocess as sp
import sys
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt


# conversion postscript points to matplotlib inches
PT2IN = 1. / 72.

# conversion picas to inches
PC2IN = 20. / 72.

# max width residual
MAXERROR = 1.0e-3


# --- user-defined commands ---------------------------------------------------


# SEG figure widths in inch
# change as you see fit
COLUMNWIDTH = 20. * PC2IN   # column width 20pc
PAGEWIDTH = 42. * PC2IN     # two-column width incl. gap 42pc

# ghostscript command to extract bounding box
# correct the executable gswin64c, but keep the remaining options
GHOSTCMD = "gswin64c -dBATCH -dNOPAUSE -q -sDEVICE=bbox "

# additional postscript commands
# change the face color, but the other options are needed for a tight box
POSTCMD = {                           # as dict
    'pad_inches': 0,                  # no padding
    'bbox_inches': 'tight',           # tight layout
    'facecolor': 'xkcd:mint green'}   # background showing figure box

# matplotlib style sheet
# any style sheet will do
STYLESHEET = 'seg.mplstyle'

# additional information
PRINT = 2   # 0 show figure, 1 print final size, 2 print intermediate size


# --- set the figure style ----------------------------------------------------


def set_style(style=STYLESHEET):
    """
    Importing Matplotlib style for SEG publications.

    Returns
    -------
    None.

    """
    # import and use a style
    plt.style.use(style)


# -----------------------------------------------------------------------------


def set_size(fig=None, width=None, ghostcmd=None, postcmd=None):
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
    (new.wd, new.ht) : dict of floats
        figure width and height

    """
    # default
    if width is None:
        width = COLUMNWIDTH
    if ghostcmd is None:
        ghostcmd = GHOSTCMD
    if postcmd is None:
        postcmd = POSTCMD
    # matplotlib
    mpl.set_loglevel("error")   # suppress warning about transparency, etc
    # init parameter
    para = Para(width=width)
    # print
    if PRINT > 0:
        print(f"requested figure width:   {width:9.6f}")
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
        print(f"final figure size:        {new.wd:9.6f}, {new.ht:9.6f}")
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
            print(f"intermediate figure size: {self.wd:9.6f}, {self.ht:9.6f}")
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


def set_font():
    """
    Define the fonts used in all SEG-conforming plots.

    Returns
    -------
    None.

    """
    # set fonts https://stackoverflow.com/a/39566040
    plt.rc('text', usetex=True)              # Latex for versatility
    plt.rc('font', family='Helvetica')       # fontstyle
    plt.rc('ps', usedistiller='xpdf')        # avoiding bitmap
    plt.rc('font', size=8)                   # controls default text sizes
    plt.rc('axes', titlesize=8)              # fontsize of the axes title
    plt.rc('axes', labelsize=8)              # fontsize of x and y labels
    plt.rc('xtick', labelsize=8)             # fontsize of the tick labels
    plt.rc('ytick', labelsize=8)             # fontsize of the tick labels
    plt.rc('legend', fontsize=8)             # legend fontsize
    plt.rc('figure', titlesize=8)            # fontsize of the figure title
    plt.rc('figure', figsize=(20./6., 5.))   # figure size for 1 column SEG


# --- set up a test case ------------------------------------------------------


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
        set_size(
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
    # set style
    set_font()
    # show figure
    fig.tight_layout()
    plt.draw()
    # return
    return fig


if __name__ == '__main__':
    main()
