"""
Helper functions/classes for models.
"""
import re
from django.db import models
from django.db.models.aggregates import Max
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.utils.text import capfirst, get_text_list
from django.utils.translation import ugettext_lazy as _


# Add 'order_within_fields' meta option to django
models.options.DEFAULT_NAMES = models.options.DEFAULT_NAMES + ('order_within_fields',)


class OrderedModelManager(models.Manager):
    """
    Model manager for models that inherit from ``OrderedModel``.
    """
    def moveup(self, item_or_id):
        """
        Reorders an item up one spot.
        """
        item = item_or_id if isinstance(item_or_id, OrderedModel) else self.get(id=item_or_id)
        filters = item.get_order_within_fields_filters()
        prevs = self.filter(ordering__lt=item.ordering, **filters).order_by('-ordering')[:2]

        if len(prevs) == 2:
            self.reorder(item, prevs[1])
        elif len(prevs) == 1:
            self.reorder(item, None)

    def movedown(self, item_or_id):
        """
        Reorders an item down one spot.
        """
        item = item_or_id if isinstance(item_or_id, OrderedModel) else self.get(id=item_or_id)
        filters = item.get_order_within_fields_filters()
        next = self.filter(ordering__gt=item.ordering, **filters).order_by('ordering')[:1]

        if next:
            self.reorder(item, next[0])

    def reorder(self, item_or_id, after_item_or_id):
        """
        Reorders an item, placing it after ``after_item``.

        Note that the ``order_within_fields`` values in ``item`` must
        be equal to those in ``after_item`` (otherwise we're reordering
        between different lists...)

        Automatically rebalances the ordering values if necessary.
        """
        item = item_or_id if isinstance(item_or_id, OrderedModel) else self.get(id=item_or_id)
        filters = item.get_order_within_fields_filters()
        pre = after_item_or_id \
              if after_item_or_id is None or isinstance(after_item_or_id, OrderedModel) \
              else self.get(id=after_item_or_id)

        if not item.id or (pre is not None and not pre.id):
            raise ValueError('Cannot reorder unsaved items.')

        if pre is None:
            post = self.filter(**filters).order_by('ordering')
        else:
            post = self.filter(ordering__gt=pre.ordering, **filters).order_by('ordering')
        post = post[0] if len(post) > 0 else None

        # Check if we're moving to same place - noop
        if item == pre or item == post:
            return

        # Check pre/post have the same order_within_fields values as item
        tocheck = pre or post
        if tocheck:
            for f in item.get_order_within_fields():
                if getattr(item, f) != getattr(tocheck, f):
                    raise ValueError('Cannot items to reorder have different values for field "{}"'.format(f))

        # Calculate ordering positions of item before and after
        pre_ordering = pre.ordering if pre else 0
        post_ordering = post.ordering if post else pre.ordering + 200

        # No room left? Rebalance all ordering values & run recursively
        if post_ordering - pre_ordering <= 1:
            self.rebalance_ordering(models_to_update=[item] + [pre] if pre else [], **filters)
            self.reorder(item, pre)
            return

        # We have room, set item.ordering to the mid-point of pre and post
        # then save.
        item.ordering = (pre_ordering + post_ordering) // 2
        item.save()

    def rebalance_ordering(self, models_to_update=None, **order_within_field_values):
        """
        Rebalances the ordering values for a given set of ``order_within_fields``,
        using gaps of 100.

        For example, if the model represents menu items belonging to a menu,
        and we want to rebalance all items for ``menu.id = 5``::

            rebalance_ordering(menu=5)

        ``models_to_update`` can be an iterable of model instances to update
        if their orderings change.
        """
        models_to_update = {m.id: m for m in (models_to_update or ())}
        next_ordering = 100
        for item in self.filter(**order_within_field_values).order_by('ordering'):
            item.ordering = next_ordering
            item.save()
            if item.id in models_to_update:
                models_to_update[item.id].ordering = next_ordering
            next_ordering += 100

    def rebalance_ordering_for_all_records(self):
        """
        Rebalances the ordering for all possible values of ``order_within_fields``.
        """
        item_filters = self.distinct().values(*self.model._meta.order_within_fields)
        for flt in item_filters:
            self.rebalance_ordering(**flt)


