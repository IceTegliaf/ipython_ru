from pymongo.objectid import ObjectId
from drm.connection import get_connection, get_db
import types
from bisect import bisect
from drm.utils import to_json, get_value
from drm import exceptions
from drm.lazy import LazyDoc



def subclass_exception(name, parents, module):
    return type(name, parents, {'__module__': module})



class Options(object):
    
    def __init__(self, name, klass):
        self.props = []
        self.collection_name = name
        self.klass = klass
        self.exclude = ['__module__']
        
        
    def add_property(self, name, prop):
        prop.name = name
        self.props.insert(bisect(self.props, prop), prop)
        
    def add_exclude(self, name):
        if isinstance(name, types.ListType):
            for n in name:
                self.add_exclude(n)
        if name not in self.exclude: 
            self.exclude.append(name)
        
        
    def propery_names(self):
        return [prop.name for prop in self.props]
        
    def properties(self):
        return self.props
    
    def get_prop_by_name(self, name):
        #TODO: use local cache for performance
        for prop in self.props:
            if prop.name == name:
                return prop
        return None
    
#    def names_to_save(self):
#        print "klass:", self.klass
#        print "all:", dir(self)
#        print "exclude:", self.exclude
#        return list(set(dir(self.klass)) - set(self.exclude))


    
class Manager(object):
    
    def __init__(self):
        self._meta = None
    
    def get_collection(self):
        return getattr(get_db(), self._meta.collection_name)
    collection = property(get_collection)
    
    def count(self):
        return self.collection.count()
    
    def get(self, **kwargs):
        doc = self.collection.find_one(kwargs)
        if not doc:
            raise self._meta.klass.DoesNotExist()
        return self._meta.klass( **doc )
         
    
    def delete(self, **kwargs):
        self.collection.remove(kwargs)
        
        
class BaseMongoDoc(type):
    
    def __new__(cls, name, bases, dct):
        parents = [b for b in bases if isinstance(b, BaseMongoDoc)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return type.__new__(cls, name, bases, dct)
        
        
        module = dct.pop('__module__')
        klass = type.__new__(cls, name, bases, {'__module__': module})
                    
        opts = klass._meta = Options(name, klass)
        opts.exclude=dir(klass)
        
        for base in bases:
            if hasattr(base, "_meta"):
                opts.add_exclude(base._meta.exclude)
                
            for prop_name in dir(base):
                if prop_name == "documents":
                    continue
                
                value = getattr(base, prop_name)
                
                if not hasattr(value, "contribute_to_class"):
                    opts.add_exclude(prop_name)
            
        
        for prop_name, value in dct.items():
            if prop_name == "documents":
                continue
                            
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(klass, prop_name)
            else:
                opts.add_exclude(prop_name)
                setattr(klass, prop_name, value)

        if not hasattr(klass, 'documents'):
            klass.documents = Manager()
            opts.add_exclude('documents')

        klass.documents._meta = klass._meta            
        klass.DoesNotExist = subclass_exception('DoesNotExist', (exceptions.ObjectDoesNotExist,), name)
        opts.add_exclude('DoesNotExist')
        
        #load all props
        #klass._std_fields = [] #set(dir(klass))
        #self.inner_order
        return klass
    


    
        

        

class MongoDoc(object):
    __metaclass__ = BaseMongoDoc
    
    
    def __init__(self, **kwargs):
        self._id=None
        for name, value in kwargs.items():            
            prop = self._meta.get_prop_by_name(name)
            if prop:
                value = prop.clean(self, value)
#            else:
#                #dynamic props
#                if name!="_id" and isinstance(value, ObjectId):
#                    value = LazyDoc(self, value)
            setattr(self, name, value)
        
        #set default values
        for prop in self._meta.properties():
            if hasattr(self, prop.name):
                continue
            
            if prop.required:
                raise exceptions.ValueRequiredError(type(self).__name__, prop.name)            
            setattr(self, prop.name, prop.default_value())
                        
                    
    def pre_save(self):
        pass

    def post_save(self):
        pass
    
    def save(self):
        self.pre_save()        
        prepare = {}
        names_to_save = set(dir(self)) - set(self._meta.exclude)
        for name in names_to_save:
            
            value = get_value(self, name)
            
            if name=="_id" and not value: #skeep non _id
                continue           
            
            prop = self._meta.get_prop_by_name(name)
            if prop:
                value = prop.clean(self, value)
                if value:
                    value = prop.to_json( self, value )                
            else:           
                value = to_json(value)            
            prepare[name] = value
            
        self._id = self.documents.collection.save(prepare)
        self.post_save()
        
    def __eq__(self, other):
        return self._id == other._id
    
    def __ne__(self, other):
        return self._id != other._id 