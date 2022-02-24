"""
Provides the ``AuthXAbstractUser`` base class supporting
emails as usernames and email verification.

support to return the correct subclasses when using model
inheritance with a number of different ``AuthXAbstractUser`` subclasses.
"""
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dwtools3.django.helpers.fields import StrippedCharField
from dwtools3.django.helpers.models import check_model_is_unique_with_conditions

from .settings import AuthXSettings


class CustomUsernameValidator(UnicodeUsernameValidator):
    """Ensures usernames can contain all valid email characters"""
    regex = r"^[\w.@+\-!#$%&'*/=?^_`{}|~]+\Z"


class AuthXUserManager(UserManager):
    """
    Default manager for the ``AuthXAbstractUser`` subclasses.
    """
    def get_by_natural_key(self, username):
        """
        Add support for case-insensitive usernames.
        """
        if self.model.authx_username_case_insensitive:
            return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})
        else:
            return super().get_by_natural_key(username)

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        """
        Creates a new user.

        :param str username: The username for this user. Defaults to email.
        :param str email: The email address of the user.
        :param str password: The password for this user. If not
            provided, creates a random password.

        :return: The created ``User`` instance with an additional ``raw_password``
            attribute set to the user's password.
        """
        if not username and not email:
            raise ValueError('One of username or email must be provided.')

        username = username or email
        email = email or ''
        password = password or self.make_random_password(
            AuthXSettings.AUTHX_GENERATED_PASSWORD_LENGTH)

        # Create a new user & store the raw password for the caller
        user = super().create_user(
            username=username, email=email, password=password, **extra_fields)
        user.raw_password = password

        return user


class AuthXAbstractUser(AbstractUser):
    """
    Base class for user models supporting emails as usernames
    and optional email verification.
    """
    username = models.CharField(
        _('username'), max_length=254, unique=True,
        help_text=_('Required. Letters, digits and @/./+/-/_ only.'),
        validators=[CustomUsernameValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    first_name = StrippedCharField(_('first name'), max_length=150, blank=True)
    last_name = StrippedCharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), max_length=254, blank=True)
    is_email_verified = models.BooleanField(
        default=False,
        help_text=_('Indicates whether this user has validated their email address.'))

    objects = AuthXUserManager()

    authx_first_last_name_required = False
    authx_email_required = False
    authx_username_case_insensitive = False

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.authx_first_last_name_required:
            self._meta.get_field('first_name').blank = False
            self._meta.get_field('last_name').blank = False
        if self.authx_email_required:
            self._meta.get_field('email').blank = False

    def clean(self):
        super().clean()
        if self.authx_username_case_insensitive:
            msg = self._meta.get_field('username').error_messages['unique']
            check_model_is_unique_with_conditions(
                self, ('username',), error_message=msg,
                error_field='username', case_insensitive=True)
