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


class ScopedRateThrottleBase(
        DefaultRateMixin, PostRequestThrottleMixin, ScopedRateThrottle):
    """Base class to define a scoped rate throttle on POST request."""


class LoginRateThrottle(ScopedRateThrottleBase):
    default_rate = '10/hour'


class UsernameLoginRateThrottle(LoginRateThrottle):
    def get_cache_key(self, request, view):
        if request.user.is_authenticated():
            return None  # Only throttle unauthenticated requests

        ident = request.POST.get('username')
        if ident is None:
            return None  # Only throttle username requests

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident.strip().lower(),
        }


class PasswordResetRateThrottle(ScopedRateThrottleBase):
    """Set `default_rate` for scoped rate POST requests on password reset."""
    default_rate = '3/hour'


class ResendConfirmationEmailRateThrottle(ScopedRateThrottleBase):
    """Set `default_rate` for scoped rate POST requests on `ResendConfirmationEmail`."""
    default_rate = '3/hour'
