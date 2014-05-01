from django.core.exceptions import ValidationError
from django.test import TestCase

from .. import admin_forms
from . factories import UserFactory


class UserCreationFormTest(TestCase):
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
    def test_clean_password(self):
        password = 'pass123'
        data = {'password': password}
        user = UserFactory.build()

        form = admin_forms.UserChangeForm(data, instance=user)

        self.assertNotEqual(form.clean_password(), password)
