from urllib.parse import urlsplit
from django.shortcuts import redirect
from django.utils.http import urlencode


def default_list_filter(callable=None, **default_filters):
    """
    Class decorator used to decorate a ModelAdmin class, and provide
    default list filter values when the page is initially opened.

    Eg.

        @default_list_filter(is_active__exact=1, my_enum__exact=foo)
        class MyAdmin(admin.ModelAdmin)
            list_filter = ('is_active', 'my_enum',)
            ...

    Can also pass a single `callable` function which takes `request` and returns a dict
    of filter parameters.
    """
    def decorator(cls):
        old_changelist_view = getattr(cls, 'changelist_view')
        def new_changelist_view(self, request, *args, **kwargs):
            if urlsplit(request.META.get('HTTP_REFERER', '')).path != request.path and \
                    not request.META.get('QUERY_STRING'):
                filters = callable(request) if callable else default_filters
                print(filters)
                if filters:
                    return redirect('{}?{}'.format(request.path, urlencode(filters)))
            return old_changelist_view(self, request, *args, **kwargs)
        setattr(cls, 'changelist_view', new_changelist_view)
        return cls
    return decorator
