# -*- coding: utf-8 -*-
r"""
Juypyter Notebook magic that
(1) wraps any LaTeX fragment into LaTeX'es pre-set pre- and postamble,
(2) replaces placeholders with substitute text, and
(3) processes all such generated LaTeX documents.
The LaTeX fragment can be input as line magic
    % steinkauz r\"\"\"<LaTeX>\"\"\",
as cell magic
    %% steinkauz
    r\"\"\"
        <LaTeX>
    \"\"\"
or through a TPL file. Principally, there is no limitation on the LaTeX input.

Docstring:
::

  %steinkauz [-o {reference,notebook,printout,setup,clean}] [-i DPI] [-m MAG] [-q PREDIR] [-p PREFILE] [-d TEXDIR]
                 [-f TEXFILE] [-a] [-n] [-s]
                 [entries [entries ...]]

Define the entry point -- and name -- of the magic.

Parameters
----------
line : str
    magic line input
cell : str
    magic cell input
local_ns :
    local enironment

Returns
-------
None.

positional arguments:
  entries               list of placeholders

optional arguments:
  -o <{reference,notebook,printout,setup,clean}>, --option <{reference,notebook,printout,setup,clean}>
                        use-for options
  -i DPI, --dpi DPI     DPI of PNG output
  -m MAG, --mag MAG     magnification of PNG output
  -q PREDIR, --predir PREDIR
                        directory containing file with user preamble
  -p PREFILE, --prefile PREFILE
                        file with user preamble
  -d TEXDIR, --texdir TEXDIR
                        directory containing file with LaTeX fragment
  -f TEXFILE, --texfile TEXFILE
                        file with LaTeX fragment
  -a, --assign          return PNG filename
  -n, --noshow          do not show PNG output
  -s, --show            show PNG output
  
There are options:
    "setup" for setting up a Steinkauz environment
    "notebook" for printing PNG output to screen within the Jupyter
        environment,
    "printout" for printing everything at current status to PDF
    "clean" for cleaning up unnecessary files

DPI and MAG specify the DPI and magnification of the PNG output, where higher
DPI and smaller MAG provide better resolution at higher expense in time and
disk space

2 Nov 2021
version 2.0.1
@author: Björn E. Rommel
"""


# --- do not change --- do not change --- do not change --- do not change ---


# imports
import os
import shutil
from copy import deepcopy as cp
from subprocess import run
import platform
import tempfile as tmp
from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_magic, line_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments
from IPython.core.magic_arguments import parse_argstring
from IPython import display as dsp
from IPython.core.magic import needs_local_scope
from PIL import Image as pil   # name collision!


# pylint disabler
# pylint: disable=too-many-lines                 # easier to copy
# pylint: disable=too-many-instance-attributes   # well, yes, no add classes
# pylint: disable=too-many-public-methods        # better so


# --- change --- change --- change --- change --- change --- change --- change



# default option for steinkauz (out of 'reference', 'notebook', 'printout')
# "notebook":
# when using Jupyter notebook, LaTeX fragments are either read in from line or
# cell input and written to TPL file, or they are read in from a TPL file;
# then, a tex file is produced; and finally a PNG image is output
# "printout":
# when compiling an entire LaTeX document, a master TeX file is processed, and
# a PDF file is output
# "reference":
# a master TeX file is processed (by the command 'latex') to produce a list of
# references ('aux' file)
OPTION = 'notebook'


# default dpi for screen output (note, always str)
DPI = str(150)


# default magnification on screen (note, always float)
MAGNIFICATION = float(1.0)


# absolute(!) default folder for all files
FOLDER = os.getcwd()   # also containing the Jupyter notebook


# default basename of files
TEXFILE = tmp.NamedTemporaryFile(delete=False)   # pylint: disable=consider-using-with
TEXFILE = TEXFILE.name
TEXDIR = tmp.gettempdir()


# default entries
ENTRIES = None


# user-defined preamble file
PREFILE = None
PREDIR = FOLDER


# user-written main file
MAINFILE = None
MAINDIR = FOLDER


# steinkauz directory
STEINKAUZDIR = os.path.join(FOLDER, '.steinkauz')


# template LaTeX wrapper for all fragments
TEMPLATE = r"""
    \documentclass[class=article,preview=true]{standalone}

    %% references
    \usepackage{xr}
    %%\externaldocument{MAINFILE}   % main file

    %% imports
    \usepackage{etoolbox}   % conditionals needed for checking counters
    \usepackage{import}   % subfiles with correct paths

    %% preamble file
    %%\input{PREFILE}   % user-specified preamble

    \begin{document}
    \IfFileExists{./INCOUNTER}{\input{./INCOUNTER}}{}%
    CELL%
    \IfFileExists{./OUTCOUNTER}{\input{./OUTCOUNTER}}{}%
    \end{document}
"""
TEMPLATE = TEMPLATE.replace('    ', '')   # remove formatting
TEMPLATE = TEMPLATE[1:-1]                 # remove EOL's

TEMPLATEFILE = os.path.join(FOLDER, STEINKAUZDIR, 'template.tex')


