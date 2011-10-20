
class Node(object):
    
    def __init__(self, name):
        self.name = name
        self.attrs={}        
        self.childs = []
        self.data
        
    def set(self, name, value):
        self.attrs[name] = unicode(value)
        
    def data(self, data):
        self.data = data
        
        
    def to_string(self):
        out=["<%s" % self.name]
        if self.attrs:
            out.append(" ")
            out.append(" ".join([ '%s="%s"' % (name, value.replace('"','\\"')) for name,value in self.attrs.items() ]))
        out.append(">")

        out+=[child.to_string() for child in self.childs]
        
        out.append("</%s>" % self.name)
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
        return node                
        
    def end(self):
        self.stack.pop()
        if self.stack:
            self.last=self.stack[-1]
        else:
            self.last=None
            
    def set(self, name, value, skip_none = False):
        if skip_none and not value:
            return
        self.last.set(name, value)

    def data(self, name, value):
        self.last.data(name, value)
        
        
    def to_string(self):
        root = self.begin("dox:ipython_ru")
        self.set("xsi:schemaLocation", "dox.xsd")
        self.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.set("xmlns:dox", "http://ipython.ru/dox/v1")
        
        for pkg in self.packages:
            self.begin("package")
            self.set("name", pkg.name)
            self.set("version", pkg.version, skip_none = True)
            self.set("file", pkg.file)
            self.end()
        
        self.end()
        assert self.last==None
        
        return '<?xml version="1.0" encoding="utf-8"?>' + root.to_string()
 
            
        
        
        
        