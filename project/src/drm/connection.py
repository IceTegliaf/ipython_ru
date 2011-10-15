
from pymongo import Connection
from tools.shortcuts import get_settings

def get_connection():
    try:
        return get_connection._db
    except AttributeError:
        get_connection._db =  Connection()
    return get_connection._db

def get_db():
    return get_connection()[get_settings("MONGODB_DATABSSE_NAME", "default")]