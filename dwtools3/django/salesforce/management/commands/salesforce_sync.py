import time
import logging
import pprint
from django.core.management.base import BaseCommand
from ... import api


class Command(BaseCommand):
    help = 'Synchronize scheduled salesforce updates from the sync queue'

    def add_arguments(self, parser):
        parser.add_argument('--max-runtime', action='store', type=int, dest='max_runtime',
                            default=0, help='Maximum runtime of a single sync run (secs).')

    def set_verbosity(self, options):
        verbosity = int(options.get('verbosity'))
        if verbosity < 1:
            logging.getLogger(None).setLevel(logging.WARN)
            api.logger.setLevel(logging.WARN)

    def handle(self, *args, **options):
        self.set_verbosity(options)

        api.logger.info('Starting salesforce sync...')

        start_time = time.time()
        while True:
            if (options['max_runtime'] > 0 and
                    time.time() - start_time + 30 > options['max_runtime']):
                api.logger.info('Max runtime exceeded, exiting.')
                break

            item = api.get_next_scheduled_sync_function()
            if not item:
                api.logger.info('All items processed, exiting.')
                break

            api.logger.info('\n%s()\n%s', item.function, '-' * (len(item.function) + 2))

            try:
                api.run_sync_function(item)
            except Exception:
                api.logger.exception(
                    'Error while processing salesforce sync function %s().\n\n'
                    'Parameters:\n%s\n\n',
                    item.function,
                    pprint.pformat(item.params, indent=2))

                if item.reschedule_on_error is not None:
                    api.reschedule_sync_function(item)
