#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def version():
    import gocd
    return gocd.__version__

extra_dependencies = []
if sys.version_info < (2, 7):
    extra_dependencies = [
        'mock==1.0.1',
        'contextlib2',
        'backport_collections',
    ]

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='gocd',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',
    license='MIT License',
    url='https://github.com/gaqzi/py-gocd/',
    description='A Python API for interacting with Go Continuous Delivery',
    long_description=README,
    version=version(),
    packages=find_packages(exclude=('tests',)),
    cmdclass={'test': PyTest},
    tests_require=[
        'pytest',
        'vcrpy',
    ] + extra_dependencies,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
