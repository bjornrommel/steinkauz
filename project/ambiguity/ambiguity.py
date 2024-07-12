# -*- coding: utf-8 -*-
"""

Simulating wave propagation through a stack of inclined layers before and after
a stretch

Date: 1.5.2023 1.0.0
Date: 8.6.2024 1.0.1 correcting printout of bounding box
Date: 9.7.2024 1.0.2 suppressing warnings when calling plt.figure and .savefig
Date: 11.7.2024 1.1.0 updating the initialization of a canvas

@author: Björn Rommel (rommel@seisrock.com)
"""


# for ease of submission
# pylint: disable=too-many-lines


# libraries to be imported
import sys
import platform as pf
import subprocess
import warnings
from copy import deepcopy as cp
import itertools
import bdb
import numpy as np
import matplotlib.pyplot as plt
# ### import matplotlib as mpl    # needed only for mpl.use initializing graph
from IPython import get_ipython   # comment if not using ipython


# ### change the "user-defined parameters" below as you see fit ###


# layer parameters
# <name of layer> = {
#   'name': any, but a unique name
#   'key': 'generic'
#   'vvv0': reference velocity
#   'rrr2': 2. phase-velocity coefficient
#   'rrr4': 4. phase-velocity coefficient
#   'tilt': tilt of symmetry axis
#   'thick': thickness of a layer measured along the vertical
#   'depth': depth of a reflector measured along the vertical below the source
#   'dip': dip of a reflector, with positive for dipping downwards
#   'ggg': stretch factor
# units of times and distances are arbitrary, but must be applied consistently
# units of angles are degree
# use key': 'generic' for now until epsilon, delta, etc are implemented; see
# also the class Layer
OVERBURDEN = {
    'name': 'overburden',
    'key': 'generic',
    'vvv0': 330.,
    'rrr2': 0.2,
    'rrr4': -0.3,
    'thick': 500.,
    'dip': +10.,
    'ggg': 0.5}
ROCK = {
    'name': 'rock',
    'key': 'generic',
    'vvv0': 1000.,
    'rrr2': -0.2,
    'rrr4': 0.1,
    'thick': 1500.,
    'dip': -5.,
    'ggg': -0.}
TARGET = {
    'name': 'target',
    'key': 'generic',
    'vvv0': 1500.,
    'rrr2': -0.3,
    'rrr4': -0.2,
    'thick': 1400.,
    'dip': -15.,
    'ggg': 0.}


# model = stack of layers
# STACK = [<1'st layer>, <2'nd layer>, ..., <n'th layer>, where all
# <i'th layer> must be a <name of layer> from above and given in top-down order
STACK = [OVERBURDEN, ROCK]
STACK = [OVERBURDEN, ROCK, TARGET]


# source radiation angles
# SOURCE = {'first': <first>, 'last': <last>, 'nos': <nos>}, where
# <first> denotes a first angle,
# <last> a last angle, and
# <nos> an integer number of angles
SOURCE = {
    'first': -90,
    'last': +90,
    'nos': 1800001}
# travelpath
# PATH = [<name of 1'st layer>, ..., <name of n'th layer>];
# note, SURFACE = depth of source will be added automatically at the end
PATH = ['overburden', 'rock', 'target', 'target', 'rock', 'overburden']
# ### PATH = ['overburden', 'rock', 'rock', 'overburden']
# ### PATH = ['overburden', 'overburden']


# traveltime
# TRAVELTIMES = [<1'st traveltime>, ..., <n'th traveltime], with wavefronts
# to be plotted at these times
TRAVELTIMES = [123456789.0]   # some large traveltime for plotting rays
TRAVELTIMES = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]


# graphics window
GRAPHICS = {'xmin': -2000., 'xmax': 4500., 'zmin': -100., 'zmax': 4000.}
# (zmin=-4 just draws the surface on my screen, but zmin=0 won't)

# set canvas controller
# !!! GRAPHICS['control'] = 'ipython'
GRAPHICS['control'] = 'matplotlib'
# select options for canvas manager
if GRAPHICS['control'] == 'ipython':   # suitable for use with, e.g., Spyder
    # plot 'inline' or external in a 'qt' window
    GRAPHICS.update({'modus': 'inline'})
    # !!! GRAPHICS.update({'modus': 'qt5'})
# select options for matplotlib
if GRAPHICS['control'] == 'matplotlib':   # suitable for use with Python
    GRAPHICS.update({'modus': 'QtAgg'})


# interface properties
FACEDASHES = {'original': [1, 0], 'stretch': [20, 5]}


# ray properties
LINECOLOR = ['b', 'g', 'r', 'c', 'm', 'y', 'b', 'g', 'r', 'c', 'm', 'y']
LINEDASHES = {'original': [1, 0], 'stretch': [8, 2]}
assert \
    len(LINECOLOR) >= len(TRAVELTIMES), \
    'not enough COLOR\'s for all TRAVELTIMES'


# printouts
ANGLEPRINT = False       # emission angles of the source
STACKPRINT = True        # depth / dip of the layer stack
PATHPRINT = False        # layer(s) and their top(s) along travelpath
FRONTPRINT = False       # coordinates of the wavefront(s)
PHASEPRINT = False       # phase velocity
DIFFPHASEPRINT = False   # differential phase velocity
DIFFPHASECHECK = False   # check analytic versus numerical diff phase vel
ENERGYPRINT = False      # energy velocity
SLOWPRINT = False        # slowness
RAYPRINT = False         # ray info
CROSSPRINT = True        # cross points
SEGMENTPRINT = False     # traveltime in segment
# Note, DIFFPHASECHECK compares numerically calculated differences between
# successive phase angles with the analytically calculated differential; so,
# use an extremely small interval for the source angle and a large number of
# source angles. Uses numpy gradient. Only a check used during engineering.


# plots
FACEPLOT = True     # plot stretched / unstretched interfaces
SOURCEPLOT = True   # plot source
FRONTPLOT = True    # plot wavefronts
RAYPLOT = False     # T/F for ray
CONSTPLOT = [False, False, False]
# RAYPLOT works best with 1 huge traveltime and very few angles


# printouts
PUBLIC = False
PUBLICWIDTH = 524 / 72.27   # width PS points for SEG article / LaTeX big point
PUBLICHEIGHT = 20           # something larger than required
PUBLICEPS = "SubsurfaceModel.eps"
PUBLICWIN = True            # routine correcting bounding box on Windows
PUBLICPNG = ""              # file not written if string empty
# note, PUBLICWIN is fragile: it requires gswin64c, hardcoded that is, from
# ghostscript, and it works only on Windows


# ### hard-wired parameters ### hard-wired parameters ### hard-wired parameters
# ### do not change unless you know what you are doing ###

# characterize media
# org: the original medium
# new: the newly stretched medium
DEMO = ['original', 'stretch']


# SOURCE.update({
#   'xxx': origin of coordinate system
#   'zzz': origin of coordinate system
#   'time': source time
#   'g': stretch factor in source layer
# For now, the source is located at the surface and, hence, emit only
# downwards. To treat a buried source, split the source layer above and below
# the source level, and propagate accordingly. Not tested.
SOURCE.update({
    'xxx': 0.,
    'zzz': 0.,
    'time': 0.,
    'ggg': STACK[0]['ggg']})


# surface
SURFACE = {
    'name': 'surface',   # for convenient identification only
    'depth': 0.,         # required only to ease logical flow
    'dip': 0.}           # as above


# minimum distance to an interface
FACETOL = +1.e-10


# accuracy of the phase angle
MAXDSINE = 1.e-10   # maximum last update in radian to exit search
SCLFAC = 0.5        # scaling factor of update; note, decreased during search
MAXITERAT = 1000    # emergency break: maximum number of iterations


# some insane large distance
LARGEDISTANCE = 1234567890


# zero coordinate
# note, stretching / updating is calculated for hard-wired x=0.
NULL = 0.


# list of velocity parameters
PARAMETERLIST = [
    'name',   # name (for reference only)
    'vvv0',   # reference velocity
    'rrr2',   # 2nd phase velocity coefficient
    'rrr4',   # 4th phase velocity coefficient
    'tilt',   # tilt of symmetry axis
    'ggg'     # stretch factor
]


# list of interface parameters
FACELIST = [
    'name',    # name (for reference only)
    'depth',   # base reflector depth
    'dip'      # base reflector dip
]


# factor indicating direction of propagation
DIRECT = {'down': +1, 'up': -1}


# Python helper to recognize None as a type
# https://stackoverflow.com/questions/40553285/determining-a-variables-type-is-nonetype-in-python/40553322#40553322
NONETYPE = type(None)


# testing only
DEBUG = True


# ### parameter ### parameter ### parameter ### parameter ### parameter ###


class Control():
    """
    Define all parameters controlling the simulation.

    """

    # pylint: disable=too-many-instance-attributes

    __slots__ = \
        ('demo', 'direct', 'sign', 'time', 'itim', 'ipat', 'nos', 'done')

    def __init__(self):
        """
        Initialize control.

        Instance
        --------
        self.demo : str
            state of computation: either "org" or "stretch" for original or
            stretched
        self.direct : str
            direction of propagation: either "down" or "up";
            will be translated by DIRECT to +1 or -1, respectively
        self.sign : +/-1
            difference in sign in various formulae for down-/upward propagation
        self.time : list of float
            traveltimes at which wavefronts may be plotted;
            note, a single large float suffices for computing rays
        self.index : int
            current index of traveltime under consideration
        self.nos : int
            number of rays
        self.done : bool
            F / T for ray or wavefront to be computed or computed, respectively

        Returns
        -------
        none

        """
        # reset
        self.demo = None
        self.direct = None
        self.sign = None
        self.time = None
        self.itim = np.nan
        self.ipat = np.nan
        self.nos = None
        self.done = None

    def setup(self, demo=None):
        """
        Initialize state.

        Set to original; to be modified for a more general setup.

        Parameters
        ----------
        demo : str
            one state out of DEMO

        Returns
        -------
        self
            demo : str
                set to some initial state

        """
        # set up state
        assert demo in DEMO, f"Control.setup: unknown state {demo}"
        self.demo = 'original'
        # return
        return self

    def direction(self, direct=None):
        """
        Update the control for direction and sign of direction.

        Parameters
        ----------
        direct : str
            direction of propagation: either "down" or "up";
            will be translated by DIRECT to +1 or -1, respectively

        Returns
        -------
        self : Control
            direct : str
                direction of propagation: either "down" or "up";
                will be translated by DIRECT to +1 or -1, respectively
            sign : +/-1
                sign in various formulae for down-/upward propagation

        """
        # get direction and translate into corresponding sign
        assert \
            direct in ("down", "up"), \
            "direct in class Control neither down nor up"
        self.direct = cp(direct)
        self.sign = DIRECT[direct]
        # return
        return self

    def demonstration(self, demo=None):
        """
        Set the state: original or stretched.

        Parameters
        ----------
        demo : str
            state, one of either "org" or "stretch"

        Returns
        -------
        self : Control
            demo :
                see above

        """
        # register state
        assert demo in DEMO, "Control.demonstration: unknown state!"
        self.demo = demo
        # return
        return self

    def doing(self, nos=None):
        """
        Reset the status of calculation.

        True / False for wavefronts and rays calculated or not calculated,
        respectively, for the current traveltime and state

        Parameters
        ----------
        nos : int
            number of rays

        Returns
        -------
        self : Control
            done : bool
                see above

        """
        # register
        assert \
            isinstance(nos, int) and nos > 0, \
            f'Control.doing: {nos} no number!'
        self.nos = nos
        self.done = np.full(self.nos, False, dtype=bool)
        # return
        return self

    def report(self, base=None, top=None):
        """
        Print current status of the simulation.

        Parameters
        ----------
        base : str
            see below
        top : str
            name of top interface (in computational sense); note, top is the
            geological base for downward propagation, but the geological top
            for upward propagation

        Returns
        -------
        self : Control
            reported, but unchanged

        """
        # message
        output = '\nworking on the {:s} state from {:s} to {:s} for {:f}'
        print(output.format(self.demo, base.name, top.name, self.time))
        # return
        return self


# ### layer ### layer ### layer ### layer ### layer ### layer ### layer ###


