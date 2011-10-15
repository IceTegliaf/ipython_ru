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