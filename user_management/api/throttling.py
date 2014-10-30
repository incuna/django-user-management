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

    def allow_request(self, request, view):
        if request.META['REQUEST_METHOD'] != 'POST':
            return True
        return super(PasswordResetRateThrottle, self).allow_request(
            request,
            view,
        )
