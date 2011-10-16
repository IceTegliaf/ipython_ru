from django.utils.translation import ugettext as _


class BaseError(Exception):
    
    def __init__(self, reason):
        self.reason = reason
        
    __unicode__ = lambda self: self.reason
    __str__ = lambda self: self.reason
    
    
class ValidationError(BaseError):
    pass


class InvalidValueError(ValidationError):
    def __init__(self, class_name, prop_name, value, info=""):
        self.value = value
        self.class_name = class_name
        self.prop_name = prop_name
        self.info = info
        
    __unicode__ = lambda self: _("%(class_name)s.%(prop_name)s can't set value '%(value)s' %(info)s") % {
                                                                                     "class_name": self.class_name,
                                                                                     "prop_name": self.prop_name,
                                                                                     "value": self.value,
                                                                                     "info": self.info
                                                                                     }
    
class PropertyToJsonError(InvalidValueError):
    
    __unicode__ = lambda self: _("Can't convert value '%(value)s' of  %(class_name)s.%(prop_name)s to json") % {
                                                                                     "class_name": self.class_name,
                                                                                     "prop_name": self.prop_name,
                                                                                     "value": self.value
                                                                                     }     



class InvalidArgumentError(BaseError):
    pass

class ValueRequiredError(BaseError):
    
    def __init__(self, doc_name, prop_name):
        self.doc_name, self.prop_name = doc_name,prop_name
        
    __unicode__ = lambda self: _("Required value for %(doc)s.%(prop)s") % {
                                                                           "doc": self.doc_name,
                                                                           "prop":self.prop_name
                                                                           }

class ObjectDoesNotExist(Exception):
    "The requested object does not exist"
    
    __unicode__ = lambda self: "The requested object does not exist"
    __str__= __unicode__
    
    
class UnknownDocumentRef(Exception):
    
    def __init__(self, doc_type):
        self.doc_type = doc_type
        
    __unicode__ = lambda self: _("Unknown document reference '%(type)s'") % {
                                                                             "type": self.doc_type.__name__
                                                                             }
    __str__= __unicode__
    
    
class ValueNotInChoincesError(ValidationError):
    
    def __init__(self, prop, value):
        self.prop = prop
        self.value = value
        
    __unicode__ = lambda self: _("Can't get display name for %(class)s.%(prop)s=%(value)s" % {
                                                                                              'class': self.prop.klass.__name__,
                                                                                              'prop': self.prop.name,
                                                                                              'value': self.value,
                                                                                              })