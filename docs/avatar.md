# Avatar

## Mixin

`user_management.models.mixins.AvatarMixin` adds an avatar field. The
serializers for this field require `django-imagekit` to be installed.

## Installation

To install `django-user-management` with avatar functionality:

    pip install django-user-management[avatar]

Add the urls to your `ROOT_URLCONF`:

    urlpatterns = [
        ...
        url(r'', include('user_management.api.avatar.urls.avatar')),
        ...
    ]

## View

`user_management.api.avatar.views.ProfileAvatar` provides an endpoint to retrieve
and update the logged-in user's avatar.

`user_management.api.avatar.views.UserAvatar` provides an endpoint to retrieve
and update another user's avatar. Only an admin user can update other users' data.

Both avatar views provides an endpoint to retrieve a thumbnail of the
authenticated user's avatar.

Thumbnail options can be specified as GET arguments. Options are:
    width: Specify the width (in pixels) to resize/crop to.
    height: Specify the height (in pixels) to resize/crop to.
    crop: Whether to crop or not (allowed values: 0 or 1)
    anchor: Where to anchor the crop, top/bottom/left/right (allowed values: t, b, l, r)
    upscale: Whether to upscale or not (allowed values: 0 or 1)

If no options are specified, the user's avatar is returned.

For example, to return an avatar cropped to 100x100 anchored to the top right:
    avatar?width=100&height=100&crop=1&anchor=tr
