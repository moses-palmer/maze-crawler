import json
import os

# The available plugin classes
PLUGINS = {}

from ..util.data import ConfigurationStore

PLUGIN_PATH = os.getenv('MAZEWEB_PLUGIN_PATH', os.path.dirname(__file__))
__path__ = PLUGIN_PATH.split(os.pathsep) + [os.path.dirname(__file__)]


class Plugin(object):
    """
    A class describing the interface to plugin modules.
    """
    def pre_initialize(self, maze):
        """
        Called when the maze has been initialised and all plugins loaded, but
        before the maze is initialised.

        @param maze
            The newly created maze.
        """
        pass

    def post_initialize(self, maze):
        """
        Called when the maze has been initialised and all plugins loaded, and
        the maze has been initialised.

        @param maze
            The newly created maze.
        """
        pass

    def get_maze(self, maze, result):
        """
        Called when the wire representation of the maze is generated.

        This callback is called after the standard representation is generated.

        @param maze
            The maze for which the wire representation is being generated.
        @param result
            The dict representing the maze.
        """
        pass

    def update_maze(self, maze, value, result):
        """
        Called when the maze is being updated by the client and the wire
        representation is generated.

        This callback is called after the standard representation is generated,
        and after get_maze has been called for the newly updated maze.

        @param maze
            The maze for which the wire representation is being generated.
        @param value
            The value sent by the client.
        @param result
            The dict representing the maze.
        """
        pass

    def get_room(self, maze, room_pos, neighbor_details, result):
        """
        Called when the wire representation of a room is generated.

        This callback is called after the standard representation is generated.

        @param maze
            The maze for which the wire representation is being generated.
        @param room_pos
            The position of the room.
        @param neighbor_details
            Whether the client has requested neighbour details. This is merely
            an informational parameter; this callback will be called for the
            neighbouring rooms as well.
        @param result
            The dict representing the room.
        """
        pass

    def __init__(self):
        self.data_dir = os.path.join(os.getenv('MAZEWEB_DATA_DIR', '.'),
            self.name)
        self.cache_dir = os.path.join(os.getenv('MAZEWEB_CACHE_DIR', '.'),
            self.name)
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

    @property
    def name(self):
        """The name of this plugin"""
        return self.__plugin_name__

    @property
    def dependencies(self):
        """The names of the plugins on which this plugin depends"""
        return getattr(self, '__plugin_dependencies__', [])

    @property
    def conflicts(self):
        """The names of the plugins on which this plugin has conflicts"""
        return getattr(self, '__plugin_conflicts__', [])

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
    Loads all configured plugin classes from all directories in
    $MAZEWEB_PLUGIN_PATH or this directory.

    Plugins are loaded from all packages located under the directory, and they
    are loaded as if they were subpackages of this package. All subclasses of
    Plugin that have a configuration in $MAZEWEB_CONFIG_DIR/plugins are loaded.

    Plugins loaded are put in PLUGINS, where the key is Plugin.__name__ and the
    value if the plugin class.
    """
    for plugin_dir in __path__:
        for name in os.listdir(plugin_dir):
            import importlib

            # Ignore non-packages
            pathname = os.path.join(plugin_dir, name)
            if not os.path.isdir(pathname) \
                    or not os.path.isfile(os.path.join(pathname,
                        '__init__.py')):
                continue

            # Import the package and load all plugins
            m = importlib.import_module('.' + name, __package__)
            all_plugins = {}
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
                    if value.CONFIGURATION('plugin.enabled', True) is True:
                        if not hasattr(value, '__plugin_dependencies__'):
                            PLUGINS[value.__plugin_name__] = value
                        else:
                            all_plugins[value.__plugin_name__] = value
                except ValueError as e:
                    pass

            # Load all plugins with dependencies
            continue_loading = bool(all_plugins)
            while continue_loading:
                continue_loading = False
                for plugin in list(all_plugins.keys()):
                    if all(d in PLUGINS
                            for d in all_plugins[
                                plugin].__plugin_dependencies__):
                        PLUGINS[plugin] = all_plugins[plugin]
                        del all_plugins[plugin]
                        continue_loading = True

            # Unload plugins with conflicts
            continue_unloading = False
            for plugin in list(PLUGINS.keys()):
                conflicts = getattr(PLUGINS[plugin], '__plugin_conflicts__', [])
                if any(c in PLUGINS for c in conflicts):
                    del PLUGINS[plugin]
                    continue_unloading = True

            # Unload plugins depending on conflicted plugins
            while continue_unloading:
                continue_unloading = False
                for plugin in list(PLUGINS.keys()):
                    dependencies = getattr(PLUGINS[plugin],
                        '__plugin_dependencies__', [])
                    if not all(d in PLUGINS for d in dependencies):
                        del PLUGINS[plugin]
                        continue_unloading = True


def unload():
    """
    Clears all cached plugin classes.
    """
    PLUGINS.clear()
