# Welcome to django-user-management documentation

Documentation generated with [mkdocs.org](http://mkdocs.org).


`django-user-management` contains user management model mixins and API views. The mixins
provide common user-related functionality such as custom avatars and email verification
during the registration process. The API views provide endpoints to support this
functionality.

## API endpoints

Auth:

- url: `/auth`

Password reset:

- url: `/auth/password_reset/confirm/<uid>/<token>`
- url: `/auth/password_reset`

Profile:

- url: `/profile`
- url: `/profile/password`

Register:

- url: `/register`
- url: `/resend-confirmation-email`

Users:

- url: `/users`
- url: `/users/<pk>`

Verify email:

- url: `/verify_email/<uid>/<token>`
