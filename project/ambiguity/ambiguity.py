# -*- coding: utf-8 -*-
"""

@author: bjorn.rommel@seisrock.com
"""


# for ease of submission
# pylint: disable=too-many-lines


# libraries to be imported
from copy import deepcopy as cp
import numpy as np
import matplotlib.pyplot as plt


# ### change the "user-defined parameters" below as you see fit ###


# layer parameters
# <name of layer> = {
#   'name': any, but a unique name
#   'vvv0': reference velocity
#   'rrr2': 2. phase-velocity coefficient
#   'rrr4': 4. phase-velocity coefficient
#   'tilt': tilt of symmetry axis
#   'depth': depth of a reflector measured along the vertical below the source
#   'dip': dip of a reflector, with positive for dipping downwards
#   'ggg': stretch factor
# units of times and distances are arbitrary, but must be applied consistently
# units of angles are degree
OVERBURDEN = {
    'name': 'overburden',
    'key': 'generic',
    'vvv0': 1000.,
    'rrr2': 0.2,
    'rrr4': 0.3,
    'thick': 1000.,
    'dip': 20.,
    'ggg': 0.4}
ROCK = {
    'name': 'rock',
    'key': 'generic',
    'vvv0': 1200.,
    'rrr2': -0.1,
    'rrr4': 0.2,
    'thick': 1500.,
    'dip': 10.,
    'ggg': 0.1}
TARGET = {
    'name': 'target',
    'key': 'generic',
    'vvv0': 1500.,
    'rrr2': 0.2,
    'rrr4': 0.1,
    'thick': 1000.,
    'dip': 15.,
    'ggg': 0.1}


# model
# STACK = [<1'st layer>, <2'nd layer>, ..., <n'th layer>, where all
# <i'th layer> must be a <name of layer> from above and given in top-down order
STACK = [OVERBURDEN, ROCK, TARGET]


# source radiation angles
# SOURCE = {'first': <first>, 'last': <last>, 'nos': <nos>}, where
# <first> denotes a first angle,
# <last> a last angle, and
# <nos> an integer number of angles
SOURCE = {
    'first': -90,
    'last': +90,
    'nos': 3001}


# travelpath
# PATH = [<name of 1'st layer>, ..., <name of n'th layer>];
# note, SURFACE = depth of source will be added automatically at the end
PATH = ['overburden', 'rock', 'target', 'target', 'rock', 'overburden']
PATH = ['overburden', 'rock', 'rock', 'overburden']
#PATH = ['overburden', 'overburden']


# traveltime
# TRAVELTIMES = [<1'st traveltime>, ..., <n'th traveltime], where wavefronts
# plotted at these times
TRAVELTIMES = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
TRAVELTIMES = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
# TRAVELTIMES = [1.0, 2.0, 3.0]


# graphics window
GRAPHICS = {'xmin': -3000., 'xmax': 5000., 'zmin': -100., 'zmax': 6000.}
# (zmin=-4 just draws the surface on my screen, but zmin=0 won't)


# interface properties
FACEDASHES = {'org': [1, 0], 'stretch': [20, 5]}


# line properties
LINECOLOR = ['b', 'g', 'r', 'c', 'm', 'y', 'b', 'g', 'r', 'c', 'm', 'y']
LINEDASHES = {'org': [1, 0], 'stretch': [10, 1]}
assert \
    len(LINECOLOR) >= len(TRAVELTIMES), \
    'not enough COLOR\'s for all TRAVELTIMES'


# print outs
ANGLEPRINT = False       # emission angles of the source
STACKPRINT = False       # depth / dip of the layer stack
PATHPRINT = False        # layer(s) and their computational top(s) along travelpath
FRONTPRINT = False       # coordinates of the wavefront(s)
PHASEPRINT = False       # phase velocity
DIFFPHASEPRINT = False   # differential phase velocity
DIFFPHASECHECK = False    # check analytic versus numerical diff phase vel
ENERGYPRINT = False      # energy velocity
SLOWPRINT = False        # slowness
PLOTFACES = True         # plot stretched / unstretched interfaces
PLOTSOURCE = True        # plot source
PLOTFRONTS = True        # plot wavefronts
DEBUG = False            # T/F switch debug on / graphics off and vice versa
DEMOPRINT = True         # T/F for printing ray info
DEMOPLOT = False         # T/F for ray
                         # (best with 1 huge traveltime and very few angles)


# ### hard-wired parameters ### hard-wired parameters ### hard-wired parameters


# characterize media
# org: the original medium
# new: the newly stretched medium
DEMO = ['org', 'stretch']


# SOURCE.update({
#   'xxx': origin of coordinate system
#   'zzz': origin of coordinate system
#   'time': source time
#   'g': stretch factor in source layer
# (For now, the source is located at the surface and, hence, emit only
# downwards. To treat a buried source, split the source layer above and below
# the source level, and propagate accordingly.)
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


# accuracy of the interface distance
FACETOL = +1.e-10


# accuracy of the phase angle
MAXDSINE = 1.e-8
SCLFAC = 0.1
MAXITERAT = 10000


# some insane large distance
LARGEDISTANCE = 1234567890


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


# multiplicator depending on direction of propagation
DIRECT = {'down': +1, 'up': -1}


# Python helper to recognize None as a type
# https://stackoverflow.com/questions/40553285/determining-a-variables-type-is-nonetype-in-python/40553322#40553322
NONETYPE = type(None)


# ### parameter ### parameter ### parameter ### parameter ### parameter ###


