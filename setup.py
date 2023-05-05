#!/usr/bin/env python3

import os
import glob
import shutil
from setuptools import setup, Command
import distutils.cmd
import distutils.log
import setuptools
import subprocess

# get key package details from py_pkg/__version__.py
about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'emerge', '__version__.py')) as f:
    exec(f.read(), about)

# load the README file and use it as the long_description for PyPI
with open('README.md', 'r') as f:
    readme = f.read()


class PyTestCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'Run pytest tests'
    user_options = [

    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        command = [
            'pytest --full-trace --verbose --color=yes --disable-pytest-warnings --no-summary --pyargs emerge.tests']

        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.Popen(command, shell=True)


class PylintCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run Pylint on Python source files'
    user_options = [
        # The format is (long option, short option, description).
        ('pylint-rcfile=', None, 'path to Pylint config file'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.pylint_rcfile = ''

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), (
                'Pylint config file %s does not exist.' % self.pylint_rcfile)

    def run(self):
        """Run command."""
        command = ['pylint blazer']
        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.Popen(command, shell=True)


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './docs/build ./*.out ./*.log ./work/* ./build ./dist ./__pycache__ ./emerge/cli/__pycache__ ./*/__pycache__ ./*.pyc ./ssh*py ./*.tgz ./.pytest_cache ./*.egg-info'.split(
        ' ')

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        global here

        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(
                os.path.join(here, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(here):
                    # Die if path in CLEAN_FILES is absolute + outside this directory
                    raise ValueError(
                        "%s is not a path inside %s" % (path, here))
                print('removing %s' % os.path.relpath(path))
                try:
                    shutil.rmtree(path)
                except:
                    os.remove(path)


# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name=about['__title__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['emerge', 'emerge.zmq', 'emerge.data', 'emerge.core', 'emerge.node', 'emerge.fs', 'emerge.file',
              'emerge.compute', 'emerge.cli', 'emerge.tests'],
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        'pytest',
        'click',
        'black',
        'isort',
        'flake8',
        'zerorpc'
    ],
    license=about['__license__'],
    zip_safe=False,
    cmdclass={
        'clean': CleanCommand,
        'pylint': PylintCommand,
        'test': PyTestCommand
    },

    entry_points={
        'console_scripts': ['emerge=emerge.cli:cli']
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='cli, tools, utility'
)
