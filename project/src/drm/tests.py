from django import test
from drm import properties, exceptions
from drm.base import MongoDoc, Options
from drm.exceptions import ObjectDoesNotExist
import datetime
from django.conf import settings
from drm.connection import get_connection, get_db
from pymongo import Connection
from copy import copy

#TODO: write tests for data navigation (properties.Link, List ,Dictionary and etc)

class Doc1(MongoDoc):
    name = properties.String()
    age = properties.Integer()
    d1 = properties.Date()
    when = properties.DateTime()
    
class DocWithRequires(MongoDoc):
    name = properties.String(required = True)
    age = properties.Integer(required = True)
    d = properties.Date(required = True)
    dt = properties.DateTime(required = True)
    
class DocWithLink(MongoDoc):
    parent = properties.Link(Doc1)


class DocTest(test.TestCase):
    
    @classmethod
    def setUpClass(cls):
        if hasattr(settings, "MONGODB_DATABSSE_NAME"):
            cls._old_db = settings.MONGODB_DATABSSE_NAME
        else:
            cls._old_db = None
        settings.MONGODB_DATABSSE_NAME = "test_db"
        
         
    @classmethod         
    def tearDownClass(cls):
        get_connection().drop_database(settings.MONGODB_DATABSSE_NAME)
        if cls._old_db:        
            settings.MONGODB_DATABSSE_NAME = cls._old_db
        else:
            del settings.MONGODB_DATABSSE_NAME
    
    def test_metaclass(self):
        obj =  Doc1()
        assert issubclass(obj.DoesNotExist, ObjectDoesNotExist)
        assert isinstance(obj._meta, Options)
        assert obj._meta.propery_names()==["name", "age", "d1", "when"]
        assert id(Doc1._meta)!=id(DocWithRequires._meta)
        assert id(Doc1.documents)!=id(DocWithRequires.documents)
        assert id(Doc1._meta.klass)!=id(DocWithRequires._meta.klass)
        assert Doc1._meta.klass == Doc1
        assert DocWithRequires._meta.klass == DocWithRequires
         
        
    def test_validation(self):
        self.assertRaises(exceptions.ValidationError, Doc1, d1 = "wrong value")
        self.assertRaises(exceptions.ValidationError, Doc1, d1 = 4)
        self.assertRaises(exceptions.ValidationError, Doc1, d1 = "01-02-2003")
                
        self.assertRaises(exceptions.ValidationError, Doc1, age = "cool")
        
    def test_data_save_load(self):
        obj =  Doc1(
                    name = "doc name",
                    age = 100500,
                    d1 = datetime.date.today(),
                    when = datetime.datetime.today(),
                    )
        obj.save()
        
        obj2 = Doc1.documents.get(_id = obj._id)
        
        assert obj == obj2
        
        assert obj2.name=="doc name"
        assert isinstance(obj2.name, unicode)
        assert isinstance(obj2.age, int)
        assert isinstance(obj2.d1, datetime.date)
        assert isinstance(obj2.when, datetime.datetime)
        
        #link save
        obj3 = DocWithLink(parent = obj)
        obj3.save()
        
        obj3_2 = DocWithLink.documents.get(_id = obj3._id)
        assert obj3_2.parent.name == "doc name"
        assert obj3_2.parent.age == 100500
        
        dwr = DocWithRequires(
                              name = "doc name",
                              age = 100500,
                              d = datetime.date.today(),
                              dt = datetime.datetime.today()
                              )
        obj3_2.parent = obj2
        obj3_2.save()

        def test(obj, obj2):
            obj.parent = obj2
        self.assertRaises(exceptions.InvalidValueError, test, obj3_2, dwr)
        obj3_2.save()
        
        
    def test_require(self):
        data = {
                "name":"cool",
                "age": 18,
                "d": datetime.date.today(),
                "dt": datetime.datetime.today(),
                }
        
        for key in data.keys():
            test1 = copy(data)
            del test1[key]
            self.assertRaises(exceptions.ValueRequiredError, DocWithRequires, **test1)

            
#    def test_link(self):
        