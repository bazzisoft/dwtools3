"""
Provides the ``AuthXAbstractUser`` base class supporting
emails as usernames and email verification.

Provides built-in ``InheritanceQuerySet``/``InheritanceManager``
support to return the correct subclasses when using model
inheritance with a number of different ``AuthXAbstractUser`` subclasses.
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.core import validators
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from dwtools3.django.helpers.models import check_model_is_unique_with_conditions
from ..helpers.inheritance import InheritanceManagerMixin
from .settings import AuthXSettings


# Add 'authx_first_last_name_required' and 'authx_email_required' meta options to django
models.options.DEFAULT_NAMES = (models.options.DEFAULT_NAMES +
                                ('authx_first_last_name_required',
                                 'authx_email_required',
                                 'authx_username_case_insensitive'))


class AuthXUserManager(InheritanceManagerMixin, UserManager):
    """
    Default manager for the ``AuthXAbstactUser`` subclasses.

    Supports ``InheritanceQuerySet``/``InheritanceManager`` functionality.
    """
    def create_user(self, username=None, email=None, password=None):
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
        password = password or self.make_random_password(AuthXSettings.AUTHX_GENERATED_PASSWORD_LENGTH)

        # Create a new user & store the raw password for the caller
        user = super().create_user(username=username, email=email, password=password)
        user.raw_password = password

        return user


class AuthXAbstactUser(AbstractBaseUser, PermissionsMixin):
    """
    Base class for user models supporting emails as usernames
    and optional email verification.
    """
    username = models.CharField(_('username'), max_length=254, unique=True,
        help_text=_('Required. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    email = models.EmailField(_('email address'), max_length=254, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    is_email_verified = models.BooleanField(default=False,
        help_text=_('Indicates whether this user has validated their email address.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = AuthXUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')
        authx_first_last_name_required = False
        authx_email_required = False
        authx_username_case_insensitive = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self._meta, 'authx_first_last_name_required', False):
            self._meta.get_field('first_name').blank = False
            self._meta.get_field('last_name').blank = False
        if getattr(self._meta, 'authx_email_required', False):
            self._meta.get_field('email').blank = False

    def clean(self):
        if getattr(self._meta, 'authx_username_case_insensitive', True):
            check_model_is_unique_with_conditions(self, ('username',), error_field='username', case_insensitive=True)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
