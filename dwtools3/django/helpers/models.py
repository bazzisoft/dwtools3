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
    def _get_ordered_id_list_and_current_index(self, item_or_id):
        """
        Returns the specified item, a list of all IDs in correct order
        except the specified item's ID, and the index at which the current
        item was in the list.
        """
        item = item_or_id if isinstance(item_or_id, OrderedModel) else self.get(id=item_or_id)
        assert item.id, 'Cannot order unsaved items.'
        id_list = list(self.filter(**item.get_order_within_fields_filters())
                       .values_list('id', flat=True))

        try:
            current_idx = id_list.index(item.id)
            del id_list[current_idx]
        except ValueError:
            current_idx = None

        return item, id_list, current_idx

    def _move_item_to_index(self, item, id_list, new_idx):
        """
        Reorders an item, placing it at ``new_idx``.

        If ``new_idx`` is less than 0, the item is placed at the start.

        If ``new_idx`` is greater-equal than the number of items, the item
        is placed at the end.
        """
        # Find the ordering of the previous item at the new position
        if not id_list or new_idx <= 0:
            pre_id = None
            pre_ordering = 0
        else:
            if new_idx < len(id_list):
                pre_id = id_list[new_idx - 1]
            else:
                pre_id = id_list[-1]
            pre_ordering = self.get(id=pre_id).ordering

        # Find the ordering of the next item at the new position
        if not id_list or new_idx >= len(id_list):
            post_id = None
            post_ordering = pre_ordering + 200
        else:
            if new_idx >= 0:
                post_id = id_list[new_idx]
            else:
                post_id = id_list[0]
            post_ordering = self.get(id=post_id).ordering

        # Check if we're moving to same place - no-op
        if item.id == pre_id or item.id == post_id:
            return

        # No room left? Rebalance all ordering values & run recursively
        if post_ordering - pre_ordering <= 1:
            self.rebalance_ordering(models_to_update=[item],
                                    **item.get_order_within_fields_filters())
            self._move_item_to_index(item, id_list, new_idx)
            return

        # We have room, set item.ordering to the mid-point of pre and post
        # then save.
        item.ordering = (pre_ordering + post_ordering) // 2
        item.save(update_fields=['ordering'])

    def moveup(self, item_or_id):
        """
        Reorders an item up one spot.
        """
        item, id_list, current_idx = self._get_ordered_id_list_and_current_index(item_or_id)
        self._move_item_to_index(item, id_list, current_idx - 1)

    def movedown(self, item_or_id):
        """
        Reorders an item down one spot.
        """
        item, id_list, current_idx = self._get_ordered_id_list_and_current_index(item_or_id)
        self._move_item_to_index(item, id_list, current_idx + 1)

    def moveto(self, item_or_id, index):
        """
        Reorders an item to the specified index. If index is None, the item
        is placed at the end.
        """
        item, id_list, _current_idx = self._get_ordered_id_list_and_current_index(item_or_id)

        if index is None:
            index = len(id_list)

        self._move_item_to_index(item, id_list, index)

    def reorder(self, item_or_id, after_item_or_id):
        """
        Reorders an item, placing it after ``after_item``.

        If ``after_item`` is None, the item is placed at the top.

        Note that the ``order_within_fields`` values in ``item`` must
        be equal to those in ``after_item`` (otherwise we're reordering
        between different lists...)
        """
        item, id_list, _current_idx = self._get_ordered_id_list_and_current_index(item_or_id)

        after_id = (after_item_or_id.id if isinstance(after_item_or_id, OrderedModel)
                    else after_item_or_id)

        # Ordering to same place? No-op
        if item.id == after_id:
            return

        if after_id is not None:
            try:
                new_idx = id_list.index(after_id) + 1
            except ValueError:
                assert False, 'Cannot reorder items with different `order_within_fields` values.'
        else:
            new_idx = 0

        self._move_item_to_index(item, id_list, new_idx)

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
        for item in self.filter(**order_within_field_values):
            item.ordering = next_ordering
            item.save(update_fields=['ordering'])
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

    @classmethod
    def get_order_within_fields(cls):
        return cls._meta.order_within_fields

    def get_order_within_fields_filters(self):
        return {f: getattr(self, f) for f in self._meta.order_within_fields}

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        if not self.id:
            if self.ordering is None:
                filters = self.get_order_within_fields_filters()
                maximum = self.__class__.objects.filter(**filters).aggregate(Max('ordering'))
                self.ordering = (maximum['ordering__max'] or 0) + 100
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


def check_exactly_one_field_is_not_none(model_instance, fields, error_message=None):
    """
    Checks the given model instance has exactly one of `fields` set to a non-None value.

    ``error_message`` specified the error to display of the unique check fails.
    If ``None``, one is automatically created.

    Eg.::

        def clean():
            check_exactly_one_field_is_not_none(self, ('fkey1', 'fkey2'))
    """
    non_none = [1 for f in fields if getattr(model_instance, f) is not None]
    if len(non_none) != 1:
        if not error_message:
            field_str = ', '.join(fields[:-1]) + ' and ' + fields[-1]
            error_message = _('Exactly one of {} must be specified.').format(field_str)
        raise ValidationError(error_message)


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
