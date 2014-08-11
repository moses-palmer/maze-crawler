# coding: utf-8
# mazeweb
# Copyright (C) 2012-2014 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import json
import os

#: The available plugin classes
PLUGINS = {}

from ..util.data import ConfigurationStore, wrap, unwrap

PLUGIN_PATH = os.getenv('MAZEWEB_PLUGIN_PATH', None)
__path__ = (PLUGIN_PATH.split(os.pathsep) if not PLUGIN_PATH is None else []) \
    + [os.path.dirname(__file__)]


class Plugin(object):
    """A class describing the interface to plugin modules.
    """

    #: The name of this plugin
    __plugin_name__ = None

    def pre_initialize(self, maze):
        """Called when the maze has been initialised and all plugins loaded, but
        before the maze is initialised.

        :param maze.BaseMaze maze: The newly created maze.
        """
        pass

    def post_initialize(self, maze):
        """Called when the maze has been initialised and all plugins loaded, and
        the maze has been initialised.

        :param maze.BaseMaze maze: The newly created maze.
        """
        pass

    def get_maze(self, maze, result):
        """Called when the wire representation of the maze is generated.

        This callback is called after the standard representation is generated.

        :param maze.BaseMaze maze: The maze for which the wire representation is
            being generated.

        :param dict result: The dict representing the maze.
        """
        pass

    def update_maze(self, maze, value, result):
        """Called when the maze is being updated by the client and the wire
        representation is generated.

        This callback is called after the standard representation is generated,
        and after get_maze has been called for the newly updated maze.

        :param maze.BaseMaze maze: The maze for which the wire representation is
            being generated.

        :param dict value: The JSON value sent by the client.

        :param dict result: The dict representing the maze.
        """
        pass

    def get_room(self, maze, room_pos, neighbor_details, result):
        """Called when the wire representation of a room is generated.

        This callback is called after the standard representation is generated.

        :param maze.BaseMaze maze: The maze for which the wire representation is
            being generated.

        :param room_pos:
            The position of the room.
        :type room_pos: (int, int)

        :param bool neighbor_details: Whether the client has requested neighbour
            details. This is merely an informational parameter; this callback
            will be called for the neighbouring rooms as well.

        :param dict result: The dict representing the room.
        """
        pass

    def __init__(self):
        self.data_dir = os.path.join(os.getenv('MAZEWEB_DATA_DIR', '.'),
            self.name)
        self.cache_dir = os.path.join(os.getenv('MAZEWEB_CACHE_DIR', '.'),
            self.name)
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)
        self._configuration = None

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
        """The plugin configuration as a
        :class:`~mazeweb.util.data.ConfigurationStore`"""
        if self._configuration is None:
            self._configuration = ConfigurationStore(unwrap(self.CONFIGURATION))
        return self._configuration

    @classmethod
    def load_configuration(self):
        """Loads the configuration for this plugin and caches it in the class.

        The configuration is read from the directories in
        ``$MAZEWEB_CONFIG_DIR`` as
        ``$MAZEWEB_CONFIG_DIR_PART/<self.__plugin_name__>.json``. The first file
        found is used. ``$MAZEWEB_CONFIG_DIR`` is split on :attr:`os.pathsep`.

        If the environment variable ``$MAZEWEB_CONFIG_DIR`` is not set, the
        current directory will be used as ``$config_dir``.

        The value cached is a :class:`~mazeweb.util.data.ConfigurationStore`.

        :raises ValueError: if the configuration cannot be read
        """
        # Iterate over all directories in $MAZEWEB_CONFIG_DIR
        configuration_dirs = os.getenv('MAZEWEB_CONFIG_DIR', '.').split(
            os.pathsep)

        has_configuration = False
        for configuration_dir in configuration_dirs:
            # Load the JSON data and continue if it fails
            filename = os.path.join(configuration_dir,
                'plugins', self.__plugin_name__ + '.json')
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                has_configuration = True
                break
            except IOError:
                pass

        if not has_configuration:
            raise ValueError('Plugin %s does not have a configuration at %s',
                self.__name__, filename)

        # Wrap the configuration to make access easy
        self.CONFIGURATION = ConfigurationStore(data)


def load():
    """Loads all configured plugin classes from all directories in
    ``$MAZEWEB_PLUGIN_PATH`` and this directory.

    Plugins are loaded from all packages located under the directory, and they
    are loaded as if they were subpackages of this package. All subclasses of
    Plugin that have a configuration in ``$MAZEWEB_CONFIG_DIR/plugins`` are
    loaded.

    Plugins loaded are put in ``PLUGINS``, where the key is ``Plugin.__name__``
    and the value the plugin class.
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
    """Clears all cached plugin classes.
    """
    PLUGINS.clear()
