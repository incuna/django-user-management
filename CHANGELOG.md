Changelog for django-user-management

This project uses Semantic Versioning (2.0).

## 18.0.0

* BREAKING: Add a app_name to each of the urls entry points. See the docs/views.md for updated default url namespaces.
* Fix Pillow security issue
* Drop support for Python < 3.6
* Add support for Python 3.6, 3.7 and 3.8
* Drop support for Django < 1.11
* Add Django 2.2 and 3.0 to travis
* Update djangorestframework>=3.9.1 for XSS fix https://github.com/encode/django-rest-framework/commit/75a489150ae24c2f3c794104a8e98fa43e2c9ce9
* Update incuna_mail>=4.1.0 for Django 3 support

## 17.0.0

* Backwards incompatible: Use `CIEmailField` from Django 1.11 for a case-insensitive email field.

## 16.1.1

* Fix bug using VERIFIED_QUERYSTRING with a LOGIN_URL.

## 16.1.0

* Allow VerifyUserEmailView get_redirect_url function to accept an extra string.
* Allow user login after email verification providing a setting is true in an apps settings file.
  This works in Django 1.10.

## 16.0.1

* Fix email verification when `LOGIN_URL` is a url name.

## 16.0.0

* Update `VerifyUserEmailView` to redirect to login without providing a next.
* Redirect to the login when attempting to verify an email address that is already verified.

## 15.0.0

* Updated for compatibility with Python 3.5 and Django 1.10

## v14.5.0

* Allow changing the subject of email verification and password reset emails with
  Django settings (`DUM_PASSWORD_RESET_SUBJECT` and `DUM_VALIDATE_EMAIL_SUBJECT`).

## v14.4.0

* Make `VerifyUserEmailView` redirect to the login page if `LOGIN_URL` is set (and `/`
  otherwise).

## v14.3.0

* Add `headers` to `utils.email_handler` enabling custom email headers to be sent.

## v14.2.1

* Fix the URL for `VerifyUserEmailView`.

## v14.2.0

* Refactor the UI `VerifyUserEmailView` to function in the same way as the existing API
  `VerifyAccountView`.

## v14.1.0

* Add `VerifyUserEmailView` to handle links from registration verification emails. 

## v14.0.0

* Clarify error message when your old and new passwords match, you will need to update translations.
* Add translation for email in `RegistrationSerializer` and `UserSerializerCreate`.

## v13.1.1

* Swap `request.DATA` (deprecated in DRF v3.0, removed in DRF v3.2) for `request.data`.

## v13.1.0

* Make token to verify account to expires if `VERIFY_ACCOUNT_EXPIRY` is set to
a value in seconds.

### Notes

* If `VERIFY_ACCOUNT_EXPIRY` is not set the token will never expire.

## v13.0.0

* Make `RegistrationSerializer` and `EmailSerializerBase` fields a tuple.

### Notes

`RegistrationSerializer` or `EmailSerializerBase` subclasses adding new fields
with a `list` will generate a `TypeError`:

```
class CustomRegistration(RegistrationSerializer):
    class Meta(RegistrationSerializer.Meta):
        fields = RegistrationSerializer.Meta.fields + ['custom_field']

TypeError: can only concatenate tuple (not "list") to tuple`
```

To fix the previous error we use a tuple instead:

```
class CustomRegistration(RegistrationSerializer):
    class Meta(RegistrationSerializer.Meta):
        fields = RegistrationSerializer.Meta.fields + ('custom_field',)
```

## v12.0.1

* Ensure new and old passwords differ when changing password.

## v12.0.0

* Update factories to use `class Meta:` syntax instead of `FACTORY_FOR`.

## v11.1.0

* Add correct HTML to HTML email templates.
* Add `django v1.8` support.

## v11.0.0

* Add `django-rest-framework v3` support.
* Drop `django-rest-framework v2` support.

## v10.1.0

* Allow authenticated user to receive a new confirmation email.

### Notes

* Previously only anonymous could request a new confirmation email.

## v10.0.0

* Replace `default_token_generator` with `django.core.signing`.

### Notes

* Previously not validated emails would be invalid.

## v9.0.1

* Send `user_logged_in` and `user_logged_out` signals from `GetAuthToken` view.

## v9.0.0

* Replace `email_verification_required` flag with `email_verified` flag.
 * Note that `email_verified == not email_verification_required`.
 * A data migration will be necessary.

## v8.2.0

**This release backports a specific change from v14.0.0**

* Clarify error message when your old and new passwords match, you will need to update translations.

## v8.1.2

**This release backports a specific change from v12.0.1**

* Ensure new and old passwords differ when changing password.


## v8.1.1 (Partial backport of fefdf6a from v11)

* Bugfix: Don't show "passwords do not match" when the first password is invalid.

## v8.1.0

* Add docstrings for views.

Docstrings will be displayed in `django-rest-framework` browsable API.

## v8.0.1

* Fix translation for notifications.

## v8.0.0

* Use `incuna-pigeon` for notifications.

## v7.0.1

* Fix `UserChangeForm` admin form `fields` to only include fields used in `UserAdmin.fieldsets`.

## v7.0.0

* Add `delete` to `ProfileDetail` view

### Notes

* When an object is referencing the user model with a foreign key it is possible
to define the behavior with `on_delete`.

see https://docs.djangoproject.com/en/1.7/ref/models/fields/#django.db.models.ForeignKey.on_delete

## v6.0.0

* Raise an error when user is not active at login

## v5.0.0

* Return 400 instead of 401 when `uidb64` or `token` is expired or not valid.

## v4.2.0

* Return `AuthenticationFailed` `401` instead of `404` `NotFound` for not valid
`uidb64` and `token`

## v4.1.0

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
