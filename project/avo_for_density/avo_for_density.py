# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 07:52:18 2021

@author: Bjorn
"""


# import
import os
import sys
import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt
import config as cfg


# default range of angles for the theoretical AVA curve
ANG = [float(iii) / 100. for iii in range(0,3001,100)]


# parameters for the demo wavelet
WAVELET = 'triangle'   # type of wavelet
NWL = 10               # half-width of wavelet


# indices
IVP, IVS, IRHO = 0, 1, 2


# debug switch
DEBUG = True


# --- do not change below --- do not change below --- do not change below ---


# suppress traceback
if not DEBUG:
    sys.tracebacklimit = 0


def comp_ava():
    """
    Display a theoretical AVA curve based on given priors.

    Parameters
    ----------
    mod : array of floats
        normalized vp, vs, and density contrasts
    vsp : float
        inverse P-to-S velocity
    angs : array of floats
        incidence angles, default given

    Returns
    -------
    None.

    """

    def catch_data(event=None):
        # preserve
        cfg.ang += [event.xdata]
        print(cfg.amp, type(cfg.amp))
        cfg.amp += [event.ydata]
        print('***')
        print(cfg.ang, cfg.amp)
        # plot data point
        plt.plot(event.xdata, event.ydata, 'or')
        # show curve + data points if any
        event.canvas.draw()
        plt.show()

    def onclick(event, vsp=cfg.vsp, snr=cfg.snr, est=cfg.est, prior=cfg.mod):
        """
        Mark and preserve clicked points in an AVA plot.

        Parameters
        ----------
        event : Mouse_event
            on-click event

        Returns
        -------
        None.

        """
        # catch event
        catch_data(event=event)
        # invert AVA
        invert_ava()

    # convert angle from degree to radiant
    rang = np.deg2rad(ANG)
    # compute normalized Fréchet derivative
    # (in form of a matrix[angle, component])
    # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
    gmat = np.array([
        0.5 / np.cos(rang) ** 2,
        -4. * cfg.vsp ** 2 * np.sin(rang) ** 2,
        0.5 * (1. - 4. * cfg.vsp ** 2 * np.sin(rang) ** 2)],
        dtype=float)
    gmat = gmat.transpose()
    # compute reflection coefficients
    # (in form of a vector[angle])
    cfg.coeff = np.dot(gmat, cfg.mod)
    # close old figure
    plt.close(1)
    # set figure
    fig = plt.figure(1)
    # plot curve
    plt.plot(ANG, cfg.coeff, 'b')
    plt.xlim(left=0., right=45.)
    plt.ylim(bottom=-1., top=+1.)
    # show figure
    plt.show()
    # register clicks on data points
    fig.canvas.mpl_connect('button_press_event', onclick)
    # save print figure
    plt.tight_layout()
    plt.savefig("curve.eps", dpi=1200, format='eps')


def plot_wavelet(wavelet=WAVELET):
    """
    Demo a wavelet contaminated with random noise

    Parameters
    ----------
    snr : float
        Signal-to-noise ratio. The default is 0..
    wavelet : char
        Type of wavelet. The default is WAVELET defined above.

    Raises
    ------
    UserWarning
        Wavelet must be associated with a script computing it.

    """

    def triangle(nnn=NWL):
        """
        Create a triangular wavelet.

        Parameters
        ----------
        nnn : int, optional
            Length of triangle in number of samples. The default is NWL.

        Returns
        -------
        signal : list of float
            Samples of a triangular wavelet.

        """
        # ramp up
        signal = [1. / float(nnn) * iii for iii in range(1,nnn+1)]
        # ramp down
        signal += [1. / float(nnn) * iii for iii in range(nnn-1,0,-1)]
        # return
        return signal

    # define wavelets
    wavelets = {'triangle': triangle}
    # close old figure
    plt.close(1)
    # set figure
    plt.figure(1)
    # create wavelet
    try:
        wavelets[wavelet]
    except KeyError as msg:
        string = "plot_wavelet: cannot find wavelet {wavelet:}"
        string = string.format(wavelet=wavelet)
        print(string)
        raise UserWarning(msg) from msg
    # generate normally distributed random noise
    trace = cfg.snr * default_rng().standard_normal(12*NWL)
    # mix wavelet and noise
    trace[2*NWL:4*NWL-1] += wavelets[wavelet](nnn=NWL)
    # plot data
    plt.plot(trace)
    # adjust abscissa
    plt.xlim(left=1, right=12*NWL)
    # adjust ordinate
    plt.ylim(bottom = -0.5, top=1.5)
    plt.xticks(ticks=[], labels=None)
    # show figure
    plt.show()
    # check directory for wavelet
    if not os.path.isdir('wavelet'):
        os.mkdir('wavelet')
    # save printout
    plt.tight_layout()
    plt.savefig('wavelet/wavelet.eps', dpi=1200, format='eps')


def invert_ava():
    print(cfg.amp)
    if len(cfg.amp) >= 3:
        # convert to radiant
        rang = np.deg2rad(cfg.ang)
        # compute normalized Fréchet derivative
        # (in form of a matrix[angle, component])
        # (see Aki&Richards, Quantitative Seismology, Theory and Methods, I)
        gmat = np.array([
            0.5 / np.cos(rang) ** 2,
            -4. * cfg.vsp ** 2 * np.sin(rang) ** 2,
            0.5 * (1. - 4. * cfg.vsp ** 2 * np.sin(rang) ** 2)],
            dtype=float)
        gmat = gmat.transpose()
        # compute uncertainty
        # initialize with data-controlled part
        print(cfg.amp)
        print(gmat)
        print(cfg.snr)
        cfg.post_cov = (
            np.matmul(
                np.matmul(
                    np.transpose(gmat), np.linalg.inv(cfg.snr)),
                gmat))
        # add model-controlled part
        cfg.post_cov += np.linalg.inv(cfg.prior_cov)
        # invert to posterior uncertainty
        cfg.post_cov = np.linalg.inv(cfg.post_cov)
        # initialize data-controlled part of inversion amplitude
        amp = (
            np.dot(
                np.matmul(np.transpose(gmat), np.linalg.inv(cfg.snr)),
                cfg.amp))
        # add model-controlled part
        amp += (
            np.dot(
                np.linalg.inv(cfg.prior_cov), cfg.prior_mod))
        # inversion
        cfg.post_mod = (
            np.dot(np.linalg.inv(cfg.post_cov), amp))
        print(cfg.post_cov)
        print(cfg.post_mod)


if __name__ == '__main__':
    # Forward AVA simulation requires only the normalized contrasts of 
    # seismic properties and the S-to-P velocity ratio, not the seismic 
    # properties themselves. However, it is more intuitive to input seismic
    # properties. 
    # -------------------------------------------------------------------------
    # input seismic properties of the top medium and their uncertainties
    VP1, DVP1 = 2000, 20
    VS1, DVS1 = 1500, 20
    RHO1, DRHO1 = 2400, 50
    # input properties of the bottom medium
    VP2, DVP2 = 2000, 20
    VS2, DVS2 = 1500, 20
    RHO2, DRHO2 = 2600, 50
    # input signal-to-noise ratio
    SNR = 0.05
    # compute the background
    cfg.back = np.array([VP1 + VP2, VS1 + VS2, RHO1 + RHO2]) / 2.
    cfg.vsp = cfg.back[IVS] / cfg.back[IVP]
    # compute the normalized contrasts -> model, in Bayes' theory prior model,
    # and the covariance matrix
    cfg.mod = np.divide(
        np.array([VP2 - VP1, VS2 - VS1, RHO2 - RHO1]),
        cfg.back)
    cfg.prior['mod'] = cfg.mod   # intentionally identical
    cfg.prior['cov'] = (
        np.diag(
            np.array([
                (VP2 * DVP1) ** 2 + (VP1 * DVP2) ** 2,        # 
                (VS2 * DVS1) ** 2 + (VS1 * DVS2) ** 2,
                (RHO2 * DRHO1) ** 2 + (RHO1 * DRHO2) ** 2])
            /                                                 # element-wise
            np.power(cfg.back, 4)))                           # back ** 4
    # compute reflection coefficients as forward problem
    cfg.coeff['amp'] = []
    cfg.coeff['ang'] = ANG
    # record the data and the signal-to-noise ratio -> data covariance
    cfg.data['amp'] = []
    cfg.data['ang'] = []
    cfg.data['cov'] = np.eye(3,3) * SNR ** 2   # covariance
    # compute AVA curve
    comp_ava()
