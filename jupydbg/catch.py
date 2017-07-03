import sys
import inspect
import traceback
import six
from .errdisp import AccordionTbFormatter
from IPython.core.display import HTML, display,Markdown
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython import get_ipython

shell = get_ipython()
 
import linecache

"""Magic to capture an error and interactively check the stacktrace.
Usage (from a jupyter notebook):

>>> from jupydbg import catch

>>> %%catch
<insert you buggy code here>>

then select the frame and click on the button next 
to the code
>>> % eval <expression using local variables of that frame>
"""

@magics_class
class CatchMagics(Magics):

    @line_magic
    def eval(self, line):
        if getattr(self,'lcl',None) is None:
            print('You need to set the environment firts by clicking on a stack button', file=sys.stderr)
            return
        if line:
            return eval(line,self.lcl,self.glb)
        return self.lcl

    @cell_magic
    def catch(self, line, cell):
        self.lcl = None
        self.glb = None
        display_stack = AccordionTbFormatter(self.set_vars)
        context = int(line or 1)
        try:
            shell.ex(cell)
        except Exception:
            etype,evalue,tb = sys.exc_info()
            display(display_stack(etype,evalue,tb.tb_next.tb_next))

    def set_vars(self,lcl,glb):
        self.lcl = lcl
        self.glb = glb

ip = get_ipython()

ip.register_magics(CatchMagics)
