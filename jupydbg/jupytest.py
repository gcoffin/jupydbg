import importlib
import inspect
import linecache
import os
import sys
import traceback
import unittest
from .errdisp import display_stack

"""Jupyter interactive unittest runner.
Usage
%%test <your package/case or method>

If there is an error, open the stack, select
the frame and click on the button then
% eval <expression using local variables>
"""

import six

from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython.core.display import HTML, display,Markdown
from ipywidgets import FloatProgress, Accordion, Text, Label, VBox, HBox, Button, Layout
from ipywidgets import HTML as wHTML

class StackHelper(object):
    """a container that will be assigned the local variables from the
    selected function in the stack"""
    def __init__(self):
        self._s = None
        self._g = None

    def set(self,local_vars,global_vars):
        self._s = local_vars
        self._g = global_vars

    def __getattr__(self,attr):
        return self._s[attr]

    def __str__(self):
        return str(list(self._s.keys()))

    __repr__ = __str__

    def eval_(self,line):
        if self._s is None:
            raise Exception("StackHelper is not set")
        return eval(line,self._s,self._g)

class JupyterTestRunner(object):
    def __init__(self, var_store=None):
        self.var_store = var_store if var_store is not None else StackHelper()

    def run_suite(self,test_suite):
        count_test_cases = test_suite.countTestCases()
        progress = FloatProgress(min=0,max=count_test_cases,
                                      bar_style='success')
        display(progress)
        current = Text()
        display(current)
        error_display = Accordion()
        display(error_display)
        test_result = JupyTestResults(current, progress, error_display, self.var_store)
        test_suite.run(test_result)
        display(HTML("%d tests, %d errors, %d failures, %d skipped"%(
                    count_test_cases,
                    len(test_result.errors),
                    len(test_result.failures),
                    len(test_result.skipped))))

class RollbackImporter:
    """This is used to make sure that modules under test will be
    reloaded the next time they are imported.
    """
    def __init__(self):
        self.previousModules = sys.modules.copy()

    def rollback_imports(self,local_only=False):
        localpath = os.path.realpath('.') if local_only else ''
        
        for modname in sys.modules.copy().keys():
            if not modname in self.previousModules:
                path = getattr(sys.modules[modname],'__file__','')                
                if path.startswith(localpath):
                    # Force reload when modname next imported
                    del(sys.modules[modname])

IMPORTER = RollbackImporter()

class ModuleTestRunner(JupyterTestRunner):
    """Will run the test and display the results in the jupyter
    console. Select a function in the stack to populate the 
    var_store with its local variables"""
    def __init__(self,*names,**options):
        self.local_only = options.pop('local_only',False)
        super(ModuleTestRunner,self).__init__(**options)
        self.names = list(names)
        #for module in modules:
        #    self.add_module(module)

    def add(self,name):
        self.names.append(name)

    def run(self):
        IMPORTER.rollback_imports(self.local_only)
        test_suite = unittest.TestSuite()
        for name in self.names:
            #module = importlib.import_module(*moddesc)
            test_suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
        self.run_suite(test_suite)

SUCCESS,FAILURE,ERROR = 0,1,2
LEVELS = {SUCCESS: 'success',
          FAILURE: 'warning',
          ERROR:'danger'}

class JupyTestResults(unittest.TestResult):
    """A TestResult that makes callbacks to its associated GUI TestRunner.
    Used by BaseGUITestRunner. Need not be created directly.
    """
    def __init__(self, current, progress,error_display, var_store):
        unittest.TestResult.__init__(self)
        self.current = current
        self.progress = progress
        self.count_errors = 0
        self.count_success = 0
        self.level = SUCCESS
        self.error_display = error_display
        self.var_store = var_store

    def set_bar_style(self,level):
        if level>self.level:
            self.level = level
            self.progress.bar_style = LEVELS[self.level]

    def display_err(self,test,excinfo):
        (errtype,err,tb) = excinfo
        box = display_stack(errtype,err,tb,self.var_store.set)
        self.error_display.children += (box,)
        self.error_display.set_title(len(self.error_display.children)-1,str(test))

    def addError(self,test,err):
        super(JupyTestResults,self).addError(test,err)
        self.set_bar_style(ERROR)
        self.display_err(test,err)

    def addFailure(self,test,err):
        super(JupyTestResults,self).addFailure(test,err)
        self.set_bar_style(FAILURE)
        self.display_err(test,err)

    def addSuccess(self,test):
        super(JupyTestResults,self).addSuccess(test)
        self.count_success += 1

    def startTest(self,test):
        super(JupyTestResults,self).startTest(test)
        self.progress.value += 1
        self.current.value = str(test)

@magics_class
class JupytestMagics(Magics):

    @line_magic
    def eval(self, line):
        if line:
            return self.test_runner.var_store.eval_(line)
        return self.test_runner.var_store

    @line_magic
    def test(self, line):
        module = line.strip()
        self.test_runner = ModuleTestRunner(local_only=True)
        self.test_runner.add(line)
        self.test_runner.run()



ip = get_ipython()

ip.register_magics(JupytestMagics)
