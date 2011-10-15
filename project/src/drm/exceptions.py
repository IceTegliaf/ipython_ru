
class BaseError(Exception):
    
    def __init__(self, reason):
        self.reason = reason
        
    __unicode__ = lambda self: self.reason
    __str__ = lambda self: self.reason
    
    
class ValidationError(BaseError):
    pass


class InvalidArgumentError(BaseError):
    pass



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
    