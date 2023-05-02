# -*- coding: utf-8 -*-
"""
Symbolic computation of the linearized energy velocity and angle.

Date: 1.5.2023

@author: Björn Rommel (rommel@seisrock.com)
"""


import sympy as sp


# pylint:disable=invalid-name   # let's accept r2, r4


def main():
    """
    Calculate 3-term approximations of energy velocity, magnitude + angle.

    Returns
    -------
    none

    """
    # define symbolic parameters and variables
    r2, r4, theta, sin, cos = sp.symbols("r2, r4, theta, sin, cos")
    # define velocity
    vel = sp.sqrt(1 + r2 * sp.sin(theta) ** 2 + r4 * sp.sin(theta) ** 4)
    # define differential phase velocity
    dvel = sp.diff(vel, theta)
    dvel = dvel.factor()
    # output
    print("phase velocity:\n", vel)
    print("derivative of phase velocity:\n", dvel)
    # prepare for sympy
    vel = vel.replace(sp.sin(theta), sin)
    dvel = dvel.replace(sp.sin(theta), sin)
    dvel = dvel.replace(sp.cos(theta), sp.sqrt(1 - sin ** 2))
    # compute the squared energy velocity, magnitude
    mag2 = vel ** 2 + dvel ** 2                # Berryman
    mag2 = sp.series(mag2, x=sin, x0=0, n=6)   # Taylor of sin
    print("magnitude of squared energy velocity:\n", mag2)
    # compute the tangent
    num = vel * sin + dvel * cos
    denom = vel * cos - dvel * sin
    denom = denom.replace(sp.sqrt(1 - sin ** 2), cos)   # to facilitate next
    num = sp.expand(num / sin)
    denom = sp.expand(denom / cos)
    tan = num / denom
    tan = tan.replace(cos, sp.sqrt(1 - sin ** 2))
    tan = tan.expand().factor()
    tan = sp.expand(sp.series(tan, x=sin, x0=0, n=6))
    print("tangent of energy angle:\n", tan)


if __name__ == "__main__":
    main()
