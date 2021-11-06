# -*- coding: utf-8 -*-
"""
Linear AVO-Inversion

@author: Björn E. Rommel
"""


# libraries
import numpy as np


def back_contrast(
        vp1=None, vp2=None, vs1=None, vs2=None, rho1=None, rho2=None):
    bg_vp = 0.5 * (vp1 + vp2)
    bg_vs = 0.5 * (vs1 + vs2)
    bg_rho = 0.5 * (rho1 + rho2)
    ct_vp = vp2 - vp1 
    ct_vs = vs2 - vs1
    ct_rho = rho2 - rho1 
    
def pdown_pup(
        vp0=None, vs0=None, rho0=None,
        ct_vp=None, ct_vs=None, ct_rho=None,
        ang=None):
    """
    Calculate linearized Pdown-Pup reflection coefficients.

    Parameters
    ----------
    vp0 : float
        background P velocity
    vs0 : float
        background S velocity
    rho0 : float
        background density
    ct_vp : float
        P velocity contrast
    ct_vs : float
        S velocity contrast
    ct_rho : float
        density contrast
    ang : np.array([float, ...])
        incidence angles

    Returns
    -------
    amp : float
        linearized Pdown-Pup reflection coefficient

    """
    # calculate ray parameter
    ray = np.sin(ang) / vp0
    # calculate coefficients
    coeff = np.full(3, np.NAN)
    coeff[0] = 0.5 * (1. - 4. * vs0 ** 2 * ray ** 2)
    coeff[1] = 0.5 / np.cos(ang) ** 2
    coeff[2] = -4. * vs0 ** 2 * ray ** 2
    # calculate normalized coefficients
    coeff[0] /= vp0
    coeff[1] /= vs0
    coeff[2] /= rho0
    # calculate reflection amplitude
    amp = coeff[0] * ct_vp + coeff[1] * ct_vs + coeff[2] * ct_rho
    # return
    return amp
