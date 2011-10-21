import sys
import types
from tools.class_loader import get_class_by_string, extract_module_name
import os
from dox.harvester.dox_serializer import Serialize
from inspect import isclass, getargspec

PYTHON_EXT = [".py", ".pyc", ".pyo"]

class Variable(object):
    
    def __init__(self, pkg, name):
        self.pkg = pkg
        self.name = name
    
    def get_doc(self):
        return self.value.__doc__
        
    doc = property(get_doc)
    value = property(lambda self: getattr(self.pkg.mod, self.name))
    type = property(lambda self: type(self.value))
    
    type_name = property(lambda self: type(self.value).__name__)
    
#    def value_is_object(self):
#        return isinstance(self.value, types.ObjectType)

    def is_local(self):
        if hasattr(self.value, "__module__"):
            return self.value.__module__==self.pkg.name
        return True
    
    def source_module(self):
        if hasattr(self.value, "__module__"):
            return self.value.__module__
        return None
        
        
class Function(Variable):    
    
    argspec = property(lambda self: getargspec(self.value))



class VariableContainer(object):
    
    def __init__(self):
        self.vars = []
    
    def find_var(self, name):
        for var in self.vars:
            if var.name==name:
                return var
        return None
    
class ClassContainer():
    
    def __init__(self):
        self.classes = []
        
class FunctionContainer():
    
    def __init__(self):
        self.functions = []        
            
class Class(Variable, VariableContainer, FunctionContainer):
    pass

        
#    def is_ref(self):
#        return self.value.__module__!=self.pkg.name
    
    
    
class Package(VariableContainer, ClassContainer, FunctionContainer):
    VERSION_VARIANTS = ['__version__', 'version', 'VERSION']
    SKIP_VARS = ['__builtins__', '__name__', '__doc__', '__path__', '__package__']
    
    
    def __init__(self, spider, name):
        VariableContainer.__init__(self)
        ClassContainer.__init__(self)
        FunctionContainer.__init__(self)
        
        self.spider = spider
        self.name = name
        self.file = ''
        
        self.depending_on=[]
        self.import_error = None
        
    def get_version(self):
        for variant in Package.VERSION_VARIANTS:
            version = self.find_var(variant)
            if version:
                return version.value
        return ""
    version = property(get_version)
    
    def get_doc(self):
        return self.mod.__doc__
    
    def add_depending_on(self, name):
        if name not in self.depending_on:
            self.depending_on.append(name)
            
    
    

        
    def harvest(self):
#        print "Run harvest for '%s'" % self.name
        names = self.name.split(".")
        try:
            self.mod = __import__(self.name, {}, {}, [names[-1]])
        except Exception, e:
            self.import_error = e
            return
            
        for name, value in self.mod.__dict__.items():
            #find module
            if isinstance(value, types.ModuleType):
                self.spider.harvest_package(value.__name__)
                continue

            #class
            if isclass(value):
                cls = Class(self, name)                
                self.classes.append(cls)
                if not cls.is_local():                
                    self.spider.harvest_package(cls.source_module())
                continue
            
            #function
            if isinstance(value, types.FunctionType):
                func = Function(self, name)
                self.functions.append(func)
                if not func.is_local():                
                    self.spider.harvest_package(func.source_module())                
                continue
            
            #parse local vars
            if name == "__file__":
                self.file = self.spider.normalize_file_name(value)
                
            elif name not in Package.SKIP_VARS:
                v = Variable(self, name)
                
                if not v.is_local():
                    self.spider.harvest_package(v.source_module())
                self.vars.append(v)
                
        #scan files
        if os.path.basename(self.mod.__file__).startswith("__init__."): #scan all files
            base, dirs, files = os.walk(os.path.dirname(self.mod.__file__)).next()
                
            if "__init__.py" in files or "__init__.pyc" in files or "__init__.pyo" in files:
                #detect module
                for file_name in files:
                    for ext in PYTHON_EXT:
                        if file_name.endswith(ext):
                            package_name = file_name[:-len(ext)]
                            if package_name=="__init__":
                                continue
                            self.spider.harvest_package('%s.%s' % (self.name, package_name))
             

            
            
        
        
        
#        #---------        
#        print self.file
#        for var in self.vars:
#            print "    %s='%s'    \n    -----------------------------------------\n" % (var.name, var.value)
            
        
        
        
        
    
    

class Spider(object):
    
    def __init__(self, package_name):
        self.to_harvest = []
        self.harvested = []
        self.packages = []
        self.depending_on=[]
        self.current_pkg = None        
        self.base = package_name
                        
        self.harvest_package(self.base)        
        
        
        
    def harvest_package(self, name):
        if not name:
            return
        if not name.startswith(self.base):
            
            self.current_pkg.add_depending_on(name)
            
            if name not in self.depending_on: 
                self.depending_on.append(name)
                
        elif name not in self.to_harvest and name not in self.harvested:
            self.to_harvest.append(name)
        
    def harvest(self):
        while self.to_harvest:
            self.current_pkg = Package(self, self.to_harvest.pop())
            self.harvested.append(self.current_pkg.name)
            self.current_pkg.harvest()
            self.packages.append(self.current_pkg)
            
    def normalize_file_name(self, file_name):
        result = file_name
        for path in sys.path:
            if file_name.startswith(path):
                candidate = file_name[len(path):]
                if len(result)>len(candidate):
                    result = candidate
        return result
    
    
    def xml(self):
        return Serialize(self.packages).to_string()
            
        
            
            