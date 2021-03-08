"""
Useful form mixins.
"""
from django import forms


class KeepCurrentInstanceChoicesModelFormMixin:
    """
    ``ModelForm`` mixin that finds all ``ModelChoiceFields`` and ``ModelMultipleChoiceFields``
    in the form, and ensures all values currently assigned to the instance
    are still selectable on save (even if they are disallowed due to the
    specified querysets.)

    For example, a user that has been deactivated can still be saved on the
    form for existing instances, but not for new ones.

    **IMPORTANT**: This mixin must be inherited *before* ``ModelForm``.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.instance, 'This mixin can only be used with ModelForms.'
        if not self.instance.id:
            return

        for fieldname, field in self.fields.items():
            if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)):
                curval = getattr(self.instance, fieldname, None)
                if curval:
                    if hasattr(curval, 'pk'):
                        field.queryset = (
                            field.queryset | curval.__class__.objects.filter(pk=curval.pk)
                        ).distinct()
                    elif hasattr(curval, 'target_field'):
                        field.queryset = (
                            field.queryset |
                            curval.target_field.related_model.objects.filter(pk__in=curval.all())
                        ).distinct()
                    else:
                        # TODO: Other cases we need to handle?
                        pass
