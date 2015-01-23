from string import (
    ascii_letters,
    ascii_lowercase,
    ascii_uppercase,
    digits,
    punctuation
)

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


too_simple = _(
    'Password must have at least ' +
    'one upper case letter, one lower case letter, and one number.'
)

too_fancy = _(
    'Password only accepts the following symbols !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
)


def validate_password_strength(value):
    """
    Passwords should be tough.

    That means they should use:
    - mixed case letters,
    - numbers,
    - (optionally) ascii symbols and spaces.

    The (contrversial?) decision to limit the passwords to ASCII only
    is for the sake of:
    - simplicity (no need to normalise UTF-8 input)
    - security (some character sets are visible as typed into password fields)

    TODO: In future, it may be worth considering:
    - rejecting common passwords. (Where can we get a list?)
    - rejecting passwords with too many repeated characters.

    It should be noted that no restriction has been placed on the length of the
    password here, as that can easily be achieved with use of the min_length
    attribute of a form/serializer field.
    """
    used_chars = set(value)
    good_chars = set(ascii_letters + digits + punctuation + ' ')
    required_sets = (ascii_uppercase, ascii_lowercase, digits)

    if not used_chars.issubset(good_chars):
        raise ValidationError(too_fancy)

    for required in required_sets:
        if not used_chars.intersection(required):
            raise ValidationError(too_simple)
