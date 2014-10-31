from rest_framework.throttling import ScopedRateThrottle


class DefaultRateMixin(object):
    def get_rate(self):
        try:
            return self.THROTTLE_RATES[self.scope]
        except KeyError:
            return self.default_rate


class PostRequestThrottleMixin(object):
    def allow_request(self, request, view):
        """
        Throttle POST requests only.
        """
        if request.method != 'POST':
            return True

        return super(PostRequestThrottleMixin, self).allow_request(request, view)


class LoginRateThrottle(
        DefaultRateMixin,
        PostRequestThrottleMixin,
        ScopedRateThrottle):
    default_rate = '10/hour'


class PasswordResetRateThrottle(
        DefaultRateMixin,
        PostRequestThrottleMixin,
        ScopedRateThrottle):
    default_rate = '3/hour'
