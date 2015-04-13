"""
Useful validators for registration/profile forms.

Designed to be used from a Form's ``clean()`` method.
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from .settings import AuthXSettings


def validate_username(form, username_field, user_id=None, message=None, case_insensitive=True):
    """
    Validates the specified ``username_field`` on ``form`` is not already in use
    by another user.

    ``user_id`` specifies the id of the instance in question which is excluded
        from the check to support updates.

    ``message`` is the error message to display if username is already taken.

    ``case_insensitive`` indicates whether to perform case-insensitive username
        matching (default: ``True``)
    """
    if message is None:
        if user_id is None:
            message = _('This email already exists, perhaps try recovering your password?')
        else:
            message = _('This email address is not available.')

    UserModel = get_user_model()
    username = form.cleaned_data.get(username_field, '')
    try:
        qs = UserModel.objects.all()
        if user_id:
            qs = qs.exclude(id=user_id)
        cmp = 'iexact' if case_insensitive else 'exact'
        flt = {'username__' + cmp: username}
        qs.get(**flt)
        form.add_error(username_field, message)
    except UserModel.DoesNotExist:
        pass


def validate_password(form, password_field, message=None):
    """
    Validates that ``password_field`` on ``form`` contains at least
    the number of characters specified in the setting ``AUTHX_MINIMUM_PASSWORD_LENGTH``.

    ``message`` is the error message to display if invalid.
    """
    message = message or _('Password must contain at least {} characters.').format(AuthXSettings.AUTHX_MINIMUM_PASSWORD_LENGTH)
    password = form.cleaned_data.get(password_field, '')
    if len(password) and len(password) < AuthXSettings.AUTHX_MINIMUM_PASSWORD_LENGTH:
        form.add_error(password_field, message)


def validate_confirm_password(form, password_field, confirm_field, message=None):
    """
    Validates that ``password_field`` and ``confirm_field`` on ``form`` match.

    ``message`` is the error message to display if they don't.
    """
    message = message or _('Confirmation did not match password.')
    password = form.cleaned_data.get(password_field, '')
    confirm = form.cleaned_data.get(confirm_field, '')
    if len(confirm) and password != confirm:
        form.add_error(confirm_field, message)