class Control():
    """
    Define all parameters controlling the simulation.
    """

    def __init__(self, direct=None):
        """
        Initialize control.

        Parameters
        ----------
        direct : str
            direction of propagation: either "down" or "up";
            will be translated by DIRECT to +1 or -1, respectively

        Returns
        -------
        None.

        Instance
        --------
        self.demo : str, see DEMO for options
            current wavefront to be demonstrated
        direct : str
            direction of propagation: either "down" or "up";
            will be translated by DIRECT to +1 or -1, respectively
        self.index : int
            running index of traveltimes at which wavefronts are shown
        self.sign : +/-1
            difference in sign in various formulae for down-/upward propagation
        self.time : float
            current traveltime

        """
        # current state
        self.demo = None
        # direction of propagation
        self.direct = None
        # translate direct into +/-1 by DIRECT and deepcopy
        self.sign = DIRECT[direct]
        # current traveltime index
        self.index = np.NAN
        # current traveltime
        self.time = np.NAN

    def update(self, direct=None):
        """
        Update the control for direction and sign of direction.

        Parameters
        ----------
        direct : str
            direction of propagation: either "down" or "up";
            will be translated by DIRECT to +1 or -1, respectively
        self.sign : +/-1
            difference in sign in various formulae for down-/upward propagation

        Returns
        -------
        self : Control
            updated direct and sign

        """
        # get direction and translate into corresponding sign
        if direct:
            self.direct = direct
            self.sign = DIRECT[direct]
        # return
        return self

    def report(self, top=None):
        """
        Print current status of the simulation.

        Parameters
        ----------
        top : str
            name of top interface (in computational sense); note, top / base
            are the geological base / top for downward propagation, but the
            geological base / top for upward propagation

        Returns
        -------
        self : Control
            reported, but unchanged

        """
        # message
        output = '\nworking on the {:s} state towards {:s} for {:f}'
        print(output.format(self.demo, top.name, self.time))
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
        self.name = surface['name']
        self.depth = surface['depth']
        self.dip = surface['dip']


class LayerGeneric():
    """
    Characterize a 3-term medium.
    """

    # pylint: disable=too-few-public-methods

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
                g=<float>        # stretch factor
            Parameters of TTI elasticity and a layer

        Returns
        -------
        None.

        """
        # pylint: disable=invalid-name # so as to use common physical terms
        self.name = layer['name']
        self.vvv0 = layer['vvv0']
        self.rrr2 = layer['rrr2']
        self.rrr4 = layer['rrr4']
        self.tilt = np.NAN   # to be defined in Stack
        self.thick = layer['thick']
        self.depth = np.NAN   # to be defined in Stack
        self.dip = np.deg2rad(layer['dip'])
        self.ggg = layer['ggg']


class Layer():
    """
    Characterize properties and structure of a layer.

    """

    LAYERCONVERT = {'generic': LayerGeneric}

    def __init__(self, layer=None):
        """
        Initialize the call to another layer conversion.

        Parameters
        ----------
        layer : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.LAYERCONVERT[layer['key']].__init__(self, layer=layer)