# delete folders including all files, if any, inside those folders
FOLDERDELETE = [r'.\.ipynb_checkpoints', r'.\__pycache__', r'.\.steinkauz']
# delete additional non-steinkauz and non-jupyter directories
FOLDERDELETE += []
# delete all files with postfixes as in MAINDELETE from folders MAINFOLDER
MAINDELETE = [
    'dvi', 'epi', 'eps', 'log', 'png', 'png64', 'ps', 'pyc', 'synctex',
    'synctex(busy)']
MAINFOLDER = ['.']
# delete all files with postfixes as in SUBDELETE in all sub directories
SUBDELETE = ['aux', 'pdf', 'tex']
SUBDELETE += MAINDELETE
# delete additional files anywhere
FILEDELETE = [
    'INCOUNTER', 'OUTCOUNTER', 'DATAMEAN',
    'RECORDSAMPLE', 'RECORDSTDRECORD', 'RECORDSTDTHEORY']


# --- change at your risk --- change at your risk --- change at your risk ---


# define LaTeX counters
LATEXCOUNTER = [
    'part', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph',
    'subparagraph','page','equation','figure', 'table', 'footnote',
    'mpfootnote', 'enumi', 'enumii', 'enumiii', 'enumiv']

# write out LaTeX counters
LATEXINSTRING = r"""\ifdef{{\the{placecounter:}}}"""
LATEXINSTRING += r"""{{\setcounter{{{placecounter:}}}{{{placevalue:}}}}}"""
LATEXINSTRING += r"""{{}}""" + """\n"""

# read in LaTeX counters
LATEXOUTSTRING = r"""\ifdef{{\the{placecounter:}}}"""
LATEXOUTSTRING += r"""{{\immediate\write16{{"""
LATEXOUTSTRING += """{placecounter:}"""
LATEXOUTSTRING += r"""=\arabic"""
LATEXOUTSTRING += """{{{placecounter:}}}}}}}"""
LATEXOUTSTRING += r"""{{}}""" + """\n"""

# set project data
PROJECTFILE = 'PROJECT'
PROJECT = {counter: 0 for counter in LATEXCOUNTER}


# operationg system
# https://stackoverflow.com/a/1857/6056880
PLATFORM = platform.system()


# PS -> EPS switch
# check for ps2eps from the CTAN repository
if shutil.which('ps2eps'):
    # if installed ...
    # call ps2eps on Linux, or
    # call perl <fully qualified name of the perl script> on Windows, or
    # call ps2eps on Windows if perl script in located in path and SHELL set
    # to True
    PS2EPSOPTION = {
        'Linux': ['ps2eps'],
        'Windows': ['perl', shutil.which('ps2eps')],
        ### 'Windows': ['ps2eps']   # with PS2EPSSHELL = True
        }
    # name command as PS2EPSCMD, a list(!)
    PS2EPSCMD = PS2EPSOPTION[PLATFORM]
    # flag the command option (for controlling program flow)
    PS2EPSFLAG = 'ps2eps'
else:
    # if not installed, assume ps2epsi from the ghostscript distribution on
    # both Linux and Windows
    PS2EPSCMD = ['ps2epsi']
    PS2EPSFLAG = 'ps2epsi'


# shell
# mybinder.org typiclly requires subprocess.run(shell=False)
# Windows mostly works either way, but note above PS2EPSSHELL
SHELL = False            # default
PS2EPSSHELL = SHELL      # special for ps2eps
### PS2EPSSHELL = True   # for ps2eps on Windows (if not invoked with perl)


# ghostscript switch
GSOPTION = {'Linux': ['gs'], 'Windows': ['gswin64c']}
GSCMD = GSOPTION[PLATFORM]
GSCMD += ['-dSAFER', '-dEPSCrop', '-sDEVICE=pngalpha']


# epstool
EPSCMD = ['epstool', '--copy', '--bbox']
# !! Note, epstool calls gswin32c; on Windows at least, copy gswin64c and
# rename it gswin32c !!

# suppress traceback (no need for user to see all that!)
### sys.tracebacklimit = 0    # default


# --- do not change below --- do not change below --- do not change below ---


# "If you want to create a class with a different constructor that holds
# additional state, then you should always call the parent constructor and
# instantiate the class yourself before registration:
# https://ipython.readthedocs.io/en/stable/config/custommagics.html

