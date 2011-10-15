from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from drm import exceptions
import datetime
import re
import time
import types
from pymongo.objectid import ObjectId
from pymongo.errors import PyMongoError
from drm.lazy import LazyDoc

     
class BaseProperty(object):
    
    inner_creation_counter = 0
        
    def __init__(self, verbose_name = "", required = False, db_index = False, default=None):
        self.verbose_name = verbose_name
        self.required = required
        self.db_index = db_index
        self.default = default

        BaseProperty.inner_creation_counter+=1
        self.creation_counter = BaseProperty.inner_creation_counter
        
    def contribute_to_class(self, klass, name):
        #setattr(klass, name, value)
        klass._meta.add_property(name, self)
        self.klass=klass
        
    def to_python(self, instance,  value):
        return value
    
    def to_json(self, instance, value):
        return value
    
    def clean(self, instance,  value):
        if self.required and not value:
            raise exceptions.ValueRequiredError(self.klass.__name__, self.name)
        return self.to_python(instance, value)
    
    def __cmp__(self, other):
        # This is needed because bisect does not take a comparison function.
        return cmp(self.creation_counter, other.creation_counter)
    
    def default_value(self):
        val =  self.default
        if self.required and not val:
            raise exceptions.ValueRequiredError(self.klass.__name__, self.name)                        
        return val 
        
    
class Integer(BaseProperty):
    
    def to_python(self, instance, value):
        try:
            return int(value)
        except ValueError, e:
            raise exceptions.ValidationError("property Integer error: %s" % e)
    
    def to_json(self, instance, value):
        return int(value)
    
    
class String(BaseProperty):
    
    def to_python(self, instance, value):
        return unicode(value)
    
    def to_json(self, instance, value):
        return unicode(value)    



ansi_date_re = re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$')

class Date(BaseProperty):
    
    def to_python(self, instance, value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        
        value = unicode(value)
        
        if not ansi_date_re.search(value):
            raise exceptions.InvalidValueError(self.klass.__name__, self.name, value)
        
        year, month, day = map(int, value.split('-'))
        
        try:
            return datetime.date(year, month, day)
        except ValueError, e:
            raise exceptions.ValidationError(_("Value error: %(reason)s") % {"reason": _(str(e))})
        
    def to_json(self, instance, value):
        if not isinstance(value, datetime.date):
            raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
        return value.strftime("%Y-%m-%d")
    
    
    
class DateTime(BaseProperty):
    
    def to_python(self, instance, value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value

        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        
        # Attempt to parse a datetime:
        value = smart_str(value)
        # split usecs, because they are not recognized by strptime.
        if '.' in value:
            try:
                value, usecs = value.split('.')
                usecs = int(usecs)
            except ValueError:
                raise exceptions.InvalidValueError(self.klass.__name__, self.name, value)
        else:
            usecs = 0
        kwargs = {'microsecond': usecs}
        try: # Seconds are optional, so try converting seconds first.
            return datetime.datetime(*time.strptime(value, '%Y-%m-%d %H:%M:%S')[:6],
                                     **kwargs)

        except ValueError:
            try: # Try without seconds.
                return datetime.datetime(*time.strptime(value, '%Y-%m-%d %H:%M')[:5],
                                         **kwargs)
            except ValueError: # Try without hour/minutes/seconds.
                try:
                    return datetime.datetime(*time.strptime(value, '%Y-%m-%d')[:3],
                                             **kwargs)
                except ValueError:
                    raise exceptions.InvalidValueError(self.klass.__name__, self.name, value)
                
    def to_json(self, instance, value):
        if not isinstance(value, datetime.datetime):
            raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
        return value.strftime('%Y-%m-%d %H:%M:%S')


     
    
    

        
        
#    def __getattr__(self, name):
#        if hasattr(self, name):
#            return getattr(self, name)
#        
#        print "__getattr__", name
#        self._load()
#        return getattr(self.ref_doc, name)
#    
#    #TODO: implement __setattr__  (see Django ForeignKey contibute to class)
#    
#    def __unicode__(self):
#        print "__unicode__"
#        self._load()
#        return unicode(self.ref_doc)
#    __str__ = __unicode__
#    
#    
#    def  __eq__(self, doc):
#        self._load()
#        return self.ref_doc == doc
#    
#    def __ne__(self, doc):
#        self._load()
#        return self.ref_doc != doc
#
#    def __hasattr__(self, name):
#        self._load()
#        print "__hasattr__"
#        return hasattr(self.ref_doc, name)
    
        
    
#TODO: add Link (ForeignKey)
class Link(BaseProperty):
    
    id_name = property(lambda self: "%s_id" % self.name)
    cache_name = property(lambda self: "%s_doc" % self.name)
    
    def __init__(self, rel_class, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)
        self.rel_class = rel_class
        
    def contribute_to_class(self, klass, name):
        super(Link, self).contribute_to_class(klass, name)
        setattr(klass, name,  LazyDoc(self))
        self.klass._meta.add_exclude(self.id_name)
        self.klass._meta.add_exclude(self.cache_name)
    
    def to_python(self, instance, value):
        from drm.base import MongoDoc
        
        if isinstance(value, LazyDoc):
            return getattr(instance, self.id_name)
        
        if isinstance(value, MongoDoc):
            return value._id

        try:
            return ObjectId(value)
        except (PyMongoError, TypeError), e:
            raise exceptions.InvalidValueError(self.klass.__name__, self.name, value, unicode(e))
        
    
    def to_json(self, instance, value):
        from drm.base import MongoDoc
        
        if isinstance(value, LazyDoc):
            print "to_json LazyDoc"
            return getattr(instance, self.id_name)
        
        
        if isinstance(value, (LazyDoc, MongoDoc)):
            return value._id
        
        if isinstance(value, ObjectId):
            return value
        
        raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
    
    def get(self, instance):
        try:
            return getattr(instance, self.cache_name)
        except AttributeError:
            _id = getattr(instance, self.id_name)
            doc = self.rel_class.documents.get(_id = _id)
            setattr(instance,  self.cache_name, doc)
            
        return doc
    
    def set(self, instance, value):
        setattr(instance, self.id_name, self.clean(instance, value))
        
        
        
        
    

        
        
        
        
 
#TODO: add DateTime
#TODO: add Time
#TODO: add Boolean
#TODO: add Float        
#TODO: add Email

#TODO: add List
#TODO: add Dictionary
