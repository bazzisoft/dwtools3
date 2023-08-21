"""
Application-specific settings for salesforce.
Override these in your Django settings file.
"""
from ..helpers import SettingsProxy


class SalesforceSettings(SettingsProxy):
    """ """

    SALESFORCE_ENABLED = False
    """
    Whether salesforce updates are applied.
    """

    SALESFORCE_USE_SANDBOX = True
    """
    Whether to use the salesforce sandbox APIs.
    """

    SALESFORCE_USERNAME = ""
    """
    Username for salesforce API.
    """

    SALESFORCE_PASSWORD = ""
    """
    Password for salesforce API.
    """

    SALESFORCE_SECURITY_TOKEN = ""
    """
    Security token for salesforce API.
    """

    SALESFORCE_EXTERNAL_ID_FIELD = "ExternalID__c"
    """
    Specify the default field to use as an External ID on leads, accounts and contacts.
    """

    SALESFORCE_API_VERSION = None
    """
    Specify the salesforce API version to use, eg '39.0'
    """
