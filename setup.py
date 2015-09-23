from setuptools import find_packages, setup


version = '8.2.0'


install_requires = (
    'djangorestframework>=2.4.4,<3',
    'incuna_mail>=2.0.0,<4.0.0',
    'incuna-pigeon>=0.1.0,<1.0.0',
)

extras_require = {
    'avatar': [
        'django-imagekit>=3.2',
    ],
    'utils': [
        'raven>=5.1.1',
    ],
}

setup(
    name='django-user-management',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='User management model mixins and api views.',
    long_description='',
    keywords='django rest framework user management api',
    author='Incuna',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-user-management/',
    install_requires=install_requires,
    extras_require=extras_require,
    zip_safe=False,
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
