
class BaseError(Exception):
    
    def __init__(self, reason):
        self.reason = reason
        
    __unicode__ = lambda self: self.reason
    __str__ = lambda self: self.reason
    
    
class ValidationError(BaseError):
    pass


class InvalidArgumentError(BaseError):
    pass