class Surface():
    """
    Characterize a "surface" layer.

    Note, used for simplifying computational logic only.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, surface=None):
        """
        Initialize Surface parameters, typically set in global SURFACE.

        Parameters
        ----------
        surface : Surface

        Instance
        --------
        name : str
            name of surface, which typically is just that "surface"
        depth : float
            depth of surface, which typically is 0
        dip : float
            dip of surface, which typically is 0
        Note, a different depth or dip has not been tested yet. Recall, though,
        a source and all receivers are assumed at SURFACE['depth']; so, there's
        a stretch below and above to consider. Dip, on the other hand, is
        solely for computational ease as the whole stack can be rotated.

        Returns
        -------
        none

        """
        # default
        if isinstance(surface, NONETYPE):
            surface = SURFACE
        # transfer values to attributes
        self.name = surface['name']
        self.depth = surface['depth']
        self.dip = surface['dip']


class LayerGeneric():
    """
    Characterize a generic 3-term medium.

    3-term as opposed to delta, epsilon, etc specific for P or SV wave. Those
    ones are not yet implemented.

    """

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=invalid-name

    def __init__(self, layer=None):
        """
        Initialize the characterization of a 3-term medium.

        In future, media belonging to different elasticity classes are calling
        respective functions and, here, are characterized as a 3-term medium.

        Parameters
        ----------
        layer :
            dict(
                name=<str>,      # identifying name
                vvv0=<float>,    # reference velocity, updated for stretch
                rrr2=<float>,    # anisotropy parameter
                rrr4=<float>,    # anisotropy parameter
                tilt=<float>),   # tilt of symmetry axis
                thick=<float>,   # thickness perpendicular to top under source
                depth=<float>,   # depth of base interface
                dip=<float>,     # layer dip in deg, to be converted into rad
                ang=<float>,     # opening angle: dip_(i) - dip_(i-1)
                g=<float>        # stretch factor
            Parameters of TTI elasticity and a layer

        Returns
        -------
        none

        """
        self.name = layer['name']
        self.vvv0 = layer['vvv0']
        self.rrr2 = layer['rrr2']
        self.rrr4 = layer['rrr4']
        self.tilt = np.nan                    # to be defined in Stack
        self.thick = layer['thick']
        self.depth = np.nan                   # to be defined in Stack
        self.dip = np.deg2rad(layer['dip'])
        self.ang = np.nan
        self.ggg = layer['ggg']


class Layer():
    """
    Characterize properties and structure of a layer.

    """

    # pylint: disable=too-few-public-methods

    LAYERCONVERT = {'generic': LayerGeneric}

    def __init__(self, layer=None):
        """
        Initialize the call to another layer conversion.

        Parameters
        ----------
        layer : dict
            layer parameters as defined in LayerGeneric

        Returns
        -------
        none

        """
        # call correct layer conversion
        self.LAYERCONVERT[layer['key']].__init__(self, layer=layer)


class Stack(list):
    """
    Characterize a stack of layers.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, stack=None):
        """
        Initialize a stack of layers.

        Parameters
        ----------
        stack : list
            a list of layers, which follow the definition in Layer

        Instance
        --------
        self[i].attribute where
            i : number of layers in stack
            attribute : any attribute of Layer
        self[i].tilt : tilt of symmetry axis, with
            self[0].tilt perpendicular to surface as required
        self.nos : number of layers in stack

        Returns
        -------
        none

        """
        # convert STACK according to Layer notation and create a stack
        stack = [Layer(layer=layer) for layer in stack]
        # inherit
        super().__init__(stack)   # defining self as list subclass here
        # number of layers
        self.nos = len(stack)
        # tilt of symmetry axis relative to vertical:
        # note, the vertical is rotated normal to the layer top
        # note, the angle is measured with respect to the vertical, not the
        # horizontal as the layer dip
        self[0].tilt = 0.
        for iii in range(1, self.nos):
            self[iii].tilt = -1 * self[iii-1].dip
        # opening angle
        self[0].ang = self[0].dip
        for iii in range(1, self.nos):
            self[iii].ang = self[iii].dip - self[iii-1].dip
        # depth
        stack[0].depth = stack[0].thick
        for iii in range(1, self.nos, 1):
            self[iii].depth = self[iii-1].depth + self[iii].thick
        # cross point
        self.cross = None


class StackAux():
    """
    Define auxiliary variables for Stacks

    """

    # pylint: disable=too-few-public-methods

    __slots__ = ('gfac', 'rot', 'velfac', 'dist', 'iii', 'jjj')

    def __init__(self):
        """
        Define auxiliary variables.

        Instance
        --------
        gfac : float
            stretch factor as defined in the paper
        rot : float
            amount of rotation as defined in the paper
        velfac : float
            velocity increase as defined in the paper
        dist : float
            length of top normal, used while computing a new thickness
        iii : int
            index of layer to be stretched
        jjj : int
            index of any layer underneath the stretched one

        Returns
        -------
        none

        """
        # define stretch-related parameters
        self.gfac = np.nan
        self.rot = np.nan
        self.velfac = np.nan
        # define length of the "normal" vector
        self.dist = np.nan
        # indices
        self.iii = np.nan   # index of layer to be stretched
        self.jjj = np.nan   # index of layer underneath the stretched one

    def inside(self):
        """
        Reset auxiliary variables for the stretched layer.

        Returns
        -------
        self : StackAux
            gfac : 1
                stretch factor reset (neutral value = 1)
            dist : np.nan
                nan'ed for safety

        """
        # reset
        self.gfac = np.nan
        self.rot = np.nan
        self.velfac = np.nan
        self.dist = np.nan
        self.iii = self.iii    # keep
        self.jjj = np.nan
        # return
        return self

    def below(self):
        """
        Reset auxiliary variables for layers below the stretched one.

        Returns
        -------
        self : StackAux
            gfac : 1
                stretch factor reset (neutral value = 1)
            dist : np.nan
                nan'ed for safety

        """
        # reset
        self.gfac = 1.              # neutral
        self.rot = self.rot         # keep
        self.velfac = self.velfac   # keep
        self.dist = np.nan          # initially unknown
        self.iii = self.iii         # keep
        self.jjj = self.jjj         # keep
        # return
        return self

    def setup(self, stack=None):
        """
        Define all stretch-involved parameters.

        Parameters
        ----------
        stack : Stack
            original stack of layers

        Returns
        -------
        self : StackAux
            gfac : float
                stretch factor
            rot : float
                incremental rotation
            velfac : float
                velocity factor

        """
        # calculate stretch term
        self.gfac = np.sqrt(1. + stack[self.iii].ggg)
        # calculate additive base rotation
        self.rot = (
            np.arctan(self.gfac * np.tan(stack[self.iii].ang))
            -
            stack[self.iii].ang)
        # calculate multiplicative velocity increase
        self.velfac = (
            np.sqrt(
                1. + stack[self.iii].ggg * np.sin(stack[self.iii].ang) ** 2))
        # return
        return self


