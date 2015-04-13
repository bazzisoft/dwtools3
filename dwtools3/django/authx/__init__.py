"""
Extends the django.contrib.auth functionality with a light wrapper
and extra functionality:

    - ``AuthXAbstractUser`` base class that supports emails as usernames,
      email verification and multiple user models (subclasses).
    - Validation functions for registration/profile forms.
    - User login hash generation/check functionality
    - Upgraded functionality for login via API and authentication backends.


Dependencies
------------
    - ``django.contrib.auth``
    - ``dwtools3.django.helpers``


Installation
------------

    - Set your base user model::

        AUTH_USER_MODEL = 'accounts.User'

    - Set one of the authentication backends::

        AUTHENTICATION_BACKENDS = (
            'dwtools3.django.authx.backends.AuthXModelBackend',
            #'dwtools3.django.authx.backends.CaseInsensitiveAuthXModelBackend',
            #'dwtools3.django.authx.backends.InheritanceQuerySetAuthXModelBackend',
            #'dwtools3.django.authx.backends.CaseInsensitiveInheritanceQuerySetAuthXModelBackend',
        )

    - If you want to use the auto-login middleware (logs a user based
      on ``&u=username&p=password`` present in the URL), add this to
      your middleware::

        MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
            'dwtools3.django.authx.middleware.AuthXQueryStringLoginMiddleware',
        )

    - Add the following settings for ``django.contrib.auth``::

        LOGIN_URL = '/accounts/login/'     # Login page URL
        LOGOUT_URL = '/accounts/logout/'   # Logout page URL
        LOGIN_REDIRECT_URL = '/'           # Redirect here after login if no 'next' GET param
        PASSWORD_RESET_TIMEOUT_DAYS = n    # The number of days reset password/login links are valid for

    - Customize settings for authx. See :py:class:`.settings.AuthXSettings`.


Usage
-----
    - After installation, you must first create one or more
      model subclasses deriving from ``AuthXAbstractUser``.
      You must have a single concrete base user model, from which
      you can then derive as many different user/account types
      as you like.

      The concrete base user model, derived from ``AuthXAbstractUser``,
      is the one specified in ``AUTH_USER_MODEL``.

      Consider adding default values to all new fields so that
      users can be created with just a username and password.
      ::

        # models.py

        from django.db import models
        from dwtools3.django.authx.models import AuthXAbstractUser

        class User(AuthXAbstractUser):
            class Meta:
                # If you want case-sensitive username unique checks
                authx_username_case_insensitive = False

                # If you want first + last name as required fields
                authx_first_last_name_required = True

                # If you want email as a required field
                authx_email_required = True


        class Customer(User):
            facebook_id = models.PositiveIntegerField(default=0)
            friends = models.ManyToManyField('self', blank=True)


    - Register your new models in admin.py.
      See the :py:mod:`.admin` module for more details::

        from django.contrib import admin
        from dwtools2.django.authx.admin import AuthXUserAdmin
        from .models import Customer

        @admin.register(Customer)
        class CustomerAdmin(AuthXUserAdmin):
            fieldsets = (
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': ('is_active', 'is_email_verified', 'is_staff', 'is_superuser', 'groups')}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                (_('Extra fields'), {'fields': ('facebook_id', 'friends')}),
            )

    - You may now create & query your Customer objects in the
      same way you'd query User objects.

    - When a user is logged in, ``request.user`` will always be an
      instance of the correct User subclass, in our case ``Customer``.

    - The default user manager will have a couple of additional methods::

        # This will return the correct subclass of User
        # rather than a User instance that needs to be
        # resolved
        User.objects.get_subclass(username='johnsmith')

        # This will return the correct subclass of User
        # for each model matching the queryset
        User.objects.select_subclasses().all()

    - Make use of the API functions. See :py:mod:`.api`
"""
from .api import LoginResult, authenticate, login, logout, \
    create_single_use_login_hash, verify_single_use_login_hash, \
    create_multi_use_login_hash, verify_multi_use_login_hash
from .validators import validate_username, validate_password, validate_confirm_password
