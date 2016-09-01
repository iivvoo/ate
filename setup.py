#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "simpleeval==0.8.7"
]

test_requirements = [
    "pytest"
]

setup(
    name='ate',
    version='0.1.0',
    description="Programmer friendly and user friendly python templating",
    long_description=readme + '\n\n' + history,
    author="Ivo van der Wijk",
    author_email='ivo+ate@in.m3r.nl',
    url='https://github.com/iivvoo/ate',
    packages=[
        'ate',
    ],
    package_dir={'ate':
                 'ate'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='ate',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    setup_requires=['pytest-runner'],
    tests_require=test_requirements
)
