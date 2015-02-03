from django.core.exceptions import ValidationError
from django.test import TestCase

from . factories import UserFactory
from .. import admin_forms


class UserCreationFormTest(TestCase):
    def test_fields(self):
        """Assert `fields`."""
        fields = admin_forms.UserCreationForm.base_fields.keys()
        expected = ('email', 'password1', 'password2')
        self.assertCountEqual(fields, expected)

    def test_required_fields(self):
        """Assert required `fields` are correct."""
        form = admin_forms.UserCreationForm({})
        expected = 'This field is required.'
        self.assertIn(expected, form.errors['email'])
        self.assertIn(expected, form.errors['password1'])
        self.assertIn(expected, form.errors['password2'])

    def test_clean_email(self):
        email = 'Test@example.com'

        form = admin_forms.UserCreationForm()
        form.cleaned_data = {'email': email}

        self.assertEqual(form.clean_email(), email.lower())

    def test_clean_duplicate_email(self):
        user = UserFactory.create()

        form = admin_forms.UserCreationForm()
        form.cleaned_data = {'email': user.email}

        with self.assertRaises(ValidationError):
            form.clean_email()

    def test_clean(self):
        data = {'password1': 'pass123', 'password2': 'pass123'}

        form = admin_forms.UserCreationForm()
        form.cleaned_data = data

        self.assertEqual(form.clean(), data)

    def test_clean_mismatched(self):
        data = {'password1': 'pass123', 'password2': 'pass321'}

        form = admin_forms.UserCreationForm()
        form.cleaned_data = data

        with self.assertRaises(ValidationError):
            form.clean()

    def test_save(self):
        data = {
            'email': 'test@example.com',
            'password1': 'pass123',
            'password2': 'pass123',
        }

        form = admin_forms.UserCreationForm(data)
        self.assertTrue(form.is_valid(), form.errors.items())

        user = form.save()
        self.assertEqual(user.email, data['email'])


class UserChangeFormTest(TestCase):
    def test_fields(self):
        """Assert `fields`."""
        fields = admin_forms.UserChangeForm.base_fields.keys()
        expected = (
            'avatar',
            'email',
            'email_verification_required',
            'groups',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'name',
            'password',
            'user_permissions',
        )
        self.assertCountEqual(fields, expected)

    def test_clean_password(self):
        password = 'pass123'
        data = {'password': password}
        user = UserFactory.build()

        form = admin_forms.UserChangeForm(data, instance=user)

        self.assertNotEqual(form.clean_password(), password)
