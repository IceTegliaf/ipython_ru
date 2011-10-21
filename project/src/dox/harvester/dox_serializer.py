import urllib
from django.utils.encoding import force_unicode
import types

class Node(object):
    ESCAPE_VALUE = (("&", "&amp;"), ("<","&lt;"), (">","&gt;"), ('\\','\\\\'), ('"', '\\"'))
    ESCAPE_DATA = ((u"\x04", "\\x04"), )
    
    def __init__(self, name):
        self.name = name
        self.attrs=[]        
        self.childs = []
        self._data = None
        
    def set(self, name, value):
        if isinstance(value, types.BooleanType):
            value = "True" if value else "False"
        
        self.attrs.append((name,unicode(value)))
        
    def data(self, data):
        if isinstance(data, types.BooleanType):
            self._data = "True" if data else "False"
        else:
            self._data = data
        
    
    @staticmethod
    def escape_value(value):
        #TODO: may be regex faste?
        for v in Node.ESCAPE_VALUE:
            value = value.replace(*v)
        return value 
#        return urllib.quote(value, " ")

    @staticmethod
    def  escape_data(data):
        for v in Node.ESCAPE_DATA:
            data = data.replace(*v)
        return data 
 
        
        
    def to_string(self):
        out=["<%s" % self.name]
        if self.attrs:
            out.append(" ")
            out.append(" ".join([ '%s="%s"' % (name, Node.escape_value(value)) for name,value in self.attrs ]))
        out.append(">")
        
        if self._data:
            out.append("<![CDATA[")
            out.append(Node.escape_data(force_unicode(self._data)))        
            out.append("]]>")

        out+=[child.to_string() for child in self.childs]
        
        out.append("</%s>\n" % self.name)
        return "".join(out)


class Serialize(object):
    
    def __init__(self, packages):
        self.packages = packages
        self.stack = []
        self.last = None
        
    def begin(self, name):
        node = Node(name)
        if self.last:
            self.last.childs.append(node)
        self.last = node
        self.stack.append(node)
        return self                
        
    def end(self):
        self.stack.pop()
        if self.stack:
            self.last=self.stack[-1]
        else:
            self.last=None
            
    def set(self, name, value, skip_none = False):
        if skip_none and not value:
            return self
        self.last.set(name, value)
        return self

    def data(self, value):
        self.last.data(value)
        return self
        
        
    def add_object(self, vars, functions, classes):
        for var in vars:
            if not var.is_local():
                self.begin("import_attribute")\
                    .set("name", var.name)\
                    .set("type", var.type_name)\
                    .set("module", var.source_module())\
                    .end()

        for func in functions:
            if not func.is_local():                
                self.begin("import_function")\
                    .set("name", func.name)\
                    .set("module", func.source_module())\
                    .end()   
                                
        for cls in classes:
            if not cls.is_local():                
                self.begin("import_class").set("name", cls.name).set("module", cls.source_module())
                self.end()
                
             

        for var in vars:
            if var.is_local():
                self.begin("attribute").set("name", var.name).set("type", var.type_name)
                
                self.begin("value").data(var.value).end()
                self.end()


        for func in functions:
            if func.is_local():
                self.begin("function").set("name", func.name)
                spec = func.argspec
#                print "func:", func.name, spec
                self.set("args", spec.varargs, skip_none = True)
                self.set("kwargs", spec.keywords, skip_none = True)
                
                #TODO: check type="static"                 
                self.begin("doc").data(func.get_doc()).end()
                
                num=1
                for name in spec.args:
                    self.begin("argument").set("name", name)
                    pos = len(spec.args) - num
                    if spec.defaults and pos<len(spec.defaults):
                        value = spec.defaults[len(spec.defaults)-1-pos]
                        self.set("type", type(value).__name__)
                        
                        self.begin("value").data(value).end()
#                        self.set("value", value)
                    self.end()
                    num+=1
                
                                
                self.end()
                                
        for cls in classes:
            if cls.is_local():
                self.begin("class").set("name", cls.name).end()
                
                self.begin("doc").data(cls.get_doc()).end()
                
                self.add_object(cls.vars, cls.functions, cls.classes)
                
                

        
        
    def to_string(self):
        self.begin("dox:ipython_ru")\
            .set("xsi:schemaLocation", "dox.xsd")\
            .set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")\
            .set("xmlns:dox", "http://ipython.ru/dox/v1")
            
        root = self.last
        
        for pkg in self.packages:
            self.begin("package")\
                .set("name", pkg.name)\
                .set("version", pkg.version, skip_none = True)\
                .set("file", pkg.file)
            
            if pkg.import_error:
                self.set("error", pkg.import_error)
            else:
                #add doc
                self.begin("doc").data(pkg.get_doc()).end()
                
                #depends
                for depends in pkg.depending_on:
                    self.begin("depends").set("name", depends).end()
                
                #add attributes + function + classes
                self.add_object(pkg.vars, pkg.functions, pkg.classes)
                
            
            self.end()
        
        self.end()
        assert self.last==None
        
        return '<?xml version="1.0" encoding="utf-8"?>' + root.to_string()
 
            
        
        
        
        