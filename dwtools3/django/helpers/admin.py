from urllib.parse import urlsplit
from django.shortcuts import redirect
from django.utils.http import urlencode


def default_list_filter(**default_filters):
    """
    Class decorator used to decorate a ModelAdmin class, and provide
    default list filter values when the page is initially opened.

    Eg.

        @default_list_filter(is_active__exact=1, my_enum__exact=foo)
        class MyAdmin(admin.ModelAdmin)
            list_filter = ('is_active', 'my_enum',)
            ...
    """
    def decorator(cls):
        old_changelist_view = getattr(cls, 'changelist_view')
        def new_changelist_view(self, request, *args, **kwargs):
            if urlsplit(request.META.get('HTTP_REFERER', '')).path != request.path and \
                    not request.META.get('QUERY_STRING'):
                return redirect('{}?{}'.format(request.path, urlencode(default_filters)))
            return old_changelist_view(self, request, *args, **kwargs)
        setattr(cls, 'changelist_view', new_changelist_view)
        return cls
    return decorator
