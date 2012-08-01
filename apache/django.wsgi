import os
import sys


path = os.path.abspath(os.path.dirname(__file__))+'/..'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'as2.settings'


import django.core.handlers.wsgi


if False:
	class Debugger:

	    def __init__(self, object):
	        self.__object = object

	    def __call__(self, *args, **kwargs):
	        import pdb, sys
	        debugger = pdb.Pdb()
	        debugger.use_rawinput = 0
	        debugger.reset()
	        sys.settrace(debugger.trace_dispatch)

	        try:
	            return self.__object(*args, **kwargs)
	        finally:
	            debugger.quitting = 1
            sys.settrace(None)

	application = Debugger( django.core.handlers.wsgi.WSGIHandler() )
else:
	application = django.core.handlers.wsgi.WSGIHandler()
