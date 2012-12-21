import json
import os

from ..util.data import ConfigurationStore

PLUGIN_DIR = os.getenv('MAZEWEB_PLUGIN_DIR', os.path.dirname(__file__))
__path__ = [PLUGIN_DIR, os.path.dirname(__file__)]

# The available plugin classes
PLUGINS = {}


class Plugin(object):
    """
    A class describing the interface to plugin modules.
    """
    def __init__(self):
        self.data_dir = os.path.join(os.getenv('MAZEWEB_DATA_DIR', '.'),
            self.name)

    @property
    def name(self):
        """The name of this plugin"""
        return self.__plugin_name__

    @property
    def configuration(self):
        """The plugin configuration"""
        return self.CONFIGURATION

    @classmethod
    def load_configuration(self):
        """
        Loads the configuration for this plugin and caches it in the class.

        The configuration is read from the file
        $MAZEWEB_CONFIG_DIR/<self.__plugin_name__>.json. If this file does not
        exist, ValueError is raised.

        If the environment variable $MAZEWEB_CONFIG_DIR is not set, the
        configuration will be loaded from the current directory.

        The value cached is a ConfigurationStore.

        @raise ValueError if the configuration cannot be read
        """
        # Load the JSON data and stop if it fails
        filename = os.path.join(os.getenv('MAZEWEB_CONFIG_DIR', ''),
            'plugins', self.__plugin_name__ + '.json')
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except IOError:
            raise ValueError('Plugin %s does not have a configuration at %s' % (
                self.__name__, filename))

        # Wrap the configuration to make access easy
        self.CONFIGURATION = ConfigurationStore(data)


def load():
    """
    Loads all configured plugin classes from $MAZEWEB_PLUGIN_DIR or this
    directory.

    Plugins are loaded from all packages located under the directory, and they
    are loaded as if they were subpackages of this package. All subclasses of
    Plugin that have a configuration in $MAZEWEB_CONFIG_DIR/plugins are loaded.

    Plugins loaded are put in PLUGINS, where the key is Plugin.__name__ and the
    value if the plugin class.
    """
    for name in os.listdir(PLUGIN_DIR):
        import importlib

        # Ignore non-packages
        pathname = os.path.join(PLUGIN_DIR, name)
        if not os.path.isdir(pathname) \
                or not os.path.isfile(os.path.join(pathname,
                    '__init__.py')):
            continue

        # Import the package and load all plugins
        m = importlib.import_module('.' + name, __package__)
        for name in dir(m):
            value = getattr(m, name)

            # Ignore non-Plugin subclasses
            try:
                if not issubclass(value, Plugin) or value is Plugin:
                    continue
            except TypeError:
                continue

            try:
                value.load_configuration()
                PLUGINS[value.__plugin_name__] = value
            except ValueError as e:
                pass


def unload():
    """
    Clears all cached plugin classes.
    """
    PLUGINS.clear()