class OrderedModel(models.Model):
    """
    Abstract model that includes an ``ordering`` field which stores
    the order of the items in the model. Smaller values are higher
    in the list.

    ``Meta.order_within_fields`` is a tuple of key fields which
    have their own ordering. For example, for menu items, the
    ``menu`` foreign key would be set in ``order_within_fields``,
    and each menu would have its own ordering of items.

    If you override the model manager, be sure to inherit from
    OrderedModelManager().

    You may omit a value for the ``ordering`` field when adding a new record
    to have it automatically placed at the end.

    You may optional set a ``unique_together`` constraint for
    all ``order_within_fields`` plus ``ordering``.
    """
    ordering = models.PositiveIntegerField(blank=True, db_index=True)

    objects = OrderedModelManager()

    class Meta:
        abstract = True
        ordering = ('ordering',)
        order_within_fields = ()

    def get_order_within_fields(self):
        return self._meta.order_within_fields

    def get_order_within_fields_filters(self):
        return {f: getattr(self, f) for f in self._meta.order_within_fields}

    def save(self, *args, **kwargs):
        if not self.id:
            if self.ordering is None:
                filters = self.get_order_within_fields_filters()
                max = self.__class__.objects.filter(**filters).aggregate(Max('ordering'))
                self.ordering = (max['ordering__max'] or 0) + 100
        super(OrderedModel, self).save(*args, **kwargs)


class TimestampedModel(models.Model):
    """
    Abstract model that includes ``created_at`` and ``modified_at``
    auto-updating fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def check_model_is_unique_with_conditions(model_instance, unique_fields, qs_conditions=None, error_message=None, error_field=None, case_insensitive=False):
    """
    Checks the given model instance is unique with respect to ``unique_fields``.

    ``qs_conditions`` is a dict with additional keyword args added to the queryset
    when performing the unique check. For example, to skip the unique check
    for inactive items.

    ``error_message`` specified the error to display of the unique check fails.
    If ``None``, one is automatically created.

    ``error_field`` is the field to which to assign the error message, or None
    to just assign to the ``__all__`` list.

    ``case_insensitive`` indicates to perform insensitive string matching on the
    field values.

    Eg.::

        def clean():
            check_model_unique_with_conditions(self, ('name', 'type'), {'is_active': True})
    """
    model = type(model_instance)
    filter_kwargs = {(f + ('__iexact' if case_insensitive else '')): getattr(model_instance, f) for f in unique_fields}
    if qs_conditions is not None:
        filter_kwargs.update(qs_conditions)
    qs = model.objects.filter(**filter_kwargs)

    if model_instance.pk is not None:
        qs = qs.exclude(pk=model_instance.pk)

    if qs.count() > 0:
        if error_message is None:
            model_name = str(model._meta.verbose_name)
            field_labels = [model._meta.get_field(f).verbose_name for f in unique_fields]
            field_labels = str(get_text_list(field_labels, _('and')))
            error_message = _('A {} with this {} already exists.').format(model_name, field_labels)
        if error_field is None:
            raise ValidationError(error_message)
        else:
            raise ValidationError({error_field: [error_message]})


def unique_slugify(instance, value, slug_field_name='slug', queryset=None, slug_separator='-'):
    """
    Automatically create a unique slug for a model.

    Note that you don't need to do::

        obj.slug = ...

    since this method updates the instance's slug field directly.
    All you usually need is::

        unique_slugify(obj, obj.title)

    A frequent usage pattern is to override the save method of a model and
    call unique_slugify before the super(...).save() call.

    Borrowed from: http://djangosnippets.org/snippets/690/

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
        # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
        # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value
