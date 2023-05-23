# -*- coding: utf-8 -*-
"""
Python code for the "avo_for_density" Notebook.

@author: Björn E. Rommel, version: 1.0.0
"""


# import
import os
import sys
from copy import deepcopy as cp
import numpy as np
from numpy.random import default_rng as rnd
from matplotlib import pyplot as plt


# --- change --- change --- change --- change --- change --- change --- change


# default range of angles for the AVA curves
DEG = [float(iii) / 1000. for iii in range(0, 40001)]


# default top properties
VP1, DVP1 = 2000, 20
VS1, DVS1 = 1200, 12
RHO1, DRHO1 = 2400, 100

# default bottom properties
VP2, DVP2 = 2500, 25
VS2, DVS2 = 1500, 15
RHO2, DRHO2 = 2600, 100


# default signal-to-noise ratio
SNR = 1   # neutral value


# parameters for the prior AVA curve
COEFFCOLOR = 'b-'


# parameters for the data points
DATACOLOR = 'mo'
DATAERRORCOLOR = 'r-'


# parameters for the posterior AVA curve
AVACOLOR = 'g-'


# parameters for the demo wavelet
WAVELETS = {'triangle': 'triangle'}    # dict of identifier and function
WAVELETNAME = 'triangle'               # type of wavelet
WAVELETHALFWIDTH = 10                  # half-width of wavelet
LEFTSIGNAL = 2 * WAVELETHALFWIDTH      # first index of wavelet
RIGHTWAVELET = 12 * WAVELETHALFWIDTH   # last index of entire signal
WAVELETCOLOR = 'b-'                    # Matplotlib line options


# --- do not change below --- do not change below --- do not change below ---


# modes
# COEFF: plot prior AVA curve
# COEFF+: plot prior AVA +/- standard deviation curve
# DATA: plot data points
# DATA+: plot data points with data uncertainty bars
# AVA: plot posterior AVA curve
# AVA+: plot posterior AVA +/- standard deviation curve


# pylint:disable=too-many-lines


# environment
PLOTENVIRONMENT = 'jupyter'
CANVASENVIRONMENT = 'ipython'


# definition of figure class
class Fig():
    """
    Generic figure class.

    """

    def __init__(self, num=None, title=None):
        """
        Initialize a figure.

        Parameters
        ----------
        num : int
            Figure number.
        title : char
            Title of figure. Default is no title.

        Returns
        -------
        None.

        """
        # close old figure
        plt.close(fig=num)
        # set new figure
        self.fig = plt.figure(num=num)
        # set figure title
        if title:
            plt.title(title)
        # set AVA line
        self.line = {
            'amp': None, 'amp+std': None, 'amp-std': None, 'other': None}

    def del_line(self):
        """
        Delete the AVA curve if any.

        Returns
        -------
        None.

        """
        # loop through lines
        for line in ['amp', 'amp+std', 'amp-std', 'other']:
            # check key in dict
            if line in self.line.keys():
                # protect against None
                if self.line[line]:
                    # remove
                    self.line[line].pop(0).remove()

    def plt_line(self, x=None, y=None, key='other', opt='k-'):   # pylint:disable=invalid-name
        """
        Plot an AVA curve.

        Parameters
        ----------
        x : float, optional
            Abscissa of an AVA curve. The default is None.
        y : float, optional
            Ordinate of an AVA curve. The default is None.
        key : char
            Identifier of a line. Default is 'other'.
        opt : str, optional
            Matplotlib color for the AVA curve. The default is standard black.

        Returns
        -------
        None.

        """
        if not isinstance(y, NONETYPE):
            if isinstance(x, NONETYPE):
                x = range(0, len(y), 1)
            self.line[key] = plt.plot(x, y, opt)


# definition of a figure dict
fig = dict()


# initialize AVA points
# (amp, ..., deg and cov depend on the number of samples; so, empty lists)
DATA = {
    'nos': 0,        # number of data points
    'deg': [],       # at incidence angle
    'amp': [],       # data amplitude
    'amp+std': [],   # data amplitude + STD
    'amp-std': [],   # data amplitude - STD
    'snr': np.NAN,   # single-valued signal-to-noise ratio
    'std': np.NAN}   # data standard deviation

# AVA data
coeff = cp(DATA)
data = cp(DATA)
ava = cp(DATA)


# initialize models
MODEL = {
    'mod': np.full(3, fill_value=np.NAN),        # model
    'cov': np.full((3, 3), fill_value=np.NAN),   # covariance
    'std': np.full(3, fill_value=np.NAN)}        # standard deviation

# halfspaces
top = cp(MODEL)
bot = cp(MODEL)

# background
back = cp(MODEL)

# prior contrast model
precon = cp(MODEL)

# prior model in Bayes' theory
prior = cp(MODEL)

# posterior model in Bayes' theory
post = cp(MODEL)

# posterior contrast model
poscon = cp(MODEL)


# parameter in Bayes' theory
para = {'vsp': np.NAN}   # S-to-P velocity ratio
para = {'vsp': np.sqrt(3.)}   # S-to-P velocity ratio


