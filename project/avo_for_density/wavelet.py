# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 07:52:18 2021

@author: Bjorn
"""


# import
import os
import sys
import csv
from copy import deepcopy as cp
import numpy as np
from numpy.random import default_rng as rnd
import matplotlib.pyplot as plt
import config as cfg


# --- change --- change --- change --- change --- change --- change --- change


# parameters for the demo wavelet
WAVELET = 'triangle'   # type of wavelet
NWL = 10               # half-width of wavelet


# --- do not change below --- do not change below --- do not change below ---


# suppress traceback
if __name__ == '__main__':
    DEBUG = True
    sys.tracebacklimit = 5   # default number of traceback levels
else:                           # specifically for use with Jupyter
    DEBUG = True
    sys.tracebacklimit = 1000


def init_fig():
    """
    Initialize figure

    Returns
    -------
    None.

    """
    # close old figure
    plt.close(1)
    # set figure
    cfg.fig['fig'] = plt.figure(1)
    
    
def plot_wavelet(wavelet=WAVELET):
    """
    Demo a wavelet contaminated with random noise

    Parameters
    ----------
    wavelet : char
        Type of wavelet. The default is WAVELET as defined above.

    Raises
    ------
    UserWarning
        Wavelet must be associated with a script computing it.

    Creates
    -------
    Display of a noise-contaminated wavelet.

    """

    def triangle(nwl=NWL):
        """
        Create a triangular wavelet atop random noise.

        Parameters
        ----------
        nwl : int, optional
            Half-length of triangle in number of samples. The default is NWL.

        Returns
        -------
        signal : list of float
            Samples of a triangular wavelet.

        """
        # ramp up
        signal = [1. / float(nwl) * iii for iii in range(1,nwl+1)]
        # ramp down
        signal += [1. / float(nwl) * iii for iii in range(nwl-1,0,-1)]
        # return
        return signal

    # define wavelets
    wavelets = {'triangle': triangle}
    # set figure
    plt.figure(1)
    # create wavelet
    try:
        wavelets[wavelet]
    except KeyError as msg:
        string = "plot_wavelet: cannot find wavelet {wavelet:}"
        string = string.format(wavelet=wavelet)
        print(string)
        raise AssertionError(msg) from msg
    # generate normally distributed random noise
    trace = cfg.data['std'] * rnd().standard_normal(12*NWL)
    # mix wavelet and noise
    trace[2*NWL:4*NWL-1] += wavelets[wavelet](nnn=NWL)
    # plot data
    plt.plot(trace)
    # adjust abscissa
    plt.xlim(left=1, right=12*NWL)
    # adjust ordinate
    plt.ylim(bottom = -1.5, top=1.5)
    plt.xticks(ticks=[], labels=None)
    # show figure
    plt.show()
    # check directory for wavelet
    if not os.path.isdir('wavelet'):
        os.mkdir('wavelet')
    # save printout
    plt.tight_layout()
    plt.savefig('wavelet/wavelet.eps', dpi=1200, format='eps')


def read_data():
    # read AVA data
    with open('ava.dat', 'r') as file:
        lines = csv.reader(file, delimiter=" ")
        for line in lines:
            cfg.data['deg'] += [float(line[0])]
            cfg.data['amp'] += [float(line[1])]
        # invert AVA
        if len(cfg.data['amp']) >= 3:   # min 3 samples for inversion
            invert_ava()
            get_postcontrast()
            
            
def comp_ava():
    """
    Displays a theoretical AVA curve based on a given model.

    Catches click events to construct an observed AVA curve.

    Parameters
    ----------
    para : dict
        'vsp' S-to-P velocity ratio
        'deg' list of incidence angles
    prior : dict
        'mod' model
        'cov' covariance
        'std' standard deviation

    Creates
    -------
    Display of a theoretical AVA curve.

    Returns
    -------
    coeff : dict
        'amp' amplitude
        'deg' incidence angles

    """
    # check sanity
    if not np.all(np.isfinite(cfg.prior['mod'])):
        string = 'comp_ava: unknown prior model {}'.format(cfg.prior['mod'])
        raise AssertionError(string)
    # convert angle from degree to radiant
    rad = np.deg2rad(cfg.para['deg'])
    # compute normalized Fréchet derivative
    # (in form of a matrix[angle, component])
    # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
    gmat = np.array([
        0.5 / np.cos(rad) ** 2,
        -4. * cfg.para['vsp'] ** 2 * np.sin(rad) ** 2,
        0.5 * (1. - 4. * cfg.para['vsp'] ** 2 * np.sin(rad) ** 2)],
        dtype=float)
    gmat = gmat.transpose()
    # compute reflection coefficients
    # (in form of a vector[angle])
    cfg.coeff['amp'] = np.dot(gmat, cfg.prior['mod'])
    cfg.coeff['deg'] = cp(cfg.para['deg'])
    # init figure
    cfg.fig['fig']
    # plot curve
    plt.plot(cfg.coeff['deg'], cfg.coeff['amp'], 'b')
    # set axis
    plt.xlim(left=0., right=45.)
    plt.ylim(bottom=-1., top=+1.)
    # show figure
    plt.show()
    # register clicks on data points
    cfg.fig['fig'].canvas.mpl_connect('button_press_event', onclick)
    # save print figure
    plt.tight_layout()
    plt.savefig("curve.eps", dpi=1200, format='eps')


def onclick(event):
    """
    Capture user-picked data and invert AVA.

    Parameters
    ----------
    event : Mouse_event
        Coordinates of a pick event.

    Returns
    -------
    None.

    """
    if event.xdata and event.ydata:     # if triggered by in-the-box event
        # catch event
        catch_data(event=event)
        # invert AVA
        if len(cfg.data['amp']) >= 3:   # min 3 samples for inversion
            invert_ava()
            get_postcontrast()


def catch_data(event):
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
    Caught click events.

    """
    # preserve event coordinates
    cfg.data['deg'] += [event.xdata]
    cfg.data['amp'] += [event.ydata]
    # plot additional data point
    plt.plot(cfg.data['deg'][-1], cfg.data['amp'][-1], 'or')
    # plot 3 x uncertainty
    xxx = [cfg.data['deg'][-1], cfg.data['deg'][-1]]
    yyy = [
        cfg.data['amp'][-1] - cfg.data['std'],
        cfg.data['amp'][-1] + cfg.data['std']]
    plt.plot(xxx,yyy,'r')
    # show curve + data points if any
    event.canvas.draw()
    plt.show()


