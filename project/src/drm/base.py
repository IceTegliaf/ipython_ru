from pymongo.objectid import ObjectId
from drm.connection import get_connection
import types
from drm.properties import LazyDoc
from drm.exceptions import ObjectDoesNotExist, UnknownDocumentRef
from django.utils.datastructures import SortedDict


def subclass_exception(name, parents, module):
    return type(name, parents, {'__module__': module})



class Options(object):
    
    def __init__(self, name, klass):
        self.props = SortedDict()
        self.name = name
        self.klass = klass
        self.exclude = []
        
    def add_property(self, name, prop):
        self.props[name] = prop
        
    def add_exclude(self, name):
        self.exclude.append(name)
        
        
    def propery_names(self):
        return self.props.keys()
        
    def properties(self):
        return self.props.items()


    
class Manager(object):
    
    def get_docs(self):
        return getattr(get_connection(), self.docs_name)
    docs = property(get_docs)
    
    def count(self):
        return self.docs.count()
    
    def get(self, **kwargs):
        doc = self.docs.find_one(kwargs)
        if not doc:
            raise self.docs_type.DoesNotExist()
        return self.docs_type( **doc )
         
    
    def delete(self, **kwargs):
        self.docs.remove(kwargs)
        
        
class BaseMongoDoc(type):
    
    def __new__(cls, name, bases, dct):
        klass =  type.__new__(cls, name, bases, {})
        

        opts = klass._meta = Options(name, klass)
        
        opts.exclude=dir(klass)
        
        for name, value in dct.items():            
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(klass, name, value)
            else:
                opts.add_exclude(name)
                setattr(klass, name, value)
        
        if name!="MongoDoc":
            if not hasattr(klass, 'objects'):
                klass.objects = Manager()

            klass.objects._meta = klass._meta            
            klass.DoesNotExist = subclass_exception('DoesNotExist', (ObjectDoesNotExist,), name)
            #load all props
            #klass._std_fields = [] #set(dir(klass))
             
            
            
        
            
        return klass
    


    
        

        

class MongoDoc(object):
    __metaclass__ = BaseMongoDoc
    
    
    def __init__(self, **kwargs):
        self._id=None
        for name, value in kwargs.items():
            if name!="_id" and isinstance(value, ObjectId):
                value = LazyDoc(self, value)
            setattr(self, name, value)
        
    def pre_save(self):
        pass

    def post_save(self):
        pass
    
    def _to_mongo(self, val):
        if isinstance(val, MongoDoc):
            if not val._id:
                raise UnknownDocumentRef(type(self), type(val))                 
            val = val._id
            
        if isinstance(val, types.ListType):
            val = [self._to_mongo(v) for v in val]
        
        return val
        
    
    def save(self):
        self.pre_save()        
        prepare = {}
        for name in set(dir(self)) - self._std_fields:
            val = getattr(self, name)
            if name=="_id" and not val: #skeep non _id
                continue
            prepare[name] = self._to_mongo(val)
            
#        print "save obj:", prepare
        self._id = self.objects.docs.save(prepare)        
        self.post_save()
        
    def __eq__(self, other):
        return self._id == other._id
    
    def __ne__(self, other):
        return self._id != other._id 