from django.contrib.auth import get_user_model
from rest_framework import generics, parsers
from rest_framework.permissions import IsAuthenticated

from . import serializers
from user_management.api import permissions


User = get_user_model()


class ProfileAvatar(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update the authenticated user's avatar. Pass get parameters to
    retrieve a thumbnail of the avatar.

    Thumbnail options are specified as get parameters. Options are:
        width: Specify the width (in pixels) to resize / crop to.
        height: Specify the height (in pixels) to resize / crop to.
        crop: Whether to crop or not [1,0]
        anchor: Where to anchor the crop [t,r,b,l]
        upscale: Whether to upscale or not [1,0]

    If no options are specified the users avatar is returned.

    To crop avatar to 100x100 anchored to the top right:
        avatar?width=100&height=100&crop=1&anchor=tr
    """
    model = User
    serializer_class = serializers.AvatarSerializer
    parser_classes = (parsers.MultiPartParser,)

    def get_object(self):
        return self.request.user


class UserAvatar(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update the user's avatar. Pass get parameters to
    retrieve a thumbnail of the avatar.

    Thumbnail options are specified as get parameters. Options are:
        width: Specify the width (in pixels) to resize / crop to.
        height: Specify the height (in pixels) to resize / crop to.
        crop: Whether to crop or not [1,0]
        anchor: Where to anchor the crop [t,r,b,l]
        upscale: Whether to upscale or not [1,0]

    If no options are specified the users avatar is returned.

    To crop avatar to 100x100 anchored to the top right:
        avatar?width=100&height=100&crop=1&anchor=tr
    """
    model = User
    permission_classes = (IsAuthenticated, permissions.IsAdminOrReadOnly)
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializers.AvatarSerializer
