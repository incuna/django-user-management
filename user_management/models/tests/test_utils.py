from unittest import TestCase

from ..utils import timezone_choices


class TestTimeZoneChoices(TestCase):
    timezones = [
        'Arctic/Longyearbyen',
        'Asia/Qyzylorda',
        'America/Argentina/Ushuaia',
        'America/Iqaluit',
        'GMT',
        'Indian/Christmas',
        'UTC',
    ]

    def setUp(self):
        self.choices = timezone_choices(self.timezones)

    def test_exclude_GMT_UTC(self):
        self.assertNotIn('GMT', self.choices)
        self.assertNotIn('UTC', self.choices)

    def test_choice_groups(self):
        expected_choices = (
            (
                'Arctic',
                (
                    ('Arctic/Longyearbyen', 'Longyearbyen'),
                ),
            ),
            (
                'Asia',
                (
                    ('Asia/Qyzylorda', 'Qyzylorda'),
                ),
            ),
            (
                'America',
                (
                    ('America/Argentina/Ushuaia', 'Argentina/Ushuaia'),
                    ('America/Iqaluit', 'Iqaluit'),
                ),
            ),
            (
                'Indian',
                (
                    ('Indian/Christmas', 'Christmas'),
                ),
            ),
        )

        self.assertEqual(self.choices, expected_choices)