# suppress traceback
if __name__ == '__main__':
    DEBUG = True
    sys.tracebacklimit = 100   # default number of traceback levels
else:                         # specifically for use with Jupyter
    DEBUG = True
    sys.tracebacklimit = 100


# indices
IVP, IVS, IRHO = 0, 1, 2


# lists / dicts abbreviations
PROP = ['vp', 'vs', 'rho']
DPROP = ['dvp', 'dvs', 'drho']
HALFSPACE = {'top': top, 'bot': bot}


# type None
NONETYPE = type(None)


# --- figure --- figure --- figure --- figure --- figure --- figure --- figure


def init_plot(num=None, title=None):
    """
    Initialize a plot.

    Parameters
    ----------
    num : int
        Figure number. Default is Matplotlib's default numbering.
    title : char
        Title of figure. Default is no title.

    Returns
    -------
    None.

    """
    # create figure
    fig[num] = Fig(num=num, title=title)


def exit_plot(env=None):
    """
    Plot a figure.

    Parameters
    ----------
    env : char
        Environment plot / canvas

    Raises
    ------
    AssertionError
        environment not found in the accepted list of environments

    Returns
    -------
    None.

    """
    if env not in [CANVASENVIRONMENT, PLOTENVIRONMENT]:
        string = 'exit_plot: no environment {}!'.format(env)
        raise AssertionError(string)
    # show plot depending on environment
    if env == CANVASENVIRONMENT:
        plt.draw()
    if env == PLOTENVIRONMENT:
        plt.show()


# --- input --- input --- input --- input --- input --- input --- input ---


def get_data(snr=SNR):
    """
    Get the signal-to-noise ratio and estimate a noise standard deviation.

    The signal-to-noise ratio shall be defined as the ratio of peak signal
    amplitude and (almost) maximum noise sample. Recall, Bayes' theory requires
    the data standard deviation, and the (almost) maximum sample of a normal
    distribution lies roughly at the edge of 3 times the data standard
    deviation of that distribution. So, 1 / (3 signal-to-noise) approximates
    the data standard deviation.

    This parameter is not required for classical = non-Bayesian inversion. So,
    None and np.NAN are accepted indicating classical inversion, and a positive
    finite value, unless it raises an assertion error for various numerical
    errors, for Bayesian inversion.

    Parameters
    ----------
    snr : float
        Signal-to-noise ratio. Default is SNR:
        np.NAN for classical inversion
        positive finite (within limits) for Bayesian inversion

    Raises
    ------
    AssertionError
        None, negative, zero, too large or too small a signal-to-noise ratio

    Returns
    -------
    data : dict of floats
        'snr' : Original signal-to-noise ratio
        'std' : Standard deviation

    """
    # check for None
    if not snr:
        string = 'signal-to-noise ratio {} not NAN or positive finite!'
        raise AssertionError()
    # rule out NAN
    # (NAN for classical = non-Bayesian inversion)
    if not np.isnan(snr):
        # check for +/-Inf
        if not np.isfinite(snr):
            snr = SNR
            # check of data standard deviation: negative, zero
        if snr <= 0.:
            string = 'get_data: negative/zero signal-to-noise ratio {}!'
            string = string.format(SNR)
            raise AssertionError(string)
        # check for numerical errors
        with np.errstate(
                divide='raise', over='raise', under='raise',
                invalid='raise'):
            try:
                1 / ((1. / (3. * snr)) ** 2)
            except ZeroDivisionError as toosmall:
                string = 'get_data: (1 / 3 SNR) ** 2 with SNR = {} '
                string += 'gives division by zero!'
                string = string.format(snr)
                raise AssertionError(string) from toosmall
            except OverflowError as toolarge:
                string = 'get_data: (1 / 3 SNR) ** 2 with SNR = {} '
                string += 'gives overflow!'
                string = string.format(snr)
                raise AssertionError(string) from toolarge
            except FloatingPointError as unknown:
                string = 'get_data: (1 / 3 snr) ** 2 with SNR = {} '
                string += 'gives floating point error!'
                string = string.format(data['std'])
                raise AssertionError(string) from unknown
    # preserve signal-to-noise ratio
    data['snr'] = snr
    # assign data standard deviation
    data['std'] = 1. / (3. * snr)


# --- wavelet and noise --- wavelet and noise --- wavelet and noise ---


