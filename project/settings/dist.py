# coding=utf8


ADMINS = (
    ('Kovalenko Pavel', 'pavel@bitrain.ru'),
)

MANAGERS = ADMINS

DATABASES = {
    'default':{
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     '',
        'USER':     '',
        'PASSWORD': '',
        'HOST':     '',
        'PORT':     '',
    }
}

INTERNAL_IPS = ('127.0.0.1',)

DEBUG = True
TEMPLATE_DEBUG = True
