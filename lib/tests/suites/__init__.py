import errno
import os
import re

# Add the environment variables used by mazeweb
RESOURCE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, 'resources'))
CACHE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, 'cache'))
os.environ['MAZEWEB_CONFIG_DIR'] = RESOURCE_DIR
os.environ['MAZEWEB_DATA_DIR'] = RESOURCE_DIR
os.environ['MAZEWEB_CACHE_DIR'] = CACHE_DIR
os.environ['MAZEWEB_PLUGIN_PATH'] = os.pathsep.join((
    os.path.join(RESOURCE_DIR, 'plugins'),
    os.path.join(RESOURCE_DIR, 'plugins-extra')))


# Create the regular expression to find test modules
extension = '.py'
pattern = re.compile(
    r'[^_].*?'
    + re.escape(extension) + '$')

# Define __all__ to make "from tests.suites import *" work
__all__ = [f[:-len(extension)]
    for f in os.listdir(__path__[0])
    if pattern.match(f)]
