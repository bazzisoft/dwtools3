TODO - dwtools3
===============
- Context manager or function to run multiple validation functions
  and collate all error messages into local dict or something
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


Django Changes (1.6 >> 1.9)
===========================

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


Django Changes 1.6 >> 1.11
==========================

MAJOR CHANGES
-------------

### dwtools2
- Delete any unused code in dwtools2, probably not Python 3 compatible.


### Settings
- Rewrite settings files to work with latest version of Django.
    - Templates
    - Middleware. Especially / redirect middleware.
- Copy new project scaffolds (`wsgi.py`, `manage.py` etc).
- Fix logging per hstalks
- New `DATA_UPLOAD_MAX_MEMORY_SIZE` limited to 2.5MB. Will need to set this larger as per nginx. <https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-DATA_UPLOAD_MAX_MEMORY_SIZE>


### URLs
- Use new URLs format:

        from django.conf.urls import url
        from myapp import views
        
        urlpatterns = [
            url('^$', views.myview),
            url('^other/$', views.otherview),
        ]


### Migrations
- Apply all migrations to all servers. Delete all migrations and remove South. Recreate all initial migrations via Django. Run `migrate --fake-initial` to indicate they are applied.

- The name field of `django.contrib.contenttypes.models.ContentType` has been removed by a migration and replaced by a property. That means it’s not possible to query or filter a ContentType by this field any longer. Be careful if you upgrade to Django 1.8 and skip Django 1.7. If you run manage.py migrate --fake, this migration will be skipped and you’ll see a RuntimeError: Error creating new content types. exception because the name column won’t be dropped from the database. Use manage.py migrate --fake-initial to fake only the initial migration instead.

- `djorm_pgarray` lib no longer needed as can use built in `ArrayField`.


### User Model/Auth
- Create combined user model from AbstractUser. Set AUTH_USER_MODEL. Remove long username hacks. Migrate to new user model somehow. Remove subclassing inheritance query thingy for loading AccountUser.
- Migrate to dwtools3 version of AuthX
- `django.contrib.auth` in settings may now be deprecated????? Not sure on this one.


### Template Tags
- `@simple_tag` is now wrapped in conditional escape. Must return HTML output wrapped in `mark_safe()` or `format_html()`.

- Django 1.4 added the assignment_tag helper to ease the creation of template tags that store results in a template variable. The simple_tag() helper has gained this same ability, making the assignment_tag obsolete. Tags that use assignment_tag should be updated to use simple_tag.


### Management Commands
- Based on `argparse`, may not work anymore with `optparse`. Delete old unused management commands. See <https://docs.djangoproject.com/en/2.0/releases/1.8/#extending-management-command-arguments-through-command-option-list>


### API
- Upgrade to latest `django_rest_framework`. Fix API permission hacks for current version? (Limit querysets callable?)
- Rejiggle django-rest-swagger so it works on latest.
- `DjangoFilterBackend` may need rejiggle.
- Check DRF API docs: <http://www.django-rest-framework.org/topics/3.6-announcement/>


SPECIFICS
---------

### Database
- The minimum supported version of psycopg2 is increased from 2.4.5 to 2.5.4.

  
### Users/Auth
- Using `User.is_authenticated()` and `User.is_anonymous()` as methods is now deprecated (to Django 2), prefer property access.
- The `HttpRequest` is now passed to `authenticate()` which in turn passes it to the authentication backend if it accepts a request argument.
- Function-based password change/reset/login/logout views are deprecated???


### BigAutoField
- `apps.alerting.models.PerformanceDataPoint` uses the `BigAutoField` from dwtools2. Replace this with the Django equivalent in the new version.


### Settings
- For static files storage, changed `CachedStaticFilesStorage` to `ManifestStaticFilesStorage`.
- All settings now lists.
- The PostgreSQL backend `django.db.backends.postgresql_psycopg2` is now available as `django.db.backends.postgresql`.


### Models
- `Model._meta` formalized. Search for uses of it a check against <https://docs.djangoproject.com/en/2.0/ref/models/meta/#migrating-old-meta-api>.
- The `on_delete` argument of ForeignKey and OneToOneField will be required in Django 2.0. Update models and existing migrations to explicitly set the argument. Since the default is `models.CASCADE`, add `on_delete=models.CASCADE` to all ForeignKey and OneToOneFields that don’t use a different option.
- `Field.rel` and its methods and attributes have changed to match the related fields API. Used by `BigAutoField`, `InheritanceQuerySet` which should be removed or updated.


### Forms
- `django.forms.util` renamed to `django.forms.utils`.
- The unused choices keyword argument of the Select and SelectMultiple widgets’ render() 
method is removed. The choices argument of the render_options() method is also removed, 
making selected_choices the first argument.


### Fabric/Manage
- The `-n` flag for `dumpdata` has been renamed to `--natural-foreign`. See `manage.py` in fabric modules dwtools2/uptime.


### Requests
- `request.REQUEST` is now deprecated, use `GET` or `POST`. 


### Middleware
- Middleware has been upgraded, may need to adapt: <https://docs.djangoproject.com/en/2.0/topics/http/middleware/#upgrading-middleware>
- SessionAuthenticationMiddleware is built in & may be removed.


### Enums
- Will they still work with old enum class???


### Templates
- The dictionary and context_instance parameters for the following functions are removed:

        django.shortcuts.render()
        django.shortcuts.render_to_response()
        django.template.loader.render_to_string()

- `django.template.backends.django.Template.render()` prohibits non-dict context. Must receive a dictionary of context rather than Context or RequestContext.


### Admin
- The `allow_tags` attribute on methods of `ModelAdmin` has been deprecated. Use `format_html()`, `format_html_join()`, or `mark_safe()` when constructing the method’s return value instead.

- Django admin tools needs template loader: Starting from this version (0.7.0) you must add ``admin_tools.template_loaders.Loader`` to your templates loaders variable in your settings file, see here for details: <https://django-admin-tools.readthedocs.io/en/latest/configuration.html>


REFACTORING
-----------

### Forms
- Use `form.add_error()` instead of accessing `form._errors`.


### Dependencies
- Review all dependencies, remove unused, upgrade what can be upgraded.


TESTING
-------
### ValidationError
- Possible that `ValidationError.error_list`, `error_dict` or `update_error_dict()` return `ValidationError` instances instead of strings.  
  <https://docs.djangoproject.com/en/2.0/releases/1.7/#validation-error-constructor-and-internal-storage>