def mk_wavelet(name=WAVELETNAME, hwd=WAVELETHALFWIDTH, num=None):
    """
    Demo a wavelet contaminated with random noise.

    Parameters
    ----------
    name : char
        Type of wavelet. The default is WAVELETNAME.
    hwd : int
        Half width of wavelet. The default is WAVELETHALFWIDTH.
    num : int
        Figure number.

    Raises
    ------
    UserWarning
        Wavelet must be associated with a script computing it.

    Creates
    -------
    Display of a noise-contaminated wavelet.

    """

    def triangle(hwd=WAVELETHALFWIDTH):   # pylint:disable=unused-variable
        """
        Create a triangular wavelet.

        Parameters
        ----------
        hwd : int
            Half-length of a triangle in number of samples. The default is
            WAVELETHALFWIDTH.
            index 0         amplitude 0.
                  1                   1. / hwd
                  hwd                 1.
                  2 * hwd             0.

        Returns
        -------
        signal : list of float
            Samples of a triangular wavelet.

        """
        # ramp up
        signal = [1. / float(hwd) * iii for iii in range(1, hwd + 1)]
        # ramp down
        signal += [1. / float(hwd) * iii for iii in range(hwd - 1, 0, -1)]
        # return
        return signal

    # set wavelet
    try:
        eval(WAVELETS[name])   # pylint:disable=eval-used
    except KeyError as msg:
        string = "mk_wavelet: cannot find wavelet {}".format(name)
        print(string)
        raise AssertionError(msg) from msg
    # set wavelet indices
    if LEFTSIGNAL + 2 * hwd - 1 > RIGHTWAVELET:
        raise AssertionError('check LEFTSIGNAL + 2 hwd - 1 < RIGHTWAVELET!')
    if LEFTSIGNAL < 0:
        raise AssertionError('check LEFTSIGNAL > 0!')
    if RIGHTWAVELET < 0:
        raise AssertionError('check RIGHTWAVELET > 0!')
    # generate normally distributed random noise
    trace = data['std'] * rnd().standard_normal(RIGHTWAVELET)
    # mix wavelet and noise
    trace[LEFTSIGNAL:LEFTSIGNAL+2*hwd-1] += eval(WAVELETS[name])(hwd=hwd)   # pylint:disable=eval-used
    # plot data
    fig[num].del_line()
    fig[num].plt_line(y=trace, opt=WAVELETCOLOR)
    # adjust abscissa
    plt.xlim(left=1, right=RIGHTWAVELET)
    # adjust ordinate
    plt.ylim(bottom=-1.5, top=1.5)
    plt.xticks(ticks=[], labels=None)
    # check directory for wavelet
    if not os.path.isdir('wavelet'):
        os.mkdir('wavelet')
    # save printout
    plt.tight_layout()
    plt.savefig('wavelet/wavelet.eps', dpi=1200, format='eps')


# --- AVA curve and inversion --- AVA curve and inversion --- AVA curve ---


def replot_data_ava(mode=None, num=None):
    """
    Replot user-picked data.

    Needed by Jupyter to re-plot previously caught data points.

    Parameters
    ----------
    mode : char
        Operational mode.
        'ava' Produces an AVA curve based on a prior model.
        'data' Inputs AVA data points and produces a best-fitting AVA curve.
    num : int
        Figure number.

    Globals
    -------
    data : dict
        Data points.
        'amp' Data amplitude.
        'std' Data STD.
    ava : dict
        Posterior AVA curve.
        'amp' Amplitude.
        'amp+std' Amplitude plus STD.
        'amp-std' Amplitude minus STD.

    Creates
    -------
    Replot after-click data and AVA curve as needed by Jupyter.

    """
    # set axis
    plt.xlim(left=0., right=45.)
    plt.ylim(bottom=-1., top=+1.)
    # previous data points
    if 'DATA' in mode:
        for iii in range(len(data['amp'])):   # loop over all data points
            # plot data point
            plt.plot(data['deg'][iii], data['amp'][iii], DATACOLOR)
            # plot error bars 3 x uncertainty
            if 'DATA+' in mode:   # but not in data mode
                if not np.isnan(data['std']):   # and only with valid STD
                    xxx = [data['deg'][iii], data['deg'][iii]]
                    yyy = [
                        data['amp'][iii] - data['std'],
                        data['amp'][iii] + data['std']]
                    plt.plot(xxx, yyy, DATAERRORCOLOR)   # error bars
    # previous AVA curves
    if 'AVA' in mode:
        if len(ava['amp']) > 0:
            fig[num].plt_line(
                x=DEG, y=ava['amp'], key='amp', opt=AVACOLOR)
        if 'AVA+' in mode:
            for key in ['amp-std', 'amp+std']:
                if len(ava[key]) > 0:
                    fig[num].plt_line(
                        x=DEG, y=ava[key], key=key, opt=AVACOLOR)
    # exit figure
    exit_plot(env=PLOTENVIRONMENT)


def comp_gmat(deg=DEG):
    """
    Compute the Pdown-Pup reflection matrix.

    See Aki&Richards, Quantitative Seismology, Theory and Methods, I

    Parameters
    ----------
    deg : list
        Incidence angles. Default is DEG.

    Globals
    -------
    para : dict
        'vsp': S-to-P velocity ratio

    Returns
    -------
    gmat : numpy ndarray
        Reflection matrix of size nx3
    gmat2 : numpy ndarray
        Reflection matrix with each element squared.

    """
    # sanity check
    if not np.isfinite(para['vsp']):
        string = 'no S-to-P velocity ratio {}'.format(para['vsp'])
        raise AssertionError(string)
    # convert angle from degree to radiant
    rad = np.deg2rad(deg)
    # compute normalized Fréchet derivative
    # (in form of a matrix[angle, component])
    # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
    gmat = np.array([
        0.5 / np.cos(rad) ** 2,
        -4. * para['vsp'] ** 2 * np.sin(rad) ** 2,
        0.5 * (1. - 4. * para['vsp'] ** 2 * np.sin(rad) ** 2)],
        dtype=float)
    gmat = gmat.transpose()
    # square
    gmat2 = gmat ** 2
    # return
    return gmat, gmat2


