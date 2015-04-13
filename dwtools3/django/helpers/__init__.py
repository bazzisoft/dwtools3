"""
Various Django helper functions and shortcuts.

Installation
------------
    - Add to your ``INSTALLED_APPS``::

        INSTALLED_APPS = INSTALLED_APPS + (
            'dwtools3.django.helpers',
        )

"""
from .inheritance import InheritanceQuerySet, InheritanceManager, InheritanceManagerMixin
from .settings import SettingsProxy
