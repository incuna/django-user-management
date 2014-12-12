# Avatar

## Mixin

`user_management.models.mixins.AvatarMixin` adds an avatar field. The 
serializers require `django-imagekit`.

## Installation

Install with avatar functionality

    pip install django-user-management[avatar]

Add the urls to your `ROOT_URLCONF`

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.avatar.urls.avatar')),
        ...
    )

## View

`user_management.api.avatar.views.ProfileAvatar` provides an endpoint to retrieve 
and update the logged in user's avatar.

`user_management.api.avatar.views.UserAvatar` provides an endpoint to retrieve 
and update other user's avatar. Only admin user can update other user's data.

Both avatar views provides an endpoint to retrieve a thumbnail of the
authenticated user's avatar.

    Thumbnail options can be specified as get parameters. Options are:
        width: Specify the width (in pixels) to resize / crop to.
        height: Specify the height (in pixels) to resize / crop to.
        crop: Whether to crop or not [1,0]
        anchor: Where to anchor the crop [t,r,b,l]
        upscale: Whether to upscale or not [1,0]

    If no options are specified the users avatar is returned.

    To crop avatar to 100x100 anchored to the top right:
        avatar?width=100&height=100&crop=1&anchor=tr
