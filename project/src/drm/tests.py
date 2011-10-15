from django import test
from drm import properties
from drm.base import MongoDoc, Options
from drm.exceptions import ObjectDoesNotExist

#TODO: write tests for properties types conversion
#TODO: write tests for data save
#TODO: write tests for data load
#TODO: write tests for data navigation (properties.Link, List ,Dictionary and etc)

class Doc1(MongoDoc):
    name = properties.String("verbose_name")
    

class DocTest(test.TestCase):
    
    def test_metaclass(self):
        obj =  Doc1()
        assert issubclass(obj.DoesNotExist, ObjectDoesNotExist)
        assert isinstance(obj._meta, Options)
        assert obj._meta.propery_names()==["name"]
        
        
        
        