class Stack(list):
    """
    Characterize a stack of layer.

    """

    def __init__(self, stack=None):
        """
        Initialize a stack of layer.

        Parameters
        ----------
        stack : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        # convert STACK according to Layer notation and create a stack
        stack = [Layer(layer=layer) for layer in stack]
        # inherit
        super().__init__(stack)   # defining self as list subclass here
        # number of layers
        self.nos = len(stack)
        # tilt of symmetry axis
        self[0].tilt = 0.
        for iii in range(1, self.nos):
            self[iii].tilt = self[iii-1].dip


class Stacks(dict):
    """
    Describe a stack of layers and modify their properties.

    The stack of layer is described as a list subclass, and the functions as
    methods of that subclass.

    """

    @staticmethod
    def _org(stack=None):
        """
        Work on the stack in original state only.

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
    def _stretch(stack=None):
        """
        Work on the stack in the stretched state only.

        For the rotation of a line around a point see
        https://math.stackexchange.com/questions/1064832/rotate-a-line-by-a-given-angle-about-a-point

        """
        # loop through all layers in stack
        for iii in range(stack.nos):
            # check stretching and return if there is none
            if stack[iii].ggg != 0.: 
                # preserve depth relative to current base
                # (needed when rotating and thickening layer stack below)
                depth = np.full(stack.nos, np.NAN)    # init
                depth[iii] = 0.                       # rel. current base
                for kkk in range(iii+1, stack.nos):   # iterat. add layer thick
                    depth[kkk] = depth[kkk-1] + stack[kkk].thick
                # (depth[jjj] now encompasses the entire layer stack from the 
                # base of the stretched layer to the base of layer jjj)
                # calculate stretch term
                gfac = np.sqrt(1. + stack[iii].ggg)
                # calculate additive base rotation
                rot = np.arctan(gfac * np.tan(stack[iii].dip)) - stack[iii].dip
                # calculate multiplicative velocity increase
                velfac = (
                    np.sqrt(1. + stack[iii].ggg * np.sin(stack[iii].dip) ** 2))
                # print additional infos
                if DEMOPRINT:
                    output = "\ncharacterizing stretch in {:s}"
                    output += "\nstretch={:+9.6f}"
                    output += ", rotation={:10.6f}"
                    output += ", factor={:10.6f}"
                    string = [stack[iii].name, gfac, np.rad2deg(rot), velfac]
                    print(output.format(*string))
                    output = "h_vert={:11.6f}, dip={:9.6f}"
                    string = [stack[iii].thick, np.rad2deg(stack[iii].dip)]
                    print(output.format(*string))
                # stretch layer thickness
                stack[iii].thick *= gfac
                # apply base rotation
                stack[iii].dip += rot
                # recalculate layer depth
                stack[iii].depth = np.sum(
                    [stack[kkk].thick for kkk in range(iii+1)])
                # reset stretch term 
                # (no stretching below, just rotation and thickening)
                gfac = 0.
                # print additional infos
                if DEMOPRINT:
                    output = "h_vert={:11.6f}, dip={:9.6f}"
                    string = [stack[iii].thick, np.rad2deg(stack[iii].dip)]
                    print(output.format(*string))
                # loop through all layers in stack below the current layer
                # (these layers are uniformly rotated and thickened)
                for jjj in range(iii+1, stack.nos):
                    # print additional infos
                    if DEMOPRINT:
                        output = "\ncharacterizing stretch in {:s}"
                        output += "\nstretch={:+9.6f}"
                        output += ", rotation={:10.6f}"
                        output += ", factor={:10.6f}"
                        string = [stack[jjj].name, gfac, np.rad2deg(rot), velfac]
                        print(output.format(*string))
                        output = "h_vert={:11.6f}, dip={:9.6f}"
                        string = [stack[jjj].thick, np.rad2deg(stack[jjj].dip)]
                        print(output.format(*string)) 
                    # re-calculate normal layer depth
                    depth[jjj] *= velfac
                    # rotate normal to verticallayer depth
                    depth[jjj] *= (
                        np.cos(stack[jjj].dip) / np.cos(stack[jjj].dip + rot))
                    # re-assign true depth 
                    # (plus base depth of stretched layer)
                    stack[jjj].depth = stack[iii].depth + depth[jjj]
                    # re-calculate stretched thickness
                    stack[jjj].thick = stack[jjj].depth - stack[jjj-1].depth
                    # rotate base dip
                    stack[jjj].dip += rot
                    # rotate symmetry tilt
                    stack[jjj].tilt += rot
                    # stretch reference velocity
                    stack[jjj].vvv0 *= velfac
                    # print additional infos
                    if DEMOPRINT:
                        output = "h_vert={:11.6f}, dip={:9.6f}"
                        string = [stack[jjj].thick, np.rad2deg(stack[jjj].dip)]
                        print(output.format(*string))
        # return
        return stack

    # create multiple objects of type Layer and list them
    # https://stackoverflow.com/questions/14600620/creating-multiple-objects-within-the-same-class-in-python
    # list subclass allowing to add methods to an otherwise built-in type
    # http://igorsobreira.com/2011/02/06/adding-methods-dynamically-in-python.html
    def __init__(self, stack=None):
        """
        Subclass a list containing a stack of layers.

        """
        # get an instance of Stack
        stack = Stack(stack=stack)
        # copy stack in all states
        state = {'org': self._org, 'stretch': self._stretch}
        stacks = {demo: state[demo](stack=cp(stack)) for demo in DEMO}
        # inherit
        super().__init__(stacks)   # defining self as dict subclass here
        # number of layers
        self.nos = stack.nos

    def info(self):
        """
        Print layers making up the layer stack.

        Returns
        -------
        None.

        """
        # identify
        stack = self
        # check switch
        if STACKPRINT:
            # write title
            print('\nlayer stack:')
            # write header for structure
            width = max(
                [len(stack['org'][index].name) for index in range(stack.nos)])
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
                    stack['org'][index].name,
                    stack['org'][index].depth,
                    stack['stretch'][index].depth,
                    np.rad2deg(stack['org'][index].dip),
                    np.rad2deg(stack['stretch'][index].dip))
                print(output.format(*string))
            # write title
            print('\nlayer stack:')
            # write header for elasticity
            width = max(
                [len(stack['org'][index].name) for index in range(stack.nos)])
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
                    stack['org'][index].name,
                    stack['org'][index].vvv0,
                    stack['stretch'][index].vvv0,
                    stack['org'][index].rrr2,
                    stack['stretch'][index].rrr2,
                    stack['org'][index].rrr4,
                    stack['stretch'][index].rrr4,
                    np.rad2deg(stack['org'][index].tilt),
                    np.rad2deg(stack['stretch'][index].tilt))
                print(output.format(*string))
        # return
        return stack


class Para():
    """
    Get the parameters characterizing velocities.

    """

    def __init__(self, layer=None):
        """
        Extract those velocity parameters from layer information.

        """
        # copy all parameters of PARAMETERLIST from layer
        for item in PARAMETERLIST:
            setattr(self, item, getattr(layer, item))


class Face():
    """
    Get the parameters characterizing interfaces

    """

    def __init__(self, layer=None):
        """
        Extract the interface parameters from layer information.

        """
        # copy all parameters of FACELIST from layer
        for item in FACELIST:
            setattr(self, item, getattr(layer, item))