# The class MUST call this class decorator at creation time
# https://ipython.readthedocs.io/en/stable/config/custommagics.html
@magics_class
class Steinkauz(Magics):
    """
    Define a cell magic that processes *all* LaTeX input.

    Note, your LaTeX input is wrapped inside Steinkauz's pre-set pre- and
    postamble. Hence, you must(!) supply only the fragment between, but
    excluding, '\\begin{documentclass}[...]{...}' and '\\end{document}'.
    """


    def __init__(self, shell, project):
    ### def __init__(self, shell):   # for use without shell imports
        """
        Initialize the magic.

        Parameters
        ----------
        shell : TYPE
            DESCRIPTION.
        project : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # You must call the parent constructor
        # https://ipython.readthedocs.io/en/stable/config/custommagics.html
        super().__init__(shell)
        # preserve state
        self.project = cp(project) if project else dict()
                                          # externally provided LaTeX counters
        # initialize other variables
        self.option = cp(OPTION)          # process options, see above
        self.dpi = str(DPI)               # DPI resolution (str!)
        self.mag = float(MAGNIFICATION)   # magnification (float!)
        self.predir = cp(PREDIR)          # folder of user-defined preamble
        self.prefile = cp(PREFILE)        # user-defined preamble file
        self.texdir = cp(TEXDIR)          # working folder incl TeX file
        self.texfile = cp(TEXFILE)        # name of TeX file
        self.maindir = cp(MAINDIR)        # folder with main file
        self.mainfile = cp(MAINFILE)      # name of main file
        self.entries = cp(ENTRIES)        # arguments in line input
        self.fragment = None              # user-defined LaTeX fragment
        self.doc = None                   # completed LaTeX document
        self.png = None                   # png output
        self.assign = False               # assign PNG filename to variable
        self.show = True                  # display PNG graphics


    # pylint: disable=inconsistent-return-statements   # return only if asked
    @magic_arguments()
    @argument(
        '-o', '--option', type=str,
        choices=['reference', 'notebook', 'printout', 'setup', 'clean'],
        help='use-for options', default=cp(OPTION))
    @argument(
        '-i', '--dpi', type=str, help='DPI of PNG output', default=str(DPI))
    @argument(
        '-m', '--mag', type=str, help='magnification of PNG output',
        default=float(MAGNIFICATION))
    @argument(
        '-q', '--predir', type=str,
        help='directory containing file with user preamble',
        default=cp(FOLDER))
    @argument(
        '-p', '--prefile', type=str, help='file with user preamble',
        default=None)   
    @argument(
        '-d', '--texdir', type=str,
        help='directory containing file with LaTeX fragment',
        default=cp(TEXDIR))
    @argument(
        '-f', '--texfile', type=str, help='file with LaTeX fragment',
        default=cp(TEXFILE))
    @argument(
        '-t', '--maindir', type=str,
        help='directory containing main LaTeX document',
        default=cp(MAINDIR))
    @argument(
        '-u', '--mainfile', type=str, help='file with LaTeX document',
        default=cp(MAINFILE))
    @argument(
        '-a', '--assign', action='store_true', help='return PNG filename',
        default=False)
    @argument(
        '-n', '--noshow', dest='show', help='do not show PNG output',
        action='store_false', default=True)
    @argument(
        '-s', '--show', dest='show', help='show PNG output',
        action='store_true', default=True)
    @argument(
        'entries', type=str, nargs='*', help='list of placeholders',
        default=cp(ENTRIES))
    @needs_local_scope
    @line_cell_magic
    def steinkauz(self, line=None, cell=None, local_ns=None):   # pylint:disable=unused-argument
        """
        Define the entry point -- and name -- of the magic.

        Parameters
        ----------
        line : str
            magic line input
        cell : str
            magic cell input
        local_ns :
            local enironment

        Returns
        -------
        None.

        """

        # import local environment
        # https://stackoverflow.com/a/64020076/6056880
        # via needs_local_scope
        # transfer LaTeX line input to cell input
        line, cell = self.proc_cell(line=line, cell=cell)
        # extract options, placeholders, relative folder and base from command
        self.proc_args(args=parse_argstring(self.steinkauz, line))
        # extract counter
        self.proc_count()
        # work through
        proc_cmd = {
            'setup': self.proc_cmd_setup,
            'notebook': self.proc_cmd_notebook,
            'printout': self.proc_cmd_printout,
            'clean': self.proc_cmd_clean}
        pngfile = proc_cmd[self.option](cell=cell)
        # return
        if self.assign:      # return filename only if asked
            return pngfile
        return None


# -----------------------------------------------------------------------------


    # pylint: disable=no-self-use       # consistent notation for all ...
    # pylint: disable=unused-argument   # ... proc_<xxx>


    def proc_args(self, args=None):
        """
        Process the arguments.

        Parameters
        ----------
        args : list of str
            command line arguments

        Returns
        -------
        None.

        """
        # extract option
        self.option = cp(args.option)
        # extract DPI
        self.dpi = str(args.dpi)
        # extract magnification
        self.mag = float(args.mag)
        # extract TPL, TEX file
        self.texdir = cp(args.texdir)
        self.texfile = cp(args.texfile)
        # extract preamble file
        self.predir = cp(args.predir)
        self.prefile = cp(args.prefile)
        # extract main file
        self.maindir = cp(args.maindir)
        self.mainfile = cp(args.mainfile)
        # extract assignment switch
        self.assign = args.assign
        # extract show PNG switch
        self.show = args.show
        # extract placeholders
        self.entries = cp(args.entries)


    def proc_count(self):
        """
        Extract LaTeX counter assignments.

        Command line arguments are searched for <counter>=<int> and assign
        self.project[<counter>] = <int>.

        Returns
        -------
        None.

        """
        # loop through entries
        for entry in self.entries[::-1]:
            # split at equal sign
            split = entry.split('=')
            if len(split) == 2:
                # identify counter on left side of equal sign
                if split[0] in LATEXCOUNTER:
                    # check right side of equal sign being int
                    try:
                        int(split[1])
                    # catch error if not int
                    except ValueError:
                        # do not assign, but pass over
                        pass
                    else:
                        # assign to counter
                        self.project[split[0]] = int(split[1])
                        # remove from entries list
                        self.entries.remove(entry)


    def proc_cell(self, line=None, cell=None):
        """
        Convert LaTeX line fragment into cell fragment.

        Parameters
        ----------
        line : str
            magic line input
        cell : str
            magic cell input

        Returns
        -------
        line : str
            magic line input with LaTeX fragment removed
        cell : str
            magic cell input with LaTeX fragment prepended

        """
        # initialize LaTeX fragment
        fragment = None
        # check line
        if line:
            # split along r""" and """
            temp = None
            if 'r"""' in line:
                temp = line.replace('r"""','"""').split('"""')
            # extract fragment between r""" and either """ or end of line
            if temp:
                if len(temp) >= 2:       # at least one """ present
                    fragment = temp[1]   # assign to fragment
                    if 'r"""' in line:
                        line = (         # remove fragment from line
                            line.replace('r"""' + fragment + '"""', ''))
                    # add fragment to cell
                    cell = fragment + cell if cell else fragment
        # return fragment
        return line, cell


    def proc_status(self, cell=None):
        """
        Identify status of PNG versus TPL file: updateable or not.

        Parameters
        ----------
        cell : str
            unused

        Returns
        -------
        bool
            True / False for to be or not to be updated

        """
        # return True if there is cell input (by definition new input)
        if cell:
            return True
        # return True if any placeholder (by definition an update to the TPL)
        if self.entries:
            return True
        # get fully qualified filenames for TPL and PNG
        tplfile = self.fullname(folder=self.texdir, file=self.texfile+'.tpl')
        pngfile = self.fullname(folder=self.texdir, file=self.texfile+'.png')
        # return True if PNG does not exist
        if not os.path.isfile(pngfile):
            return True
        # return True if TPL older than PNG
        if os.path.getmtime(tplfile) > os.path.getmtime(pngfile):
            return True
        # otherwise, return False
        return False