class Stacks(dict):
    """
    Describe a stack of layers and modify their properties.

    The stack of layer is described as a list subclass, and the functions as
    methods of that subclass.

    """

    # pylint:disable=unused-argument # called from dict with other functions
    @staticmethod
    def _org(stack=None, graph=None):
        """
        Work on the stack in original state only.

        Parameters
        ----------
        stack : Stack
            stack in original state
        graph : Graphics
            graphics (not currently in use)

        Returns
        -------
        stack : Stack
            stack in original state, plus vertical depth

        """
        # loop through all layers in stack
        for layer in stack:
            # zero out stretch factor
            layer.ggg = 0.0
        # depth of layers in stack
        for iii in range(stack.nos):
            stack[iii].depth = np.sum(
                [stack[jjj].thick for jjj in range(iii+1)])
        # return
        return stack

    @staticmethod
    def _stretch(stack=None, graph=None):
        """
        Work on the stack in the stretched state only.

        For the rotation of a line around a point see
        https://math.stackexchange.com/questions/1064832/rotate-a-line-by-a-given-angle-about-a-point

        Parameters
        ----------
        stack : Stack
            stack in original state
        graph : Graphics
            graphics

        Returns
        -------
        stack : Stack
            stack in stretched state, plus vertical depth

        """

        # pylint: disable=too-many-statements

        def _open(newstack=None):
            """
            Update opening angle.

            Returns
            -------
            newstack : Stack
                ang : list of float or nan, updated opening angle

            """
            # calculate opening angle
            newstack[0].ang = newstack[0].dip
            for iii in range(1, newstack.nos):
                newstack[iii].ang = newstack[iii].dip - newstack[iii-1].dip
            # return
            return newstack

        def _stackprint(add="", layer=None, aux=None):
            """
            Print infos about the stack of layers

            Parameters
            ----------
            layer : Layer
                exactly that, a layer whose parameters are to be printed
            aux : StackAux
                auxiliary variables
                    gfac : stretch factor
                    rot : rotation
                    velfac : velocity factor

            Returns
            -------
            none

            """
            # call
            if STACKPRINT:
                _stackprint1(add=add, layer=layer, aux=aux)
                _stackprint2(layer=layer, aux=aux)

        def _stackprint1(add=None, layer=None, aux=None):
            """
            Print additional layer information

            Parameters
            ----------
            add : str
                addition to standard header
            layer : Layer
                exactly that, one layer before / after stretch + rotation
            aux : StackAux
                auxiliary

            Returns
            -------
            none

            """
            if STACKPRINT:
                output = "\ncharacterizing stretch in {:s}" + add
                output += "\nstretch={:+9.6f}"
                output += ", rotation={:+9.6f}"
                output += ", factor={:8.6f}"
                string = [
                    layer.name, aux.gfac, np.rad2deg(aux.rot), aux.velfac]
                print(output.format(*string))

        def _stackprint2(layer=None, aux=None):
            """
            Print additional layer information.

            h_norm : length of top normal
            h_vert : layer thickness along vertical
            dip : layer dip

            Parameters
            ----------
            layer : Layer
                exactly that, one layer before / after stretch + rotation
            aux : StackAux
                auxiliary

            Returns
            -------
            none

            """
            if STACKPRINT:
                output = "h_norm={:11.6f}, h_vert={:11.6f}, dip={:9.6f}"
                string = [aux.dist, layer.thick, np.rad2deg(layer.dip)]
                print(output.format(*string))

        def _conpoint(zero=None, point=None, anno=None):
            # shift coordinates
            if isinstance(zero, NONETYPE):
                totpoint = point
            else:
                totpoint = Point().add(point1=zero, point2=point)
            # plot point
            plt.plot(totpoint.xxx, totpoint.zzz, marker='o', markersize=5)
            # annotate
            if not isinstance(anno, NONETYPE):
                plt.annotate(anno, xy=(totpoint.xxx, totpoint.zzz))
            # show graphics
            plt.draw()

        def _conline(zero=None, point1=None, point2=None, anno=None):
            # shift coordinates
            if isinstance(zero, NONETYPE):
                totpoint1 = point1
                totpoint2 = point2
            else:
                totpoint1 = Point().add(point1=zero, point2=point1)
                totpoint2 = Point().add(point1=zero, point2=point2)
            # plot line
            plt.plot(
                [totpoint1.xxx, totpoint2.xxx], [totpoint1.zzz, totpoint2.zzz])
            # annotate
            if not isinstance(anno, NONETYPE):
                plt.annotate(anno, xy=(totpoint2.xxx, totpoint2.zzz))
            # show graphics
            plt.draw()

        def _dip(stack=None, aux=None):
            """
            Calculate the dip of a normal.

            """
            # calculate dip
            dip = sys.float_info.max
            if aux.iii == 0:       # at the surface
                dip = np.pi / 2.   # vertical down in (x,z) coordinate system
            else:                  # all other interfaces
                if stack[aux.iii-1].dip >= 0:                 # pos. face dip
                    dip = stack[aux.iii-1].dip - np.pi / 2.   # up
                else:                                         # neg. face dip
                    dip = stack[aux.iii-1].dip + np.pi / 2.   # down
            # check
            assert \
                np.abs(dip) <= +1. * np.pi / 2., \
                "Stack._inside: check dip " + dip
            # return
            return dip

        def _inside(stack=None, newstack=None, aux=None):
            """
            Project vertical onto normal, stretch, and project back.

            Note, do not rotate the normal vector. Inside the layer to be
            stretched, the base rotation is subsequently defined; see paper.

            Lines are defined as y = m x + b, where m = tan(phi). E.g., insert
            any point (x_0, z_0) and solve for intercept b. Or solve for the
            cross point of two lines by equating m1 x + b1 = m2 x + b2 and
            solve for x, then insert x into any one line.

            Parameters
            ----------
            stack : Stack
                current stack of layers
            newstack : Stack
                stretched / rotated stack of layers
            aux : StackAux
                auxiliary

            Returns
            -------
            newstack: Stack
                stretched / rotated stack of layers with correct depth

            """

            # pylint:disable=too-many-locals

            # (1) define  zero point = intercept of top
            zzz1 = 0. if aux.iii == 0 else stack[aux.iii-1].depth
            zero = \
                Point(xxx0=NULL, zzz0=zzz1).\
                printout(title="top intercept")
            if CONSTPLOT[aux.iii]:
                _conpoint(point=zero, anno="top intercept")
            # (2) define a line normal to top (not yet a normal vector)
            dip1 = _dip(stack=stack, aux=aux)
            line1 = Line(dip=dip1, point=zero)
            # (3) define base
            zzz2 = stack[aux.iii].depth
            intercept = \
                Point(xxx0=NULL, zzz0=zzz2).\
                printout(title="base intercept")
            if CONSTPLOT[aux.iii]:
                _conpoint(point=intercept, anno="base intercept")
            dip2 = stack[aux.iii].dip
            line2 = Line(dip=dip2, point=intercept)
            # (4) calculate crossing point of top normal and base
            cross = \
                Point().cross(line1=line1, line2=line2).\
                printout(title="base cross")
            if CONSTPLOT[aux.iii]:
                _conpoint(point=cross, anno="base cross")
            # preserve crossing point for layers below
            stack[aux.iii].cross = cp(cross)
            # (5) define a normal vector
            normal = Vector(foot=zero, head=cross)
            if CONSTPLOT[aux.iii]:
                _conline(point1=zero, point2=cross)
            # (6) stretch normal vector
            normal.stretch(fac=aux.gfac)
            newcross = normal.head
            normal.head.\
                printout(title="new base cross")
            if CONSTPLOT[aux.iii]:
                _conpoint(point=newcross, anno="new base cross")
                _conline(point1=cross, point2=newcross)
            # preserve new crossing point
            newstack[aux.iii].cross = cp(newcross)
            # (7) project normal vector onto vertical
            dip7 = newstack[aux.iii].dip                # new dip of base
            line7 = Line(dip=dip7, point=newcross)
            newintercept = Point(xxx0=NULL, zzz0=line7.bbb).\
                printout(title="new base intercept")
            if CONSTPLOT[aux.iii]:
                _conpoint(point=newintercept, anno="new base intercept")
            # preserve new intercept as depth, calculate thickness
            newstack[aux.iii].depth = newintercept.zzz
            newstack[aux.iii].thick = \
                newstack[aux.iii].depth if aux.iii == 0 \
                else newstack[aux.iii].depth - stack[aux.iii-1].depth
            # extract new depth and return
            return stack, newstack

        def _below(stack=None, newstack=None, aux=None):
            """
            Project vertical onto normal, stretch, rotate and project back.

            Lines are defined as y = m x + b, where m = tan(phi). E.g., insert
            any point (x_0, z_0) and solve for intercept b. Or solve for the
            cross point of two lines by equating m1 x + b1 = m2 x + b2 and
            solve for x, then insert x into any one line.

            Parameters
            ----------
            stack : Stack
                current stack of layers
            newstack : Stack
                stretched / rotated stack of layers
            aux : StackAux
                auxiliary

            Returns
            -------
            newstack: Stack
                stretched / rotated stack of layers with correct depth

            """

            # pylint:disable=too-many-locals

            # (1) define a top normal relative to the cross point on the base
            # of the layer above
            # note, the dip is determined by the stretch axis in the layer
            # undergoing stretching above.
            oldzero = \
                stack[aux.iii].cross .\
                printout(title="old top cross")
            dip1 = stack[aux.iii].dip - np.pi / 2.   # dip in the layer above
            line1 = Line(dip=dip1, point=oldzero)
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=oldzero, anno="old top cross")
            # (2) define base
            # note, the depth of that base is stack[i].depth at the vertical
            zzz2 = stack[aux.jjj].depth
            intercept = \
                Point(xxx0=NULL, zzz0=zzz2).\
                printout(title="base intercept")
            dip2 = stack[aux.jjj].dip
            line2 = Line(dip=dip2, point=intercept)
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=intercept, anno="base intercept")
            # (3) calculate the cross point of top normal and base
            cross = \
                Point().\
                cross(line1=line1, line2=line2).\
                printout(title="base cross")
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=cross, anno="base cross")
            # (4) define a normal vector
            normal = Vector(foot=oldzero, head=cross)
            if CONSTPLOT[aux.jjj]:
                _conline(point1=oldzero, point2=cross)
            # (5) rotate the normal vector
            normal.rotate(angle=aux.rot)
            rotatecross = normal.head
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=rotatecross, anno="rotated base cross")
            # (6) stretch the normal vector
            normal.stretch(fac=aux.velfac)
            newstretch = normal.head.\
                printout(title="stretched base cross")
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=newstretch, anno="stretched base cross")
            # (7) attach to new top cross
            newzero = newstack[aux.iii].cross
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=newzero, anno="new top zero")
            normal.move(fro=stack[aux.iii].cross, too=newzero)
            # (8) project the normal vector back onto the vertical
            # note, the headpoint of the normal vector is along the new base
            dip7 = newstack[aux.jjj].dip
            line7 = Line(dip=dip7, point=normal.head)
            newintercept = Point(xxx0=NULL, zzz0=line7.bbb).\
                printout(title="new base intercept")
            if CONSTPLOT[aux.jjj]:
                _conpoint(point=newintercept, anno="new base intercept")
            # extract new depth
            newstack[aux.jjj].depth = newintercept.zzz
            # return
            return newstack

        def _execute(stack=None, aux=None, graph=None):
            """
            Execute the stretching of a layer and updating of layers below.

            Parameters
            ----------
            stack : Stack
                original stack of layers
            graph : Graphics
                graphics
            aux : StackAux
                auxiliary variables

            Returns
            -------
            newstack : Stack
                stack of stretched / updated layers

            """
            # reset auxiliary variables
            aux.inside()
            # copy stack
            # note, newstack contains the parameters of the stretched stack,
            # but all calculations below are still done with the parameters of
            # the current stack
            newstack = cp(stack)   # copy!
            # print additional infos
            _stackprint(
                add=" before stretching", layer=newstack[aux.iii], aux=aux)
            # set up all stretch-involved parameters
            aux.setup(stack=stack)
            # apply base rotation (eq. 7)
            newstack[aux.iii].dip = stack[aux.iii].dip + aux.rot
            # calculate cross points, depth and thickness
            stack, newstack = _inside(stack=stack, newstack=newstack, aux=aux)
            # print additional infos
            _stackprint(
                add=" after stretching", layer=newstack[aux.iii], aux=aux)
            # loop through all layers in stack below the current layer
            for aux.jjj in range(aux.iii+1, stack.nos):
                # set auxiliary variable to that below a stretched layer
                aux.below()
                # print additional infos
                _stackprint(
                    add=" before updating", layer=stack[aux.jjj], aux=aux)
                # rotate base dip
                newstack[aux.jjj].dip = stack[aux.jjj].dip + aux.rot
                # rotate symmetry tilt
                newstack[aux.jjj].tilt = stack[aux.jjj].tilt - aux.rot
                # stretch reference velocity
                newstack[aux.jjj].vvv0 = stack[aux.jjj].vvv0 * aux.velfac
                # calculate layer thickness
                newstack = _below(stack=stack, newstack=newstack, aux=aux)
                # re-calculate depth of base
                newstack[aux.jjj].thick = \
                    newstack[aux.jjj].depth - newstack[aux.jjj-1].depth
                # print additional infos
                _stackprint(
                    add=" after updating", layer=newstack[aux.jjj],
                    aux=aux)
            # copy back into stack
            newstack = _open(newstack=newstack)
            # return
            return newstack

        # initialize auxiliary variables
        aux = StackAux()   # reset for each run through stack
        # loop through all layers in stack
        for aux.iii in range(stack.nos):
            if stack[aux.iii].ggg != 0.:   # no need to do anything otherwise
                # call the stretch process
                stack = _execute(stack=stack, aux=aux, graph=graph)
            # note, stretching based on parameters of layer iii now completed
        # return
        return stack

    # create multiple objects of type Layer and list them
    # https://stackoverflow.com/questions/14600620/creating-multiple-objects-within-the-same-class-in-python
    # list subclass allowing to add methods to an otherwise built-in type
    # http://igorsobreira.com/2011/02/06/adding-methods-dynamically-in-python.html
    def __init__(self, stack=None, graph=None):
        """
        Subclass a list containing a stack of layers.

        Parameters
        ----------
        stack : Stack
            list of layers
        graph : Graphics
            graphics

        Instance
        --------
        self{demo}.stack
            demo : one of original or stretched state
            stack : a list of layers in either original or stretched state

        Returns
        -------
        none

        """
        # default
        if isinstance(stack, NONETYPE):
            stack = STACK
        # get an instance of Stack
        stack = Stack(stack=stack)
        # copy stack in all states
        state = {'original': self._org, 'stretch': self._stretch}
        stacks = {
            demo: state[demo](stack=cp(stack), graph=graph)   # copy stack!
            for demo in DEMO}
        # inherit
        super().__init__(stacks)   # defining self as dict subclass here
        # number of layers
        self.nos = stack.nos

    def info(self):
        """
        Print layers making up the layer stack.

        Returns
        -------
        none

        """
        # identify
        stack = self
        # check switch
        if STACKPRINT:
            # write title
            print('\nlayer stack:')
            # write header for structure
            width = \
                max(
                    len(stack['original'][index].name)
                    for index in range(stack.nos))
            header = 'name'                         # name
            header += ' ' * (width + 6) + 'depth'   # depth (w variable offset)
            header += ' ' * 15 + 'dip'              # dip
            print(header)
            # define format for structure
            output = f"{{:{width}s}}"           # name
            output += "   {:8.3f}, {:8.3f}"     # depth
            output += "   {:+7.3f}, {:+7.3f}"   # dip
            # collect data and print structure layer by layer
            for index in range(stack.nos):
                string = (
                    stack['original'][index].name,
                    stack['original'][index].depth,
                    stack['stretch'][index].depth,
                    np.rad2deg(stack['original'][index].dip),
                    np.rad2deg(stack['stretch'][index].dip))
                print(output.format(*string))
            # write title
            print('\nlayer stack:')
            # write header for elasticity
            width = \
                max(
                    len(stack['original'][index].name)
                    for index in range(stack.nos))
            header = 'name'                       # name
            header += ' ' * (width + 6) + 'v_0'   # ref velocity
            header += ' ' * 16 + 'r_2'            # r2 coeff
            header += ' ' * 14 + 'r_4'            # r4 coeff
            header += ' ' * 15 + 'tilt'           # symm tilt
            print(header)
            # define format for elasticity
            output = f"{{:{width}s}}"           # name
            output += "   {:8.3f}, {:8.3f}"     # ref velocity
            output += "   {:+1.3f}, {:+1.3f}"   # r2 coeff
            output += "   {:+1.3f}, {:+1.3f}"   # r4 coeff
            output += "   {:+7.3f}, {:+7.3f}"   # symm tilt
            # collect data and print elasticity layer by layer
            for index in range(stack.nos):
                string = (
                    stack['original'][index].name,
                    stack['original'][index].vvv0,
                    stack['stretch'][index].vvv0,
                    stack['original'][index].rrr2,
                    stack['stretch'][index].rrr2,
                    stack['original'][index].rrr4,
                    stack['stretch'][index].rrr4,
                    np.rad2deg(stack['original'][index].tilt),
                    np.rad2deg(stack['stretch'][index].tilt))
                print(output.format(*string))
        # return
        return stack