class Path():
    """
    Extract parameters and interfaces along a travelpath.

    """

    def __init__(self, path=None, surface=None, stack=None):
        # extract number of layers in path
        self.nos = len(path)
        # extract available layer names in stack
        layname = [layer.name for layer in stack]
        # index path layers by correlating path names with layer names
        self.index = [layname.index(path[iii]) for iii in range(self.nos)]
        # extract properties
        self.para = [
            Para(layer=stack[self.index[iii]]) for iii in range(self.nos)]
        # direction of travel
        # (extract from the difference in layer indices)
        invdirect = dict(zip(DIRECT.values(), DIRECT.keys()))
        self.direct = ['down']   # downwards in source layer
        self.direct += [
            invdirect[index] if index != 0
            else ('up' if self.direct[index-1] == 'down' else 'down')
            for index in list(np.diff(self.index))]
        # extract interfaces
        # (base interface is defined in layer: so, base interface is in current
        # layer = current layer index, and top interface is base interface of
        # layer above = current layer index - 1)
        self.face = [
            Face(
                layer=stack[
                    self.index[iii] if self.direct[iii] == 'down'
                    else self.index[iii]-1])
            for iii in range(self.nos-1)]
        self.face += [Face(layer=surface)]   # add surface

    def info(self):
        """
        Print travelpath.

        Note, provided PATHPRINT is switched on

        Returns
        -------
        self : PATH
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
                [len(self.para[iii].name) for iii in range(len(self.para))])
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

    def next(self):
        for iii in range(self.nos):
            para = self.para[iii]
            face = self.face[iii]
            bottom = ([None] + self.face)[iii]
            yield iii, para, bottom, face


class Paths(dict):
    def __init__(self, path=None, surface=None, stacks=None):
        surface = Surface(surface=surface)
        paths = {
            demo: Path(path=path, surface=surface, stack=stacks[demo])
            for demo in DEMO}
        super().__init__(paths)

    def info(self):
        """
        Write out the entire travelpath.

        The travelpath remains identical for all DEMO's; so, writing it out
        once is sufficient.

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
            angle=<np.array>,   # all emission angles
            nos=<int>            # number of emission angles

        """
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
        self :
            returns itself

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


class Front():
    """
    Describe location and time of a wavefront.
    """

    def __init__(self, source=None, color=None, dashes=None):
        """
        Initialize a wavefront.

        Parameters
        ----------
        source : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.color = color
        self.dashes = dashes
        self.length = np.NAN
        self.xxx = np.array([source.xxx] * source.nos)
        self.zzz = np.array([source.zzz] * source.nos)
        self.time = np.array([source.time] * source.nos)
        self.done = np.array([False] * source.nos)
        self.nos = source.nos

    def _raylength(self, todos, top=None, energy=None):
        # initialize length to some nonsense
        length = np.full(self.nos, np.NAN)
        # calculate length of segment
        # (for propagation parallel to an interface, the below denominator goes
        # through zero, and length becomes +/- inf; catch respective indices
        # of length; then, make length large to mimick near-parallel
        # propagation)
        with np.errstate(divide='raise', over='raise'):
            try:
                num = (
                    float(top.depth)
                    -
                    self.zzz[todos]
                    +
                    np.multiply(self.xxx[todos], np.tan(top.dip))
                )
                denom = (
                    np.cos(energy.angle[todos])
                    -
                    np.multiply(np.sin(energy.angle[todos]), np.tan(top.dip))
                )
                length[todos] = np.divide(num, denom)
            except FloatingPointError:
                # check for +/- inf and set to something large
                length[np.isinf(length)] = LARGEDISTANCE
            except (ZeroDivisionError, OverflowError) as unexpect:
                # exit ungracefully
                raise AssertionError('bug in front._raylength!') from unexpect
        # check for negative values
        # (length becomes negative if a potential cross point is behind =
        # opposite to the direction of propagation; instead, assume the ray
        # propagates in the positive direction without ever crossing the
        # interface)
        length[length < 0] = LARGEDISTANCE
        # return
        return length

    def crosspoint(self, ctl=None, top=None, energy=None):
        # omit rays already completed
        todos = np.logical_not(self.done)
        # calculate length of segment
        self.length = self._raylength(todos, top=top, energy=energy)
        # construct segment to next interface
        xxx = self.length[todos] * np.sin(energy.angle[todos])
        zzz = self.length[todos] * np.cos(energy.angle[todos])
        # calculate time of propagation through segment
        time = self.length[todos] / energy.mag[todos]
        # determine fraction of remaining traveltime to be spent in segment: if
        # <1 wavefront ends in segment, if =1 wavefront ends at interface, and
        # if >1 continues into next layer
        frag = (ctl.time - self.time[todos]) / time
        # determine completeness
        # (wavefront ends within segment or at interface)
        self.done[todos] = np.array(frag <= 1.)
        # limit to segment or fraction of segment
        # (frag=1 or frag<1, respectively; don't overshoot)
        frag = np.minimum(frag, np.array(1.))
        # check ray path
        if DEMOPRINT or DEMOPLOT:
            # pick one ray in the middle
            mid = int(self.nos / 2)
            if DEMOPRINT:
                # check todos
                # !!! replace mid with something sensible
                if np.all(todos):
                    # print length and incidence angle
                    output = "dl={:8.6f}, ang={:8.6f}"
                    inn = (self.length[mid], np.rad2deg(energy.angle[mid]))
                    print(output.format(*inn))
                    # print traveltime and coordinates
                    output = "dt={:8.6f}, dx={:+9.3f}, dz={:8.3f}"
                    inn = (time[mid], xxx[mid], zzz[mid])
                    print(output.format(*inn))
        if DEMOPLOT:
            # plot rays
            for iii in range(len(xxx)):
                plt.plot(
                    [self.xxx[iii], self.xxx[iii] + xxx[iii]],
                    [self.zzz[iii], self.zzz[iii] + zzz[iii]], color='blue', dashes=self.dashes)
                # replot former coordinate 
                # (to overplot ray)
                plt.plot(self.xxx[iii], self.zzz[iii], marker='o', color='red')
            # redraw
            plt.draw()
        # add segment distance to coordinates
        self.xxx[todos] += frag * xxx
        self.zzz[todos] += frag * zzz
        # add traveltime along segment to total traveltime
        self.time[todos] += frag * time
        if DEMOPRINT:
            output = "t={:6.3f}, x={:+9.3f}, z={:8.3f}"
            inn = (self.time[mid], self.xxx[mid], self.zzz[mid])
            print(output.format(*inn))
        # check ray path
        if DEMOPLOT:
            # plot current coordinates
            plt.plot(self.xxx[mid], self.zzz[mid], marker='o', color='red')
            # redraw
            plt.draw()
        # remove all wavefront points above surface
        delete = self.zzz < -10000 * FACETOL
        # remove all wavefronts left of graphics window
        delete = np.logical_and(delete, self.xxx < GRAPHICS['xmin'])
        # remove all wavefronts above graphics window
        delete = np.logical_and(delete, self.zzz > GRAPHICS['zmax'])
        # remove all wavefronts right of graphics window
        delete = np.logical_and(delete, self.xxx > GRAPHICS['xmax'])
        # execute deletion above
        self.xxx[delete] = np.NAN
        self.zzz[delete] = np.NAN
        self.time[delete] = np.NAN
        self.done[delete] = np.NAN
        # return
        return self


