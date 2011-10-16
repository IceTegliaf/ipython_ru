from drm.unitest import MongoDocTest
from docs.models import Module, Function
from drm.lazy import LazyObjectRef


class DocTest(MongoDocTest):
    
    def test_module(self):
        mod = Module(
                     name="test",
                     source_file = "test.py"
                     )
        function = Function(name="test_cool_data")
        function.save()
        
        mod.functions.append(function)
        mod.save()
        
        print "-------------------------"
        mod = Module.documents.get(_id = mod._id)
        print mod.name
        for f in mod.functions:
            f = LazyObjectRef(Function, f)
            
            
            print f.name
        
        