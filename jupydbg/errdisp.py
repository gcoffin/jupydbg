from ipywidgets import (FloatProgress, Accordion, Text, 
                        Label, VBox, HBox, Button, Layout, HTML, Accordion)
import linecache
import os

"""a module that displays the stack trace as jupyter widgets"""

class _TbInspect:
    def __init__(self,*args):
        if not args:
            args = sys.exc_info()
        self.e,self.te,self.tb = args
    
    def __iter__(self):
        t = self.tb
        while t is not None:
            f = t.tb_frame
            yield (f.f_code.co_filename,f.f_lineno,f.f_code.co_name,f.f_locals, f.f_globals)
            t = t.tb_next

class TracebackFormatter(object):
    def __init__(self,set_vars_callback):
        self.set_vars_callback = set_vars_callback

    def iter_stack(self,etype,evalue,excinfo):
        for filename,lineno,funname,local_vars,global_vars in _TbInspect(etype,evalue,excinfo):
            btn = Button(layout=Layout(width='10px'))
            def _set_vars(*args,lcl=local_vars,glb=global_vars):
                self.set_vars_callback(lcl,glb)
            btn.on_click(_set_vars)
            yield filename,lineno,funname,btn

class AccordionTbFormatter(TracebackFormatter):
    def __init__(self,set_vars_callback,len_context=3):
        super(AccordionTbFormatter,self).__init__(set_vars_callback)
        self.len_context=len_context

    def __call__(self,etype,evalue,excinfo):
        accordion = Accordion()
        stack = []
        titles = []
        for cnt,(filename,lineno,funname,btn) in enumerate(self.iter_stack(etype, evalue, excinfo)):
            if cnt>40:
                break
            titles.append("{}.{}".format(os.path.basename(os.path.splitext(filename)[0]),funname))
            code = []
            for i in range(lineno - self.len_context,lineno + 1 + self.len_context):
                code.append('<div style="{}">{}</div>'.format(
                        'color:#0c0' if i==lineno else '',
                        linecache.getline(filename,i).replace(' ','&nbsp;')))
            stack.append(
                VBox([HBox([Text(filename, layout=Layout(width='30em',margin="0")),
                            HTML(str(lineno), layout=Layout(width='5em')),
                            HTML(funname, layout=Layout(width='20em'))]),
                      HBox([btn,
                            HTML(''.join(code))])
                      ]))
        accordion.children = stack
        for i,t in enumerate(titles):
            accordion.set_title(i,t)
        return VBox([HTML("%s: %s"%(etype.__name__,evalue)),
                     accordion])
            


class TableTbFormatter(TracebackFormatter):
    def __call__(self,etype,evalue,excinfo):
        stack = [HTML("%s: %s"%(etype.__name__,evalue))]
        for filename,lineno,funname,btn in self.iter_stack(etype, evalue, excinfo):
            stack.append(HBox([btn,
                               VBox([
                                HBox([Text(filename, layout=Layout(width='30em',margin=0)),
                                      HTML(str(lineno), layout=Layout(width='5em')),
                                      HTML(funname, layout=Layout(width='20em'))]),
                                HTML(''.join(['<div style="{}">{}</div>'.format(
                                                'color:#0c0' if i==lineno else '',
                                                linecache.getline(filename,i).replace(' ','&nbsp;'))
                                              for i in [lineno-1,lineno,lineno+1]])
                                     )
                                ])
                               ]))
            return VBox(stack)


def display_stack(etype,evalue,excinfo,set_vars_callback):
    stack = [HTML("%s: %s"%(etype.__name__,evalue))]
    for filename,lineno,funname,local_vars,global_vars in _TbInspect(etype,evalue,excinfo):
        btn = Button(layout=Layout(width='10px'))
        def _set_vars(*args,lcl=local_vars,glb=global_vars):
            set_vars_callback(lcl,glb)
        btn.on_click(_set_vars)
        stack.append(HBox([btn,
                           VBox([
                            HBox([Text(filename, layout=Layout(width='30em',margin=0)),
                                  HTML(str(lineno), layout=Layout(width='5em')),
                                  HTML(funname, layout=Layout(width='20em'))]),
                            HTML(''.join(['<div style="{}">{}</div>'.format(
                                            'color:#0c0' if i==lineno else '',
                                            linecache.getline(filename,i).replace(' ','&nbsp;'))
                                            for i in [lineno-1,lineno,lineno+1]])
                                )
                            ])
                           ]))
    return VBox(stack)
        

def display_stack(etype,evalue,excinfo,set_vars_callback):
    accordion = Accordion()
    stack = []
    titles = []
    for filename,lineno,funname,local_vars,global_vars in _TbInspect(etype,evalue,excinfo):
        titles.append("{}.{}".format(os.path.basename(os.path.splitext(filename)[0]),funname))
        btn = Button(layout=Layout(width='10px'))
        def _set_vars(*args,lcl=local_vars,glb=global_vars):
            set_vars_callback(lcl,glb)
        btn.on_click(_set_vars)
        stack.append(
            VBox([   
                    HBox([Text(filename, layout=Layout(width='30em',margin=0)),
                          HTML(str(lineno), layout=Layout(width='5em')),
                          HTML(funname, layout=Layout(width='20em'))]),
                    HBox([btn,
                          HTML(''.join(['<div style="{}">{}</div>'.format(
                                            'color:#0c0' if i==lineno else '',
                                            linecache.getline(filename,i).replace(' ','&nbsp;'))
                                        for i in [lineno-1,lineno,lineno+1]])
                               )
                            ])
                           ]))
    accordion.children = stack
    for i,t in enumerate(titles):
        accordion.set_title(i,t)
    return VBox([HTML("%s: %s"%(etype.__name__,evalue)),
                 accordion])