class Fronts(dict):

    # list subclass allowing to add methods to an otherwise built-in type
    # http://igorsobreira.com/2011/02/06/adding-methods-dynamically-in-python.html
    def __init__(self, ctl=None, source=None):
        """
        Subclass a list containing a set of wavefronts.

        """
        # create individual fronts for each state
        fronts = {
            demo:
                Front(
                    source=source, color=LINECOLOR[ctl.index],
                    dashes=LINEDASHES[demo])
            for demo in DEMO}
        # inherit
        super().__init__(fronts)   # now initializing self as dict subclass

    def info(self):
        """
        Print wavefront coordinates.

        Returns
        -------
        None.

        """
        # check switch
        if FRONTPRINT:
            # number of digits in nos
            width = int(np.log10(self['org'].nos)) + 1
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
            for index in range(self['org'].nos):
                if self['org'].done[index] or self['stretch'].done[index]:
                    numbers = (
                        index,
                        float(self['org'].xxx[index]),
                        float(self['stretch'].xxx[index]),
                        float(self['org'].zzz[index]),
                        float(self['stretch'].zzz[index]),
                        float(self['org'].time[index]),
                        float(self['stretch'].time[index]))
                    print(output.format(*numbers))
        # return
        return self


# ### velocity ### velocity ### velocity ### velocity ### velocity ###


class Vel():
    """
    Describe incidence angle, magnitude and components of a velocity.
    """

    def __init__(self, nos=None):
        self.name = None                      # name (for identification only)
        self.angle = np.full(nos, np.NAN)     # angle
        self.xxx = np.full(nos, np.NAN)       # horizontal component
        self.zzz = np.full(nos, np.NAN)       # vertical component
        self.mag = np.full(nos, np.NAN)       # magnitude
        self.nos = nos                        # no

    def _info(self, title=None, mag=None, xxx=None, zzz=None):
        # print title
        print(title)
        # print header
        header = ' ' + 'angle'
        header += ' ' * 9 + 'abs'
        header += ' ' * 11 + 'x'
        header += ' ' * 12 + 'z'
        print(header)
        # define output format
        output = '{:+7.3f},   {:9.3f},   {:9.3f},   {:9.3f}'
        # print data
        for index in range(self.nos):
            numbers = (
                float(np.rad2deg(self.angle[index])),
                float(mag[index]),
                float(xxx[index]),
                float(zzz[index]))
            print(output.format(*numbers))
        # return
        return self

    def _comp(self):
        # calculate components
        self.xxx = self.mag * np.sin(self.angle)
        self.zzz = self.mag * np.cos(self.angle)
        # return
        return self


