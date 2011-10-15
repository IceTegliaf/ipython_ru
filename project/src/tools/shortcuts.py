from django.conf import settings


def get_settings(name, default=None):
    try:
        return getattr(settings, name)
    except AttributeError:
        return default