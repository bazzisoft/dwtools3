TODO - dwtools3
===============
- **AJAX/JSON decorators:** should use new JSONResponse class.


Python 3 Changes
================

Major
-----
- Unicode fixed (`str`/`bytes`)
- Built-in virtual envs (`pyvenv`)
- Built-in `Enum` class in `enum` package

Syntax
------
- `nonlocal x` to reference x in between local and global scope
- Extended Iterable Unpacking. You can now write things like `a, b, *rest = some_sequence`. And even `*rest, a = stuff`. The rest object is always a (possibly empty) list; the right-hand side may be any iterable.
- Dictionary comprehensions: `{k: v for k, v in stuff}`
- Set literals, e.g. `{1, 2}`
- New metaclass syntax: `class C(metaclass=M):`
- `yield from` for generator delegation

Exceptions
----------
- Include inner exception: `raise ValueError() from exc`
- Discard previous exception: `raise ValueError() from None`
- All IO exceptions inherit from `OSError`

StdLib
------
- New `io` package for all IO
- New `selectors` package for high-level `select()` operations
- New `pathlib` package for high-level, os independent path manipulation
- New `statistics` module with math operations

Django Changes
==============

Major
-----
- Migrations
- AppConfig (customize app names, labels, settings, ready() callback)

Models
-----
- DB raw SQL cursors work as context managers
- Formalized `Model._meta` API
- `Prefetch` objects for customizing `prefetch_related` (eg. filtering prefetched objects)
- `Lookup` and `Transform` classes for creating custom queryset filtering (eg. `day_lte` for a `DateField`)
- `QuerySet.update_or_create()`
- `F()` expressions, including arithmetic `F(field1) - F(field2)`
- Query expressions (`aggregate`/`annotate` with complex F-expressions) and conditional expressions (`Case`, `When`...)
- `ForeignKey`/`ManyToManyField.limit_choices_to` accepts a callable.
- `QuerySet.order_by('foreignkey_id')`
- Postgres specific field types: `ArrayField`, `HStoreField`, `Range Fields`, and `unaccent` lookup.
- New field types: `UUIDField` and `DurationField`
- `ImageField` with image validation

Views
-----
- New `JsonResponse` to automatically encode JSON
- Added `SecurityMiddleware` with a bunch of optional checks
- URLpatterns new format is:

        urlpatterns = [
            url('^$', views.myview),
            url('^other/$', views.otherview),
        ]

Forms
-----
- `Form.add_error()` method to add a field-specific error from `clean()` or the view.
- Forms & fields have a `label_suffix` argument, eg for specifying trailing colon.

Auth
----
- New `send_email()` method in `ForgotPasswordForm` that can be overridden for custom emails.
- Forgot password view takes `html_email_template_name` to send HTML forgot password emails.

Admin
-----
- You can now implement `site_header`, `site_title`, and `index_title` attributes on a custom AdminSite in order to easily change the admin site’s page title and header text. No more needing to override templates!
- `@register` decorator to save `admin.site.register()` calls.
- Can set `list_display_links=None` to prevent editing from the grid.
- `InlineModelAdmin` has `show_change_link`
- `RelatedOnlyFieldListFilter` in `ModelAdmin.list_filter` to limit the list_filter choices to foreign objects which are attached to those from the ModelAdmin.

Email
-----
- send_email() accepts a `html_message` param. Worth checking if it auto-creates a text version.

Misc
----
- `ManifestStaticFilesStorage` preferred way to manage static files on production.
- Sitemaps framework