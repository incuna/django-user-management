from collections import defaultdict, OrderedDict


class DefaultOrderedDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory


def timezone_choices(timezones, exclude=('GMT', 'UTC')):
    choices = DefaultOrderedDict(list)

    for timezone in timezones:
        if timezone in exclude:
            continue

        continent, _sep, town = timezone.partition('/')
        choices[continent].append((timezone, town))

    return tuple((c, tuple(t)) for c, t in choices.items())
