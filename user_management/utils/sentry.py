from django.views.debug import SafeExceptionReporterFilter
from raven.contrib.django.client import DjangoClient


class SensitiveDjangoClient(DjangoClient):
    """
    Hide sensitive request data from being logged by Sentry.

    Borrowed from http://stackoverflow.com/a/23966581/240995
    """
    def get_data_from_request(self, request):
        request.POST = SafeExceptionReporterFilter().get_post_parameters(request)
        result = super(SensitiveDjangoClient, self).get_data_from_request(request)

        # override the request.data with POST data
        # POST data contains no sensitive info in it
        result['request']['data'] = request.POST

        # remove the whole cookie as it contains DRF auth token and session id
        if 'cookies' in result['request']:
            del result['request']['cookies']
        if 'Cookie' in result['request']['headers']:
            del result['request']['headers']['Cookie']

        return result
