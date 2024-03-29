from drm.exceptions import UnknownDocumentRef
import types


def to_json(val):
    from drm.base import MongoDoc
    
    if isinstance(val, MongoDoc):
        if not val._id:
            raise UnknownDocumentRef(type(val))                 
        val = val._id
        
    if isinstance(val, types.ListType):
        val = [to_json(v) for v in val]
    
    return val    


def get_value(instance, name):
    if name in instance.__dict__:
        return instance.__dict__[name]
    
    if name in type(instance).__dict__:
        return type(instance).__dict__[name]
    
    return None
 
 
def has_value(instance, name):
     
    if name in instance.__dict__:
        return True
    
    if name in type(instance).__dict__:
        return True
    
    return False     