class Para():
    """
    Get the parameters characterizing velocities.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, layer=None):
        """
        Extract velocity parameters from layer information.

        Parameters
        ----------
        layer : Layer
            all information specifically for a layer

        Returns
        -------
        none

        """
        # copy all parameters of PARAMETERLIST from layer
        for item in PARAMETERLIST:
            setattr(self, item, getattr(layer, item))


class Face():
    """
    Get the parameters characterizing the interface a wave is impinging on.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, layer=None):
        """
        Extract the interface parameters from layer information.

        Parameters
        ----------
        layer : Layer
            see Layer for definition

        Instance
        --------
        self.attribute
            where attribute to be copied from layer are defined in FACELIST

        Returns
        -------
        none

        """
        # copy all parameters of FACELIST from layer
        for item in FACELIST:
            setattr(self, item, getattr(layer, item))


class Path():
    """
    Extract parameters and interfaces along a travelpath.

    """

    def __init__(self, path=None, surface=None, stack=None):
        """


        Parameters
        ----------
        path : Path
            travelpath taken
        surface : Surface
            surface layer
        stack : Stack
            one of the original or stretched stacks of layers

        Returns
        -------
        none

        """
        # extract number of layers in path
        self.nos = len(path)
        # extract available layer names in stack
        name = [layer.name for layer in stack]
        # index path layers by correlating path names with layer names
        self.index = [name.index(path[iii]) for iii in range(self.nos)]
        # extract properties
        self.para = [
            Para(layer=stack[self.index[iii]]) for iii in range(self.nos)]
        # direction of travel:
        # extract from the difference in layer indices
        direct = dict(zip(DIRECT.values(), DIRECT.keys()))
        self.direct = ['down']   # downwards in source layer
        self.direct += [
            direct[index] if index != 0
            else ('up' if self.direct[index-1] == 'down' else 'down')
            for index in list(np.diff(self.index))]
        # extract interfaces
        # (base interface is defined in layer: so, base interface is in current
        # layer = current layer index, and top interface is base interface of
        # layer above = current layer index - 1)
        self.face = [
            Face(
                layer=cp(
                    stack[
                        self.index[iii] if self.direct[iii] == 'down'
                        else self.index[iii]-1]))
            for iii in range(self.nos-1)]
        # add surface
        self.face += [Face(layer=cp(surface))]

    def info(self):
        """
        Print travelpath.

        Note, provided PATHPRINT is switched on.

        Returns
        -------
        self : Path
            report, but unchanged

        """
        # check switch
        if PATHPRINT:
            # write title
            print('\ntravelpath:')
            # number of digits in nos
            width1 = int(np.log10(self.nos)) + 2
            # number of characters
            width2 = max(
                len(self.para[iii].name) for iii in range(len(self.para)))
            # write header
            output = f"{{:{width1}s}}"
            output += "   {:4s}"
            output += f"   {{:{width2}s}}"
            output += f"   {{:{width2}s}}"
            string = ['id', 'd/u', 'layer', 'interface']
            print(output.format(*string))
            # write data in PATH
            output = f"{{:{width1}d}}"
            output += "   {:4s}"
            output += f"   {{:{width2}s}}"
            output += f"   {{:{width2}s}}"
            for iii in range(self.nos):
                numbers = [
                    self.index[iii], self.direct[iii], self.para[iii].name,
                    self.face[iii].name]
                print(output.format(*numbers))
        # return
        return self

    def next(self, surface=None):
        """
        Returns a generator with layer index, its properties and interaces.

        Yields
        ------
        iii : int
            layer index according to stacks
        para : Para
            layer parameters
        base : str
            name of top interface (in computational sense); note, top / base
            are the geological base / top for downward propagation, but the
            geological base / top for upward propagation
        face : Face
            top interface = base interface of next layer in stacks
        Recall, SURFACE is always added to stacks.

        """
        # surface
        if isinstance(surface, NONETYPE):
            surface = Surface(SURFACE)
        if isinstance(surface, dict):
            surface = Surface(surface)
        # loop over all layers in stacks
        for iii in range(self.nos):
            para = self.para[iii]
            face = self.face[iii]
            base = ([surface] + self.face)[iii]
            yield iii, para, base, face        # return generator


class Paths(dict):
    """
    A dictionary of Path's, one Path for each element in DEMO.

    """

    def __init__(self, path=None, surface=None, stacks=None):
        """
        Set up travelpaths through original or stretched stacks of layers.

        Note, multiples are possible.
        Note, specify each layer passed; omitted layers will be missing.
        Note, for now, travelpaths begins / ends at the surface.

        Parameters
        ----------
        path : PATH
            user-defined travelpath. the default is PATH.
        surface : SURFACE
            Exactly that, surface. The default is SURFACE.
        stacks : STACKS
            original or stretched stacks of layers; the travelpath passes
            through the same set of layers, although obviously the geometry
            differs.

        Returns
        -------
        none

        """
        # default
        assert \
            not isinstance(path, NONETYPE), \
            "Paths.__init__: no path given!"
        assert \
            not isinstance(surface, NONETYPE), \
            "Paths.__init__: no surface given!"
        assert \
            not isinstance(stacks, NONETYPE), \
            "Paths.__init_: stacks in class Paths undefined!"
        # transfer user-defined surface to variable surface
        surface = Surface(surface=surface)
        # set up paths
        paths = {
            demo: Path(path=path, surface=surface, stack=stacks[demo])
            for demo in DEMO}
        super().__init__(paths)

    def info(self):
        """
        Write out the entire travelpath.

        The travelpath remains identical for all DEMO's; so, writing it out
        once is sufficient.

        Returns
        -------
        self : Paths
            report, but unchanged

        """
        # write travelpath
        self[DEMO[0]].info()   # path info identical for all DEMO's
        # return
        return self


# ### source ### source ### source ### source ### source ### source ###


