
from pymongo import Connection
from tools.shortcuts import get_settings

def get_connection():
    return Connection()[get_settings("MONGODB_DATABSSE_NAME", "default")]