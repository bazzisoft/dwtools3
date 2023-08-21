"""
Useful validators for registration/profile forms.

Designed to be used from a Form's ``clean()`` method.
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .settings import AuthXSettings


def validate_username(
    username, user_id=None, message=None, case_insensitive=True, error_field=None
):
    """
    Validates the specified username is not already in use by another user.

    ``user_id`` specifies the id of the instance in question which is excluded
        from the check to support updates.

    ``message`` is the error message to raise if username is already taken.

    ``case_insensitive`` indicates whether to perform case-insensitive username
        matching (default: ``True``)

    ``error_field`` indicates under which field key to place the message of the
        ``ValidationError``. By default a string message with no field is passed
        to the ``ValidationError`` instance.
    """
    if message is None:
        if user_id is None:
            message = _("This email already exists, perhaps try recovering your password?")
        else:
            message = _("This email address is not available.")

    UserModel = get_user_model()
    try:
        qs = UserModel.objects.all()
        if user_id:
            qs = qs.exclude(id=user_id)
        cmp = "iexact" if case_insensitive else "exact"
        flt = {"username__" + cmp: username}
        qs.get(**flt)

        if error_field:
            raise ValidationError({error_field: [message]})
        else:
            raise ValidationError(message)
    except UserModel.DoesNotExist:
        pass


def validate_password(password, message=None, error_field=None):
    """
    Validates that the given password contains at least the number of
    characters specified in the setting ``AUTHX_MINIMUM_PASSWORD_LENGTH``.

    ``message`` is the error message to raise if invalid.

    ``error_field`` indicates under which field key to place the message of the
        ``ValidationError``. By default a string message with no field is passed
        to the ``ValidationError`` instance.
    """
    message = message or _("Password must contain at least {} characters.").format(
        AuthXSettings.AUTHX_MINIMUM_PASSWORD_LENGTH
    )
    if len(password) and len(password) < AuthXSettings.AUTHX_MINIMUM_PASSWORD_LENGTH:
        if error_field:
            raise ValidationError({error_field: [message]})
        else:
            raise ValidationError(message)


def validate_confirm_password(password, confirm_password, message=None, error_field=None):
    """
    Validates that ``password`` and ``confirm_password`` match.

    ``message`` is the error message to raise if they don't.

    ``error_field`` indicates under which field key to place the message of the
        ``ValidationError``. By default a string message with no field is passed
        to the ``ValidationError`` instance.
    """
    message = message or _("Confirmation did not match password.")
    if len(confirm_password) and password != confirm_password:
        if error_field:
            raise ValidationError({error_field: [message]})
        else:
            raise ValidationError(message)


def validate_username_on_form(
    form, username_field, user_id=None, message=None, case_insensitive=True
):
    """
    Validates the specified ``username_field`` on ``form`` is not already in use
    by another user.

    ``user_id`` specifies the id of the instance in question which is excluded
        from the check to support updates.

    ``message`` is the error message to display if username is already taken.

    ``case_insensitive`` indicates whether to perform case-insensitive username
        matching (default: ``True``)
    """
    username = form.cleaned_data.get(username_field, "")

    try:
        validate_username(username, user_id, message, case_insensitive)
    except ValidationError as e:
        form.add_error(username_field, e.message)


def validate_password_on_form(form, password_field, message=None):
    """
    Validates that ``password_field`` on ``form`` contains at least
    the number of characters specified in the setting ``AUTHX_MINIMUM_PASSWORD_LENGTH``.

    ``message`` is the error message to display if invalid.
    """
    password = form.cleaned_data.get(password_field, "")
    try:
        validate_password(password, message)
    except ValidationError as e:
        form.add_error(password_field, e.message)


def validate_confirm_password_on_form(form, password_field, confirm_field, message=None):
    """
    Validates that ``password_field`` and ``confirm_field`` on ``form`` match.

    ``message`` is the error message to display if they don't.
    """
    password = form.cleaned_data.get(password_field, "")
    confirm = form.cleaned_data.get(confirm_field, "")
    try:
        validate_confirm_password(password, confirm, message)
    except ValidationError as e:
        form.add_error(confirm_field, e.message)