def comp_coeff(mode=None):
    """
    Displays a theoretical AVA curve as computed from the prior.

    Parameters:


    Globals
    ----------
    para : dict
        'vsp' S-to-P velocity ratio.
    prior : dict
        'mod' Model.
        'cov' Covariance.
        'std' Standard deviation.

    Returns
    -------
    coeff : dict
        'amp' Amplitude.
        'amp+std' Amplitude + STD.
        'amp-std' Amplitude - STD.

    """
    # check mode
    if 'COEFF' in mode:
        # check sanity
        if not np.all(np.isfinite(prior['mod'])):
            string = 'comp_coeff: no prior model {}!'.format(prior['mod'])
            raise AssertionError(string)
        # get reflection matrix
        gmat, gmat2 = comp_gmat()
        # compute reflection coefficients
        # (in form of a vector[angle])
        coeff['amp'] = np.dot(gmat, prior['mod'])
        # check mode
        if 'COEFF+' in mode:
            # check sanity
            if not np.all(np.isfinite(prior['std'])):
                string = 'comp_coeff: no prior covariance {}!'
                string = string.format(prior['mod'])
                raise AssertionError(string)
            # compute reflection coefficients +/- standard deviation
            coeff['std'] = np.sqrt(np.dot(gmat2, prior['std'] ** 2))
            coeff['amp+std'] = coeff['amp'] + coeff['std']
            coeff['amp-std'] = coeff['amp'] - coeff['std']


def plot_all(mode=None, num=None):
    """
    Plot an AVA curve.

    Parameters
    ----------
    mode : char
        Operational mode.
        'ava' produces an AVA curve based on a prior model.
        'data' inputs AVA data points and produces a best-fitting AVA curve.

    Returns
    -------
    None.

    """
    # set axis
    plt.xlim(left=0., right=45.)
    plt.ylim(bottom=-1., top=+1.)
    # plot curve
    if 'COEFF' in mode:
        plt.plot(DEG, coeff['amp'], COEFFCOLOR)
    if 'COEFF+' in mode:
        for key in ['amp+std', 'amp-std']:
            if len(coeff[key]) > 0:
                plt.plot(DEG, coeff[key], COEFFCOLOR)
    # register clicks on data points
    if 'DATA' in mode:
        plt.gcf().canvas.mpl_connect(
            'button_press_event',
            lambda event: onclick(event, mode=mode, num=num))
    # check directory for AVA curve
    if not os.path.isdir('ava'):
        os.mkdir('ava')
    # save print figure
    plt.tight_layout()
    plt.savefig("ava/curve.eps", dpi=1200, format='eps')


def onclick(event, mode=None, num=None):
    """
    Controls a sequence of events after a user having clicked a data point.

    Captures user-picked data and, if sufficient data points are available,
    inverts those, constructs an inversion-based AVA curve and computes the
    posterior contrast.

    Parameters
    ----------
    event : Mouse_event
        Coordinates of a pick event.
    mode : char
        Operational mode, here, either 'data' or 'ava+data'
    num : int
        Figure number.

    Returns
    -------
    None.

    """
    if event.xdata and event.ydata:     # if triggered by in-the-box event
        # catch event
        catch_data(mode=mode, event=event)
        # invert for posterior model
        if 'AVA' in mode:
            # continue with inversion
            if len(data['amp']) >= 3:   # min 3 samples for inversion
                # invert AVA
                invert_ava(mode=mode)
                # compute new AVA curve
                comp_post_ava()
                # plot new AVA curve
                plot_post_ava(mode=mode, num=num)
                # compute posterior contrast
                get_poscon(mode=mode)
        # show curve + data points if any
        exit_plot(env=CANVASENVIRONMENT)


def catch_data(mode=None, event=None):
    """
    Capture incidence angle and amplitude of user-picked data.

    Parameters
    ----------
    data : dict
        'amp' amplitude
        'deg' incidence angles
    event : MouseEvent
        Coordinates of a pick event.

    Returns
    -------
    None

    """
    # preserve event coordinates
    data['deg'] += [event.xdata]
    data['amp'] += [event.ydata]
    data['nos'] = len(data['amp'])
    # plot data points
    if 'DATA' in mode:
        plt.plot(data['deg'][-1], data['amp'][-1], DATACOLOR)
    # plot 3 x uncertainty
    if 'DATA+' in mode:
        if not np.isnan(data['std']):
            xxx = [data['deg'][-1], data['deg'][-1]]
            yyy = [
                data['amp'][-1] - data['std'],
                data['amp'][-1] + data['std']]
            plt.plot(xxx, yyy, DATAERRORCOLOR)


