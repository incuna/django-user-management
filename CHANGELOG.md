## v0.2.0

* Move `avatar` related code to self-contained app so it does not break
  when extra dependencies are not installed.
  **Note: this is backward incompatible release.**

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