# -----------------------------------------------------------------------------


    def proc_cmd_setup(self, cell=None):
        """
        Process the entire steinkauz stack of commands for option 'setup'.

        Parameters
        ----------
        cell : str
            unused

        Returns
        -------
        None.

        """
        # default
        template = TEMPLATE
        # set fully-qualified filename if prefile exisits
        if self.prefile:
            impstring = r'''\import'''
            predir = self.fulldir(folder=self.predir, tex=True)
            dirstring = r'''{''' + predir + r'''/}'''
            filestring = r'''{''' + self.prefile + r'''}'''
            template = (
                template.replace(
                    r'''%%\input{PREFILE}''',
                    impstring + dirstring + filestring))
        if self.mainfile:
            self.mainfile = (
                self.fullname(
                    folder=self.maindir,
                    file=self.mainfile,
                    tex=True))
            template = (
                template.replace(
                    r'''%%\externaldocument{MAINFILE}''',
                    r'''\externaldocument{''' + self.mainfile + r'''}'''))
        with open(TEMPLATEFILE, 'w') as file:
            file.write(template)


    def proc_cmd_notebook(self, cell=None):
        """
        Process the entire steinkauz stack of commands for notebook.

        Parameters
        ----------
        cell : str
            cell input

        Returns
        -------
        None.

        """
        if self.proc_status(cell=cell):
            # create a file providing current counters to LaTeX
            self.make_incnt()
            # create a file returning current counters from LaTeX
            self.make_outcnt()
            # get / write LaTeX fragment from / to tpl file
            self.prep_tpl(cell)   # assigning to self.fragment
            # create full LaTeX document
            self.make_doc()   # assigning to self.doc
            # write LaTeX document to tex file
            self.make_tex()
            # convert tex format with LaTeX into dvi format
            self.make_dvi()
            # convert dvi format with dvips into ps format
            self.make_ps()
            # convert ps format with ps2eps or ps2epsi to eps format
            self.make_epxx()
            # convert eps / epi format with magick into png format
            self.make_png()
        # display PNG
        pngfile = self.show_png()
        # return
        return pngfile


    def proc_cmd_printout(self, cell=None):   # pylint:disable=unused-argument
        """
        Process the entire steinkauz stack of commands for option 'printout'.

        Parameters
        ----------
        cell : str
            unused

        Returns
        -------
        None.

        """
        # convert tex format with LaTeX into dvi format
        self.make_dvi()
        # convert dvi format with dvips into ps format
        self.make_ps()
        # convert ps format with ps2pdf into pdf format
        self.make_pdf()


    def proc_cmd_clean(self, cell=None):   # pylint:disable=unused-argument
        """
        Clean up entire package (for distribution).

        Parameters
        ----------
        cell : str
            unused

        Returns
        -------
        None.

        """

        def cleanfile(file):
            try:
                os.remove(file)
            except FileNotFoundError as msg:
                string = "!!! cleanfile: file {} not found !!!\n".format(file)
                print(string)
                raise UserWarning(msg) from msg
            except PermissionError as msg:
                string = "!!! cleanfile: file {} in use !!!\n".format(file)
                print(string)
                raise UserWarning(msg) from msg

        def cleanplusfile(file, delete=None):
            # clean if postfix in list
            postfix = file.split('.')[-1]
            if postfix in delete:
                cleanfile(file)

        def cleanfolder(folder):
            # clean out files
            for root, _, files in os.walk(folder):
                for file in files:
                    cleanfile(os.path.join(root, file))
            # delete folder
            try:
                os.rmdir(folder)
            except PermissionError as msg:
                string = "!!! cleanfolder: folder {folder:} in use !!!\n"
                string = string.format(folder=folder)
                print(string)
                raise UserWarning(msg) from msg
            except (OSError, FileNotFoundError) as msg:
                string = "!!! cleanfolder: folder {folder:} not found !!!\n"
                string = string.format(folder=folder)
                print(string)
                raise UserWarning(msg) from msg

        # delete all files in notebook tree
        for root, _, files in os.walk('.'):
            for file in files:
                # delete all file in FILEDELETE in any subfolder
                if file in FILEDELETE:
                    cleanfile(os.path.join(root, file))
                if root in MAINFOLDER:
                    # delete all MAINDELETE in MAINFOLDER
                    cleanplusfile(os.path.join(root, file), delete=MAINDELETE)
                else:
                    # delete all *.postfix in SUBDELETE in any subfolder
                    cleanplusfile(os.path.join(root, file), delete=SUBDELETE)
        # delete checkpoints including files
        for folder in FOLDERDELETE:
            cleanfolder(folder)


