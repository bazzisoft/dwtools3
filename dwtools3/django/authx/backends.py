"""
Custom authentication backend that supports case-insensitive usernames
and/or automatically retrieving the appropriate user
subclass into ``request.user`` when multiple user subclasses exist.

If the ``AUTHX_ENFORCE_EMAIL_VERIFICATION`` setting is enabled,
it will reject logins that don't have their email verified.

Installation
------------
In your Django settings::

    AUTHENTICATION_BACKENDS = (
        # Regular authentication, support for email verification before login
        'dwtools3.django.authx.backends.AuthXModelBackend',

        # Case-insensitive usernames
        'dwtools3.django.authx.backends.CaseInsensitiveAuthXModelBackend',

        # Retrieve appropriate user subclass
        'dwtools3.django.authx.backends.InheritanceQuerySetAuthXModelBackend',

        # Case-insensitive usernames + retrieve appropriate user subclass
        'dwtools3.django.authx.backends.CaseInsensitiveInheritanceQuerySetAuthXModelBackend',
    )
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from ..helpers import InheritanceQuerySet
from .settings import AuthXSettings


class AuthXModelBackendBase(ModelBackend):
    username_cmp = 'exact'

    def get_queryset(self, model_cls):
        return QuerySet(model_cls)

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        flt = {'{}__{}'.format(UserModel.USERNAME_FIELD, self.username_cmp): username}
        qs = self.get_queryset(UserModel)

        try:
            user = qs.get(**flt)

            if AuthXSettings.AUTHX_ENFORCE_EMAIL_VERIFICATION and not user.is_superuser and not user.is_email_verified:
                return None

            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        qs = self.get_queryset(UserModel)
        try:
            return qs.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class CaseInsensitiveAuthXModelBackendMixin:
    username_cmp = 'iexact'


class InheritanceQuerySetAuthXModelBackendMixin:
    def get_queryset(self, model_cls):
        return InheritanceQuerySet(model_cls).select_subclasses()


class AuthXModelBackend(AuthXModelBackendBase):
    """
    An authentication backend that mimics the default Django model backend.
    """
    pass


class CaseInsensitiveAuthXModelBackend(CaseInsensitiveAuthXModelBackendMixin, AuthXModelBackendBase):
    """
    An authentication backend that supports case-insensitive matching of usernames.
    """
    pass


class InheritanceQuerySetAuthXModelBackend(InheritanceQuerySetAuthXModelBackendMixin, AuthXModelBackendBase):
    """
    An authentication backend that uses ``InheritanceQuerySet`` internally to
    automatically return the correct user subclass in ``request.user``,
    when using multiple user model subclasses.
    """
    pass


class CaseInsensitiveInheritanceQuerySetAuthXModelBackend(InheritanceQuerySetAuthXModelBackendMixin, CaseInsensitiveAuthXModelBackendMixin, AuthXModelBackendBase):
    """
    Combines case-insensitive username matching with ``InheritanceQuerySet``
    for returning appropriate user subclasses.
    """
