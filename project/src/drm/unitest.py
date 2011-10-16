from django import test
from django.conf import settings
from drm.connection import get_connection


class MongoDocTest(test.TestCase):
    
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