class Phase(Vel):
    """
    Describe a phase velocity.

    """

    __slots__ = [
        'vvv0', 'rrr2', 'rrr4', 'tilt',   # phase velocity parameter
        'g',                        # stretch factor
        'angle0', 'angle',          # original / stretched phase angle
        'mag0', 'mag', 'diffmag',   # orig. / stre. pure / diff phase velocity
        'xxx', 'diffxxx',           # pure / differential parallel component
        'zzz', 'diffzzz',           # pure / differential perp. component
        'nos',                      # number angles
        'name']                     # layer name

    def __init__(self, nos=None):
        """
        Initialize a velocity.
        """
        # inherit with correct length
        super().__init__(nos=nos)
        # for differentials
        self.diffxxx = np.full(nos, np.NAN)   # horizontal diff component
        self.diffzzz = np.full(nos, np.NAN)   # vertical diff component
        self.diffmag = np.full(nos, np.NAN)   # magnitude differential
        # for 3-term velocity characterization
        self.vvv0 = np.NAN   # reference phasevelocity
        self.rrr2 = np.NAN   # 2nd phase velocity coefficient
        self.rrr4 = np.NAN   # 4th phase velocity coefficient
        self.tilt = np.NAN   # tilt of symmetry axis (positive downwards)
        # stretch
        self.angle0 = np.full(nos, np.NAN)   # unstretched phase angle
        self.mag0 = np.full(nos, np.NAN)     # unstretched velocity magnitude
        self.ggg = np.NAN                    # stretch factor

    def initpara(self, para=None):
        """
        Update the layer parameters controlling a phase velocity.

        """
        # update
        for attr in para.__dict__.keys():
            setattr(self, attr, cp(getattr(para, attr)))
        # return
        return self

    def initangle(self, angle0=None):
        """
        Initialize a phase velocity with the emission angles of a source.

        """
        # copy angle
        self.angle0 = cp(angle0)
        self.angle = cp(angle0)
        # return
        return self

    def calc(self, ctl=None):
        # calculate absolute velocity
        self._magnitude(ctl=ctl)   # giving self.mag0
        # calculate stretch
        # (which calculates the new absolute velocity and phase angle)
        self._stretch()   # giving self.mag and self.angle
        # calculate components
        self._comp()
        # return
        return self

    def diffcalc(self, ctl=None):
        # calculate differential velocity
        # (only stretched one, original not required)
        self._diffstretchmagnitude(ctl=ctl)   # giving self.diffmag
        # calculate components
        self._diffcomp()
        # return
        return self

    def _magnitude(self, ctl=None):
        """
        Calculate a P- or SV-phase velocity in a TTI medium.

        Note, the phase angle is seen relative to the vertical.

        """
        # compensate phase angle for tilt
        tiltangle = self.angle0 + ctl.sign * self.tilt
        # calculate velocity
        self.mag0 = cp(self.vvv0)   # reference velocity
        self.mag0 *= (   # angular variation
            np.sqrt(
                1.
                +
                self.rrr2 * np.sin(tiltangle) ** 2
                +
                self.rrr4 * np.sin(tiltangle) ** 4))

    def _stretch(self):
        """
        Stretch a layer according to paper.

        """
        # copy magnitude into stretched magnitude
        self.mag = cp(self.mag0)
        # check whether stretching necessary
        if self.ggg != 0.:
            # stretch according to paper
            self.mag *= (
                np.sqrt(
                    (1 + self.ggg)
                    /
                    (1 + self.ggg * np.sin(self.angle0) ** 2)))
        # copy angle into stretched angle
        self.angle =  cp(self.angle0)
        # check whether stretching necessary
        if self.ggg != 0.:
            # calculate stretch angle
            # (since the tangent has an unwanted pi-periodicity, the stretched
            # angle must be moved back into the right quadrant)
            self.angle = (
                np.arctan(
                    np.sqrt(1. + self.ggg) * np.tan(self.angle)))
            self.angle[self.angle0 < -np.pi / 2.] -= np.pi
            self.angle[self.angle0 > +np.pi / 2.] += np.pi

    def _diffstretchmagnitude(self, ctl=None):
        """
        Differentiate a stretch term.

        """
        # compensate phase angle for tilt
        tiltangle = self.angle0 + ctl.sign * self.tilt
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
        todos = np.logical_not(np.isnan(self.angle0))
        #self.diffmag[todos] = np.gradient(self.mag[todos], self.angle[todos])
        # return
        return self

    def _diffcomp(self):
        # calculate components
        self.diffxxx = self.diffmag * np.sin(self.angle)
        self.diffzzz = self.diffmag * np.cos(self.angle)
        # return
        return self

    def search(self, ctl=None, slow=None, bottom=None):
        # initiate zero-offset incidence (or close to)
        # (set initial angle perpendicular to the interface,
        # spread over array, and set phase angle)
        self.initangle(
            angle0=np.full_like(slow.xxx, -1. * ctl.sign * bottom.dip))
        # initiate loop finding incidence angle
        eps = np.finfo(float).eps
        scl = np.full_like(slow.xxx, 1.)
        lnan = np.full_like(slow.xxx, False, dtype=bool)
        rnan = np.full_like(slow.xxx, False, dtype=bool)
        iterat = 0
        while True:
            # firstly, calculate phase velocity with updated
            # layer parameter+stretch, but old phase angle;
            # later, recalculate phase velocity with updated
            # phase angle
            self.calc(ctl=ctl)
            # rotate angle coordinate system relative to bottom
            dipangle = self.angle + ctl.sign * bottom.dip
            # define sin(angle)
            sine = np.sin(dipangle)
            # difference p*v - sin(angle)
            dsine = slow.xxx * self.mag - sine
            # updated sin(angle), still relative to bottom
            sine += scl * dsine
            # limit to interval [-1, +1]
            sine = np.minimum(+1.+eps, np.maximum(-1.-eps, sine))
            # reduce sine increment when hitting -/+1 barrier
            # nan if not recovering from -/+1 barrier 2 times in a row
            scl[sine == -1.] *= SCLFAC   # move slower from now on
            nan = np.logical_and(sine == -1.-eps, lnan)   # 2 times offenders
            sine[nan] = np.NAN   # exclude those
            lnan = np.logical_or(sine == -1.-eps, np.isnan(sine))   # mark them
            scl[sine == +1.] *= SCLFAC
            nan = np.logical_and(sine == +1.+eps, rnan)
            sine[nan] = np.NAN
            rnan = np.logical_or(sine == +1.+eps, np.isnan(sine))
            # if all nan
            if np.all(np.isnan(sine)):
                # nan all angles
                self.angle = np.full_like(slow.xxx, np.NAN)
                self.angle0 = np.full_like(slow.xxx, np.NAN)
                # done with it
                break 
            # exclude first-time offenders further on
            sine[sine == -1. - eps] = np.NAN
            sine[sine == +1. + eps] = np.NAN
            # convert to angle
            dipangle = np.arcsin(sine)
            # rotate angle coordinate system back
            self.angle = dipangle - ctl.sign * bottom.dip
            # convert angle to original state
            if self.ggg == 0.:
                self.angle0 = cp(self.angle)
            else:
                fac = 1. + self.ggg * (1. - np.sin(self.angle) ** 2)
                fac = np.sqrt(fac)
                self.angle0 = np.arcsin(np.sin(self.angle) / fac)
                # arcsin(sin(angle)) destroys the correct quartel for 
                # angle0; re-assign the same as for angle
                todos = self.angle > 0.5 * np.pi
                self.angle0[todos] = np.pi - self.angle0[todos]
                todos = self.angle < -0.5 * np.pi
                self.angle0[todos] = -np.pi - self.angle0[todos]
            # get maximum remaining error in sine,
            # max(abs(delta(sine))) where -1 < sine < +1
            maxdsine = dsine[np.abs(sine) != 1.0]
            maxdsine = float(np.nanmax(np.abs(maxdsine)))
            # when remaining error < max allowed error, exit; expected exit
            if maxdsine < MAXDSINE:
                # check sanity
                tmp = np.diff(self.angle)
                if np.any(tmp == 0.):
                    output = "\nconstant Snell's angles:"
                    output += "\ndecrease MAXDSINE or number of SOURCE angles"
                    raise AssertionError(output)
                if np.any(tmp < 0.):
                    output = "\nnot monotonously increasing Snell's angles"
                    output += "\npossibly a triplication in the phase front"
                    output += "\n(not implemented yet)"
                    raise AssertionError(output)
                # exit loop normally at last
                break
            # emergency abortion
            iterat += 1
            if iterat > MAXITERAT:
                output = "\ninfinite iteration in search for Snell's angle"
                output += "\nsine increment in search: {:8.6f}"
                output += "\nreduce scale factor SCLFAC: {:8.6f}"
                output += "\nincrease max number of iteration MAXITERAT: {:9d}"
                string = [maxdsine, SCLFAC, MAXITERAT]
                raise AssertionError(output.format(*string))
    
    def _snell(self, slow=None, sine=None):
        # close all figures
        plt.close('all')
        # open new figure
        fig = plt.figure()
        # create axes
        fig.add_subplot(111)
        #plt.plot(np.rad2deg(self.angle))
        plt.plot(dsine)

    def info(self):
        if PHASEPRINT:
            # construct title
            title = f"\nphase velocities in {self.name}:"
            self._info(title=title, mag=self.mag, xxx=self.xxx, zzz=self.zzz)
        return self

    def diffinfo(self):
        if DIFFPHASEPRINT:
            # construct title
            title = f"\ndifferential phase velocities in {self.name}:"
            self._info(
                title=title, mag=self.diffmag, xxx=self.diffxxx,
                zzz=self.diffzzz)
        # return
        return self

    def diffcheck(self):
        if DIFFPHASECHECK:
            # calculate the numerical differential
            grad = np.full_like(self.mag, np.NAN)
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

    def __init__(self, nos=None):
        # inherit
        super().__init__(nos=nos)

    def calc(self, ctl=None, phase=None):
        # calculate magnitude
        self.mag = np.sqrt(phase.mag ** 2 + phase.diffmag ** 2)
        # calculate lateral component
        self.xxx = (
            phase.mag * np.sin(phase.angle)
            +
            phase.diffmag * np.cos(phase.angle))
        # calculate vertical component
        self.zzz = (
            phase.mag * np.cos(phase.angle)
            -
            phase.diffmag * np.sin(phase.angle))
        self.zzz *= ctl.sign
        # calculate angle of incidence
        self.angle = np.arctan2(self.xxx, self.zzz)
        # name
        self.name = phase.name
        # return
        return self

    def info(self):
        # print info
        if ENERGYPRINT:
            title = f"\nenergy velocities in {self.name}"
            # print title
            print(title)
            # print header
            header = ' ' * 2 + 'angle'
            header += ' ' * 9 + 'abs'
            header += ' ' * 11 + 'x'
            header += ' ' * 12 + 'z'
            print(header)
            # print data
            output = '{:+8.3f},   {:9.3f},   {:9.3f},   {:9.3f}'
            for index in range(self.nos):
                numbers = (
                    float(np.rad2deg(self.angle[index])),
                    float(self.mag[index]),
                    float(self.xxx[index]),
                    float(self.zzz[index]))
                print(output.format(*numbers))
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

    def calc(self, ctl=None, top=None, phase=None):
        # calculate slowness
        self.mag = 1. / phase.mag
        # check angle of incidence
        self.angle = phase.angle + ctl.sign * top.dip
        nan = (
            np.logical_or(
                self.angle < -1 * np.pi / 2.,
                self.angle > np.pi / 2.))
        self.angle[nan] = np.NAN
        self.mag[nan] = np.NAN
        # calculate slownes
        self.xxx = np.sin(self.angle) * self.mag
        # number of slownesses
        self.nos = phase.nos
        # name
        self.name = top.name
        # return
        return self

    def info(self):
        # print info
        if SLOWPRINT:
            title = f"\nslowness at bottom {self.name}"
            # print title
            print(title)
            # print header
            header = ' ' + 'angle'
            header += ' ' * 10 + 'abs'
            header += ' ' * 10 + 'parallel'
            print(header)
            # print data
            output = '{:+7.3f},   {:12.9f},   {:12.9f}'
            for index in range(self.nos):
                numbers = (
                    float(np.rad2deg(self.angle[index])),
                    float(self.mag[index]),
                    float(self.xxx[index]))
                print(output.format(*numbers))
        # return
        return self


