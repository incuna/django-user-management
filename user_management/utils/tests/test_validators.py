# -*- coding: utf-8 -*-
import string

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..validators import validate_password_strength


class PasswordsTest(TestCase):
    too_simple = (
        'Password must have at least ' +
        'one upper case letter, one lower case letter, and one number.'
    )

    too_fancy = (
        'Password only accepts the following symbols ' + string.punctuation
    )

    def test_no_upper(self):
        password = 'aaaa1111'
        with self.assertRaises(ValidationError) as error:
            validate_password_strength(password)
        self.assertEqual(error.exception.message, self.too_simple)

    def test_no_lower(self):
        password = 'AAAA1111'
        with self.assertRaises(ValidationError) as error:
            validate_password_strength(password)

        self.assertEqual(error.exception.message, self.too_simple)

    def test_no_number(self):
        password = 'AAAAaaaa'
        with self.assertRaises(ValidationError) as error:
            validate_password_strength(password)

        self.assertEqual(error.exception.message, self.too_simple)

    def test_symbols(self):
        """Ensure all acceptable symbols are acceptable."""
        for symbol in string.punctuation:
            password = 'AAaa111' + symbol
            self.assertIsNone(validate_password_strength(password))

    def test_non_ascii(self):
        password = u'AA11aa££'  # £ is not an ASCII character.
        with self.assertRaises(ValidationError) as error:
            validate_password_strength(password)

        self.assertEqual(error.exception.message, self.too_fancy)

    def test_ok(self):
        password = 'AAAaaa11'
        self.assertIsNone(validate_password_strength(password))
