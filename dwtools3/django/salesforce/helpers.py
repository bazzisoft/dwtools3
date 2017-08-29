import functools
import operator

from simple_salesforce import SalesforceResourceNotFound

from .api import logger, sf
from .settings import SalesforceSettings


_STRING_ESCAPE_MAP = str.maketrans({
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
    '\b': '\\b',
    '\f': '\\f',
    '"': '\\"',
    "'": "\\'",
    '\\': '\\\\',
})

_LIKE_ESCAPE_MAP = str.maketrans({
    '_': '\\_',
    '%': '\\%',
})


def _resolve_sf_obj(name_or_obj):
    if isinstance(name_or_obj, str):
        return getattr(sf, name_or_obj)
    else:
        return name_or_obj


def escape(s):
    return s.translate(_STRING_ESCAPE_MAP)


def escape_for_like(s):
    return escape(s).translate(_LIKE_ESCAPE_MAP)


def get_by_id(sf_obj, id):
    sf_obj = _resolve_sf_obj(sf_obj)
    logger.info('Salesforce: %s.get_by_id(%s)', sf_obj.name, id)

    try:
        return sf_obj.get(id)
    except SalesforceResourceNotFound:
        return None


def get_by_external_id(sf_obj, external_id, *, external_id_field=None):
    """
    Retrieves an arbitrary salesforce object by its external ID.
    """
    sf_obj = _resolve_sf_obj(sf_obj)
    external_id_field = external_id_field or SalesforceSettings.SALESFORCE_EXTERNAL_ID_FIELD

    logger.info('Salesforce: %s.get_by_custom_id(%s)', sf_obj.name, external_id)

    try:
        return sf_obj.get_by_custom_id(external_id_field, external_id)
    except SalesforceResourceNotFound:
        return None


def get_by_email(sf_obj, email):
    """
    Retrieves an arbitrary salesforce object by its email address (Lead/Contact)
    """
    sf_obj = _resolve_sf_obj(sf_obj)

    logger.info('Salesforce: %s.get_by_email(%s)', sf_obj.name, email)

    try:
        return sf_obj.get_by_custom_id('Email', email)
    except SalesforceResourceNotFound:
        return None


def create_record(sf_obj, data, *, external_id=None, external_id_field=None):
    """
    Creates a new salesforce record of an arbitrary object, possibly
    populating the external id field along with the given data.

    :return: The salesforce id of the created record.
    """
    sf_obj = _resolve_sf_obj(sf_obj)
    external_id_field = external_id_field or SalesforceSettings.SALESFORCE_EXTERNAL_ID_FIELD

    if external_id and external_id_field not in data:
        data = dict(data, **{external_id_field: external_id})

    logger.info('Salesforce: %s.create(%s)', sf_obj.name, external_id or '')
    ret = sf_obj.create(data)
    logger.info('Salesforce: >>> %s', ret['id'])
    return ret['id']


def update_record(sf_obj, data, *, id=None, external_id=None, external_id_field=None):
    """
    Updates an arbitrary salesforce object with the given data fields,
    identifying it by salesforce id or external id.

    :return: The salesforce id if updated, None if not found.
    """
    sf_obj = _resolve_sf_obj(sf_obj)
    assert operator.xor(bool(id), bool(external_id)), 'Exactly one of id or external id must be specified.'

    if not id:
        obj = get_by_external_id(sf_obj, external_id, external_id_field=external_id_field)
        if not obj:
            return None
        id = obj['Id']

    logger.info('Salesforce: %s.update(%s)', sf_obj.name, id)
    try:
        sf_obj.update(id, data)
    except SalesforceResourceNotFound:
        id = None

    logger.info('Salesforce: >>> %s', id)
    return id


def create_or_update_record(sf_obj, data, *, id=None, external_id=None, external_id_field=None):
    """
    Creates or updates a salesforce record with the given salesforce id or
    external id.

    :return: The salesforce id of the updated or created record.
    """
    id = update_record(sf_obj, data, id=id, external_id=external_id,
                       external_id_field=external_id_field)

    if id is None:
        id = create_record(sf_obj, data, external_id=external_id,
                           external_id_field=external_id_field)

    return id


def delete_record(sf_obj, *, id=None, external_id=None, external_id_field=None):
    """
    Deletes an arbitrary salesforce object,
    identifying it by salesforce id or external id.

    :return: The salesforce id if deleted, None if not found.
    """
    sf_obj = _resolve_sf_obj(sf_obj)
    assert operator.xor(bool(id), bool(external_id)), 'Exactly one of id or external id must be specified.'

    if not id:
        obj = get_by_external_id(sf_obj, external_id, external_id_field=external_id_field)
        if not obj:
            return None
        id = obj['Id']

    logger.info('Salesforce: %s.delete(%s)', sf_obj.name, id)
    try:
        sf_obj.delete(id)
    except SalesforceResourceNotFound:
        id = None

    logger.info('Salesforce: >>> %s', id)
    return id


#----------------------------
# Accounts
#----------------------------

get_account = functools.partial(get_by_external_id, 'Account')
"""
Find an account by its External ID.
"""

create_account = functools.partial(create_record, 'Account')
"""
Create a new salesforce Account.
"""

update_account = functools.partial(update_record, 'Account')
"""
Updates a Salesforce Account.
"""

create_or_update_account = functools.partial(create_or_update_record, 'Account')
"""
Creates or updates a salesforce Account.
"""

delete_account = functools.partial(delete_record, 'Account')
"""
Deletes a salesforce Account.
"""


#----------------------------
# Contacts
#----------------------------

get_contact = functools.partial(get_by_external_id, 'Contact')
"""
Find an contact by its External ID.
"""

get_contact_by_email = functools.partial(get_by_email, 'Contact')
"""
Find an contact by its External ID.
"""

create_contact = functools.partial(create_record, 'Contact')
"""
Create a new salesforce Contact.
"""

update_contact = functools.partial(update_record, 'Contact')
"""
Updates a Salesforce Contact.
"""

create_or_update_contact = functools.partial(create_or_update_record, 'Contact')
"""
Creates or updates a salesforce Contact.
"""

delete_contact = functools.partial(delete_record, 'Contact')
"""
Deletes a salesforce Contact.
"""
