from django.contrib.auth import get_user_model
from rest_framework import generics, parsers, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_204_NO_CONTENT

from user_management.api import authentication, permissions
from . import serializers


User = get_user_model()


class AvatarAPIViewBase(generics.RetrieveUpdateAPIView):
    """
    Base class for avatar views. Probably shouldn't be used directly.

    Instead, subclass, and at least define the `permission_classes`.

    Can retrieve, update & delete the authenticated user's avatar. Pass GET
    parameters to retrieve a thumbnail of the avatar.

    Thumbnail options are specified as get parameters. Options are:
        width: Specify the width (in pixels) to resize / crop to.
        height: Specify the height (in pixels) to resize / crop to.
        crop: Whether to crop or not [1,0]
        anchor: Where to anchor the crop [t,r,b,l]
        upscale: Whether to upscale or not [1,0]

    To crop avatar to 100x100 anchored to the top right:
        avatar?width=100&height=100&crop=1&anchor=tr

    If no options are specified the users avatar is returned.
    """
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES + [
        authentication.FormTokenAuthentication,
    ]
    queryset = User.objects.all()
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializers.AvatarSerializer

    def post(self, *args, **kwargs):
        """
        Browsers like to do POST with multipart forms.

        As this is a fallback, we need to allow for that.
        """
        return self.put(*args, **kwargs)


class ProfileAvatar(AvatarAPIViewBase):
    """
    Retrieve and update the authenticated user's avatar.

    We don't inherit from `rest_framework.mixins.DestroyModelMixin` because we
    need a custom DELETE with no common functionality.
    """
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Delete the user's avatar.

        We set `user.avatar = None` instead of calling `user.avatar.delete()`
        to avoid test errors with `django.inmemorystorage`.
        """
        user = self.get_object()
        user.avatar = None
        user.save()
        return response.Response(status=HTTP_204_NO_CONTENT)


class UserAvatar(AvatarAPIViewBase):
    """
    Retrieve and update the user's avatar based upon `pk` in the url.

    Allow all users access to "safe" HTTP methods, but limit access to "unsafe"
    methods to users with the `is_staff` flag set.
    """
    permission_classes = (IsAuthenticated, permissions.IsAdminOrReadOnly)
