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
