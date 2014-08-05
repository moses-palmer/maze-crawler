# coding: utf-8
"""
mazeweb
Copyright (C) 2012-2014 Moses Palmér

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
import os

from .. import Plugin
from bottle import HTTPResponse, static_file
from mazeweb.crawler.plugin import MazePlugin


@MazePlugin.router
class StaticPlugin(Plugin):
    """Serves static files.

    The files are served from the directory ``$MAZEWEB_DATA_DIR``, or if that
    environment variable is not set, the current directory.
    """
    __plugin_name__ = 'static'

    _PATHS = None

    @classmethod
    def initialize(self):
        super(StaticPlugin, self).initialize()
        self._PATHS = []
        for path in self.CONFIGURATION('paths', []):
            self.add_path(path)

    @classmethod
    def add_path(self, path):
        """Adds a path to the lookup paths for static files.

        :param str path: The path to add. If this is not an absolute path, it is
            resolved against ``$MAZEWEB_DATA_DIR``. If the path is already
            registered, no action is taken.
        """
        if not os.path.isabs(path):
            path = os.path.join(os.getenv('MAZEWEB_DATA_DIR', '.'), path)

        if not path in self._PATHS:
            self._PATHS.insert(0, path)

    @MazePlugin.get('/static/<path:path>')
    @classmethod
    def get_file(self, path):
        """Retrieves a static resource.

        The response is a file.

        :param path: The path to the static file to retrieve.
        """
        for root in self._PATHS:
            if os.path.isfile(os.path.join(root, path)):
                return static_file(path, root)

        return HTTPResponse(status = 404)
