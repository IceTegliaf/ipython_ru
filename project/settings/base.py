# coding=utf8
import os.path
import sys


PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__),".."))
PROJECT_SRC_ROOT = os.path.normpath(os.path.join(PROJECT_ROOT, 'src'))
if PROJECT_SRC_ROOT not in sys.path:
    sys.path.insert(0,PROJECT_SRC_ROOT )
    
##ice_tools Support
#ICE_PACKAGES_ROOT =  '/usr/local/lib/python2.7/ice-packages'
#if ICE_PACKAGES_ROOT not in sys.path:
#    sys.path.insert(0,ICE_PACKAGES_ROOT )
        

INTERNAL_IPS = ( )

ADMINS = ( )

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-ru'
USE_I18N = True


# fastcgi fix
FORCE_SCRIPT_NAME = ''

# Make this unique, and don't share it with anybody.
if not hasattr(globals(), 'SECRET_KEY'):
    SECRET_FILE = os.path.join(PROJECT_ROOT, 'secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            from random import choice
            SECRET_KEY = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
            secret = file(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            raise Exception('Please create a %s file with random characters to generate your secret key!' % SECRET_FILE)


INSTALLED_APPS = [
#    "apps.tools",
#    "apps.ice_tools",
#    "apps.ice_basetypes",
    "drm",
    "docs",
]


#ICE_REGS =[
#    "apps.ice_basetypes",
#    "master"
#]
#
#ICE_SLICE =[
#    "apps.ice_tools",
#    "apps.ice_basetypes",
#    "master",
#    "apps.ice_logger",
##    "apps.passport_client",
##    "host",
#]

DEBUG = False
TEMPLATE_DEBUG = False
CONSOLE_SQL_LOG = False