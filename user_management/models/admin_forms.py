from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user with no privileges from the given username and
    password.
    """
    error_messages = {
        'duplicate_email': _('A user with that email address already exists.'),
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput,
        help_text=_('Enter the same password as above for verification.'),
    )

    class Meta:
        fields = ('email',)
        model = User

    def clean_email(self):
        """
        Since User.email is unique, this check is redundant,
        but it sets a nicer error message than the ORM. See #13147.
        """
        email = self.cleaned_data['email']
        try:
            User._default_manager.get(email__iexact=email)
        except User.DoesNotExist:
            return email.lower()
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users.

    Includes all the fields on the user, but replaces the password field with
    admin's password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        fields = (
            'email',
            'groups',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'name',
            'password',
            'user_permissions',
        )
        model = User

    def clean_password(self):
        """
        Regardless of what the user provides, return the initial value.

        This is done here, rather than on the field, because the field does
        not have access to the initial value.
        """
        return self.initial['password']