class Source():
    """
    Define an initial set of rays as emitted by a source.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, source=None):
        """
        Initialize a source.

        Parameters
        ----------
        source :
            dict(
                first=<float>,   # emission angle of first ray
                last=<float>,    # emission angle of last ray
                nos=<int>,       # number of emission angles
                xxx=<float>,     # lateral origin of coordinate system
                zzz=<float>,     # vertical origin of coordinate system
                time=<float>     # source time
            where source should trace back to SOURCE

        Returns
        -------
        self :
            xxx=<float>,         # lateral origin of coordinate system
            zzz=<float>,         # vertical origin of coordinate system
            time=<float>,        # source time (usually just 0)
            angle=<np.array>,    # all emission angles
            nos=<int>            # number of emission angles

        """
        # default
        assert \
            not isinstance(source, NONETYPE), \
            "Source.__init__: no source given!"
        # locate source
        # (right now should trace back to (0, 0))
        self.xxx = source['xxx']
        self.zzz = source['zzz']
        # set time
        # (normally just 0)
        self.time = source['time']
        # number of angles
        self.nos = source['nos']
        # set range of emission angles
        first = np.deg2rad(source['first'])
        last = np.deg2rad(source['last'])
        if self.nos == 1:
            assert first == last, \
                'Source.__init__: if nos=1, then first must equal last'
            self.angle = np.array([first])
        else:
            self.angle = np.array([
                first + iii * (last - first) / float(self.nos - 1)
                for iii in range(0, self.nos)])
        # stretch factor
        self.ggg = source['ggg']

    def info(self):
        """
        Print source emission angles.

        Returns
        -------
        self : Source
            report, but unchanged

        """
        # check switch
        if ANGLEPRINT:
            # number of digits in nos
            width = int(np.log10(self.nos)) + 1
            # print title
            print('\nemitted source angle:')
            # print header
            print(' ' * width + '   orig.')
            # format for data output
            output = f"{{:{width}d}}   {{:+7.3f}}"
            # loop over angles in org and after state
            for index in range(self.nos):   # as efficient as zip, print, ...
                numbers = (                 # but without extra memory
                    index,
                    np.rad2deg(self.angle[index]))
                print(output.format(*numbers))
        # return
        return self


# ### front ### front ### front ### front ### front ### front ### front ###


class SegmentAux():
    """
    Describing the ray segment within a layer.

    """

    # pylint:disable=too-few-public-methods

    def __init__(self):
        """
        Initialize a ray segment.

        Initialization
        --------------
        xxx, zzz, length : list of float or nan
            next x-, z-coordinate and length of ray
        time : list of float or nan
            traveltime along ray
        para : list of int
            list of parallel rays
        back : list of int
            list of anti-parallel ("behind") rays

        Returns
        -------
        none

        """
        self.xxx = None
        self.zzz = None
        self.length = None
        self.time = None
        # list of parallel rays
        self.para = None
        # list of anti-parallel ("behind") rays
        self.back = None


class Front():
    """
    Describe location and time of a wavefront.

    """

    # pylint: disable=too-few-public-methods,too-many-instance-attributes

    def __init__(self, source=None, color=None, dashes=None):
        """
        Initialize a wavefront.

        Parameters
        ----------
        source : Source
            Source.
        color : str
            Matplotlib color; efault in Fronts LINECOLOR[cntl.index]
        dashes : str
            Matplotlib dashes; default in Fronts LINEDASHES[demo]

        Instances
        ---------
        color : str
        dashes : str
        xxx, zzz : list of float or nan
            horizontal and vertical component of a point on a wavefront
        time : list of float or nan
            traveltime
        done : bool
            T / F for final wavefront point calculated / not yet calculated
        nos : int
            number of wavefront points

        Returns
        -------
        none

        """
        # initialize
        self.color = color
        self.dashes = dashes
        self.xxx = np.array([source.xxx] * source.nos)
        self.zzz = np.array([source.zzz] * source.nos)
        self.time = np.array([source.time] * source.nos)
        self.nos = source.nos

    def _rayprint(self, segment, energy):
        """
        Print information about one particular ray.

        Parameters
        ----------
        segment : SegmentAux
            length : list of float
                length of ray segment
            time : list of float
                traveltime along ray segment
        energy : Energy
            energy velocity
        xxx : list of float
            horizontal component
        zzz : list of float
            vertical component

        Returns
        -------
        none

        """
        # check switch
        if RAYPRINT:
            # pick one ray in the middle
            assert \
                self.nos % 2 != 0, \
                "Front.crosspoint: pick even number of rays when RAYPRINT!"
            mid1 = int((self.nos - 1) / 2)
            # print header
            print("\nray point:")
            # print length and incidence angle
            output = "dl={:8.6f}, ang={:8.6f}"
            inn = (segment.length[mid1], np.rad2deg(energy.angle[mid1]))
            print(output.format(*inn))
            # print traveltime and coordinates
            output = "dt={:8.6f}, dx={:+9.3f}, dz={:+8.3f}"
            inn = (segment.time[mid1], self.xxx[mid1], self.zzz[mid1])
            print(output.format(*inn))

    def crosspoint(self, cntl=None, top=None, energy=None):
        """
        Computing the crossing point of ray with interface.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation
        top : str
            name of interface (in computational sense) at end of segment:
            note, top is the geological base for downward propagation, but the
            geological top for upward propagation
        energy : Energy
            energy velocity

        Variables
        ---------
        xxx, zzz : list of floats or nan
            horizontal and vertical distance between start and endpoints of
            segment
        length : list of floats or nan
            length of segment
        time : list of floats or nan
            potential traveltime along entire segment
        frag : list of floats <= 1 or nan
            fraction of actual time over potential traveltime:
            note, actual time might be lower if specified total traveltime
            reached

        Returns
        -------
        self : Front
            crosspoint coordinates and time:
            note, absolute, that is after adding local segment to raypath
        cntl : Control
            updated for completeness

        """

        # pylint:disable=too-many-statements
        # pylint:disable=too-many-locals

        def _checkangle(xxx, zzz):
            """
            Check direction of propagation; some cross points are behind.

            Parameters
            ----------
            xxx : list of float or nan
                x distance of ray segment
            zzz : list of float or nan
                z distance or ray segment

            External Scope
            --------------
            self : Front

            Returns
            -------
            back : list of int
                indices with cross points behind in ray segment

            """
            # calculate ray angle
            checkangle = np.arctan2(xxx, zzz)
            # check ray and energy angle
            # note, theoretically, 0deg, but +/- 180deg if "behind"
            checkangle = np.abs(np.abs(checkangle - energy.angle) - np.pi)
            back = checkangle < np.pi / 123.   # close to 0deg if behind
            # convert T/F into a list of indices where T
            back = np.where(back[True])
            back = list(itertools.chain.from_iterable(back))
            # return
            return back

        def _faraway(where=None, segment=None):
            """
            Assign a fake large segment of ray.

            Note,
                1. cross point at infinity (or numerically overflow)
                2. cross point along anti-parallel ("behind") ray, where foot-
                   point->cross point are opposite to the energy direction

            Parameters
            ----------
            where : list of int
                indices at which x-, z-coordinates are at a fake large distance
            segment : SegmentAux
                ray in current segment

            Returns
            -------
            segment : SegmentAux
                ray in current segment with modified x-, z-coordinate

            """
            # assign new coordinates
            segment.xxx[where] = LARGEDISTANCE * sine[where]
            segment.zzz[where] = LARGEDISTANCE * cose[where]
            # assign length of ray
            segment.length[where] = LARGEDISTANCE
            # return modified segment
            return segment

        def _formula(segment=None, energy=None, top=None):
            """
            Calculate the next cross point of ray and interface.

            Parameters
            ----------
            segment : SegmentAux
                characterizing segment properties
            energy : Energy
                energy velocity
            top : Face
                next interface

            Raises
            ------
            AssertionError
                fails when ray and interface are (numerically) parallel
                    ZeroDivisionError : should be dealt with
                    OverflowError : should be dealt with

            Returns
            -------
            segment : SegmentAux
                segment properties with modified coordinates

            """

            # calculate numerator and denominator for cross point
            num = cose * self.xxx + (top.depth - self.zzz) * sine
            denom = cose - sine * np.tan(top.dip)
            # calculate horizontal component + check for ray being parallel to
            # the interface
            # note, parallel implies num/denom going through infinity
            with np.errstate(divide='ignore', over='raise'):   # catch numerics
                try:
                    # calculate horizontal component as numerator / denominator
                    # and assign np.inf if denominator is zero
                    segment.xxx = \
                        np.where(denom != 0., num / denom, np.inf) - self.xxx
                    # calculate vertical component
                    segment.zzz = \
                        np.tan(top.dip) * (self.xxx + segment.xxx) \
                        + top.depth \
                        - self.zzz
                    segment.length = \
                        np.sqrt(
                            segment.xxx * segment.xxx
                            + segment.zzz * segment.zzz)
                    # find all indices with xxx=np.inf's
                    # note, np.Inf from above and numerical overflows
                    segment.para = np.where(np.abs(segment.xxx) == np.inf)
                    # flatten to a single list
                    segment.para = \
                        list(itertools.chain.from_iterable(segment.para))
                    # replace the horizontal component with something large
                    # along the ray
                    segment = _faraway(where=segment.para, segment=segment)
                except ZeroDivisionError as zero:
                    # should have been caught by numpy.where
                    print("\nFront.crosspoint: unexpected zero division!!!")
                    raise AssertionError(zero) from zero
                except OverflowError as overflow:
                    # should have been produced by near-zero division, but
                    # instead np.Inf is output without overflow
                    print("\nFront.crosspoint: unexpected overflow!!!")
                    raise AssertionError(overflow) from overflow
                # verify no np.Inf left
                assert \
                    np.logical_not(np.any(np.isinf(np.abs(segment.zzz)))), \
                    "Front.crosspoint: infinity!!!"
            # check orientation of ray ("behind")
            # note, "behind" means the ray from the foot point to the cross
            # point is in opposite direction to the energy ray
            segment.back = _checkangle(xxx=segment.xxx, zzz=segment.zzz)
            segment = _faraway(where=segment.back, segment=segment)
            # calculate traveltime through segment
            segment.time = segment.length / energy.mag
            # return
            return segment

        def _fraction(cntl=None, segment=None):
            """
            Calculate time spent in a segment.

            Parameters
            ----------
            cntl : Control
                parameters controlling the simulation
            segment : Segment
                properties of the ray in a segment

            Returns
            -------
            segment : Segment
                updated properties (coordinates, length and traveltime)
            frag : float
                fraction of potential traveltime spent in the current segment

            """
            # determine the fraction of the remaining traveltime to be spent
            # inside the current segment:
            # if < 1 the wavefront ends in the current segment, if = 1 the
            # wavefront ends at the next interface, and if > 1 it continues
            # into the next layer
            frag = (cntl.time - self.time) / segment.time
            # limit to segment or fraction of segment:
            # note, frag=1 or frag<1, respectively; don't overshoot
            # note, or frag=nan if already complete
            frag = np.minimum(frag, np.array(1.))
            # reduce segment length and coordinates
            segment.length *= frag
            segment.xxx *= frag
            segment.zzz *= frag
            # reduce traveltime accordingly
            segment.time *= frag
            # return
            return segment, frag

        def _add(segment=None):
            """
            Add segment to the entire path (called front historically)-

            Parameters
            ----------
            segment : Segment
                properties of the ray in a segment

            Returns
            -------
            none

            """
            # add segment distance to total coordinates
            self.xxx += segment.xxx
            self.zzz += segment.zzz
            # add traveltime along segment to total traveltime
            self.time += segment.time

        def _edge(cntl=None):
            """
            Flag indices for which the ray has left graphics window.

            Parameters
            ----------
            cntl : Control
                parameters controlling the simulation

            Returns
            -------
            cntl : Control
                modified parameters controlling the simulation

            """
            # remove all wavefront points above surface
            cntl.done[self.zzz < GRAPHICS['zmin']] = True
            cntl.done[self.zzz < -1 * FACETOL] = True
            # remove all wavefronts below graphics window
            cntl.done[self.zzz > GRAPHICS['zmax']] = True
            # remove all wavefronts left of graphics window
            cntl.done[self.xxx < GRAPHICS['xmin']] = True
            # remove all wavefronts right of graphics window
            cntl.done[self.xxx > GRAPHICS['xmax']] = True
            # return
            return cntl

        def _segmentprint(segment=None):
            """
            Print information about the ray within a segment.

            Parameters
            ----------
            segment : SegmentAux
                segment properties

            Returns
            -------
            none

            """
            # check flag
            if SEGMENTPRINT:
                # print header
                print("\ntime spent:   ray length:     velocity:")
                # print traveltime, raypath length, and energy velocity
                output = "{:11.6f}   {:11.6f}   {:11.6f}"
                for iii in range(energy.nos):
                    print(
                        output.format(
                            segment.time[iii], segment.length[iii],
                            segment.length[iii] / segment.time[iii]))

        # initialize segment
        segment = SegmentAux()
        # calculate trig function of energy angle
        sine = np.sin(energy.angle)
        cose = np.cos(energy.angle)
        # calculate next cross point of the ray with the next interface
        segment = _formula(segment=segment, energy=energy, top=top)
        # calculate fraction of ray within segment
        segment, frag = _fraction(cntl=cntl, segment=segment)
        # print segment information
        _segmentprint(segment=segment)
        # flag wavefront points
        cntl.done[frag < 1.] = True
        # plot if RAYPLOT true
        if RAYPLOT:
            # plot rays
            for iii in range(self.nos):
                plt.plot(
                    [self.xxx[iii], self.xxx[iii] + segment.xxx[iii]],
                    [self.zzz[iii], self.zzz[iii] + segment.zzz[iii]],
                    color='blue', dashes=self.dashes)
            # redraw
            plt.draw()
        # add segment to front
        _add(segment=segment)
        # print if RAYPRINT true
        self._rayprint(segment, energy)
        # check edge of graphics
        cntl = _edge(cntl=cntl)
        # return and forget locals xxx, zzz, length, time and frag
        return self, cntl


class Fronts(dict):
    """
    A dict of Front's, one for each element in DEMO.

    """

    # dict subclass allowing to add methods to an otherwise built-in type
    # http://igorsobreira.com/2011/02/06/adding-methods-dynamically-in-python.html
    def __init__(self, cntl=None, source=None):
        """
        List coordinates of wavefronts.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation
        source : Source
            source

        Instances
        ---------
        self{<demo>: <front>}
            a dict of front, one for each demo

        Returns
        -------
        none

        """
        # create individual fronts for each state
        fronts = {
            demo:
                Front(
                    source=source,
                    color=LINECOLOR[cntl.itim], dashes=LINEDASHES[demo])
            for demo in DEMO}
        # inherit
        super().__init__(fronts)   # now initializing self as dict subclass

    def info(self, cntl=None):
        """
        Print wavefront coordinates.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation
        Returns
        -------
        self : Fronts
            report, but unchanged

        """
        # check switch
        if FRONTPRINT:
            # number of digits in nos
            width = int(np.log10(self['original'].nos)) + 1
            # print title
            print('\nwavefront:')
            # print header
            header = ' ' * width          # index
            header += ' ' * 12 + 'x'      # x coordinates
            header += ' ' * 22 + 'z'      # z coordinates
            header += ' ' * 18 + 'time'   # traveltimes
            print(header)
            # format for data output
            output = f"{{:{width}d}}"           # index
            output += "   {:+9.3f}, {:+9.3f}"   # x coordinates
            output += "   {:+9.3f}, {:+9.3f}"   # z coordinates
            output += "    {:5.3f}, {:5.3f}"    # traveltimes
            # loop through all sets of coordinates and traveltimes
            for index in range(self['original'].nos):
                if cntl.done[index]:
                    numbers = (
                        index,
                        float(self['original'].xxx[index]),
                        float(self['stretch'].xxx[index]),
                        float(self['original'].zzz[index]),
                        float(self['stretch'].zzz[index]),
                        float(self['original'].time[index]),
                        float(self['stretch'].time[index]))
                    print(output.format(*numbers))
        # return
        return self


# ### velocity ### velocity ### velocity ### velocity ### velocity ###


class Vel():
    """
    Describe angle, magnitude and components of a velocity.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, nos=None):
        """
        Initialize a velocity over its phase angles.

        Basically, all attributes like angle, components and magnitude are set
        to nos-many numpy.nan's

        Parameters
        ----------
        nos : int
            number of velocities

        Instances
        ---------
        self.name : str
            any name
        self.angle : list of floats or nan
            angle
        self.xxx, self.zzz, self.mag : lists of floats or nan
            horizontal and vertical component, magnitude
        self.nos : int
            number of velocities

        Returns
        -------
        none

        """
        self.name = None                    # name (for identification only)
        self.angle = np.full(nos, np.nan)   # angle
        self.xxx = np.full(nos, np.nan)     # horizontal component
        self.zzz = np.full(nos, np.nan)     # vertical component
        self.mag = np.full(nos, np.nan)     # magnitude
        self.nos = nos                      # no

    def _info(self, title=None, scale=1.):
        """
        Print velocity informations.

        Parameters
        ----------
        title : str
            type of velocity
        scale : float, default 1.
            scalar to apply at all values
        mag : list of float or nan
            magnitude
        xxx : list of float or nan
            horizontal components
        zzz : list of float or nan
            vertical components

        Returns
        -------
        self : Vel
            report, but unchanged

        """
        # print title
        print(title)
        # print header
        header = ' ' + 'angle'
        header += ' ' * 9 + 'abs'
        header += ' ' * 11 + 'x'
        header += ' ' * 12 + 'z'
        print(header)
        # print data
        output = '{:+7.3f},   {:9.3f},   {:9.3f},   {:9.3f}'
        for index in range(self.nos):
            numbers = (
                np.rad2deg(self.angle[index]),
                self.mag[index] * scale,
                self.xxx[index] * scale,
                self.zzz[index] * scale)
            print(output.format(*numbers))
        # return
        return self

    def _comp(self):
        """
        Compute slowness components from magnitude and angle.

        Returns
        -------
        self : Vel
            xxx, zzz : components

        """

        # calculate components
        self.xxx = self.mag * np.sin(self.angle)
        self.zzz = self.mag * np.cos(self.angle)
        # return
        return self