def invert_ava(mode=None):
    """
    Invert AVA for posterior property contrasts.

    Parameters
    ----------
    mode : char
        Operational mode.

    Globals
    ----------
    data : dict
        'amp' amplitude
        'deg' incidence angles

    Creates
    -------
    post : dict
        'mod' model
        'cov' covariance
        'std' standard deviation

    Returns
    -------
    None.

    """

    def create_covariance(nos=None, mode=None, snr=SNR):
        """
        Make up a data covariance from a single-valued data standard deviation.

        Note, not true data covariance.

        Parameters
        ----------
        nos : int
            Number of data points and, hence, dimension of the data covariance.
        mode : char
            Operational mode.
        snr : float, optional
            Signal-to-noise ratio. The default is 1, the neutral value.

        Returns
        -------
        cov : np ndarray
            Covariance.

        """
        if '-' in mode:   # conventional
            # fake a covariance
            cov = np.diag([1.] * nos)   # fall back on neutral
            icov = cp(cov)              # short for inversion
            # return
            return cov, icov
        if '+' in mode:   # Bayesian
            if np.isnan(data['std']):
                # fake a covariance if necessary
                cov = np.diag([snr] * nos)         # fall back on default
                icov = np.diag([1. / snr] * nos)   # short for inversion
            else:
                # update to true data covariance!
                cov = np.diag([data['std'] ** 2] * nos)
                icov = np.diag([1. / (data['std'] ** 2)] * nos)
            # return
            return cov, icov
        # error
        sys.exit('programming error in create_covariance!')

    # compute reflection matrix
    gmat, _ = comp_gmat(deg=data['deg'])
    # create and invert covariance
    _, icov = create_covariance(nos=len(data['amp']), mode=mode)
    # compute posterior covariance
    post['cov'] = (   # initialize with data-controlled part
        np.matmul(
            np.matmul(
                np.transpose(gmat),
                icov),
            gmat))
    if 'AVA+' in mode:
        if not np.any(np.isnan(prior['cov'])):
            post['cov'] += (   # add model-controlled part
                np.linalg.inv(prior['cov']))
    post['cov'] = (   # invert to posterior uncertainty
        np.linalg.inv(post['cov']))
    # compute posterior standard deviation
    post['std'] = (   # posterior standard deviation
        np.sqrt(
            np.diag(post['cov'])))
    # compute weighted inversion amplitude
    amp = (   # initialize data-controlled part
        np.dot(
            np.matmul(np.transpose(gmat), icov),
            data['amp']))
    if 'AVA+' in mode:
        if not np.any(np.isnan(prior['cov'])):
            amp += (   # add model-controlled part
                np.dot(
                    np.linalg.inv(prior['cov']), prior['mod']))
    # compute posterior model = perform inversion
    post['mod'] = (   # normalized contrasts
        np.dot(post['cov'], amp))
    # print
    if DEBUG:
        # ### printout(text='posterior model:', vals=post)
        # ### printout(text='posterior contrast:', vals=poscon)
        pass


def comp_post_ava():
    """
    Plot a new AVA curve based on the posterior model.

    Returns
    -------
    None.

    """
    # convert incidence angles
    rad = np.deg2rad(DEG)
    # compute normalized Fréchet derivative
    # (in form of a matrix[angle, component])
    # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
    gmat = np.array([
        0.5 / np.cos(rad) ** 2,
        -4. * para['vsp'] ** 2 * np.sin(rad) ** 2,
        0.5 * (1. - 4. * para['vsp'] ** 2 * np.sin(rad) ** 2)],
        dtype=float)
    gmat = gmat.transpose()
    gmat2 = gmat ** 2
    # compute reflection coefficients
    # (in form of a vector[angle])
    ava['amp'] = np.dot(gmat, post['mod'])
    if not np.all(np.isnan(post['std'])):
        ava['std'] = np.sqrt(np.dot(gmat2, post['std']**2))
        ava['amp+std'] = ava['amp'] + ava['std']
        ava['amp-std'] = ava['amp'] - ava['std']


def plot_post_ava(mode=None, num=None):
    """
    Plot the AVA curve from the posterior model

    Parameters
    ----------
    mode : char, optional
        Operational mode. The default is None.

    Returns
    -------
    None.

    """
    # delete lines
    fig[num].del_line()
    # plot line
    if 'AVA' in mode:
        fig[num].plt_line(
            x=DEG, y=ava['amp'], key='amp', opt=AVACOLOR)
        if 'AVA+' in mode:
            if len(ava['amp+std']) > 0:
                fig[num].plt_line(
                    x=DEG, y=ava['amp+std'], key='amp+std',
                    opt=AVACOLOR)
                fig[num].plt_line(
                    x=DEG, y=ava['amp-std'], key='amp-std',
                    opt=AVACOLOR)


# -----------------------------------------------------------------------------


