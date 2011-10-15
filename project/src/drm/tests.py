from django import test
from drm import properties
from drm.base import MongoDoc, Options
from drm.exceptions import ObjectDoesNotExist

#TODO: write tests for properties types conversion
#TODO: write tests for data save
#TODO: write tests for data load
#TODO: write tests for data navigation (properties.Link, List ,Dictionary and etc)

class Doc1(MongoDoc):
    name = properties.String("name")
    age = properties.Integer("age")
    d1 = properties.Data("date 1")
    

class DocTest(test.TestCase):
    
    def test_metaclass(self):
        obj =  Doc1()
        assert issubclass(obj.DoesNotExist, ObjectDoesNotExist)
        assert isinstance(obj._meta, Options)
        
        print obj._meta.propery_names()
        assert obj._meta.propery_names()==["name", "age", "d1"]
        
        
        
        