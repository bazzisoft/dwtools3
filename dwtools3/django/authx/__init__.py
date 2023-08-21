"""
Extends the django.contrib.auth functionality with a light wrapper
and extra functionality:

    - ``AuthXAbstractUser`` base class that supports emails as usernames, case
      insensitive usernames and email verification.
    - Validation functions for registration/profile forms.
    - User login hash generation/check functionality
    - Upgraded functionality for login via API.


Dependencies
------------
    - ``django.contrib.auth``
    - ``dwtools3.django.helpers``


Installation
------------

    - Set your base user model::

        AUTH_USER_MODEL = 'accounts.User'

    - Add the following settings for ``django.contrib.auth``::

        LOGIN_URL = '/accounts/login/'     # Login page URL
        LOGOUT_URL = '/accounts/logout/'   # Logout page URL
        LOGIN_REDIRECT_URL = '/'           # Redirect here after login if no 'next' GET param
        PASSWORD_RESET_TIMEOUT = n         # Seconds that reset password/login links are valid for

    - Customize settings for authx. See :py:class:`.settings.AuthXSettings`.


Usage
-----
    - After installation, you must first create a
      model subclass deriving from ``AuthXAbstractUser``.

      This model is the one set in ``AUTH_USER_MODEL``.

      Consider adding default values to all new fields so that
      users can be created with just a username and password.
      ::

        # models.py

        from django.db import models
        from dwtools3.django.authx.models import AuthXAbstractUser

        class User(AuthXAbstractUser):
            # If you want case-sensitive username unique checks
            authx_username_case_insensitive = False

            # If you want first + last name as required fields
            authx_first_last_name_required = True

            # If you want email as a required field
            authx_email_required = True

    - Register your new model in admin.py.
      See the :py:mod:`.admin` module for more details::

        from django.contrib import admin
        from dwtools3.django.authx.admin import AuthXUserAdmin
        from .models import Customer

        @admin.register(User)
        class UserAdmin(AuthXUserAdmin):
            fieldsets = (
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': ('is_active', 'is_email_verified', 'is_staff',
                                    'is_superuser', 'groups')}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                (_('Extra fields'), {'fields': ('facebook_id', 'friends')}),
            )

    - Make use of the API functions. See :py:mod:`.api`
"""
from .api import (
    LoginResult,
    authenticate,
    create_multi_use_login_hash,
    create_single_use_login_hash,
    login,
    logout,
    verify_multi_use_login_hash,
    verify_single_use_login_hash,
)
from .validators import (
    validate_confirm_password,
    validate_confirm_password_on_form,
    validate_password,
    validate_password_on_form,
    validate_username,
    validate_username_on_form,
)