def get_input(   # pylint:disable=too-many-arguments
        vp1=np.NAN, vs1=np.NAN, rho1=np.NAN,
        dvp1=np.NAN, dvs1=np.NAN, drho1=np.NAN,
        vp2=np.NAN, vs2=np.NAN, rho2=np.NAN,
        dvp2=np.NAN, dvs2=np.NAN, drho2=np.NAN,
        snr=np.NAN, mode=None):
    """
    Prepare the input to plotting an AVA curve and invert AVA data.

    Parameters
    ----------
    mode : char
        Operational mode.

    Creates
    -------
        top :
            properties of the top halfspace
        bot :
            properties of the bottom halfspace
        back :
            properties of the background medium
        precon :
            properties of the prior contrast
        prior :
            properties of the prior (model)
        para :
            user defined parameters
            'vsp': S-to-P velocity ratio

    Returns
    -------
    None.

    """
    # compute top model
    get_medium(
        text='top medium: ', halfspace='top',
        vp=vp1, vs=vs1, rho=rho1,
        dvp=dvp1, dvs=dvs1, drho=drho1)
    # compute bottom model
    get_medium(
        text='bottom medium: ', halfspace='bot',
        vp=vp2, vs=vs2, rho=rho2,
        dvp=dvp2, dvs=dvs2, drho=drho2)
    # compute background
    get_back(mode=mode)
    # compute prior contrasts
    get_precon(mode=mode)
    # compute the normalized contrasts -> model, in Bayes' theory prior model,
    # and their covariance matrix
    get_prior(mode=mode)
    # collect data STD
    get_data(snr=snr)
    # collect parameters
    get_para()
    # init data


def get_para(vps=np.NAN):
    """
    Collect parameters.

    Parameters
    ----------
    vps : P-to-S velocity ratio

    Globals
    -------
    back : dict
        'mod' : Background medium.

    Creates
    -------
    para : dict
        'vsp' : S-to-P velocity ratio

    Returns
    -------
    None.

    """
    # switch between parameter or background input
    if np.isfinite(vps):
        # assign S-to-P velocity ratio from parameter
        para['vsp'] = 1. / vps
    else:
        # assign S-to-P velocity ratio from background
        para['vsp'] = back['mod'][IVS] / back['mod'][IVP]
    # print
    string = 'P-to-S velocity ratio:\n   vps = {:4.3f}\n'
    string = string.format(1. / para['vsp'])
    print(string)


# pylint:disable=invalid-name,too-many-arguments
def get_medium(text='', halfspace=None, **kwargs):
    """
    Collect input of seismic properties.

    Parameters
    ----------
    text : char, optional
        Title of error message if any
    halfspace : char
        Top or bottom halfspace. Value either 'top' or 'bot', respectively.
    vp : float, optional
        P-velocity. The default is np.NAN.
    vs : float, optional
        S-velocity. The default is np.NAN.
    rho : float, optional
        Density. The default is np.NAN.
    dvp : float, optional
        Standard deviation of P-velocity. The default is np.NAN.
    dvs : float, optional
        Standard deviation of S-velocity. The default is np.NAN.
    drho : float, optional
        Standard deviation of density. The default is np.NAN.

    Creates
    -------
    top/bot : dict
        'mod' model properties
        'cov' covariance of model properties
        'std' standard deviation of model properties

    """

    def boolint(bol):
        """
        Convert numpy boolean into integer.

            True : 1
            False : 0

        Parameters
        ----------
        bol : numpy boolean
            boolean

        Raises
        ------
        AssertionError
            not a numpy boolean

        Returns
        -------
        int
            1 if True, 0 if False

        """
        # protect against None
        if bol:
            # check numpy boolean
            if isinstance(bol, np.bool_):
                # return 1 if true, 0 if not
                return 1 if bol else 0
        raise AssertionError('invalid boolean {}!'.format(bol))   # bang

    def valid0(prop='vp', val=np.NAN):
        """
        Check P-velocity for stability.

        Parameters
        ----------
        prop : char, optional
            'vp' for P-velocity.
        val : float
            Value of P-velocity. The default is np.NAN.

        Raises
        ------
        AssertionError
            Stability criterion not met.

        Returns
        -------
        bool
            Pass / fail

        """
        vs = HALFSPACE[halfspace]['mod'][1]
        if np.isfinite(val):
            if not np.isnan(vs):   # compare with S-velocity
                if val <= np.sqrt(8. / 3.) * vs:   # stability criterion
                    string = text + prop + ' < sqrt(8 / 3) * vs!'
                    raise AssertionError(string)   # bang
        return True

    def valid1(prop='vs', val=np.NAN):
        """
        Check S-velocity for stability.

        Parameters
        ----------
        prop : char, optional
            'vs' for S-velocity.
        val : float
            Value of S-velocity. The default is np.NAN.

        Raises
        ------
        AssertionError
            Stability criterion not met.

        Returns
        -------
        bool
            Pass / fail.

        """
        vp = HALFSPACE[halfspace]['mod'][0]
        if np.isfinite(val):
            if not np.isnan(vp):   # compare with P-velocity
                if val >= np.sqrt(3. / 8.) * vp:   # stability criterion
                    string = text + prop + ' >= sqrt(3 / 8) * vp!'
                    raise AssertionError(string)   # bang
        return True

    def valid2(prop=None, val=np.NAN):
        """
        Check any parameter for a positive finite value.

        Parameters
        ----------
        prop : char, optional
            Property. The default is None.
        val : float
            Value of property. The default is np.NAN.

        Raises
        ------
        AssertionError
            Stability criterion not met.

        Returns
        -------
        bool
            Pass / fail.

        """
        if np.isfinite(val):
            if val <= 0.:   # stability criterion
                string = text + prop + ' <= 0!'
                raise AssertionError(string)   # bang
        return True

    def valid(prop=None, val=np.NAN):
        """
        Switch for checking stability criteria.

        Parameters
        ----------
        prop : char
            Property. The default is None.
        val : float
            Value of property. The default is np.NAN.

        Raises
        ------
        AssertionError
            Invalid property or value.

        Returns
        -------
        bool
            Pass / fail all required stability criteria (of bang).

        """
        # list of validation functions
        validlist = {
            'vp': [valid0, valid2], 'vs': [valid1, valid2], 'rho': [valid2],
            'dvp': [valid2], 'dvs': [valid2], 'drho': [valid2]}
        # protect against None
        if val:
            # protext against non-number +/- Inf, NAN
            if np.isfinite(val):
                # return True if valid, False if not
                return (
                    np.all([
                        valid(prop=prop, val=val)
                        for valid in validlist[prop]
                    ])
                )
        string = 'no valid property {} or value {}'.format(prop, val)
        raise AssertionError(string)   # bang

    # list of properties = keys
    keys = kwargs.keys()
    # check against known properties
    for index, prop in enumerate(PROP):
        if prop in keys:
            HALFSPACE[halfspace]['mod'][index] = (
                [np.NAN, float(kwargs[prop])]           # value alternatives
                [boolint(valid(prop, kwargs[prop]))])   # index
    # check against known property uncertainties
    for index, prop in enumerate(DPROP):
        if prop in keys:
            HALFSPACE[halfspace]['std'][index] = (
                [np.NAN, float(kwargs[prop])]           # value alternatives
                [boolint(valid(prop, kwargs[prop]))])   # index
            HALFSPACE[halfspace]['cov'] = (
                np.diag(HALFSPACE[halfspace]['std'] ** 2))


