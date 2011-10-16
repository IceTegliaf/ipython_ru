

class LazyDoc(object):
    
    REF_DOC_NOT_LOADED = -1
    
    def __init__(self, prop):        
        self.prop = prop
        
                
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
                
        try:
            ret = self.prop.get_value(instance)
        except Exception, e:
            print e   
        return ret
        
    def __set__(self, instance, value):
        return self.prop.set_value(instance, value)
        
        
#class LazyLinkedDoc(object):
#    
#    REF_DOC_NOT_LOADED = -1
#    
#    def __init__(self, prop):        
#        self.prop = prop
#        self.ref_doc = LazyLinkedDoc.REF_DOC_NOT_LOADED
#        
#    def _load(self, instance):
#        if self.ref_doc==LazyLinkedDoc.REF_DOC_NOT_LOADED:
#            try:
#                self.ref_doc = self.prop.get_doc(instance)
#            except self.doc.DoesNotExist:
#                self.ref_doc = None
#                
#                
#    def __get__(self, instance, instance_type=None):
#        if instance is None:
#            return self
#        
#        print "!!!__get__"
#        
#    def __set__(self, instance, value):
#        print "___set__"
#        pass