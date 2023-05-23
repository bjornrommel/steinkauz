r"""
\section{Introduction}

Seismic instruments don't have a built-in null-line, that is they typically
do not show a perfect zero amplitude in a sound-less environment. Instead, the
null-line is determined from a seismic dataset. More precisely, since no
environment is free of noise, the null-line is defined to be the average of
infinitely many data samples of noise, without any seismic event.

Furthermore, noise, as an infinite number of independent and random events,
is typically assumed to be normally distributed. In fact, the central limit
theorem states that any distribution of random numbers, not necessarily
normally distributed random numbers, approach a normal distribution with
increasing sampling number. The point being, with increasing sampling number.
Consequently, the null-line of a large dataset can well be calibrated as the 
mean of that normal distribution.

However, sub-datasets -- our seismic records cut out of the entire dataset --
contain only a small number of samples. And even if the entire dataset is 
calibrated, the means of sub-datasets may not; there simply is no mechanism 
forcing each subset to be balanced. 
In fact, the means of such sub-datasets form themselves a normal
distribution around the mean of the dataset (or population in the language of
statisticians).

Consequently, we might well calibrate a seismic instruments from noise
samples recorded over weeks and months, with at least a 'large' sampling
number. However, once we have extracted seismic records over typically 8 to
10 seconds, their respective means will most likely not be zero.
"""
