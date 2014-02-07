from setuptools import setup, find_packages


version = '0.0.1'


install_requires = (
    'djangorestframework>=2.3.12,<3',
    'incuna_mail>=0.1.1',
)

setup(
    name='django-user-management-api',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='',
    long_description='',
    author='incuna',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-user-management-api/',
    install_requires=install_requires,
    zip_safe=False,
)
