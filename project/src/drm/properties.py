from django.utils.translation import ugettext_lazy as _
from drm import exceptions
import datetime
import re

     
class BaseProperty(object):
    
    def __init__(self, verbose_name = "", required = False, db_index = False):
        self.verbose_name = verbose_name
        self.required = required
        self.db_index = db_index
        
    def contribute_to_class(self, klass, name, value):
        setattr(klass, name, value)
        klass._meta.add_property(name, self)
        
    def to_python(self, value):
        return value
    
    def to_json(self, value):
        return value
        
    
class Integer(BaseProperty):
    
    def to_python(self, value):
        return int(value)
    
    def to_json(self, value):
        return int(value)
    
    
class String(BaseProperty):
    pass



ansi_date_re = re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$')

class Data(BaseProperty):
    
    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value        
        
        if not ansi_date_re.search(value):
            raise exceptions.ValidationError(_('Unknown date format for value "%s"' % value))
        
        year, month, day = map(int, value.split('-'))
        
        try:
            return datetime.date(year, month, day)
        except ValueError, e:
            raise exceptions.ValidationError(_("Value error: %(reason)s") % {"reason": _(str(e))})
        
    def to_json(self, value):
        if not isinstance(value, datetime.date):
            raise exceptions.InvalidArgumentError("Data.to_json value can't be '%s' type" % type(value))

        return value.strftime("%Y-%m-%d")
    
    
    
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