# -----------------------------------------------------------------------------


    def make_incnt(self):
        """
        Create a file providing the current LaTeX counters before execution.

        LaTeX counters are as defined in LATEXCOUNTER. Counters are checked
        whether they are defined in the current documentclass and, if not,
        blocked.

        Returns
        -------
        None.

        """
        # construct full name of COUNTER file
        counterfile = self.fullname(
            folder=self.texdir,
            file='INCOUNTER')
        # write to file
        with open(counterfile, 'w') as file:
            # create a series of LaTeX commands from project counters
            string = ''
            for counter in LATEXCOUNTER:
                string += LATEXINSTRING.format(
                    placecounter=counter,
                    placevalue=self.project[counter])
            # write out
            if string:
                file.write(string)


    def make_outcnt(self):
        """
        Create a file returning the current LaTeX counters after execution.

        LaTeX counters are as defined in LATEXCOUNTER. Counters are checked
        whether they are defined in the current documentclass and, if not,
        blocked. The content is static, though.

        Returns
        -------
        None.

        """
        counterfile = self.fullname(
            folder=self.texdir,
            file='OUTCOUNTER')
        with open(counterfile, 'w') as file:
            string = ''
            for counter in LATEXCOUNTER:
                string += LATEXOUTSTRING.format(placecounter=counter)
            file.write(string)


    def prep_tpl(self, cell=None):
        """
        Get or make a TPL file.

        Returns self.fragment, a cleaned up variant of the original cell input
        or the content of a TPL file if no cell input.

        Parameters
        ----------
        cell : str
            cell input through the Jupyter magic or None (to get from file)

        Returns
        -------
        self.fragment : str
            LaTeX fragment

        """

        def clean_cell(cell):
            """
            Clean up cell input

            Parameters
            ----------
            cell : str
                cell input through the Jupyter magic

            Returns
            -------
            cell : str
                without the final linefeed and string escapes

            """
            # remove "\n" at the end of a cell input
            while cell[-1] == '\n':
                cell = cell[0:-1]
            # remove 'r"""' at the start, '"""' at the end if any
            if cell[0:4] == 'r"""':
                cell = cell[5:-4]
            if cell[0:4] == "r'''":
                cell = cell[5:-4]
            # remove further "\n" if any
            while cell[0] == '\n':
                cell = cell[1:]
            while cell[-1] == '\n':
                cell = cell[0:-1]
            # return cell
            return cell

        # check cell input
        if cell:
            # write cell input to tpl file
            self.fragment = clean_cell(cell)
            self.put_tpl()
        else:
            # get tpl file
            self.get_tpl()
            self.fragment = clean_cell(self.fragment)


    def get_tpl(self):
        """
        Read the LaTeX fragment from a TPL file.

        Returns
        -------
        self.fragment : str
            LaTeX fragment

        """
        # define a tpl file
        tplfile = self.fullname(folder=self.texdir, file=self.texfile+'.tpl')
        # read the tpl file
        try:
            with open(tplfile, 'r') as file:
                self.fragment = file.read()
        except FileNotFoundError as msg:
            string = "!!! get_tpl: tplfile cannot be found !!!\n"
            string += "texdir: {}\n".format(self.texdir)
            string += "texfile: {}\n".format(self.texfile)
            print(string)
            raise UserWarning(msg) from msg


    def put_tpl(self):
        """
        Write the LaTeX fragment to a TPL file.

        Encapsulating all text into apostrophes is just a protection for
        strings being worked on in Python. Probably not strictly necessary in
        most case, but safer.

        """
        # define a tpl file
        tplfile = self.fullname(folder=self.texdir, file=self.texfile+'.tpl')
        # write the tpl file
        try:
            with open(tplfile, 'w') as file:
                out = self.fragment
                if out[0:4] != 'r"""':
                    out = 'r"""\n' + out + '\n"""'
                file.write(out)
        except FileNotFoundError as msg:
            string = "!!! put_tpl: tplfile cannot be found !!!\n"
            string += "texdir: {}\n".format(self.texdir)
            string += "texfile: {}\n".format(self.texfile)
            print(string)
            raise UserWarning(msg) from msg


    def make_doc(self):
        """
        Prepends a preamble, append closure to create a LaTeX doc.

        Parameters
        ----------
        fragment : str
            fragment input

        Returns
        -------
        self.doc : str
            LaTeX doc

        """
        # get the template
        with open(TEMPLATEFILE, 'r') as file:
            self.doc = file.read()
        # replace the cell placeholder
        self.doc = self.doc.replace("CELL", self.fragment)
        # replace any user-defined placeholders
        if self.entries:
            for entry in self.entries:
                if os.path.isfile(entry):
                    entryfile = entry
                elif os.path.isfile(os.path.join(STEINKAUZDIR, entry)):
                    entryfile = os.path.join(STEINKAUZDIR, entry)
                else:
                    string = "!!! make_doc: file not found !!!\n"
                    string += "entry: {}\n".format(entry)
                    raise UserWarning(string)
                with open(entryfile, 'r') as file:
                    inn = file.read()
                    self.doc = self.doc.replace(entry, inn)


    def make_tex(self):
        """
        Write out a TeX file.

        Returns
        -------
        None.

        """
        # construct full name of tex file
        texfile = self.fullname(folder=self.texdir, file=self.texfile+'.tex')
        # write LaTeX file
        if not self.doc:
            string = "!!! make_tex: LaTeX file appears empty !!!\n"
            string += "texfile: {}\n".format(texfile)
            raise UserWarning(string)
        with open(texfile, 'w') as file:
            file.write(self.doc)


    def make_dvi(self):
        """
        Create a DVI-formatted file from a TeX file.

        Returns
        -------
        None.

        """
        # construct full name of tex and dvi file
        texfile = self.fullname(
            folder=self.texdir, file=self.texfile+r'.tex', tex=True)
        # generate command
        dvidir = self.fulldir(folder=self.texdir)
        # LaTeX counters can be passed to latex through STDIN. Note, though,
        # setting the LaTeX counters must be delayed at least until
        # \documentclass has been processed. That is, a macro jupyter
        # containing setcounter definitions is passed in via STDIN, but
        # executed later by calling the macro \jupyter in the LaTeX doc.
        ### counters = [
        ###    r'\setcounter{' + counter + r'}{' + str(self.project[str(counter)])
        ###    + r'}'
        ###    for counter in LATEXCOUNTER]
        ### counters = counters[0:-1]
        ### stdin = r'\def\jupyter{'
        ### for counter in LATEXCOUNTER:
        ###    stdin += (
        ###        r'\setcounter{' + counter + r'}{' +
        ###        str(self.project[str(counter)]) + r'}')
        ### stdin += r'}'
        cmd = ['latex']
        ### cmd += [stdin]
        cmd += [r'-output-directory=' + dvidir, r'\input{' + texfile + r'}']
        self.run_cmd(cmd, shell=SHELL)
        ### cmd = [
        ###    'latex', '-interaction=batchmode', '-output-directory=' + dvidir,
        ###    texfile]
        self.run_cmd(cmd, shell=SHELL)


    def make_ps(self):
        """
        Create a PS formatted file from a DVI file.

        Returns
        -------
        None.

        """
        # construct full name of dvi and ps file
        dvifile = os.path.join(FOLDER, self.texdir, self.texfile+'.dvi')
        # run dvips generating a ps file
        cmd = ['dvips', dvifile]
        self.run_cmd(cmd, shell=SHELL)


    def make_pdf(self):
        """
        Create a PDF formatted file from a PS file.

        Returns
        -------
        None.

        """
        # construct full name of ps and pdf file
        psfile = os.path.join(FOLDER, self.texdir, self.texfile+'.ps')
        pdffile = os.path.join(FOLDER, self.texdir, self.texfile+'.pdf')
        # run dvips generating a ps file
        cmd = ['ps2pdf', psfile, pdffile]
        self.run_cmd(cmd, shell=SHELL)


    def make_epxx(self):
        """
        Create a EPS-formatted file from a PS file.

        Note, two alternatives: ps2eps from the CTAN repository or ps2epi
        from ghostscript.

        Raises
        ------
        UserWarning
            neither ps2eps or ps2epi found

        Returns
        -------
        None.

        """
        if PS2EPSFLAG == 'ps2eps':
            self.make_eps()
        elif PS2EPSFLAG == 'ps2epsi':
            self.make_epi()
        else:
            string = "!!! make_epxx: ps to eps converter {} not found !!!\n"
            string = string.format(PS2EPSFLAG)
            raise UserWarning(string)


    def make_eps(self):
        """
        Create a EPS-formatted file from a ps file.

        ps2eps creates two files with the postfixes eps and .eps.eps;
        overwrite the former by epstool (required?) or rename the latter.

        Returns
        -------
        None.

        """
        # construct full names of ps, eps and eps.eps files
        psfile = os.path.join(FOLDER, self.texdir, self.texfile+'.ps')
        epsfile = os.path.join(FOLDER, self.texdir, self.texfile+'.eps')
        epsepsfile = os.path.join(
            FOLDER, self.texdir, self.texfile+'.eps.eps')
        # convert ps to eps, although file named eps.eps
        cmd = list(PS2EPSCMD) + ['-f', psfile, epsfile]   # creating .eps.eps
        self.run_cmd(cmd, shell=PS2EPSSHELL)
        # correct bounding box and thereby copy .eps.eps back to .eps
        cmd = list(EPSCMD) + [epsepsfile, epsfile]
        self.run_cmd(cmd, shell=SHELL)


    def make_epi(self):
        """
        Create an EPI-formatted file from a ps file.

        ps2epsi creates a file with postfixes epi (with embedded image), but
        to be consistent with make_png let epstool output to eps.
        ps2epsi calculates bounding boxed wrongly; correct with epstool.

        Returns
        -------
        None.

        """
        # construct full name of ps, epi and eps file
        psfile = os.path.join(FOLDER, self.texdir, self.texfile+'.ps')
        epifile = os.path.join(FOLDER, self.texdir, self.texfile+'.epi')
        epsfile = os.path.join(FOLDER, self.texdir, self.texfile+'.eps')
        # convert ps to epi
        cmd = list(PS2EPSCMD) + [psfile, epifile]
        self.run_cmd(cmd, shell=SHELL)
        # correct bounding
        cmd = list(EPSCMD) + [epifile, epsfile]
        self.run_cmd(cmd, shell=SHELL)


    def make_png(self):
        """
        Create a PNG64-formatted file from an eps or epi file.

        magick recognizes the postfix png64 as request for full colour, but
        Jupyter uses the postfix png for every png flavour; rename.

        Returns
        -------
        None.

        """
        # construct full name of png64 and png file
        epsfile = os.path.join(FOLDER, self.texdir, self.texfile+'.eps')
        png64file = (
            os.path.join(FOLDER, self.texdir, self.texfile+'.png64'))
        pngfile = os.path.join(FOLDER, self.texdir, self.texfile+'.png')
        # convert eps to png
        ### cmd = [
        ###     'magick', '-density', self.dpi, '-quality', '100',
        ###     epsfile, png64file]
        # magick is not installed on mybinder; so, use convert
        # convert is blocked due to an old security vulnerability
        # https://stackoverflow.com/questions/42928765/convertnot-authorized-aaaa-error-constitute-c-readimage-453
        ### cmd = [
        ###     'convert', '-density', self.dpi, '-quality', '100',
        ###     epsfile, png64file]
        # so, use ghostscript directly
        res = '-r' + self.dpi
        # https://stackoverflow.com/a/60238216/6056880
        cmd = GSCMD + [res, '-o', png64file, epsfile]
        self.run_cmd(cmd, shell=SHELL)
        # read and resize PNG from file
        png = pil.open(png64file)
        # extract width and height
        width, height = png.size   # in pixels on file
        # resize
        png = png.resize(
            (int(round(self.mag*width)), int(round(self.mag*height))))
        # save as PNG, not PNG64
        png.save(pngfile)


    def show_png(self):
        """
        Display a PNG image.

        Returns
        -------
        None.

        """
        # construct full name of png file
        pngfile = os.path.join(FOLDER, self.texdir, self.texfile+'.png')
        # check file
        try:
            with pil.open(pngfile):
                pass
        except FileNotFoundError as msg:
            string = "!!! show_png: PNG not found !!!\n"
            string += "pngfile: {:s}\n".format(pngfile)
            print(string)
            raise UserWarning(msg) from msg
        # display
        if self.show:
            dsp.display(dsp.Image(filename=pngfile))
        # return
        return pngfile


