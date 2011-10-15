# coding=utf8


try:
    from base import *
except ImportError, e:
    import traceback, sys
    sys.stderr.write('Unable to read settings/base.py\n')
    sys.stderr.write(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
    sys.stderr.write("%s\n" %e)
    sys.exit(1)
    
                
                
try:
    from local import *
except ImportError, e:
    import sys
    sys.stderr.write('Unable to read settings/local.py\nTry copy settings/dist.py to settings/local.py\n')
    sys.stderr.write("%s\n" %e)
    sys.exit(1)
    

#fix for DjangoEvolution
DATABASE_ENGINE = DATABASES['default']['ENGINE'].split(".")[-1]