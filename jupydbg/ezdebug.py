import traceback
class TbInspect:
    def __init__(self,*args):
        if not args:
            args = sys.exc_info()
        self.e,self.te,self.tb = args
    
    @classmethod
    def run(cls,f):
        try:
            f()
        except Exception:
            return TbInspect()
        
    def __str__(self):
        return """%s - %s\\n%s"""%(self.e,self.te,'\\n'.join(traceback.format_tb(self.tb)))
    
    def __getitem__(self,n):
        t = self.tb
        if t is None:
            return None
        i = n
        tbs = [t]
        while t.tb_next is not None and i!=0:
            t = t.tb_next
            tbs.append( t )
            i-=1
        f = tbs[n].tb_frame
        print(f.f_code.co_name)
        return f.f_locals

class Catch:
    def __init__(self,on_error='display'):
        if on_error == 'display':
            self.on_error = self._print
        elif on_error == 'globals':
            self.on_error = self._set_globals
        else:
            self.on_error = on_error

    def _print(self,tb):
        print(tb[-1])
            
    def _set_globals(self,tb):
        globals()['__tb'] = tb

    def __enter__(self):
        pass
    
    def __exit__(self,*args):
        self.on_error(TbInspect(*args))

        
# with Catch()
#  your function
#
# On Exception:
# __tb[-1] # depth of the frame"