class Phase(Vel):
    """
    Describe a phase velocity.

    """

    # pylint: disable=too-many-instance-attributes

    __slots__ = [
        'vvv0', 'rrr2', 'rrr4', 'tilt',   # phase velocity parameter
        'g',                              # stretch factor
        'angle0', 'angle',                # original / stretched phase angle
        'tsine', 'tsine2',                # sine of the tilted phase angle
        'mag0', 'mag',                    # orig. / stre. phase velocity
        'diffmag',                        # diff phase velocity
        'xxx', 'diffxxx',                 # pure / diff parallel component
        'zzz', 'diffzzz',                 # pure / diff perp. component
        'nos',                            # number angles
        'name',                           # layer name
        'done']                           # complete

    def __init__(self, nos=None):
        """
        Initialize a phase velocity.

        Parameters
        ----------
        nos : int
            number of phase angles

        Returns
        -------
        none

        """
        # inherit with correct length
        super().__init__(nos=nos)
        # for differentials
        self.diffxxx = np.full(nos, np.nan)   # horizontal diff component
        self.diffzzz = np.full(nos, np.nan)   # vertical diff component
        self.diffmag = np.full(nos, np.nan)   # magnitude differential
        # for 3-term velocity characterization
        self.vvv0 = np.nan   # reference phasevelocity
        self.rrr2 = np.nan   # 2nd phase velocity coefficient
        self.rrr4 = np.nan   # 4th phase velocity coefficient
        self.tilt = np.nan   # tilt of symmetry axis (positive downwards)
        # stretch
        self.angle0 = np.full(nos, np.nan)   # unstretched phase angle
        self.mag0 = np.full(nos, np.nan)     # unstretched velocity magnitude
        self.ggg = np.nan                    # stretch factor
        # auxiliary variables
        self.t0sine = None    # sine of the unstretched tiltangle
        self.t0sine2 = None   # squared sine of the unstretched tiltangle

    def _aux(self, cntl=None):
        """
        Computing the sine of the tiltangle.

        sin(unstretched incidence angle - direction * tiltangle), where
        direction is +/- for down-/upwards

        Auxiliary function to undo repetitive computations.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation

        Returns
        -------
        tsine : array of float or nan
            sine of the tiltangle

        """
        tiltangle = self.angle0 - cntl.sign * self.tilt
        # calculate sine of tilted angle
        self.t0sine = np.sin(tiltangle)
        self.t0sine2 = self.t0sine * self.t0sine

    def initpara(self, para=None):
        """
        Update the layer parameters controlling a phase velocity.

        Parameters
        ----------
        para : Para
            parameters controlling phase velocity

        Returns
        -------
        self : Phase
            returns updated attributes

        """
        # update
        for attr in para.__dict__.keys():
            setattr(self, attr, cp(getattr(para, attr)))
        # return
        return self

    def initangle(self, ang=None):
        """
        Initialize a phase velocity with the emission angles of a source.

        Parameters
        ----------
        ang : numpy array of float
            initial phase angles (used to start simulation and Snell's angle)

        Returns
        -------
        self : Phase
            angle0, angle: original and stretched initial angle

        """
        # copy angle
        self.angle0 = cp(ang)   # deepcopy!
        self.angle = cp(ang)
        # return
        return self

    def calc(self, cntl=None):
        """
        Computes phase velocity magnitude and components.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation

        Returns
        -------
        self : Phase
            returns magnitude and components

        """

        # calculate auxiliary sine of the tilted phase angle
        # ### tiltangle = self.angle0 - cntl.sign * self.tilt
        # ### self.tsine = np.sin(tiltangle)
        self._aux(cntl=cntl)
        # calculate absolute velocity
        self._magnitude()   # giving self.mag0
        # calculate new absolute velocity and phase angle
        if self.ggg == 0.:
            self._nostretch()          # giving self.mag and self.angle
        else:
            self._stretch(cntl=cntl)   # giving self.mag and self.angle
        # calculate components
        self._comp()
        # return
        return self

    def diffcalc(self, cntl=None):
        """
        Calculate differential phase velocity.

        Parameters
        ----------
        cntl : Control
            parameters controllling the simulation

        Returns
        -------
        self : Phase
            returns differential phase velocity magnitude and components

        """
        # calculate differential velocity
        # (only stretched one, original not required)
        self._diffstretchmagnitude(cntl=cntl)   # giving self.diffmag
        # calculate components
        self._diffcomp()
        # return
        return self

    def _magnitude(self):
        """
        Calculate a P- or SV-phase velocity in an unstretched TTI medium.

        Note, the phase angle is seen relative to the vertical.

        This function is the most time-consuming one, but optimized.

        Returns
        -------
        none

        """
        # compensate phase angle for tilt
        # ### tiltangle = self.angle0 - cntl.sign * self.tilt
        # calculate velocity
        # ### tmp = np.sin(tiltangle)
        # ### tmp *= tmp -> replaced by self.t0sine2
        # calculate velocity
        self.mag0 = (
            self.vvv0
            *
            np.sqrt(
                1. + (self.rrr2 + self.rrr4 * self.t0sine2) * self.t0sine2))
        # return
        return self

    def _stretch(self, cntl=None):
        """
        Stretch a layer according to paper.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation

        Returns
        -------
        none

        """
        # compensate phase angle for tilt
        tiltangle0 = self.angle0 - cntl.sign * self.tilt
        # ### self.t0sine2 = np.sin(tiltangle0) ** 2
        # stretch according to paper
        self.mag = \
            self.mag0 * (
                np.sqrt(
                    (1 + self.ggg)
                    /
                    (1 + self.ggg * self.t0sine2)))
        # calculate stretch angle
        # (since the tangent has an unwanted pi-periodicity, the stretched
        # angle must be moved back into the right quadrant)
        tiltangle = (
            np.arctan(
                np.sqrt(1. + self.ggg) * np.tan(tiltangle0)))
        tiltangle = np.sign(tiltangle0) * np.abs(tiltangle)
        self.angle = tiltangle + cntl.sign * self.tilt
        # return
        return self

    def _nostretch(self):
        """
        Copy, but don't stretch a layer.

        Returns
        -------
        none

        """
        # copy magnitude into "stretched" magnitude
        self.mag = cp(self.mag0)   # deepcopy!
        # copy angle into stretched angle
        self.angle = cp(self.angle0)   # deepcopy!
        # return
        return self

    def _diffstretchmagnitude(self, cntl=None):
        """
        Differentiate a stretch term.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation

        Returns
        -------
        self : Phase
            diffmag: magnitude of differential phase velocity

        """
        # compensate phase angle for tilt
        tiltangle = self.angle0 - cntl.sign * self.tilt
        # copy phase velocity and differentiate stretch factor
        part1 = cp(self.mag0)
        part1 *= -0.5 * self.ggg * np.sin(2 * tiltangle)
        part1 /= np.sqrt(1. + self.ggg * np.sin(tiltangle) ** 2)
        # copy and differentiate original phase velocity
        part2 = self.vvv0 ** 2 / self.mag0
        part2 *= 0.5 * np.sin(2 * tiltangle)
        part2 *= self.rrr2 + 2 * self.rrr4 * np.sin(tiltangle) ** 2
        part2 *= np.sqrt(1. + self.ggg * np.sin(tiltangle) ** 2)
        # add together
        self.diffmag = part1 + part2
        # return
        return self

    def _diffcomp(self):
        """
        Compute components from magnitude and angle.

        Not needed in production mode.

        Returns
        -------
        self : Phase
            diffxxx, diffzzz: components

        """
        # calculate components
        self.diffxxx = self.diffmag * np.sin(self.angle)
        self.diffzzz = self.diffmag * np.cos(self.angle)
        # return
        return self

    def search(self, cntl=None, slow=None, base=None):
        """
        Searching for Snell's angle.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation
        slow : Slow
            slowness
        base : str
            name of top interface (in computational sense); note, top / base
            are the geological base / top for downward propagation, but the
            geological base / top for upward propagation

        Raises
        ------
        AssertionError
            various reasons for failing to compute Snell's angle

        Returns
        -------
        none

        """

        # check monotenous increase
        def _monotoneous():
            # differentiate angles
            tmp = np.diff(self.angle)
            # check constant differential angles
            if np.any(tmp == 0.):
                output = "\nconstant Snell's angles:"
                raise AssertionError(output)
            # check decreasing differential angles
            if np.any(tmp < 0.):
                where = np.where(tmp < 0.)
                output = "\nnot monotonously increasing Snell's angles"
                output += "\npossibly a triplication in the phase front"
                output += "\n" + str(np.rad2deg(self.angle[where]))
                raise AssertionError(output)

        # invert stretched angle to original angle:
        # note, eq 2b of paper inverted
        def _inversion(angle=None, cntl=None):
            """
            Calculating the incidence angle before stretch.

            Note, the search algorithm for Snell's angle minimizes
            slow[x] phase - sine, but that's the sine of the stretched
            incidence angle.

            Parameters
            ----------
            angle : list of float or nan
                incidence angle
            cntl : Control
                parameters controlling the simulation

            Returns
            -------
            angle0 : list of float or nan
                non-stretched incidence angle

            """
            # invert
            tiltangle = angle - cntl.sign * self.tilt
            sine = np.sin(tiltangle)
            fac = np.sqrt(1. + self.ggg * (1. - sine * sine))
            tiltangle0 = np.arcsin(sine / fac)
            angle0 = tiltangle0 + cntl.sign * self.tilt
            # return
            return angle0

        # initialize auxiliary variable
        aux = SearchAux(nos=slow.nos)
        # initiate zero-offset incidence (or close to):
        # that is, set initial angle perpendicular to the interface, spread
        # over array, and set phase angle
        self.initangle(
            ang=np.full_like(slow.xxx, -1. * cntl.sign * base.dip))
        while aux.maxdsine > MAXDSINE:
            # firstly, calculate phase velocity with possibly updated layer
            # parameter+stretch for normal incidence; later, recalculate phase
            # velocity with updated phase angle
            self.calc(cntl=cntl)   # -> self.mag
            # rotate angle coordinate system relative to base
            dipangle = self.angle + cntl.sign * base.dip
            # define sin(angle)
            aux.sine = np.sin(dipangle)
            # difference p*v - sin(angle):
            aux.dsine = slow.xxx * self.mag - aux.sine
            # check with previous result
            # note, at the lower boundary (=-1) and further decreasing or
            # conversely does not give real incidence angle
            nan = \
                np.logical_or(
                    np.logical_and(aux.sine == -1., np.sign(aux.dsine) == -1.),
                    np.logical_and(aux.sine == +1., np.sign(aux.dsine) == +1.))
            aux.sine[nan] = np.nan
            aux.dsine[nan] = np.nan
            # update sin(angle), still relative to base
            aux.sine += aux.scl * aux.dsine
            # limit to interval [-1-eps, +1+eps]
            # note, limit the updated angle just outside critical angle and
            # allow the search to recover with a decreased scl
            aux.sine = np.minimum(+1., np.maximum(-1., aux.sine))
            # reduce sine increment when hitting -/+1 barrier
            # nan above if not recovering from -/+1 barrier 2 times in a row
            aux.scl[np.abs(aux.sine) == 1.] *= SCLFAC   # move slower from now
            # convert to angle
            dipangle = np.arcsin(aux.sine)
            # rotate angle coordinate system back
            self.angle = dipangle - cntl.sign * base.dip
            # convert angle to original state
            # invert eq 2b of paper
            self.angle0 = \
                cp(self.angle) if self.ggg == 0. \
                else _inversion(angle=self.angle, cntl=cntl)
            # if all nan
            if np.all(np.isnan(aux.sine)):
                break
            # get maximum remaining error in sine,
            # max(abs(delta(sine))) where -1 < sine < +1
            try:
                aux.maxdsine = \
                    np.nanmax(np.abs(aux.dsine[np.abs(aux.sine) != 1.0]))
            except RuntimeWarning:
                # ignore if all sine = 1.0 or np.nan
                # note, sine might bounce back from +/-1., otherwise maxiterat
                pass
            # emergency abortion
            aux.iteration()
        # check sanity
        _monotoneous()
        # flag
        cntl.done[np.isnan(aux.sine)] = True
        # return
        return cntl

    def info(self):
        """
        Initiate printing phase velocity.

        Returns
        -------
        self : Phase
            report, but unchanged

        """
        if PHASEPRINT:
            # construct title
            title = f"\nphase velocities in {self.name}:"
            self._info(title=title)
        return self

    def diffinfo(self):
        """
        Initiate printing differential phase velocity.

        Obviously not needed in production mode.

        Returns
        -------
        self : Phase
            report, but unchanged

        """
        if DIFFPHASEPRINT:
            # construct title
            title = f"\ndifferential phase velocities in {self.name}:"
            self._info(title=title)
        # return
        return self

    def diffcheck(self):
        """
        Compare numerical and analytical differential phase velocity.

        Needed for verification of the code only. Not in production mode.

        Returns
        -------
        self : Phase
            report, but unchanged

        """
        if DIFFPHASECHECK:
            # calculate the numerical differential
            grad = np.full_like(self.mag, np.nan)
            todos = np.logical_not(np.isnan(self.mag))
            grad[todos] = np.gradient(self.mag[todos], self.angle[todos])
            # print title
            title = '\ncheck of differential phase velocities'
            print(title)
            # print header
            header = ' ' + 'angle'
            header += ' ' * 6 + 'analytic'
            header += ' ' * 7 + 'numeric'
            print(header)
            # print data
            output = '{:+7.3f},   {:+11.6f},   {:+11.6f}'
            # loop through all data except those containing nan
            # (there got to be a faster way)
            for index in range(self.nos):
                if todos[index]:
                    numbers = (
                        float(np.rad2deg(self.angle[index])),
                        float(self.diffmag[index]),
                        float(grad[index]))
                    print(output.format(*numbers))
        # return
        return self


