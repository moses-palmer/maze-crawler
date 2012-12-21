#!/usr/bin/env python

import os
import sys

# Add the environment variables used by mazeweb
os.environ['MAZEWEB_CONFIG_DIR'] = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'resources'))
os.environ['MAZEWEB_DATA_DIR'] = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'resources'))
os.environ['MAZEWEB_PLUGIN_DIR'] = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'resources', 'plugins'))

# Make sure import tests works
sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir))
import tests
from tests.suites import *

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
sys.exit(len(failures))
