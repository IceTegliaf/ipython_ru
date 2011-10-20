import sys
import types
from tools.class_loader import get_class_by_string, extract_module_name
import os
from dox.harvester.dox_serializer import Serialize

PYTHON_EXT = [".py", ".pyc", ".pyo"]

class Variable(object):
    
    def __init__(self, pkg, name):
        self.pkg = pkg
        self.name = name
    
    value = property(lambda self: getattr(self.pkg.mod, self.name))
    type = property(lambda self: type(self.value))


class VariableContainer(object):
    
    def __init__(self):
        self.vars = []
    
    def find_var(self, name):
        for var in self.vars:
            if var.name==name:
                return var
        return None 
            
    
class Class(Variable, VariableContainer):
    
    def is_ref(self):
        return self.value.__module__!=self.pkg.name
    
    
    
class Package(VariableContainer):
    VERSION_VARIANTS = ['__version__', 'version', 'VERSION']
    
    
    def __init__(self, spider, name):
        VariableContainer.__init__(self)
        
        self.spider = spider
        self.name = name
        self.file = ''
        self.classes = []
        self.import_error = None
        
    def get_version(self):
        for variant in Package.VERSION_VARIANTS:
            version = self.find_var(variant)
            if version:
                return version.value

        return ""
    version = property(get_version)
    

        
    def harvest(self):
        print "Run harvest for '%s'" % self.name

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
            
            if isinstance(value, types.ClassType):
                cls = Class(self, name)                
                self.classes.append(cls)
                
                self.spider.harvest_package(cls.value.__module__)
                continue
            
            #parse local vars
            if name == "__file__":
                self.file = self.spider.normalize_file_name(value)
                
            else:
                self.vars.append(Variable(self, name))
                
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
        
        self.base = package_name
                
        self.harvest_package(self.base)        
        
        
        
    def harvest_package(self, name):
        if not name.startswith(self.base):
            if name not in self.depending_on: 
                self.depending_on.append(name)
                
        elif name not in self.to_harvest and name not in self.harvested:
            self.to_harvest.append(name)
        
    def harvest(self):
        while self.to_harvest:
            pkg = Package(self, self.to_harvest.pop())
            self.harvested.append(pkg.name)
            pkg.harvest()
            self.packages.append(pkg)
            
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
            
        
            
            