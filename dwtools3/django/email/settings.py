"""
Application-specific settings for email.
Override these in your Django settings file.

"""
from ..helpers import SettingsProxy


class EmailSettings(SettingsProxy):
    """
    """

    EMAIL_EXTRA_TEMPLATE_CONTEXT = None
    """
    Set this to a dict or function of extra context to provide
    when rendering email templates.
    """