def get_back(mode=None):
    """
    Computes the background medium.

    Input are the elastic parameters of top and bottom halfspace.

    Globals
    -------
    top : dict
        Properties of the top medium.
    bot : dict
        Properties of the bottom medium

    Parameters
    ----------
    mode : char
        Operational mode

    Creates
    -------
    back : dict
        'mod' Model.
        'cov' ovariance.
        'std' Standard deviation.

    Returns
    -------
    None.

    """
    # compute the background model
    back['mod'] = (bot['mod'] + top['mod']) / 2.
    # compute the background STD
    back['std'] = np.sqrt(top['std'] ** 2 + bot['std'] ** 2) / 2.
    # compute the background covariance
    back['cov'] = np.diag(back['std'] ** 2)
    # print
    if DEBUG:
        if not isinstance(mode, NONETYPE):
            printout[mode](text='background:', vals=back)


def get_precon(mode=None):
    """
    Computes the prior contrast.

    Input are the elastic parameters of top and bottom halfspace.

    Globals
    -------
    top : dict
        Properties of the top medium.
    bot : dict
        Properties of the bottom medium

    Parameters
    ----------
    mode : char
        Operational mode

    Creates
    -------
    precon : dict
        'mod' Model.
        'cov' Covariance.
        'std' Standard deviation.

    Returns
    -------
    None.

    """
    # compute the prior contrast
    precon['mod'] = (bot['mod'] - top['mod'])
    # compute the prior contrast STD
    precon['std'] = np.sqrt(top['std'] ** 2 + bot['std'] ** 2)
    # compute the prior contrast covariance
    precon['cov'] = np.diag(precon['std'] ** 2)
    # print
    if DEBUG:
        if not isinstance(mode, NONETYPE):
            printout[mode](text='prior contrast:', vals=precon)


def get_prior(mode=None):
    """
    Computes the prior.

    Input are background and prior contrast.

    Globals:
        precon : dict
            Prior contrast.
        back : dict
            Background.
        top : dict
            Top medium.
        bot : dict
            Bottom medium.

    Parameters
    ----------
    mode : char
        Operational mode

    Creates
    -------
    prior : dict
        'mod' Model.
        'cov' Covariance.
        'std' Standard deviation.

    Returns
    -------
    None.

    """
    # compute the normalized contrast = prior
    prior['mod'] = precon['mod'] / back['mod']
    # compute the prior STD
    prior['std'] = (
        np.sqrt(
            ((bot['mod'] * top['std']) ** 2)
            +
            ((top['mod'] * bot['std']) ** 2))
        /
        (back['mod'] ** 2))
    # compute the pror covariance
    prior['cov'] = np.diag(prior['std'] ** 2)
    # print
    if DEBUG:
        if not isinstance(mode, NONETYPE):
            printout[mode](text='prior model:', vals=prior)


