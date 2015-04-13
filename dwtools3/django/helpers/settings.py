"""
Provides the ability to define application-specific settings.

By subclassing SettingsProxy and creating class attributes for
each of your app's settings, you are initializing default values
for each of those settings. The user can then override any of
those settings in the standard Django settings file.

    - ``my_app/settings.py``::

        from dwtools3.django.helpers import SettingsProxy

        class MyAppSettings(SettingsProxy):
            MYAPP_FIRST_SETTING = 'default'
            MYAPP_SECOND_SETTING = 'two'

    - Main Django ``settings.py``::

        MYAPP_FIRST_SETTING = 'overridden'
        SOME_OTHER_SETTING = ''

    - ``my_app`` code::

        print(MyAppSettings.MYAPP_FIRST_SETTING)    # output: 'overridden'
        print(MyAppSettings.MYAPP_SECOND_SETTING)   # output: 'two'
        print(MyAppSettings.SOME_OTHER_SETTING)     # raises AttributeError


"""
from django.conf import settings as django_settings


class _SettingsProxyMetaclass(type):
    """
    This metaclass intercepts creation of a SettingsProxy
    subclass. Any class attributes are checked against
    the Django settings file. If found there the values
    specified in the class are replaced with those from
    the Django settings file.
    """
    def __new__(mcs, name, bases, dct):
        for (k, v) in dct.items():
            if not k.startswith('_'):
                dct[k] = getattr(django_settings, k, v)

        return type.__new__(mcs, name, bases, dct)


class SettingsProxy(metaclass=_SettingsProxyMetaclass):
    """
    Base class for application-specific settings.
    This class defines the default settings values and
    provides easy retrieval of the default or overridden
    setting using ``Subclass.MY_SETTING``.

    Note you may not construct instances of this class.
    """
    def __init__(self):
        raise RuntimeError('Cannot create instances of SettingsProxy.')
