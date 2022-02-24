"""
Public functions exposed by the authx application.
"""
# pylint: disable=redefined-builtin
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.crypto import salted_hmac
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from ...datatypes import EnumX
from .settings import AuthXSettings


KEY_SALT = 'dwtools3.django.authx.api.user_login_hash'


class LoginResult(EnumX):
    """
    Enumeration for ``login()`` return values.
    """
    OK = 'Ok'
    NO_SUCH_USER = 'No such user'
    INCORRECT_PASSWORD = 'Incorrect password'
    ACCOUNT_INACTIVE = 'Account inactive'
    EMAIL_NOT_VERIFIED = 'Email not verified'


def authenticate(username, password):
    """
    Wrapper around django.contrib.auth.authenticate() just
    to keep things together.
    """
    return auth.authenticate(username=username, password=password)


def login(request, uid=None, username=None, password=None, skip_authentication=False):
    """
    Helper function to login a specific user, optionally
    skipping the authentication.

    :param HttpRequest request: The request object.
    :param int uid: *Optional*. The user_id to log in.
    :param str username: *Optional*. The username of the user to log in.
    :param str password: *Optional*. The password to authenticate the user with.
    :param bool skip_authentication: If True, the password is not checked and
        the user is logged in provided the user_id or username matches
        an existing user.

    :return: A value from the ``LoginResult`` enumeration.
        You can get the user from ``request.user`` if it succeeds.

    """
    # Verify parameters
    if uid is None and username is None:
        raise ValueError(_('One of uid or username must be specified.'))
    elif uid is not None and username is not None:
        raise ValueError(_('Only one of uid or username must be specified.'))
    elif not skip_authentication and username is None:
        raise ValueError(_('Username must be provided when authenticating with password.'))
    elif not skip_authentication and password is None:
        return LoginResult.INCORRECT_PASSWORD

    # Check the user exists
    UserModel = get_user_model()
    try:
        if uid:
            user = UserModel.objects.get(pk=uid)
        else:
            user = UserModel.objects.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        return LoginResult.NO_SUCH_USER

    # Check the password authenticates
    if skip_authentication:
        # Spoof the authenticate call
        backend = auth.get_backends()[0]
        user.backend = '{}.{}'.format(backend.__module__, backend.__class__.__name__)
    else:
        authenticated_user = auth.authenticate(username=username, password=password)
        if authenticated_user is None and not user.is_active:
            return LoginResult.ACCOUNT_INACTIVE
        elif authenticated_user is None:
            return LoginResult.INCORRECT_PASSWORD
        elif AuthXSettings.AUTHX_ENFORCE_EMAIL_VERIFICATION and not user.is_email_verified:
            return LoginResult.EMAIL_NOT_VERIFIED

    # Perform the login
    auth.login(request, user)
    return LoginResult.OK


def logout(request, keep_session=False):
    """
    Helper function to logout the current user.

    If keep_session is True, it doesn't flush the current
    session data, only marks the user as anonymous.

    If keep_session is a single or list of session keys, only
    those session keys are saved while the others are cleared.
    """
    if bool(keep_session):
        if isinstance(keep_session, str):
            old_session = {keep_session: request.session.get(keep_session, None)}
        elif isinstance(keep_session, (list, tuple, set)):
            old_session = {k: request.session.get(k, None) for k in keep_session}
        else:
            old_session = dict(request.session)
    else:
        old_session = None

    auth.logout(request)

    if old_session is not None:
        request.session.update(old_session)


def create_single_use_login_hash(user, used_for='default'):
    """
    Creates a hash that can be used to login or identify
    a user once (works until the next time the user logs in).

    Works using the Django forgot password mechanism, and expires
    after ``PASSWORD_RESET_TIMEOUT`` seconds.

    :param str used_for: An arbitrary string to identify the use of
        this hash, so it can't be used for password reset etc.
    """
    uidb64 = force_str(urlsafe_base64_encode(force_bytes(user.pk)))

    # Password is hashed by token generator, so add our used_for string to it
    oldpass = user.password
    user.password += used_for

    token = default_token_generator.make_token(user)
    user.password = oldpass

    return '{}+{}'.format(uidb64, token)


def verify_single_use_login_hash(hash, used_for='default'):
    """
    Verifies a single use login hash created by ``create_single_use_login_hash``,
    returning the user subclass if it is valid otherwise None.

    :param str used_for: An arbitrary string to identify the use of
        this hash, so it can't be used for password reset etc.
        Must match the used_for from ``create_single_use_login_hash``.

    URLconf: ``url(r'^myapp/mypage/(?P<hash>[\\w\\-\\+]+)/$', ...``
    """
    UserModel = get_user_model()

    try:
        (uidb64, token) = hash.split('+', 1)
    except ValueError:
        return None

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except ValueError:
        return None

    try:
        user = UserModel.objects.get(pk=uid)
    except UserModel.DoesNotExist:
        return None

    oldpass = user.password
    user.password += used_for
    if not default_token_generator.check_token(user, token):
        return None

    user.password = oldpass
    return user


def create_multi_use_login_hash(user, used_for='default'):
    """
    Creates a hash that can be used to login or identify
    a user multiple times (works until the user changes
    their username or password).

    Works by hashing ``used_for``, the user's username and password hash.

    :param str used_for: An arbitrary string to identify the use of
        this hash, so as not to conflict if using multiple
        different purposes for login hashes.
    """
    value = user.username + user.password + used_for
    hash = salted_hmac(KEY_SALT, value).hexdigest()
    uidb64 = force_str(urlsafe_base64_encode(force_bytes(user.pk)))
    return '{}+{}'.format(uidb64, hash)


def verify_multi_use_login_hash(hash, used_for='default'):
    """
    Verifies a multi use login hash created by ``create_multi_use_login_hash``,
    returning the user subclass if it is valid otherwise None.

    :param str used_for: An arbitrary string to identify the use of
        this hash, so as not to conflict if using multiple
        different purposes for login hashes.

    URLconf: ``url(r'^myapp/mypage/(?P<hash>[\\w\\-\\+]+)/$', ...``
    """
    UserModel = get_user_model()

    try:
        (uidb64, hash) = hash.split('+', 1)
    except ValueError:
        return None

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except ValueError:
        return None

    try:
        user = UserModel.objects.get(pk=uid)
    except UserModel.DoesNotExist:
        return None

    value = user.username + user.password + used_for
    calculated_hash = salted_hmac(KEY_SALT, value).hexdigest()

    if hash != calculated_hash:
        return None

    return user