# ### graphics ### graphics  ### graphics ### graphics ### graphics ###


class Graph():
    """
    Prepare a graphics of snapshots of wavefronts and interfaces.

    """

    def __init__(self):
        # close all figures
        plt.close('all')
        # open new figure
        self.fig = plt.figure()
        # show current figure
        self.show = plt.show
        # create axes
        self.axes = self.fig.add_subplot(111)

    def _interface(self, stacks=None, source=None):
        """
        Plot the interfaces at/through which a wave is reflected/transmitted.

        """
        # loop over all DEMO's variations
        for demo in DEMO:
            # surface
            self.axes.plot(
               [GRAPHICS['xmin'], GRAPHICS['xmax']],
               [source.zzz, source.zzz],
               color='black', dashes=FACEDASHES[demo])
            self.show()
            # loop over all interfaces
            for layer in stacks[demo]:
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
                    [zleft, zright], color='black', dashes=FACEDASHES[demo])
                self.show()

    def _source(self, source=None):
        """
        Plot the source point.

        """
        self.axes.plot(source.xxx, source.zzz, '*', color='red')
        self.show()

    def _wavefront(self, front=None):
        """
        Plot a wavefront.

        """
        # consider only completed wavefront parts
        # (incomplete means the time the wave needed to travel up to
        # this point is still less than the requested traveltime)
        todos = front.done
        # remove all wavefront points above surface
        # (should only happen if an interface cuts through the
        # surface, which fails the assumptions on layering made, and if
        # the window is not properly sized)
        todos = np.logical_and(todos, front.zzz > -1 * FACETOL)
        # remove all wavefronts left of graphics window
        todos = np.logical_and(todos, front.xxx > GRAPHICS['xmin'])
        # remove all wavefronts above graphics window
        todos = np.logical_and(todos, front.zzz < GRAPHICS['zmax'])
        # remove all wavefronts right of graphics window
        todos = np.logical_and(todos, front.xxx < GRAPHICS['xmax'])
        # get list of split indices
        splitter = [
            index
            for index in range(1, len(todos))
            if (
                (todos[index-1] and ~todos[index])     # True to False
                or
                (~todos[index-1] and todos[index]))]   # False to True
        # split according to splitter list
        xxx = [
            np.array(front.xxx[i:j])
            for i, j in zip([0] + splitter, splitter + [None])]
        zzz = [
            np.array(front.zzz[i:j])
            for i, j in zip([0] + splitter, splitter + [None])]
        todos = [
            np.array(todos[i:j])
            for i, j in zip([0] + splitter, splitter + [None])]
        for jjj in range(len(splitter) + 1):
            if np.all(todos[jjj]):
                if front.nos == 1:
                    self.axes.plot(
                        xxx[jjj], zzz[jjj], marker='r', color=front.color)
                else:
                    self.axes.plot(
                        xxx[jjj], zzz[jjj], color=front.color,
                        dashes=front.dashes)
        self.show()

    def _axes(self):
        """
        Plot display axes.

        """
        # set window limits
        self.axes.set_xlim([GRAPHICS['xmin'], GRAPHICS['xmax']])
        self.axes.set_ylim([GRAPHICS['zmin'], GRAPHICS['zmax']])
        # inverse y axis
        # (positive is traditionally downwards)
        self.axes.set_ylim(self.axes.get_ylim()[::-1])
        # square
        self.axes.set_aspect('equal')
        # show
        self.show()

    def setup(self, stacks=None, source=None):
        """
        Set up the graphics window and plot source and interfaces.

        """
        # check switch for plotting interfaces
        if PLOTFACES:
            # plot interfaces
            self._interface(stacks=stacks, source=source)
        # check switch for plotting source
        if PLOTSOURCE:
            # plot sources
            self._source(source=source)
        # plot display axes
        self._axes()
        # return
        return self

    def curve(self, front=None):
        """
        Plot individual wavefronts one at a time.

        """
        # plot wavefronts
        if PLOTFRONTS:
            self._wavefront(front=front)
        # return
        return self