# -----------------------------------------------------------------------------


    def run_cmd(   # pylint:disable=too-many-arguments
            self, cmd=None, shell=SHELL, capture_output=True, text=True,
            check=False, cwd=None):
        """
        Run a command possibly in a shell.

        For shell=True see https://stackoverflow.com/a/4616867; needed when
        running a built-in command on Windows.

        Check=False acceptable as return code is checked anyway.

        Parameters
        ----------
        cmd : [str, ...]
            command with options, with command line split into list of str's
            e.g.: command option file -> ['command', 'option', 'file']
        shell : boolean
            False / True, but True only for shell built-in commands
        capture_output : boolean
            True to capture stdout and stderr separately for error reporting
        text : boolean
            True to capture stdout and stderr as str's'
        check : boolean
            False to not raise an error; errors are checked programmatically
        cwd : str
            working folder

        Returns
        -------
        None.

        """

        def message(cmd=None, shell=None, cwd=None):
            string = "!!! run_cmd: check command to system !!!\n"
            string = "command: {}\n".format(cmd)
            string = "shell: {}\n".format(shell)
            string = "cwd: {}\n".format(cwd)
            return string

        # set folder
        if not cwd:
            cwd = os.path.join(FOLDER, self.texdir)
        # call system with command
        try:
            proc = run(
                cmd, shell=shell, capture_output=capture_output, text=text,
                check=check, cwd=cwd)
        except FileNotFoundError as msg:
            string = message(cmd=cmd, shell=shell, cwd=cwd)
            print(string)
            raise SystemExit(msg) from msg
        except OSError as msg:
            string = message(cmd=cmd, shell=shell, cwd=cwd)
            print(string)
            raise SystemExit(msg) from msg
        # extract LaTeX counter
        if cmd[0] == 'latex':                      # return from latex?
            lines = proc.stdout.split('\n')        # get list of lines
            for line in lines:                     # run line by line
                split = line.split('=')            # cut everything at '='
                if len(split) == 2:                # really counter + value?
                    if split[0] in LATEXCOUNTER:   # really a counter?
                        try:
                            int(split[1])          # value an int?
                        except ValueError:         # bang, value not int
                            pass                   # ignore if value not int
                        else:                      # right, assign
                            self.project[split[0]] = int(split[1])
        # check return code and abort if > 0
        if proc.returncode > 0:
            string = message(cmd=cmd, shell=shell, cwd=cwd)
            string += "!!! run_cmd: failed with return code {} !!!\n"
            string = string.format(proc.returncode)
            string += "stdout: {}".format(proc.stdout)
            string += "stderr: {}".format(proc.stderr)
            raise UserWarning(string)


    def fullname(self, folder=None, file=None, tex=False):
        """
        Create a fully qualified filename.

        Parameters
        ----------
        folder : str
            relative or absolute name of a folder
        file : str
            name of a file
        tex : bool
            switch to convert plattform-dependent name into TeX-like one

        Returns
        -------
        file : str
            fully-qualified filename

        """
        # make absolute folder
        folder = self.fulldir(folder=folder, tex=tex)
        # create fully qualified filename
        file = os.path.join(folder, file)
        # for use with tex
        if tex and (PLATFORM == 'Windows'):
            file = file.replace('\\', '/')   # Windows <-> TeX quirk
        # return
        return file


    def fulldir(self, folder=None, tex=False):
        """
        Create a fully-qualified directory.

        Parameters
        ----------
        folder : str
            relative or absolute name of a folder
        tex : bool
            switch to convert plattform-dependent name into TeX-like one

        Returns
        -------
        folder : str
            fully-qualified directory

        """
        # check folder: absolute or relative
        if not os.path.isabs(folder):
            # make folder absolute
            if folder == r'.':                          # if not subfolder
                folder = FOLDER                         # then just FOLDER
            else:                                       # if subfolder
                folder = os.path.join(FOLDER, folder)   # then create full path
        # make folder
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except FileExistsError as msg:
                string = "!!! fulldir: folder cannot be created !!!\n"
                string += "folder: {}\n".format(folder)
                print(string)
                raise UserWarning(msg) from msg
        # for use with tex
        if tex and (PLATFORM == 'Windows'):
            folder = folder.replace('\\', '/')   # Windows <-> TeX quirk
        # return
        return folder