class Energy(Vel):
    """
    Calculate energy velocity.

    """

    def __init__(self, nos=None):
        # inherit
        super().__init__(nos=nos)

    def calc(self, cntl=None, phase=None):
        """
        Calculate energy velocity magnitude, components and angle.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation
        phase : Phase
            phase velocity

        Instance
        --------
        self
            mag: magnitude
            xxx, zzz: components
            angle: angle
            name: name of layer

        Returns
        -------
        self : Energy
            see above

        """
        # compute
        with np.errstate(invalid='raise', divide='raise', over='raise'):
            try:
                # shorts
                sine = np.sin(phase.angle)
                cose = np.cos(phase.angle)
                # calculate magnitude
                self.mag = \
                    np.sqrt(
                        phase.mag * phase.mag + phase.diffmag * phase.diffmag)
                # calculate lateral component
                self.xxx = phase.mag * sine + phase.diffmag * cose
                # calculate vertical component
                self.zzz = phase.mag * cose - phase.diffmag * sine
                self.zzz *= cntl.sign
                # calculate angle of incidence
                self.angle = np.arctan2(self.xxx, self.zzz)
            # exits
            except FloatingPointError as unexpect1:
                raise AssertionError(
                    'bug in Energy.calc: floating point!') from unexpect1
            except ZeroDivisionError as unexpect2:   # how does that happen?
                raise AssertionError(
                    'bug in Energy.calc: zero division!') from unexpect2
            except OverflowError as unexpect3:
                raise AssertionError(
                    'bug in Energy.calc: overflow!') from unexpect3
        # check
        assert \
            np.all(np.isnan(self.angle) == cntl.done), \
            "Energy.calc: additional nan computed!"
        # name
        self.name = cp(phase.name)
        # return
        return self

    def info(self):
        """
        Print energy velocity angle, magnitude and components.

        Returns
        -------
        self : Energy
            report, but unchanged

        """
        # print info
        if ENERGYPRINT:
            # construct title
            title = f"\nenergy velocities in {self.name}"
            self._info(title=title)
        # return
        return self


class Slow(Vel):
    """
    Describe magnitude, components of a slowness.

    """

    __slots__ = ['angle', 'mag', 'xxx', 'zzz', 'nos', 'name']

    def __init__(self, nos=None):
        # inherit
        super().__init__(nos=nos)

    def calc(self, cntl=None, top=None, phase=None):
        """
        Calculate slowness component parallel to an interface.

        Parameters
        ----------
        cntl : Control
            parameters controlling the simulation
        top : str
            name of top interface (in computational sense); note, top is the
            geological base for downward propagation, but the geological top
            for upward propagation
        phase : Phase
            phase velocity

        Returns
        -------
        self : Slow
            angle: incidence angle on interface
            mag: magnitude
            xxx: horizontal slowness
            name: name of interface impinging on
            nos: number of slownesses

        """
        # calculate slowness magnitude
        self.mag = 1. / phase.mag
        self.mag[cntl.done] = np.nan
        # check angle of incidence
        self.angle = phase.angle + cntl.sign * top.dip
        self.angle[cntl.done] = np.nan
        # check incidence angle
        delete = (
            np.logical_or(
                self.angle < -1. * np.pi / 2.,
                self.angle > +1. * np.pi / 2.))
        self.angle[delete] = np.nan
        self.mag[delete] = np.nan
        # calculate slownes
        self.xxx = np.sin(self.angle) * self.mag
        # number of slownesses
        self.nos = phase.nos
        # name
        self.name = top.name
        # return
        return self

    def info(self):
        """
        Print slowness, that is angle, magnitude and horizontal slowness.

        Returns
        -------
        self : Slow
            report, but unchanged

        """
        # print info
        if SLOWPRINT:
            # construct title
            title = f"\n10^6 x slowness at base {self.name}"
            self._info(title=title, scale=1.e6)
        # return
        return self


# ### graphics ### graphics  ### graphics ### graphics ### graphics ###


class Graph():
    """
    Prepare a graphics of snapshots of wavefronts and interfaces.

    """

    def __init__(self, graphics=None):
        """
        Initialize the graphic, that is figure and axes.

        Note, ipt.run_line_magic throws a warning, but I don't know how to set
        'inline' with mpl.use or plt.switch_backend. Using either with the
        argument 'module://matplotlib_inline.backend_inline' creates a canvas,
        but also ends with the canvas.

        Parameters
        ----------
        graphics : GRAPHICS
            graphics parameters

        Variables
        ----------
        modus : char
            plot inline or external in a qt window
            'inline' : plot inline; default
            'qt' : plot external in a qt window

        Returns
        -------
        none

        """
        # close all figures
        plt.close('all')
        # suppress
        with warnings.catch_warnings():   # suppression of warnings
            warnings.simplefilter("ignore")
            # set canvas controller
            if graphics['control'] == 'ipython':
                # note,  my profiler cannot find run_line_magic, but continues
                # without graphics
                assert \
                    graphics['modus'] in ['inline', 'qt5'],\
                    "Graphics.__init__: unknown graphics mode"
                get_ipython().run_line_magic('matplotlib', graphics['modus'])
            if graphics['control'] == 'matplotlib':
                plt.switch_backend(graphics['modus'])
            # figure
            self.fig = plt.figure(constrained_layout=True)
        # create axes
        self.axes = self.fig.add_subplot(111)
        # plot display axes
        self._axes()
        # show current figure
        plt.draw()

    def source(self, source=None):
        """
        Set up the graphics window and plot the source.

        Parameters
        ----------
        source : Source
            source

        Returns
        -------
        self

        """
        # check switch for plotting source
        if SOURCEPLOT:
            # plot sources
            self._source(source=source)
        # return
        return self

    def stacks(self, stacks=None, source=None, cntl=None):
        """
        Set up the graphics window and plot source and interfaces.

        Parameters
        ----------
        stacks : Stacks
            original and stretched stacks of layers
        source : Source
            source
        cntl : Control
            parameters controlling the simulation

        Returns
        -------
        self

        """
        # check switch for plotting interfaces
        if FACEPLOT:
            for cntl.demo in DEMO:
                # plot interfaces
                self._stack(stack=stacks[cntl.demo], source=source, cntl=cntl)
        # return
        return self   # don't return cntl

    def front(self, cntl=None, front=None):
        """
        Plot individual wavefronts one at a time.


        Parameters
        ----------
        front : Front
            wavefront

        Returns
        -------
        self

        """
        # plot wavefronts
        if FRONTPLOT:
            self._front(cntl=cntl, front=front)
        # return
        return self

    def _stack(self, stack=None, source=None, cntl=None):
        """
        Plot the interfaces at/through which a wave is reflected/transmitted.

        Parameters
        ----------
        stack : Stack
            original or stretched stack of layers
        source : Source
            source
        cntl : Control
            parameters controlling the simulation

        Returns
        -------
        none

        """
        # plot surface
        if cntl.demo == 'original':   # only once
            self.axes.plot(
                [GRAPHICS['xmin'], GRAPHICS['xmax']], [source.zzz, source.zzz],
                color='black', dashes=FACEDASHES['original'])
        # loop over all interfaces
        for layer in stack:
            # z coord on left window side
            zleft = (
                layer.depth
                +
                GRAPHICS['xmin'] * np.tan(layer.dip))
            # z coord on right window side
            zright = (
                layer.depth
                +
                GRAPHICS['xmax'] * np.tan(layer.dip))
            # plot
            self.axes.plot(
                [GRAPHICS['xmin'], GRAPHICS['xmax']],
                [zleft, zright], color='black', dashes=FACEDASHES[cntl.demo])
        # show
        plt.draw()

    def _source(self, source=None):
        """
        Plot the source point.

        Parameters
        ----------
        source : Source
            source

        Returns
        -------
        none

        """
        # plot
        self.axes.plot(source.xxx, source.zzz, '*', color='red')
        # show
        plt.draw()

    def _front(self, cntl=None, front=None):
        """
        Plot a wavefront.

        Parameters
        ----------
        front : Front
            wavefront

        Returns
        -------
        none

        """
        # mask all elements already completed, then plot
        # ### self.axes.plot(
        # ###    np.ma.masked_where(np.logical_not(cntl.done), front.xxx),
        # ###    np.ma.masked_where(np.logical_not(cntl.done), front.zzz),
        # ###    color=front.color, dashes=front.dashes)
        front.xxx[np.logical_not(cntl.done)] = np.nan
        front.zzz[np.logical_not(cntl.done)] = np.nan
        self.axes.plot(
            front.xxx, front.zzz,
            color=front.color, dashes=front.dashes)
        # show
        plt.draw()

    def _axes(self):
        """
        Plot display axes.

        Returns
        -------
        none

        """
        # set window limits
        self.axes.set_xlim([GRAPHICS['xmin'], GRAPHICS['xmax']])
        self.axes.set_ylim([GRAPHICS['zmin'], GRAPHICS['zmax']])
        # inverse y axis
        # note, positive is traditionally downwards
        self.axes.set_ylim(self.axes.get_ylim()[::-1])
        # square
        self.axes.set_aspect('equal')
        # show
        plt.draw()

    def show(self, graphics=None):
        """
        Show the final figure.

        Parameters
        ----------
        graphics : GRAPHICS
            graphics parameters

        """
        # call show
        if "block" in graphics:
            plt.show(block=graphics['block'])
        else:
            plt.show()

    def paper(self):
        """
        Save figure into a file for later publication.

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
            command += PUBLICEPS
            # run above ghostscript command and store in result
            result = subprocess.run(command, check=True, capture_output=True)
            # extract bounding box, extract high-resolution bounding box
            result = result.stderr.decode("utf-8")
            result = result.split("\n")
            print(f"\nreplace bounding box in {PUBLICEPS}")
            print(result[1])
            # extract width and height of image
            result = result[1].split()
            width = (float(result[3]) - float(result[1])) / 72
            height = (float(result[4]) - float(result[2])) / 72
            # return width and height
            return width, height

        def _publicwin(step=0.1, errmax=1.e-3):
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
            if PUBLICWIN:
                # initialize
                width = PUBLICWIDTH   # set above when initializing graphics
                # extract old width of figure; discard height
                oldout, _ = _getsize()
                # loop
                error = sys.float_info.max
                while np.abs(error) > errmax:
                    # try another input width
                    # note, input width not identical with output width!
                    width += step
                    self.fig.set_figwidth(width)
                    plt.savefig(
                        PUBLICEPS, format='eps', bbox_inches='tight',
                        pad_inches=0, transparent=True)
                    # extract new width of figure
                    newout, _ = _getsize()
                    # slope of output width over input width
                    slope = (newout - oldout) / np.abs(step)
                    # current error
                    # note, desired PUBLICWIDTH - current output width
                    error = PUBLICWIDTH - newout
                    # preserve old current output width
                    oldout = newout
                    # calculate next input width
                    step = error / slope
                # final output
                self.fig.set_figwidth(width)
                plt.savefig(
                    PUBLICEPS, format='eps', bbox_inches='tight',
                    pad_inches=0, transparent=True)

        def _publiceps():
            """
            Write figure to a file in EPS format.

            Returns
            -------
            none

            """
            # check switch
            if PUBLICEPS:
                # save figure in EPS format
                with warnings.catch_warnings():   # suppression of warnings
                    warnings.simplefilter("ignore")
                    plt.savefig(
                        PUBLICEPS, format='eps', bbox_inches='tight',
                        pad_inches=0, transparent=True)
                # correct bounding box
                # note, switch according to system platform; here, Windows only
                platform = {'Windows': _publicwin()}
                _ = platform[pf.system()]

        def _publicpng():
            """
            Write figure to a file in PNG format.

            Returns
            -------
            none

            """
            if PUBLICPNG:
                plt.savefig(
                    PUBLICPNG, format='png', dpi=1200., pad_inches=0,
                    transparent=True)

        # check publication check
        if PUBLIC:
            # remove ticks
            self.axes.get_xaxis().set_ticks([])
            self.axes.get_yaxis().set_ticks([])
            # remove frame
            self.axes.spines['top'].set_visible(False)
            self.axes.spines['right'].set_visible(False)
            self.axes.spines['bottom'].set_visible(False)
            self.axes.spines['left'].set_visible(False)
            # set desired size
            self.fig.set_figwidth(PUBLICWIDTH)
            self.fig.set_figheight(PUBLICHEIGHT)
            # save eps file
            _publiceps()
            # save png file
            _publicpng()


# ### Geometry ### Geometry ### Geometry ### Geometry ### Geometry ### Geometry


class Vector():
    """
    Define a vector in the vertical plane.

    """

    def __init__(self, foot=None, head=None):
        """
        Initialize a vector.

        Parameters
        ----------
        foot : Point
            foot point of vector
        head : Point
            head point of vector

        Instance
        --------
        foot : Point
            foot point of vector
        head : Point
            head point of vector
        ddd : float
            length of vector

        Returns
        -------
        None

        """
        # initialize vector with foot and header
        self.foot = cp(foot)
        self.head = cp(head)
        # compute length of vector
        self.ddd = \
            np.sqrt(
                (self.head.xxx - self.foot.xxx) ** 2
                +
                (self.head.zzz - self.foot.zzz) ** 2)

    def stretch(self, fac=None):
        """
        Stretch a vector.

        Parameters
        ----------
        fac : float
            stretch factor

        Returns
        -------
        self : Vector
            vector with stretched head point and new length

        """
        # calculate new length
        self.ddd *= fac
        # move head point
        self.head.xxx = self.foot.xxx + fac * (self.head.xxx - self.foot.xxx)
        self.head.zzz = self.foot.zzz + fac * (self.head.zzz - self.foot.zzz)
        # return
        return self

    def addstretch(self, fac=None):
        """
        Stretch a vector and substract the original part of that vector.

        Parameters
        ----------
        fac : float
            stretch factor

        Returns
        -------
        self : Vector
            vector with stretched head point, original head point as base point
            and new length

        """
        # save old head point = future foot point
        xxx = self.head.xxx
        zzz = self.head.zzz
        # move head point
        self.head.xxx = self.foot.xxx + fac * (self.head.xxx - self.foot.xxx)
        self.head.zzz = self.foot.zzz + fac * (self.head.zzz - self.foot.zzz)
        # assign new foot point
        self.foot.xxx = xxx
        self.foot.zzz = zzz
        # new length
        self.ddd = \
            np.sqrt(
                (self.head.xxx - self.foot.xxx) ** 2
                +
                (self.head.zzz - self.foot.zzz) ** 2)
        # return
        return self

    def rotate(self, angle=None):
        """
        Rotate a vector.

        Parameters
        ----------
        angle : float
            rotation angle in radiant

        Returns
        -------
        self : Vector
            rotated vector with rotated head point

        """
        # shortcut
        sine = np.sin(angle)
        cose = np.cos(angle)
        # calculate distance between head and foot point
        xxx = self.head.xxx - self.foot.xxx
        zzz = self.head.zzz - self.foot.zzz
        # calculate rotated head point
        self.head.xxx = self.foot.xxx + (cose * xxx - sine * zzz)
        self.head.zzz = self.foot.zzz + (sine * xxx + cose * zzz)
        return self

    def move(self, fro=None, too=None):
        """
        Move vector into another position described by two points.

        new vector = vector + (too - from)

        Parameters
        ----------
        from, too : Point
            new foot point

        Returns
        -------
        self : Vector
            foot and head moved

        """
        # set step
        delx = too.xxx - fro.xxx
        delz = too.zzz - fro.zzz
        # get new foot point
        self.foot.xxx += delx
        self.foot.zzz += delz
        # get nead head point
        self.head.xxx += delx
        self.head.zzz += delz
        # return
        return self


class Point():
    """
    Define a point in the vertical plane.

    """

    def __init__(self, xxx0=None, zzz0=None):
        """
        Initialize a point.

        Parameters
        ----------
        xxx0 : float
            horizontal coordinate of a point
        zzz0 : float
            vertical (downward) coordinate of a point

        Instance
        --------
        self : Point
            xxx : float
                horizontal coordinate of a point
            zzz : float
                vertical (downward) coordinate of a point

        Returns
        -------
        none

        """
        self.xxx = xxx0
        self.zzz = zzz0

    def add(self, point1=None, point2=None):
        """
        Add coordinates, which typically done to undo a coordinate shift.

        Parameters
        ----------
        point1 : Point
            origin of one coordinate system
        point2 : Point
            coordinates in the other coordinate system

        Returns
        -------
        point : Point
            shifted coordinates

        """
        # calculate
        point = Point(xxx0=point1.xxx+point2.xxx, zzz0=point1.zzz+point2.zzz)
        # return
        return point

    def cross(self, line1=None, line2=None):
        """
        Calculate the cross point of two lines.

        Parameters
        ----------
        line1 : Line
            one of the lines
        line2 : Line
            the other line

        Returns
        -------
        self : Point
            a point with the coordinates of the crossing

        """
        # calculate cross point
        self.xxx = -1 * (line2.bbb - line1.bbb) / (line2.mmm - line1.mmm)
        self.zzz = line1.mmm * self.xxx + line1.bbb
        # return
        return self

    def printout(self, title=""):
        """
        Print the coordinates of a point.

        Parameters
        ----------
        title : str
            description of cross point

        Returns
        -------
        self : Point
            the same point

        """
        if CROSSPRINT:
            print('\n' + title)
            output = 'x={:f}, z={:f}'
            print(output.format(self.xxx, self.zzz))
        # return
        return self


class Line():
    """
    Calculate new layer thickness based on the geometry of cutting lines.

    Line equation: a x + b y + c = 0

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, dip=None, point=None):
        """
        Initialize a line.

        Parameters
        ----------
        dip : float
            dip angle of line
        point : Point
            coordinates of a point along the line

        Instance
        --------
        self : Line
            phi : float
                dip angle of line
            mmm : float
                slope of line or tan(phi)
            bbb : float
                constant = intercept with y axis for x=0

        Returns
        -------
        none

        """
        # initialize
        self.dip = dip
        self.mmm = np.tan(self.dip)
        self.bbb = point.zzz - self.mmm * point.xxx


