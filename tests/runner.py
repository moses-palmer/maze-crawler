#!/usr/bin/env python

import os
import sys

# Add the environment variables used by mazeweb
os.environ['MAZEWEB_CONFIG_DIR'] = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'resources'))
os.environ['MAZEWEB_DATA_DIR'] = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'resources'))
os.environ['MAZEWEB_CACHE_DIR'] = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'cache'))
os.environ['MAZEWEB_PLUGIN_PATH'] = os.pathsep.join((
    os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'resources', 'plugins')),
    os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'resources', 'plugins-extra'))))

# Make sure import tests works
sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir))
import tests.suites


def main(suite_names):
    import importlib

    suite_names = suite_names or tests.suites.__all__

    for suite_name in suite_names:
        try:
            importlib.import_module('.' + suite_name, 'tests.suites')
        except ImportError as e:
            print('Failed to import test suite %s: %s' % (suite_name, str(e)))

    failures = tests.run()
    if failures is None:
        print('Test suite was cancelled by setup')
        sys.exit(-1)

    print('')
    print('All test suites completed with %d failed tests' % len(failures))
    if failures:
        print('Failed tests:\n%s' % '\n'.join(
            '\t%s - %s' % (test.name, test.message)
                for test in failures))

    return len(failures)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
