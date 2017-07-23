from datetime import timedelta
import importlib
import logging

from django.db import transaction
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from simple_salesforce import Salesforce
from simple_salesforce.api import DEFAULT_API_VERSION
from .models import SyncQueueItem
from .settings import SalesforceSettings


#----------------------------
# Salesforce Logger
#----------------------------
logger = logging.getLogger('dwtools3.django.salesforce')
"""
Use this logger for any salesforce-related output, such as
your salesforce processor functions. All log messages
are sent to the ``dwtools3.django.salesforce`` logger.
"""


#----------------------------
# Salesforce Instance
#----------------------------

def create_salesforce_instance():
    """
    Create a low-level simple-salesforce instance to query over the REST API.
    """
    return Salesforce(username=SalesforceSettings.SALESFORCE_USERNAME,
                      password=SalesforceSettings.SALESFORCE_PASSWORD,
                      security_token=SalesforceSettings.SALESFORCE_SECURITY_TOKEN,
                      sandbox=SalesforceSettings.SALESFORCE_USE_SANDBOX,
                      version=SalesforceSettings.SALESFORCE_API_VERSION or DEFAULT_API_VERSION)


# Process-shared Salesforce instance from simple_salesforce
sf = SimpleLazyObject(create_salesforce_instance)


#----------------------------
# Sync Queue Management
#----------------------------

def schedule_sync_function(func, params, scheduled_at=None,
                           reschedule_on_error=None, prevent_repetition=False):
    """
    Schedule a sync function to run in the future to update salesforce
    via the API.
    """
    item = SyncQueueItem()
    item.scheduled_at = scheduled_at
    item.reschedule_on_error = reschedule_on_error
    item.module = func.__module__
    item.function = func.__name__
    item.params = params
    item.full_clean()

    with transaction.atomic():
        if prevent_repetition:
            (SyncQueueItem.objects
             .filter(module=item.module, function=item.function, _params=item._params)
             .delete())

        item.save()

    logger.info('Salesforce: Scheduled function %s()',
                item.function)


def get_next_scheduled_sync_function():
    """
    Pop the next sync function entry that needs to run from the queue.
    """
    now = timezone.now()
    item = (SyncQueueItem.objects
            .filter(scheduled_at__lte=now)
            .order_by('scheduled_at')
            .first())

    if item:
        SyncQueueItem.objects.filter(id=item.id).delete()
        item.pk = None

    return item


def reschedule_sync_function(item, delay_mins=None):
    """
    Reschedule a sync function entry (for example after failure due to error).
    """
    if delay_mins is None:
        delay_mins = item.reschedule_on_error or 0

    item.pk = None
    item.scheduled_at = timezone.now() + timedelta(minutes=delay_mins)
    item.full_clean()
    item.save(force_insert=True)

    logger.info('Salesforce: Rescheduled function %s() in %s mins',
                item.function, delay_mins)


def run_sync_function(item):
    """
    Execute the sync function for the given entry.
    """
    module = importlib.import_module(item.module)
    try:
        func = getattr(module, item.function)
    except AttributeError:
        raise AttributeError('Salesforce: Function "{}" not defined in module "{}".'
                             .format(item.function, item.module))

    params = item.params

    if not SalesforceSettings.SALESFORCE_ENABLED:
        logger.info('MOCKING: Salesforce: Running function %s(%s)',
                    item.function, repr(item.params))
    else:
        logger.info('Salesforce: Running function %s()',
                    item.function)

        if isinstance(params, (list, tuple)):
            func(*params)
        elif isinstance(params, dict):
            func(**params)
        else:
            func(params)
