from drm.base import MongoDoc
from drm import properties
from django.utils.translation import ugettext_lazy as _


#TODO: implement Module (extends by MongoDoc) 
#TODO: implement Class (extends by MongoDoc) 
#TODO: implement Function (extends by MongoDoc) 
#TODO: implement Variable (extends by MongoDoc) 
#TODO: implement Excample (extends by MongoDoc) 

class Author(MongoDoc):
    name = properties.String( required=True)
    email = properties.String()

class License(MongoDoc):
    name = properties.String(required=True)
    
class PythonVersion(MongoDoc):
    version = properties.String()
    
class Source(MongoDoc):
    STATUS_NEW = 0
    STATUS_IMPORT_ERROR = 1
    STATUS_IMPORT_OK = 2        
    STATUS_PARSED = 3
    
    STATUS = (
        (STATUS_NEW,             _('STATUS_NEW')),
        (STATUS_IMPORT_ERROR,    _('STATUS_IMPORT_ERROR')),
        (STATUS_IMPORT_OK,       _('STATUS_IMPORT_OK')),
        (STATUS_PARSED,          _('STATUS_PARSED')),
    )
    
    path = properties.String()
    module_name = properties.String()
    published = properties.Boolean()
    status = properties.Integer(choices = STATUS, default=STATUS_NEW)
    
class Function(MongoDoc):
    name = properties.String(required=True)
    args = properties.String()
    doc = properties.String()

class Attribute(MongoDoc):
    name = properties.String(required=True)
    doc = properties.String()
    value = properties.String()
    

class Module(MongoDoc):
    name = properties.String(required=True)
    source_file = properties.String(required=True)
    parent = properties.Link('self')
    author = properties.Link(Author)
    module_license = properties.Link(License)
    version = properties.String()
    python = properties.Link(PythonVersion)
    
    
    doc = properties.String()
    functions = properties.ListOf( properties.Link(Function) )
    attributes = properties.ListOf( properties.Link(Attribute) )
    source = properties.Link(Source)