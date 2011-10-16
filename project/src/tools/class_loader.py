import os
import sys

_class_loader_cache = {}


def get_module_name(model):
    mod_name =  model.__module__.lower()
    mod =  mod_name.split(".")
    if mod[0]=="apps":
        mod = mod[1]
    elif mod_name.startswith("django.contrib"):
        mod = "%s_%s" % (mod[0],mod[2])
    else:
        mod = mod[0]
    return mod


def extract_module_name(name):
    names = name.split(".")
    if len(names)<2:
        raise Exception("Can't found class name in string '%s'" % name)
    return ".".join(names[:-1]), names[-1], names[-2]
    


def get_class_by_string(name):
    global _class_loader_cache
    
    try:
        return _class_loader_cache[name]
    except:
        pass
    
    module_name, class_name, file_name = extract_module_name(name)
    
    klass = None
    try:
        mod = __import__(module_name, {}, {}, [file_name])
    except ImportError, e:
        raise ImportError("Error import '%s'\n%s" % (name, unicode(e)))
    
    if hasattr(mod, class_name):
        klass = getattr(mod, class_name)
        
    if not klass:
        raise Exception("Not found '%s' in '%s'" % (class_name, module_name))
    
    _class_loader_cache[name] = klass 
    return klass

def get_string_by_object(object):
    return "%s.%s" % (type(object).__module__, type(object).__name__)

def app_path_by_name(name):
    try:
        mod = sys.modules[name]
    except KeyError:
        names = name.split(".")
        mod_name = names[-1]
        try:
            mod = __import__(name, {}, {}, [mod_name])
        except Exception, e:
            raise Exception("Error import '%s'\n%s" % (name, unicode(e)))
    
    return os.path.dirname(mod.__file__)
