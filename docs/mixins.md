# Custom user model mixins

##  ActiveUserMixin

`user_management.models.mixins.ActiveUserMixin` provides a base custom user
mixin with a `name`, `email`, `date_joined`, `is_staff`, and `is_active`.

##  VerifyEmailMixin

`user_management.models.mixins.VerifyEmailMixin` extends ActiveUserMixin to
provide functionality to verify the email. It includes an additional
`email_verified` field.

By default, users will be created with `is_active = False`. A verification email
will be sent including a link to verify the email and activate the account.

##  AvatarMixin

`user_management.models.mixins.AvatarMixin` adds an avatar field. The
serializers for this field require `django-imagekit` to be installed.
