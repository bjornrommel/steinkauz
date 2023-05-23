# -*- coding: utf-8 -*-
"""
Created on Sun May 21 17:23:48 2023

@author: bjorn
"""


# import
from IPython.core.magic import register_line_magic
from IPython import display as dsp


# define magic
@register_line_magic
def inputtoggle(line=None, text="Toggle Jupyter input on/off"):  # pylint:disable=unused-argument
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
