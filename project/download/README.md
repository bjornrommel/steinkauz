# Steinkauz

Projekt Steinkauz: a series of notebooks on various topics of seismic data processing.
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bjornrommel/steinkauz/master)  

## Module steinkauz  

steinkauz.py is an iPython line/cell magics extension. It converts a LaTeX fragment, which it gets from a file or reads in from the notebook itself, into a PNG image. This PNG file will then be displayed inside the notebook. Key point being, that fragment can be updated in line with the results of computations made in that notebook. For details see the file documentation.

## Known Issue

If you intend, firstly, to display your notebook on mybinder and, secondly, use the documentclass article (or any documentclass not using the counter "chapter"), then, modify steinkauz.py as follows:

- remove the counter "chapter" from the list LATEXCOUNTER.

Reason being, mybinder.org, which uses an apparently old TeX-Live distribution, comes with a bug in the "standalone" class package. The command \begin{document} also defines \thechapter, but not the associated counter chapter. So, \ifdef{\thechapter}{\setcounter{chapter}{<value>}}{} bangs.

For that reason, steinkauz.py, as used in any of the notebooks presented on this repository, does not include that counter. Only the version here, in the folder "download", does.

## Modification

If you use any documentclass other than "article", then, modify steinkauz.py as follows:

- change the first line of TEMPLATE to \documentclass[class=<chosen documentclass>,preview=true]{standalone}.

## Collaboration and Support
 
You are invited to improve any notebook or even to donate one of your own making.

## Credit  

You can use the module and notebooks, but, please, give credit where credit is due.   

## Contact  

## Acknowledgements  

The module steinkauz has been inspired by Dan MacKinlay's latex_fragment (https://github.com/danmackinlay/latex_fragment)  
And, then, there are all the contributors to Jupyter Notebook!

