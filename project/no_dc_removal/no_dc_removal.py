# -*- coding: utf-8 -*-
"""
Python code for the "No DC Removal" Notebook.

@author: Björn E. Rommel, version 2.1.0
"""


# imports
import sys
import math as mt
import numpy as np
import matplotlib.pyplot as plt
from numpy.random import default_rng


# constants
STD = 1.    # standard deviation of normal distribution
MEAN = 0.   # mean of normal distribution
# STD > 0 can be re-defined by the user
# MEAN will be removed by calibration


# --- do not change below --- do not change below --- do not change below ---


# suppress traceback
sys.tracebacklimit = 0


# create a normally distributed noise dataset
def dataset(ns_dat=None):
    """
    Create a dataset of normally-distributed noise.

    Success / failure is given in 'flag'. If a failure, then, most likely
    because of exceeding the limit on memory allocation.

    Parameters
    ----------
    ns_dat : int, ns_dat>1
        number of samples in the dataset
        ns_dat > 1 enforced by the data box itself
        ns_dat < system limit on memory allocation caught below

    Returns
    -------
    cal_data : numpy.ndarray
        ns_dat-many normally distributed random numbers with mean 0.0 and
        standard deviation STD

    """

    # prepare normally distributed data
    def _generate():
        # generate data
        try:
            rng = default_rng()
            data = rng.normal(loc=MEAN, scale=STD, size=ns_dat)
        # exit when memory allocation fails
        except MemoryError:
            data = None
            print("!!! Cannot allocate memory; reduce sample number !!!")
        # calculate the mean of data
        data_mean = np.mean(data)
        with open("DATAMEAN", 'w') as file:
            file.write("{:f}".format(data_mean))
        # return
        return data, data_mean

    # prepare graphics
    def _plot(data=None, data_mean=None):
        # close old figure
        plt.close(1)
        # set figure
        plt.figure(1)
        # plot data
        plt.plot(data[0:ns_dat], 'ob', markersize=1)
        # plot mean over data
        plt.plot([1, ns_dat], [data_mean, data_mean], 'r')
        # adjust abscissa
        plt.xlim(left=0, right=ns_dat)
        # adjust ordinate
        lim = mt.ceil(max(abs(data)))
        plt.ylim(bottom = -1*lim, top=lim)
        # show figure
        plt.show()
        # save printout
        plt.tight_layout()
        plt.savefig("dataset/mean.eps", dpi=1200, format='eps')

    # prepare calibrated data
    def _calibrate(data=None, data_mean=None):
        # calibrate
        cal_data = data - data_mean
        # return
        return cal_data

    # prepare data
    data, data_mean = _generate()
    # prepare graphics
    _plot(data=data, data_mean=data_mean)
    # prepare calibration
    cal_data = _calibrate(data=data, data_mean=data_mean)
    # return everything
    return cal_data


def record(data=None, ns_dat=None, ns_rec=None):
    """
    Calculate the means of all records.

    Parameters
    ----------
    data : numpy.ndarray
        dataset of normally distributed random numbers
    ns_dat : int
        number of samples in dataset
    ns_rec : int
        number of samples in records

    Returns
    -------
    rec_means : numpy.ndarray
        array of means, one per record
    rec_std : float
        standard deviation of means

    """

    # prepare analysis
    def _analyse():
        # save number of record samples
        with open("RECORDSAMPLE", 'w') as file:
            file.write("{:d}".format(ns_rec))
        # calculate number of records
        no_rec = int(np.floor(ns_dat / ns_rec))
        # calculate mean for each record
        rec_means = np.ndarray(no_rec)
        for iii in range(no_rec):
            left = iii * ns_rec                         # left index
            rite = (iii + 1) * ns_rec - 1               # right index
            rec_means[iii] = np.mean(data[left:rite])   # mean of record
        # calculate standard deviation
        rec_std = np.std(rec_means)
        with open("RECORDSTDRECORD", 'w') as file:
            file.write("{:f}".format(rec_std))
        # calculate theoretical standard deviation
        # (division by the spare root of the number of samples in record)
        std = np.sqrt(STD / ns_rec)
        with open("RECORDSTDTHEORY", 'w') as file:
            file.write("{:f}".format(std))
        # return
        return rec_means, rec_std

    # prepare graphics
    def _plot(rec_means=None):
        # close old figure
        plt.close(2)
        # set figure
        plt.figure(2)
        # plot record means
        for iii, mean in enumerate(rec_means):
            left = iii * ns_rec                         # left index
            rite = (iii + 1) * ns_rec - 1               # right index
            plt.plot([left, rite], [mean, mean], 'm')
        # adjust abscissa
        plt.xlim(left=0, right=ns_dat)
        # adjust ordinate
        lim = STD   # !!! needs more flexibility
        plt.ylim(bottom = -1*lim, top=lim)
        # show figure
        plt.show()
        # save print figure
        plt.tight_layout()
        plt.savefig("record/means.eps", dpi=1200, format='eps')

    # prepare analysis
    rec_means, rec_std = _analyse()
    # prepare graphics
    _plot(rec_means=rec_means)
    # return means
    return rec_means, rec_std


def histogram(rec_means=None, rec_std=None, ns_hist=50):
    """
    Plot a histogram of record means.

    Parameters
    ----------
    rec_means : numpy.ndarray
        array of means, one per record
    rec_std : float
        standard deviation of means
    ns_hist : int
        number of bins in histogram
        (could be more general, but here just that)

    """

    # prepare graphics
    def _plot():
        # determine range
        if ns_hist % 2 == 0:
            rlimit = ns_hist // 2 * rec_std
            llimit = -1. * rlimit
        else:
            llimit = (-1. * (ns_hist // 2) - 0.5) * rec_std
            rlimit = ((ns_hist // 2) + 0.5) * rec_std
        rec_range = [llimit, rlimit]
        # close old figure
        plt.close(3)
        # set figure
        plt.figure(3)
        # set up subplot
        ax1 = plt.subplot(111)
        # plot histogram
        _, bins, _ = ax1.hist(rec_means, range=rec_range, bins=ns_hist)
        # prepare second axis
        ax2 = ax1.twiny()
        # fake plot of nothing to get correct width
        ax2.plot(bins, [0]*(ns_hist+1), linestyle='None')
        # set axis annotation
        ax2.set_xlabel('standard deviation')
        xticks = [iii * rec_std for iii in range(-3, 4)]
        ax2.set_xticks(xticks)
        ax2.set_xticklabels(iii for iii in range(-3, 4))
        ax2.grid()
        # show figure
        plt.show()
        # save print figure
        plt.tight_layout()
        plt.savefig("histogram/bars.eps", dpi=1200, format='eps')

    # prepare graphics
    _plot()
