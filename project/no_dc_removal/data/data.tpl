r"""
\section{Mean of an Infinite Dataset}

Let's do a numerical experiment assuming ideal noise. That is, the noise
samples follow a normal distribution with zero mean and one standard
deviation. Then, let me generate a large dataset of such noise samples.
Large, but nonetheless limited in size. Therefore, its mean will likely
deviate from zero (see Fig.~\ref{fig data mean}); and repeatedly generating
large datasets will likely yield slightly varying, but nonzero means. The
larger the dataset, the less variation there will be.

Although not likely a perfect zero, we define that mean as the desired
null-line of the instrument's ideal response. That is, we calibrate the
instrument response accordingly.

Now, let's cut the dataset into subsets called (seismic) records, each of which
typically contains some 1000's samples, or typically covers some 8 to 12s 
long. Although the entire dataset has been calibrated, the mean of each record 
is not (see Fig.~\ref{fig record mean}); indeed, the means fluctuate around the
null-line. In fact, the means form themselves a normal distribution (see 
Fig.~\ref{fig histogram}).

The means of any realization of a normally distributed set of random
numbers -- our records in the language of statistics -- are themselves normally 
distributed: the mean of means remains 0.0; and its standard deviation
decreases with $\sigma / \sqrt{n_{\text{record}}}$, where $\sigma$ is the standard 
deviation of random numbers individually. Strictly speaking, the entire dataset 
is, in fact, just one single realization of random numbers, albeit a large one;
and its mean is only close to the ideal 0.0 within a standard deviation of
$\sigma / \sqrt{n_{\text{dataset}}}$.
"""
