"""
Application-specific settings for authx.
Override these in your Django settings file.
"""
from ..helpers import SettingsProxy


class AuthXSettings(SettingsProxy):
    """Global settings for the ``authx`` app"""

    AUTHX_ENFORCE_EMAIL_VERIFICATION = False
    """
    If True, allow a user to login only if AuthXUserProfile.is_email_verified
    is True. (Affects the ``authx.login()`` function.)
    """

    AUTHX_MINIMUM_PASSWORD_LENGTH = 6
    """
    The minimum length of any password used when validating passwords.
    """

    AUTHX_GENERATED_PASSWORD_LENGTH = 10
    """
    The length of any auto-generated password created
    by the authx application.
    """
