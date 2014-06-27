from setuptools import setup, find_packages


version = '1.2.1'


install_requires = (
    'djangorestframework>=2.3.14,<3',
    'incuna_mail>=1.0.0,<2',
)

extras_require = {
    'avatar': [
        'django-imagekit>=3.2',
    ],
}

setup(
    name='django-user-management',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='',
    long_description='',
    author='Incuna',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-user-management/',
    install_requires=install_requires,
    extras_require=extras_require,
    zip_safe=False,
)
