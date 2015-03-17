# django-user-management
[![Build Status](https://travis-ci.org/incuna/django-user-management.png?branch=merge-version)](https://travis-ci.org/incuna/django-user-management) [![Coverage Status](https://coveralls.io/repos/incuna/django-user-management/badge.png?branch=master)](https://coveralls.io/r/incuna/django-user-management?branch=master) [![Requirements Status](https://requires.io/github/incuna/django-user-management/requirements.svg?branch=master)](https://requires.io/github/incuna/django-user-management/requirements/?branch=master)

User management model mixins and API views/serializers based on [`Django`](https://github.com/django/django)
and [`djangorestframework`](https://github.com/tomchristie/django-rest-framework).

All documentation is in the [docs](docs/) directory.

- [Installation](docs/installation.md)
- [Mixins](docs/mixins.md)
- [Views](docs/views.md)
- [Avatar](docs/avatar.md)

`user_management` model mixins give flexibility to create your own `User` model.
By default all mixins are optional. Our mixins allow to create, identify users
(from their emails instead of their username) as well as sending password reset
and account validation emails.

`user_management` API views and serializers can be grouped into four sections:
* `auth`: authenticate and destroy a user session
* `password_reset`: send and confirm a request to reset a password
* `profile`: retrieve/update/delete the current user profile
* `register`: create an account and send an email to validate it
* `users` give a list and a detail (retrieve, update, destroy) views about users
