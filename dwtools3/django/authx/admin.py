"""
Enables a single-page admin screen for user creation, for
models based on ``AbstractUser``::

    # models.py

    # Create our model that extends ``AbstractUser`` or ``AuthXAbstractUser``
    class MyUserModel(AbstractUser):
        my_field = models.CharField(max_length=100)


    # admin.py

    from django.contrib import admin
    from dwtools2.django.authx.admin import AuthXUserAdmin
    from .models import MyUserModel

    @admin.register(MyUserModel)
    class MyUserModelAdmin(AuthXUserAdmin):
        fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
            (_('Permissions'), {'fields': ('is_active', 'is_email_verified', 'is_staff', 'is_superuser', 'groups')}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
            (_('Extra fields'), {'fields': ('my_field',)}),
        )
"""
import copy
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, UserChangeForm
from django.core.exceptions import ValidationError


def build_user_creation_form(base=UserChangeForm):
    class AuthXUserCreationForm(base):
        """
        Alternative user creation form that shows all fields instead of
        just username & password.

        Created dynamically to support overriding the UserChangeForm
        by the developer of the final User subclass.
        """
        error_messages = {
            'password_mismatch': _('The two password fields didn\'t match.'),
        }

        password = forms.CharField(label=_('Password'),
                                   widget=forms.PasswordInput)
        password2 = forms.CharField(label=_('Password confirmation'),
                                    widget=forms.PasswordInput,
                                    help_text=_('Enter the same password as above, for verification.'))

        def clean_password(self):
            # Override change form password cleaning which won't work
            return self.cleaned_data.get('password')

        def clean_password2(self):
            password1 = self.cleaned_data.get('password')
            password2 = self.cleaned_data.get('password2')
            if password1 and password2 and password1 != password2:
                raise ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
            return password2

        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
            return user

    return AuthXUserCreationForm


class AuthXUserAdmin(UserAdmin):
    """
    A modified ``UserAdmin`` that creates users in one step,
    showing all user fields in the initial form.

    Use this class as the base class in place of ``UserAdmin``.
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_email_verified', 'is_staff', 'is_superuser', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = admin.ModelAdmin.get_fieldsets(self, request, obj)
        if obj is None:
            fieldsets = copy.deepcopy(fieldsets)
            password_fieldset = next((f for f in fieldsets if 'password' in f[1]['fields']), None)
            if password_fieldset is not None:
                idx = password_fieldset[1]['fields'].index('password')
                password_fieldset[1]['fields'] = list(password_fieldset[1]['fields'])
                password_fieldset[1]['fields'].insert(idx + 1, 'password2')
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': build_user_creation_form(self.form),
            })
        defaults.update(kwargs)
        return admin.ModelAdmin.get_form(self, request, obj, **defaults)

    def response_add(self, request, obj, post_url_continue=None):
        # Override default add behaviour of showing form again
        return admin.ModelAdmin.response_add(self, request, obj, post_url_continue)
