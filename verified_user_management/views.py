from rest_framework.permissions import AllowAny
from rest_framework import response, status, views

from user_management.views import OneTimeUseAPIMixin


class VerifyAccountView(OneTimeUseAPIMixin, views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if self.user.verified_email:
            return response.Response(status=status.HTTP_403_FORBIDDEN)

        self.user.verified_email = True
        self.user.is_active = True
        self.user.save()
        return response.Response(status=status.HTTP_200_OK)
