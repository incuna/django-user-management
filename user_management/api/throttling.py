from rest_framework.throttling import ScopedRateThrottle


class DefaultRateMixin(object):
    def get_rate(self):
        try:
            return self.THROTTLE_RATES[self.scope]
        except KeyError:
            return self.default_rate


class LoginRateThrottle(DefaultRateMixin, ScopedRateThrottle):
    default_rate = '10/hour'


class PasswordResetRateThrottle(DefaultRateMixin, ScopedRateThrottle):
    default_rate = '3/hour'
