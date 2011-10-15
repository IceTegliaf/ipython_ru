from django.utils.translation import ugettext_lazy as _
from mongodoc import exceptions
import datetime
import re

     
class BaseProperty(object):
    
    def __init__(self, verbose_name = "", required = False, db_index = False):
        self.verbose_name = verbose_name
        self.required = required
        self.db_index = db_index
        
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
 
#TODO: add DateTime
#TODO: add Time
#TODO: add Boolean
#TODO: add Float        