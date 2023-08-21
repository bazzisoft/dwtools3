import copy


def logging_dictmerge(*dicts):
    """
    Merges two or more logging config dicts into a single combined dict
    which can be used in Django settings for logging configuration.
    """
    result = {}
    for dct in dicts:
        for k, v in dct.items():
            if isinstance(v, dict) and k in result:
                result[k] = logging_dictmerge(result[k], v)
            else:
                result[k] = copy.deepcopy(v)

    return result


ROOT_LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console_always": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {},
    "root": {
        "handlers": ["console_always", "mail_admins"],
        "level": "INFO",
    },
}
"""
Merge this logger configuration to print output from any
custom loggers to the console, and email admins of
errors in production.
"""


DJANGO_SQL_LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {
        "django_sql": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.FileHandler",
            "mode": "w",
            "filename": "django_sql.log",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["django_sql"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
"""
Merge this logger configuration to print SQL queries
to a log file.
"""
