import os
from setuptools import setup, find_packages

setup(
    name='django-wallet',
    version='0.0.0',
    author='Caktus Consulting Group',
    author_email='solutions@caktusgroup.com',
    packages=find_packages(),
    install_requires = ['Django >= 1.1,==dev'],
    include_package_data = True,
    exclude_package_data={
        '': ['*.sql', '*.pyc'],
    },
    url='http://code.google.com/p/django-wallet/',
    license='LICENSE.txt',
    description=\
        'Pluggable bank account model supporting withdraws and deposits',
    long_description=open('README.txt').read(),
)
