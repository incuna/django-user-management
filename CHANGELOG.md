## v4.1.0 (Upcoming)

* Add `ResendConfirmationEmail` view.

## v4.0.1

* Remove calculation in translatable string

## v4.0.0

* Enforce complex passwords

## v3.5.3

* Get user by natural key in `ValidateEmailMixin`.

## v3.5.2

* Get user by natural key in `PasswordResetEmail`.

## v3.5.1

* Add timezone support: projects with `USE_TZ=True` will now work correctly

## v3.5.0

* Split `BasicUserFieldsMixin` and `VerifyEmailMixin` into mixins.

## v3.4.0

* Auth tokens offer expiration functionality.

## v3.3.0

* Add custom Sentry logging class to disallow sensitive data being logged by Sentry client.

## v3.2.0

* Add `UsernameLoginRateThrottle` to throttle users based on their username.
* `GetToken` throttle extended with `UsernameLoginRateThrottle`.

## v3.1.0

* Allow POST to avatar views.
* Allow authentication with `token` as a form field on avatar views.
* Replace `django-inmemorystorage==0.1.1` with `dj-inmemorystorage==1.2.0` in tests.

## v3.0.1

* `GetToken` throttles `POST` requests only.

## v3.0.0

**Backwards incompatible** due to required authentication when using `ProfileAvatar`

* `PasswordResetEmail` now only throttled on `POST` requests.
* Added `DELETE` method to `ProfileAvatar`.
* `ProfileAvatar` now requires authentication.

## v2.1.1

* Add missing plaintext account validation email
* Add missing `/` to html account validation email

## v2.1.0

* Update `create_user` to set last_login with a default.

 **Note: this change has been done for the upcoming version django > 1.7.0.**
 `User.last_login` default is removed from django > 1.7.0. For existing
 project using `django-user-management` project migrations would be run
 after `django.contrib.auth` migrations. The project migrations will cancel
 `last_login` `IS NULL`.

## v2.0.0

**Backwards incompatible** due to incuna-mail update

* Update VerifyEmailMixin.send_validation_email to send a multipart email by default
* Allow overriding the verification email's subject and django templates
* Update incuna-mail to v2.0.0

## v1.2.2

* Fix bug where VerifyUserAdmin.get_fieldsets is called twice

## v1.2.1

* Bump required version of `incuna-mail` in order to fix circular import.

## v1.2.0

* Protect auth login and password reset views against throttling.

## v1.1.4

* Add email field to PasswordResetEmail response to OPTIONS request

## v1.1.3

* Fix error in OneTimeUseAPIMixin that made it 500 with bad urls

## v1.1.2

* Add hooks to PasswordResetEmail view to allow easier subclassing

## v1.1.1

* Improve UserFactory to deal with passwords neatly.

## v1.1.0

* Add CaseInsensitiveEmailBackend authentication backend
* Consistently convert email addresses to lower-case

## v1.0.0

* Move sending of verification emails into UserRegister view from VerifyEmailMixin.
* Add delete method to GetToken view.
* Return HTTP_201_CREATED and ok message from VerifyAccountView.

## v0.2.0

* Move `avatar` code to self-contained app so it does not break
  when extra dependencies are not installed.

  **Note: this is backward incompatible release.**
  Avatar related code should now be imported from `api.avatar` namespace
  instead of previous `api` namespace. An example `ProfileAvatar` class view
  lives now at `user_management.api.avatar.views.ProfileAvatar`
  (not `user_management.api.views.ProfileAvatar`).

## v0.1.0

* Bump required version of incuna_mail to 0.2

## v0.0.9

* Add labels to password serializers' fields.

## v0.0.8

* Add user avatar model mixin, serializer and endpoint.
  **Requires djangorestframework>=2.3.13.**

## v0.0.7

* Ensure all urls accept a trailing slash.

## v0.0.6

* Separate user detail / list urls from (my) profile.
* Rename views to not end View.
* Make users views hyperlinked.
* Add `user_management_api` namesapce to api urls. Include with
  `include('user_management.api.urls', namespace='something', app_name='user_management_api')`


## v0.0.5

* Add admin forms and simple UserAdmin
* Add VerifyUserAdmin
* Order UserAdmin by name, not email
* Use python 2 compatible super

## v0.0.4

* Added users list
* Added urls and url tests

## v0.0.3

* Add wheel support

## v0.0.2

* Rename users template dir to user_management
* Rename UserSerializer to RegistrationSerializer
* Check new superusers are active by default
* Make User model abstract.
* Convert abstract models to mixins.
* Reorganise app into models and api modules.
* Separate verify_email_urls.
* Use self.normalize_email
* Better duplicate email test.
* Add .travis.yml
* Add Python 2.7 compatibility