# ### search ### search ### search ### search ### search ### search ### search


class SearchAux():
    """
    Define auxiliary variables in the search for Snell's angle.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, nos=None):
        """
        Initialize auxiliary variables used in the search for Snell's angle.

        Parameters
        ----------
        nos : int
            size of vector

        Returns
        -------
        none

        """
        self.scl = np.full(shape=nos, fill_value=1., dtype=float)
        self.iterat = 0
        self.sine = np.full(shape=nos, fill_value=np.nan, dtype=float)
        self.dsine = np.full(shape=nos, fill_value=np.nan, dtype=float)
        self.old_dsine = np.full(shape=nos, fill_value=np.nan, dtype=float)
        self.maxdsine = sys.float_info.max

    def iteration(self):
        """
        Check iteration limit with emergency break.

        Raises
        ------
        AssertionError
            emergency exit if iterat > MAXITERAT

        Returns
        -------
        aux : SearchAux
            iterat : int
                incremented iteration index

        """
        # increment
        self.iterat += 1
        # check iteration limit
        if self.iterat > MAXITERAT:
            output = "\ninfinite iteration in search for Snell's angle"
            output += "\nsine increment in search: {:8.6f}"
            output += "\nreduce scale factor SCLFAC: {:8.6f} ({:8.6f})"
            output += "\nincrease max number of iteration MAXITERAT: {:9d}"
            string = [self.maxdsine, SCLFAC, np.max(self.scl), MAXITERAT]
            raise AssertionError(output.format(*string))
        # return
        return self

# ### main ### main ### main ### main ### main ### main ### main ### main ###


def main():
    """
    Demonstrate the concept of depth - velocity - anisotropy ambiguity.

    Returns
    -------
    none

    """

    # pylint: disable=too-many-locals

    # set up control, that is all parameters controlling the simulation:
    # the source is assumed to be located at the surface; so, initial
    # propagation is downwards
    cntl = Control().direction(direct='down')
    # set up the graphics
    graph = Graph(graphics=GRAPHICS)
    # set up the source
    source = Source(source=cp(SOURCE)).info()
    graph.source(source=source)
    # set up the layer stack
    stacks = Stacks(stack=cp(STACK), graph=graph).info()
    # set up graphics and plot interfaces and sources
    graph.stacks(stacks=stacks, source=source, cntl=cntl)
    # set up travelpaths
    paths = Paths(path=cp(PATH), surface=cp(SURFACE), stacks=cp(stacks)).info()
    # loop through all traveltimes
    for cntl.itim, cntl.time in enumerate(TRAVELTIMES):
        # set up a list of wavefronts
        fronts = Fronts(cntl=cntl, source=cp(source))
        # loop through variations (original, stretch and possibly others)
        for demo in DEMO:
            cntl.\
                demonstration(demo=cp(demo)).\
                doing(nos=source.nos)
            # short for paths[demo]
            path = paths[cntl.demo]
            # short for wavefront[demo]
            front = fronts[cntl.demo]
            # loop through each segment of path
            slow = None   # dummy value to please linting
            for cntl.ipat, para, base, top in path.next(surface=cp(SURFACE)):
                # report current segment
                cntl.\
                    direction(direct=path.direct[cntl.ipat]).\
                    report(base=base, top=top)
                # set up phase velocity with layer parameters
                phase = \
                    Phase(nos=source.nos).\
                    initpara(para=cp(para))
                # check status of wavefront
                if not np.all(cntl.done):
                    # for first=top layer only
                    if cntl.ipat == 0:
                        # set up phase velocity with source emission angles
                        phase.initangle(ang=source.angle)
                    # for second and lower layers
                    else:
                        cntl = \
                            phase.search(
                                cntl=cntl, slow=cp(slow), base=base)
                        # note, slow is defined for all index > 0, that is
                        # after having hit first interface
                    # do/redo and report phase velocity
                    phase.calc(cntl=cntl).info()
                    # calculate differential phase velocity and check
                    phase.diffcalc(cntl=cntl).diffinfo().diffcheck()
                    # calculate energy velocity
                    energy = \
                        Energy(nos=source.nos).\
                        calc(cntl=cntl, phase=cp(phase)).\
                        info()
                    # propagate wavefront
                    front, cntl = \
                        front.crosspoint(
                            cntl=cntl, top=top, energy=cp(energy))
                    # calculate parallel slowness
                    slow = \
                        Slow(nos=source.nos).\
                        calc(cntl=cntl, top=top, phase=cp(phase)).\
                        info()
                # prepare graphics
                graph.front(cntl=cntl, front=cp(front))
        # print wavefront
        fronts.info(cntl=cntl)
    # print out
    graph.show(graphics=GRAPHICS)
    graph.paper()


def entry():
    """
    Set up warning messages and call main function.

    Note, can be omitted.

    Raises
    ------
    AssertionError:
        convert Python messages into errors
        issue all numpy warnings

    Returns
    -------
    none

    """
    # turn warnings into errors
    warnings.filterwarnings("error")
    # raise all numpy warnings
    np.seterr(all='raise')
    # call main, the entry function
    try:
        main()
    except RuntimeWarning as runtime:
        print("entry: which runtime error???")
        raise AssertionError(runtime) from runtime
    except bdb.BdbQuit:   # some debugging issue
        pass
    except Exception as exception:
        print("entry: which other error???")
        raise AssertionError(exception) from exception


###############################################################################


if __name__ == "__main__":
    if DEBUG:
        # set warnings and call main function
        entry()
    else:
        # alternatively, call main function directly
        main()
