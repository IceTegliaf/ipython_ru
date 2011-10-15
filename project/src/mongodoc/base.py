from pymongo.objectid import ObjectId
from mongodoc.connection import get_connection
import types


def subclass_exception(name, parents, module):
    return type(name, parents, {'__module__': module})


class ObjectDoesNotExist(Exception):
    "The requested object does not exist"
    
    __unicode__ = lambda self: "The requested object does not exist"
    __str__= __unicode__

class UnknownDocumentRef(Exception):
    
    def __init__(self, doc_type, name):
        self.doc_type = doc_type
        self.name = name
        
    __unicode__ = lambda self: "Unknown document reference '%s' to '%s'" % (self.doc_type.__name__, self.name)
    __str__= __unicode__
    

    
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
        klass =  type.__new__(cls, name, bases, dct)
        
        if name!="MongoDoc":
            if not hasattr(klass, 'objects'):
                klass.objects = Manager()

            klass.objects.docs_name = name
            klass.objects.docs_type = klass            
                
            klass.DoesNotExist = subclass_exception('DoesNotExist', (ObjectDoesNotExist,), name)
            
        klass._std_fields = set(dir(klass))
            
        return klass
    

class LazyDoc(object):
    
    REF_DOC_NOT_LOADED = -1
    
    def __init__(self, doc, id):
        self.doc = doc
        self.id=id
        self.ref_doc = LazyDoc.REF_DOC_NOT_LOADED
        
    def _load(self):
        if self.ref_doc==LazyDoc.REF_DOC_NOT_LOADED:
            try:
                self.ref_doc = self.doc.objects.get(_id = self.id)
            except self.doc.DoesNotExist:
                self.ref_doc = None
        
        
    def __getattr__(self, name):
        self._load()
        return getattr(self.ref_doc, name)
    
    #TODO: implement __setattr__  (see Django ForeignKey contibute to class)
    
    def __unicode__(self):
        self._load()
        return unicode(self.ref_doc)
    __str__ = __unicode__
    
    
    def  __eq__(self, doc):
        self._load()
        return self.ref_doc == doc
    
    def __ne__(self, doc):
        self._load()
        return self.ref_doc != doc

    def __hasattr__(self, name):
        self._load()
        return hasattr(self.ref_doc, name)
    
        

        

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