def get_poscon(mode=None):
    """
    Computes the posterior contrast.

    Input are the background and posterior (from AVA inversion).

    Globals
    -------
    back : dict
        Background
    post : dict
        Posterior

    Parameters
    ----------
    mode : char
        Operational mode

    Creates
    -------
    postcon : dict
        'mod' Model.
        'cov' Covariance.
        'std' Standard deviation.

    Returns
    -------
    None.

    """
    # compute the posterior contrast
    poscon['mod'] = (
        np.matmul(
            np.diag(back['mod']),
            post['mod']))
    # compute the posterior STD
    poscon['std'] = back['mod'] * post['std']
    # print
    if DEBUG:
        if not isinstance(mode, NONETYPE):
            printout[mode](text='posterior contrast:', vals=poscon)


def printout1(text=None, vals=None):
    """
    Print properties without standard deviation.

    Parameters
    ----------
    text : char
        Title of printout.
    vals : dict
        Property of printout.

    """
    # print title
    print(text)
    # generate format for data output and print
    string = f"{'   {:3s} = {{:+12.6f}}'}\n"*3
    string = string.format(*PROP)
    value = (
        sum([
            [vals['mod'][comp]]
            for comp in [IVP, IVS, IRHO]],
            [
        ])
    )
    print(string.format(*value))
    return string.format(*value)


def printout2(text=None, vals=None):
    """
    Print properties with standard deviation.

    Parameters
    ----------
    text : char
        Title of printout.
    vals : dict
        Property of printout.

    """
    # print title
    print(text)
    # generate format for data output and print
    string = f"{'   {:3s} = {{:+12.6f}} +/- {{:+12.6f}}'}\n"*3
    string = string.format(*PROP)
    value = (
        sum([
            [vals['mod'][comp], vals['std'][comp]]
            for comp in [IVP, IVS, IRHO]],
            [
        ])
    )
    print(string.format(*value))
    return string.format(*value)


# define printout options
printout = {'COEFF-DATA-AVA-': printout1, 'COEFF+DATA+AVA+': printout2}


# -----------------------------------------------------------------------------


def do_wvl(
        name=WAVELETNAME, hwd=WAVELETHALFWIDTH, snr=SNR, num=None, title=None):
    """
    Create and plot a wavelet made of the true signal and noise.

    Input is the signal-to-noise ratio and the signal form, currently limited
    to a triangle only.

    Parameters
    ----------
    name : char
        Name of wavelet. Must be defined as a function, too. Default is
        WAVELETNAME.
    hwd : int
        Half width of the wavelet. Default is WAVELETHALFWIDTH.
    snr : float
        Signal-to-noise ratio. Default is SNR.
    title : char
        Title of figure. Default is no title.
    num : int
        Figure number.

    Returns
    -------
    None.

    """
    # get data parameter
    get_data(snr=snr)
    # initialize figure
    init_plot(num=num, title=title)
    # prepare and plot wavelet
    mk_wavelet(name=name, hwd=hwd, num=num)
    # exit figure
    exit_plot(env=PLOTENVIRONMENT)


def do_avadata(mode=None, num=None, title=None):
    """
    Create an AVA curve from prior or interactively, then invert.

    Forward AVA simulation requires only the normalized contrasts of
    seismic properties and the S-to-P velocity ratio, not the seismic
    properties themselves. However, it is more intuitive to input seismic
    properties.
    Further, Bayesian inversion requires the respective uncertainties, that
    is the covariance of the normalized contrasts and that of the data.
    However, in a simplified approach, cross-dependendies are ignored.

    Parameters
    ----------
    mode : char
        Operational mode
    num : int
        Figure number.
    title : char
        Figure title.

    Returns
    -------
    None.
    """
    # initialize run
    get_input(
        vp1=VP1, vs1=VS1, rho1=RHO1,
        dvp1=DVP1, dvs1=DVS1, drho1=DRHO1,
        vp2=VP2, vs2=VS2, rho2=RHO2,
        dvp2=DVP2, dvs2=DVS2, drho2=DRHO2,
        snr=SNR, mode=mode)
    # compute AVA curve from prior
    comp_coeff(mode=mode)
    # initialize figure
    init_plot(num=num, title=title)
    # plot prior AVA curve, catch data points, invert, plot posterior AVA curve
    plot_all(mode=mode, num=num)
    # exit figure
    exit_plot(env=PLOTENVIRONMENT)


# --- main --- main --- main --- main --- main --- main --- main --- main ---


if __name__ == '__main__':
    # create a wavelet = signal + noise
    do_wvl(
        name=WAVELETNAME,       # currently limited to 'triangle', see globals
        hwd=WAVELETHALFWIDTH,   # any int > 0, see globals
        snr=SNR,                # default signal-to-noise ratio, see globals
        num=1,                  # figure number
        title='Triangular Wavelet with Noise Contamination')
    # create an AVA curve from a prior model, catch interactively data points
    # and invert for a posterior model, re-create the corresponding AVA curve
    do_avadata(
        mode='COEFF-DATA-AVA-', num=2, title='Classical AVA Analysis')
    do_avadata(
        mode='COEFF+DATA+AVA+', num=3, title='AVA Analysis under Uncertainty')