# -----------------------------------------------------------------------------


    @line_magic
    def inputtoggle(self, line=None, text="Toggle Jupyter input on/off"):  # pylint:disable=unused-argument
        """
        Insert a toggle to switch Jupyter input on/off.

        Parameters
        ----------
        line : str
            ignored, but in line with line magics

        text : str
            text shown inside button

        Returns
        -------
        toggle : HTML
            submit button

        """
        # write Javascript code
        toggle = (
            r'''
                <script>
                    code_show=true;
                    function code_toggle() {
                        if (code_show){
                            $('div.input').hide();
                        } else {
                            $('div.input').show();
                        }
                        code_show = !code_show
                    }
                    $( document ).ready(code_toggle);
                </script>
                <form action="javascript:code_toggle()">
                    <input type="submit" value="XYZ">
                </form>
            ''')
        # replace text
        toggle = toggle.replace("XYZ", text)
        # display
        dsp.display(dsp.HTML(toggle))


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# register with a running Ipython
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension` can
    be loaded via `%load_ext module.path` or be configured to beautoloaded by
    IPython at startup time.
    (https://ipython.readthedocs.io/en/stable/config/custommagics.html )
    """

    # get project info
    project = cp(PROJECT)

    # setup .steinkauz directory
    if not os.path.isdir(STEINKAUZDIR):
        try:
            os.mkdir(STEINKAUZDIR)
        except FileExistsError as msg:
            string = "!!! load_ipython_extension: folder creation failed !!!\n"
            string += "STEINKAUZDIR folder {}\n".format(STEINKAUZDIR)
            print(string)
            raise UserWarning(msg) from msg

    # define version
    if not os.path.isfile('VERSION'):
        try:
            with open('VERSION', 'w') as file:
                file.write('{}'.format(1))
        except FileNotFoundError as msg:
            string = "!!! load_ipython_extension: VERSION file not found !!!\n"
            print(string)
            raise UserWarning(msg) from msg

    # write template
    try:
        with open(TEMPLATEFILE, 'w') as file:
            file.write(TEMPLATE)
    except FileNotFoundError as msg:
        string = "!!! load_ipython_extension: file not found !!!\n"
        string += "TEMPLATEFILE file {}\n".format(TEMPLATEFILE)
        print(string)
        raise UserWarning(msg) from msg

    # This class must then be registered with a manually created instance,
    # since its constructor has different arguments from the default:
    # (https://ipython.readthedocs.io/en/stable/config/custommagics.html)
    magics = Steinkauz(ipython, project)
    ### magics = Steinkauz(ipython)   # without locally provided project
    ipython.register_magics(magics)