def invert_ava():
    """
    Invert AVA for posterior property contrasts

    Parameters
    ----------
    para : dict
        'vsp' S-to-P velocity ratio
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
    # extract number of data samples
    nos = len(cfg.data['amp'])
    # compute data uncertainty
    # (overkill, but designed to be made sample dependent later on)
    with np.errstate(
            divide='raise', over='raise', under='raise', invalid='raise'):
        try:
            cfg.data['cov'] = np.eye(nos, nos) * cfg.data['std'] ** 2
        except OverflowError as toolarge:
            string = 'invert_ava: SNR {} too small!'.format(SNR)
            raise AssertionError(string) from toolarge
        except FloatingPointError as unknown:
            string = 'invert_ava: converting STD {} to covariance!'
            string = string.format(cfg.data['std'])
            raise AssertionError(string) from unknown
    # compute inverse data uncertainty
    with np.errstate(
            divide='raise', over='raise', under='raise', invalid='raise'):
        try:
            cfg.data['icov'] = (
                np.linalg.inv(np.eye(nos, nos) * cfg.data['std'] ** 2))
        except np.linalg.LinAlgError as linalg:
            string = 'invert_ava: unknown error inverting data covariance\n{}!'
            string = string.format(cfg.data['cov'])
            raise AssertionError(string) from linalg 
    # convert to radiant
    rad = np.deg2rad(cfg.data['deg'])
    # compute normalized Fréchet derivative
    # (in form of a matrix[angle, component])
    # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
    gmat = np.array([
        0.5 / np.cos(rad) ** 2,
        -4. * cfg.para['vsp'] ** 2 * np.sin(rad) ** 2,
        0.5 * (1. - 4. * cfg.para['vsp'] ** 2 * np.sin(rad) ** 2)],
        dtype=float)
    gmat = gmat.transpose()   # column = data at angle, row = properties
    # compute posterior uncertainty
    cfg.post['cov'] = (   # initialize with data-controlled part
        np.matmul(
            np.matmul(
                np.transpose(gmat),
                cfg.data['icov']),
            gmat))
    cfg.post['cov'] += (   # add model-controlled part
        np.linalg.inv(cfg.prior['cov']))
    cfg.post['cov'] = (   # invert to posterior uncertainty
        np.linalg.inv(cfg.post['cov']))
    cfg.post['std'] = (
        np.sqrt(
            np.diag(cfg.post['cov'])))
    # compute weighted inversion amplitude
    amp = (   # initialize data-controlled part
        np.dot(
            np.matmul(np.transpose(gmat), cfg.data['icov']),
            cfg.data['amp']))
    amp += (   # add model-controlled part
        np.dot(
            np.linalg.inv(cfg.prior['cov']), cfg.prior['mod']))
    # compute posterior model = perform inversion
    cfg.post['mod'] = (   # normalized contrasts
        np.dot(cfg.post['cov'], amp))
    # print
    if DEBUG:
        printout(text='posterior model:', data=cfg.post)
    rad = np.deg2rad(cfg.para['deg'])
    # compute normalized Fréchet derivative
    # (in form of a matrix[angle, component])
    # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
    gmat = np.array([
        0.5 / np.cos(rad) ** 2,
        -4. * cfg.para['vsp'] ** 2 * np.sin(rad) ** 2,
        0.5 * (1. - 4. * cfg.para['vsp'] ** 2 * np.sin(rad) ** 2)],
        dtype=float)

    gmat = gmat.transpose()
    # compute reflection coefficients
    # (in form of a vector[angle])
    cfg.coeff['amp'] = np.dot(gmat, cfg.post['mod'])
    cfg.coeff['deg'] = cp(cfg.para['deg'])
    plt.plot(cfg.coeff['deg'], cfg.coeff['amp'],'g-')
    plt.show()
    


def prep_ava():
    """
    Prepare the input to plotting an AVA curve and invert AVA data.
    
    Creates
    -------
        cfg.top : 
            properties of the top halfspace
        cfg.bot :
            properties of the bottom halfspace
        cfg.back :
            properties of the background medium
        cfg.precon :
            properties of the prior contrast
        cfg.prior :
            properties of the prior (model)
        cfg.para :
            user-defined parameters

    Returns
    -------
    None.

    """
    # compute top model
    get_medium(
        text = 'top medium: ', halfspace='top',
        vp=VP1, vs=VS1, rho=RHO1,
        dvp=DVP1, dvs=DVS1, drho=DRHO1)
    # compute bottom model
    get_medium(
        text = 'bottom medium: ', halfspace='bot',
        vp=VP2, vs=VS2, rho=RHO2,
        dvp=DVP2, dvs=DVS2, drho=DRHO2)
    # compute background
    get_background()
    # compute prior contrasts
    get_precontrast()
    # compute the normalized contrasts -> model, in Bayes' theory prior model,
    # and their covariance matrix
    get_prior()
    # collect parameters
    get_parameter()
    
    
def get_parameter():
    """
    Collect parameters.
    
    Parameters
    ----------
    back : dict
        Background medium.
        
    Creates
    -------
    para : dict
        'vsp' : S-to-P velocity ratio
        'deg' : incidence angles
        'snr' : signal-to-noise ratio

    Returns
    -------
    None.

    """
    # assign S-to-P velocity ratio
    # (parameter in Bayes' theory)
    cfg.para['vsp'] = cfg.back['mod'][IVS] / cfg.back['mod'][IVP]
    # assign incidence angles
    # (actually another parameter in Bayes' theory
    cfg.para['deg'] = DEG
    # assign signal-to-noise ratio
    # (another parameter in Bayes' theory, but full covariance requires
    # knowing the number of data points)
    cfg.para['snr'] = SNR
    # check data standard deviation
    if SNR < 0.:
        string = 'get_parameter: negative signal-to-noise ratio {}!'
        string = string.format(SNR)
        raise AssertionError(string)
    with np.errstate(
            invalid='raise', over='raise', under='raise', divide='raise'):
        try:
            cfg.data['std'] = 1. / (3. * SNR)    # STD
        except ZeroDivisionError as toosmall:
            string = 'get_parameter: SNR {} too small!'.format(SNR)
            raise AssertionError(string) from toosmall
        except OverflowError as toolarge:
            string = 'get_parameter: SNR {} too large!'.format(SNR)
            raise AssertionError(string) from toolarge
        except FloatingPointError as floating:
           string = 'get_parameter: SNR {} ** 2!'.format(SNR)
           raise AssertionError(string) from floating
    
    
# pylint:disable=invalid-name,too-many-arguments
def get_medium(
        text='', halfspace=None,
        vp=np.NAN, vs=np.NAN, rho=np.NAN,
        dvp=np.NAN, dvs=np.NAN, drho=np.NAN):
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
    # check sanity
    if (vp <= 0.) or (vp <= np.sqrt(8. / 3.) * vs):
        print(text + '0 < vp < sqrt(8 / 3) * vs!')
        vp = np.NAN
    if (vs <= 0.) or (vs >= np.sqrt(3. / 8.) * vp):
        print(text + '0 < vs < sqrt(3 / 8) * vp!')
        vs = np.NAN
    if rho <= 0.:
        print(text + '0 < rho!')
        rho = np.NAN
    if dvp <= 0.:
        print(text + '0 < dvp!')
        dvp = np.NAN
    if dvs <= 0.:
        print(text + '0 < dvs')
        dvs = np.NAN
    if drho <= 0.:
        print(text + '0 < drho!')
        drho = np.NAN
    # create model
    HALFSPACE[halfspace]['mod'] = np.array([vp, vs, rho], dtype=float)
    HALFSPACE[halfspace]['std'] = np.array([dvp, dvs, drho], dtype=float)
    HALFSPACE[halfspace]['cov'] = np.diag(HALFSPACE[halfspace]['std'] ** 2)
    # print
    if DEBUG:
        printout(text=text, data=HALFSPACE[halfspace])


def get_background():
    """
    Computes the background medium.

    Input are the elastic parameters of top and bottom halfspace.

    Creates
    -------
    back : dict
        'mod' model
        'cov' covariance
        'std' standard deviation

    Returns
    -------
    None.

    """
    # compute the background
    # (auxiliary property, neither variable nor parameter in Bayes' theory)
    cfg.back['mod'] = (cfg.bot['mod'] + cfg.top['mod']) / 2.
    cfg.back['std'] = np.sqrt(cfg.top['std'] ** 2 + cfg.bot['std'] ** 2) / 2.
    cfg.back['cov'] = np.diag(cfg.back['std'] ** 2)
    # print
    if DEBUG:
        printout(text='background:', data=cfg.back)


def get_precontrast():
    """
    Computes the prior contrast

    Input are the elastic parameters of top and bottom halfspace.

    Creates
    -------
    precon : dict
        'mod' model
        'cov' covariance
        'std' standard deviation

    Returns
    -------
    None.

    """
    # compute the background
    # (auxiliary property, neither variable nor parameter in Bayes' theory)
    cfg.precon['mod'] = (cfg.bot['mod'] - cfg.top['mod'])
    cfg.precon['std'] = np.sqrt(cfg.top['std'] ** 2 + cfg.bot['std'] ** 2)
    cfg.precon['cov'] = np.diag(cfg.precon['std'] ** 2)
    # print
    if DEBUG:
        printout(text='prior contrast:', data=cfg.precon)


def get_prior():
    """
    Computes the prior.

    Input are background and prior contrast.

    Creates
    -------
    prior : dict
        'mod' model
        'cov' covariance
        'std' standard deviation

    Returns
    -------
    None.

    """
    # compute the normalized contrast = prior
    cfg.prior['mod'] = cfg.precon['mod'] / cfg.back['mod']
    cfg.prior['std'] = (
        np.sqrt(
            ((cfg.bot['mod'] * cfg.top['std']) ** 2)
            +
            ((cfg.top['mod'] * cfg.bot['std']) ** 2))
        /
        (cfg.back['mod'] ** 2))
    cfg.prior['cov'] = np.diag(cfg.prior['std'] ** 2)
    # print
    if DEBUG:
        printout(text='prior model:', data=cfg.prior)


def get_postcontrast():
    """
    Computes the posterior contrast.

    Input are the background and posterior (from AVA inversion)

    Creates
    -------
    postcon : dict
        'mod' model
        'cov' covariance
        'std' standard deviation

    Returns
    -------
    None.

    """
    # compute the posterior contrast
    cfg.poscon['mod'] = (
        np.matmul(
            np.diag(cfg.back['mod']),
            cfg.post['mod']))
    cfg.poscon['std'] = cfg.back['mod'] * cfg.post['std']
    # print
    if DEBUG:
        printout(text='posterior contrast:', data=cfg.poscon)


def printout(text=None, data=None):
    """
    Print properties.

    Parameters
    ----------
    text : char
        Title
    data : dict
        Property

    """
    # print title
    print(text)
    # generate format for data output and print
    string = f"{'   {:3s} = {{:10.6f}} +/- {{:8.6f}}'}\n"*3
    string = string.format(*PROP)
    value = (
        sum(
            [[data['mod'][comp], data['std'][comp]]
            for comp in [IVP, IVS, IRHO]],
            []))
    print(string.format(*value))
    return string.format(*value)


if __name__ == '__main__':
    # set switches
    DEBUG = True   # generate printouts
    #--------------------------------------------------------------------------
    # Forward AVA simulation requires only the normalized contrasts of
    # seismic properties and the S-to-P velocity ratio, not the seismic
    # properties themselves. However, it is more intuitive to input seismic
    # properties.
    # Further, Bayesian inversion requires the respective uncertainties, that
    # is the covariance of the normalized contrasts and that of the data.
    # However, in a simplified approach, let's input only the uncertainty of
    # the seismic properties and compute the covariance of the normalized
    # contrasts therefrom. Likewise, let's consider only a generic
    # signal-to-ratio. For both, cross-dependendies are ignored.
    # -------------------------------------------------------------------------
    # input seismic properties of the top medium and their uncertainties
    VP1, DVP1 = 2000, 20
    VS1, DVS1 = 1200, 20
    RHO1, DRHO1 = 2400, 50
    # input properties of the bottom medium
    VP2, DVP2 = 2500, 25
    VS2, DVS2 = 1500, 40
    RHO2, DRHO2 = 2600, 50
    # input signal-to-noise ratio
    SNR = np.sqrt(sys.float_info.min)
    SNR = np.sqrt(sys.float_info.max / 3.)
    SNR = 300
    # -------------------------------------------------------------------------
    # initialize figure
    init_fig()
    # prepare AVA curve from user input
    prep_ava()
    # compute AVA curve from user input and invert AVA data upon click event
    comp_ava()