# ### main ### main ### main ### main ### main ### main ### main ### main ###


def main():
    """
    Demonstrate the concept of depth - velocity - anisotropy ambiguity.

    Returns
    -------
    None.

    """
    # set up control, that is all parameters controlling the simulation
    # (The source is assumed to be located at the surface; so, initial
    # propagation is downwards.)
    ctl = Control(direct='down')
    # set up the layer stack
    stacks = Stacks(stack=STACK).info()
    # set up the source
    source = Source(source=SOURCE).info()
    # set up travelpaths
    paths = Paths(path=PATH, surface=SURFACE, stacks=stacks).info()
    # set up rays
    # !!! rays = Rays(source=source)
    # graphics
    if not DEBUG:
        graph = Graph().setup(stacks=stacks, source=source)
    # loop through all traveltimes
    for ctl.index, ctl.time in enumerate(TRAVELTIMES):
        # set up a list of wavefronts
        fronts = Fronts(ctl=ctl, source=source)
        # loop through variations (original, stretch and possibly others)
        for ctl.demo in DEMO:
            # short for paths[demo]
            path = paths[ctl.demo]
            # short for wavefront[demo]
            front = fronts[ctl.demo]   # includes all front.done set False
            # loop through each segment of path
            for index, para, bottom, top in path.next():
                # report current segment
                ctl.update(direct=path.direct[index]).report(top=top)
                # set up phase velocity with layer parameters
                phase = Phase(nos=source.nos).initpara(para=para)
                # check status of wavefront
                if not np.all(front.done):
                    # for first=top layer only
                    if index == 0:
                        # set up phase velocity with source emission angles
                        phase.initangle(angle0=source.angle)
                    # for second and lower layers
                    else:
                        phase.search(ctl=ctl, slow=slow, bottom=bottom)   # noqa # analysis: ignore
                        # (slow defined for all index > 0, that is after having
                        # hit first interface)
                    # do/redo and report phase velocity
                    phase.calc(ctl=ctl).info()
                    # calculate differential phase velocity and check
                    phase.diffcalc(ctl=ctl).diffinfo().diffcheck()
                    # calculate energy velocity
                    energy = Energy(nos=source.nos).calc(ctl=ctl, phase=phase).info()
                    # propagate wavefront
                    front.crosspoint(ctl=ctl, top=top, energy=energy)
                    # calculate parallel slowness
                    slow = Slow(nos=source.nos).calc(ctl=ctl, top=top, phase=phase).info()
                # prepare graphics
                if not DEBUG:
                    graph.curve(front=front)
        # print wavefront
        fronts.info()


if __name__ == "__main__":
    main()
