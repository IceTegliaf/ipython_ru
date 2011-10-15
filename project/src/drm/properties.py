from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from drm import exceptions
import datetime
import re
import time

     
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
        
    def to_python(self, value):
        return value
    
    def to_json(self, value):
        return value
    
    def clean(self, value):
        if self.required and not value:
            raise exceptions.ValueRequiredError(self.klass.__name__, self.name)
        return self.to_python(value)
    
    def __cmp__(self, other):
        # This is needed because bisect does not take a comparison function.
        return cmp(self.creation_counter, other.creation_counter)
    
    def default_value(self):
        val =  self.default
        if self.required and not val:
            raise exceptions.ValueRequiredError(self.klass.__name__, self.name)                        
        return val 
        
    
class Integer(BaseProperty):
    
    def to_python(self, value):
        try:
            return int(value)
        except ValueError, e:
            raise exceptions.ValidationError("property Integer error: %s" % e)
    
    def to_json(self, value):
        return int(value)
    
    
class String(BaseProperty):
    
    def to_python(self, value):
        return unicode(value)
    
    def to_json(self, value):
        return unicode(value)    



ansi_date_re = re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$')

class Date(BaseProperty):
    
    def to_python(self, value):
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
        
    def to_json(self, value):
        if not isinstance(value, datetime.date):
            raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
        return value.strftime("%Y-%m-%d")
    
    
    
class DateTime(BaseProperty):
    
    def to_python(self, value):
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
                
    def to_json(self, value):
        if not isinstance(value, datetime.datetime):
            raise exceptions.PropertyToJsonError(self.klass.__name__, self.name, value)
        return value.strftime('%Y-%m-%d %H:%M:%S')
        
    
    
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
    
        
    
#TODO: add Link (ForeignKey)
class Link(BaseProperty):
    
    def to_python(self, value):
        print "!!!!!!!!!!"
        return value
    
    def to_json(self, value):
        return value
        
        
 
#TODO: add DateTime
#TODO: add Time
#TODO: add Boolean
#TODO: add Float        
#TODO: add Email

#TODO: add List
#TODO: add Dictionary
