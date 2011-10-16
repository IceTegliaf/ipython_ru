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
from tools.class_loader import get_class_by_string

#TODO: add Float
#TODO: add PositiveInteger  - Integer with validation
#TODO: add choices

def get_display(prop):
    def wrap(self):
        val = getattr(self, prop.name)
        for key, name in prop.choices:
            if key==val:
                return name
        raise exceptions.ValueNotInChoincesError(prop, val)
    return wrap
     
class BaseProperty(object):
    
    inner_creation_counter = 0
        
    def __init__(self, verbose_name = "", required = False, db_index = False, default=None, choices = None):
        self.verbose_name = verbose_name
        self.required = required
        self.db_index = db_index
        self.default = default
        self.choices = choices

        BaseProperty.inner_creation_counter+=1
        self.creation_counter = BaseProperty.inner_creation_counter
        
    def contribute_to_class(self, klass, name):
        #setattr(klass, name, value)
        klass._meta.add_property(name, self)
        self.klass=klass
        if self.choices:
            setattr(klass, "get_%s_dispaly" % name, get_display(self))
        
    def to_python(self, instance,  value):
        if self.choices:
            keys = [x[0] for x in self.choices]
            if value not in keys:
                raise exceptions.ValueNotInChoincesError(self, value)            
        return value
    
    def to_json(self, instance, value):
        return value
    
    def load_clean(self, instance,  value):
        if self.required and not value:
            raise exceptions.ValueRequiredError(self.klass.__name__, self.name)
        #if 
        return self.to_python(instance, value)

    def save_clean(self, instance,  value):
        if self.required and not value:
            raise exceptions.ValueRequiredError(self.klass.__name__, self.name)
        
        if value:
            return self.to_json(instance, value)
        return value
    
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
            raise exceptions.InvalidValueError(self.klass.__name__, self.name, value, unicode(e))
    
    def to_json(self, instance, value):
        return int(value)
    
    
class String(BaseProperty):
    
    def to_python(self, instance, value):
        return unicode(value)
    
    def to_json(self, instance, value):
        return unicode(value)    

class Boolean(BaseProperty):
    def to_python(self, instance, value):
        try:
            return bool(value)
        except ValueError, e:
            raise exceptions.InvalidValueError(self.klass.__name__, self.name, value, unicode(e))
    
    def to_json(self, instance, value):
        return bool(value)


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
    
class ListOf(BaseProperty):        

    def __init__(self, element_type, *args, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = []
            
        super(ListOf, self).__init__(*args, **kwargs)
        if not isinstance(element_type, BaseProperty):
            raise exceptions.InvalidArgumentError(_("element_type must be instance of 'BaseProperty' not '%(type)s'") % type(element_type))        
        self.element_type = element_type
        
#    def contribute_to_class(self, klass, name):
#        super(ListOf, self).contribute_to_class(klass, name)
#        setattr(klass, name)
        
    def to_python(self, instance, value):
        if isinstance(value, tuple):
            value = list(value)
            
        if not isinstance(value, list):
            raise exceptions.InvalidValueError(self.klass.__name__, self.name, value)            
        
        #check list contains
        return [ self.element_type.to_python(instance, e) for e in value ]
    
    def to_json(self, instance, value):
        if isinstance(value, tuple):
            value = list(value)
            
        if not isinstance(value, list):
            raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
        
        return [ self.element_type.to_json(instance, e) for e in value ]            
        
        
    

class Link(BaseProperty):
    
    id_name = property(lambda self: "%s_id" % self.name)
    cache_name = property(lambda self: "%s_doc" % self.name)
    
    def __init__(self, rel_class, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)
        self.rel_class = rel_class
        
    def contribute_to_class(self, klass, name):
        super(Link, self).contribute_to_class(klass, name)
        
        if isinstance(self.rel_class, basestring):
            if self.rel_class=="self":
                self.rel_class = klass
            else:
                self.rel_class = get_class_by_string("%s.%s" % (klass.__module__, self.rel_class))
                
        setattr(klass, name,  LazyDoc(self))
        self.klass._meta.add_exclude(self.id_name)
        self.klass._meta.add_exclude(self.cache_name)       

        
    def to_python(self, instance, value):
        from drm.base import MongoDoc
        
        if isinstance(value, LazyDoc):
            return getattr(instance, self.id_name)
        
        if isinstance(value, MongoDoc):
            if not isinstance(value, self.rel_class):
                raise exceptions.InvalidValueError(self.klass.__name__, self.name, value)            
            return value._id

        try:
            return ObjectId(value)
        except (PyMongoError, TypeError), e:
            raise exceptions.InvalidValueError(self.klass.__name__, self.name, value, unicode(e))
        
    
    def to_json(self, instance, value):
        from drm.base import MongoDoc
        
        if isinstance(value, LazyDoc):
            if hasattr(instance, self.id_name):
                return getattr(instance, self.id_name)
            return None
        
        
        if isinstance(value, (LazyDoc, MongoDoc)):
            return value._id
        
        if isinstance(value, ObjectId):
            return value
        
        raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
    
    def get_value(self, instance):
        try:
            return getattr(instance, self.cache_name)
        except AttributeError:
            pass
        
        if hasattr(instance, self.id_name):
            _id = getattr(instance, self.id_name)
            print "load obj:", _id
            doc = self.rel_class.documents.get(_id = _id)
            setattr(instance,  self.cache_name, doc)
            return doc
            
        return None
    
    def set_value(self, instance, value):
        if isinstance(value, self.rel_class):
            setattr(instance,  self.cache_name, value)
        elif hasattr(instance,  self.cache_name):
            delattr(instance,  self.cache_name)
        setattr(instance, self.id_name, self.to_python(instance, value))
        
        
        
        
    

        
        
        
        
 
#TODO: add DateTime
#TODO: add Time
#TODO: add Boolean
#TODO: add Float        
#TODO: add Email

#TODO: add List
#TODO: add Dictionary
