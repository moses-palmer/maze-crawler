#!/usr/bin/env python
# coding: utf8

import os
import subprocess
import sys


PROJECT_NAME = 'mazecrawler'
DESCRIPTION = 'A maze serving server.'
AUTHOR_EMAIL = 'moses.palmer@gmail.com'
URL = 'https://github.com/moses-palmer/maze-crawler'

INSTALL_REQUIRES = [
    'Beaker >=1.6.4',
    'bottle >=0.11',
    'pymaze >=1.2.1']
SETUP_REQUIRES = INSTALL_REQUIRES + [
    'sphinxcontrib-httpdomain >=1.2.1']


LIB_DIR = os.path.join(
    os.path.dirname(__file__),
    'lib')
sys.path.append(LIB_DIR)


import setuptools

from setuptools.command.test import test


class test_runner(test):
    user_options = [
        ('test-suites=', 'S', 'Test suites to run, separated by comma (,)')]

    def initialize_options(self):
        self.test_suites = None

    def finalize_options(self):
        if not self.test_suites is None:
            self.test_suites = self.test_suites.split(',')

    def run(self):
        import importlib
        import tests

        self.run_command('dependencies')

        failures = tests.run(self.test_suites)
        if failures is None:
            print('Test suite was cancelled by setup')
            sys.exit(-1)

        print('')
        print('All test suites completed with %d failed tests' % len(failures))
        if failures:
            sys.stderr.write('Failed tests:\n%s\n' % '\n'.join(
                '\t%s - %s' % (test.name, test.message)
                    for test in failures))
        sys.exit(len(failures))

class dependencies(setuptools.Command):
    user_options = []

    package_command = ['npm', 'install']

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


    def node(self):
        """Makes sure that node.js is installed"""
        sys.stdout.write('Checking node.js installation...\n')

        # Since node.js picked an already used binary name, we must check
        # whether "node" is node.js or node - Amateur Packet Radio Node program;
        # The former actually provides output for the --version command
        try:
            node_output = subprocess.check_output(['node', '--version'])
            if node_output.strip():
                sys.stdout.write(node_output)
                return
        except OSError:
            pass

        # On Debian, node is called nodejs because of the above mentioned clash
        try:
            subprocess.check_call(['nodejs', '--version'])
            return
        except OSError:
            pass

        sys.stderr.write('node.js is not installed; terminating\n')
        sys.exit(1)

    def npm(self):
        """Makes sure that npm is installed"""
        sys.stdout.write('Checking npm installation...\n')

        try:
            subprocess.call(['npm', '--version'])
        except OSError:
            sys.stderr.write('npm is not installed; terminating\n')
            sys.exit(1)

    def packages(self):
        """Makes sure that dependencies are installed locally"""
        sys.stdout.write('Checking dependencies...\n')

        # Try to install it
        try:
            subprocess.check_call(self.package_command)
            return
        except (OSError, subprocess.CalledProcessError):
            sys.stderr.write('Failed to install dependencies; terminating\n')
            sys.exit(1)

    def run(self):
        self.node()
        self.npm()
        self.packages()

class dependencies_install(dependencies):
    package_command = ['npm', 'install', '-g']

COMMANDS = {
    'dependencies': dependencies,
    'dependencies_install': dependencies_install,
    'test': test_runner}


# Read globals from <package>._info without loading it
INFO = {}
for package in os.listdir(LIB_DIR):
    path = os.path.join(LIB_DIR, package)
    if not os.path.isdir(path):
        continue

    try:
        with open(os.path.join(
                path,
                '_info.py')) as f:
            for line in f:
                try:
                    name, value = (i.strip() for i in line.split('='))
                    if name.startswith('__') and name.endswith('__'):
                        INFO[name[2:-2]] = eval(value)
                except ValueError:
                    pass
    except:
        pass


try:
    # Read README
    with open(os.path.join(
            os.path.dirname(__file__),
            'README.rst')) as f:
        README = f.read()


    # Read CHANGES
    with open(os.path.join(
            os.path.dirname(__file__),
            'CHANGES.rst')) as f:
        CHANGES = f.read()
except IOError:
    README = ''
    CHANGES = ''


if __name__ == '__main__':
    try:
        setuptools.setup(
            cmdclass = COMMANDS,
            name = PROJECT_NAME,
            version = '.'.join(str(i) for i in INFO['version']),
            description = DESCRIPTION,
            long_description = README + '\n\n' + CHANGES,

            install_requires = INSTALL_REQUIRES,
            setup_requires = SETUP_REQUIRES,

            author = INFO['author'],
            author_email = AUTHOR_EMAIL,

            url = URL,

            packages = setuptools.find_packages(LIB_DIR,
                exclude = [
                    'tests',
                    'tests.suites']),
            package_dir = {'': LIB_DIR},
            zip_safe = False,

            license = 'GPLv3',
            classifiers = [])
    except Exception as e:
        try:
            sys.stderr.write('%s\n' % e.args[0] % e.args[1:])
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
