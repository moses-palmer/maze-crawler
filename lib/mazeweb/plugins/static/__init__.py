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
from bottle import HTTPResponse, ResourceManager, static_file
from mazeweb.crawler.plugin import MazePlugin


@MazePlugin.router
class StaticPlugin(Plugin):
    """Serves static files.

    The files are served from the directory ``$MAZEWEB_DATA_DIR``, or if that
    environment variable is not set, the current directory.
    """
    __plugin_name__ = 'static'

    def __init__(self):
        super(StaticPlugin, self).__init__()
        self.res = ResourceManager(
            base = os.path.join(os.getenv('MAZEWEB_DATA_DIR', '.'), '.'))

        # Add all configured paths
        for path in self.configuration.paths:
            self.res.add_path(os.path.join(path, '.'))

    @MazePlugin.get('/static/<path:path>')
    def get_file(self, path):
        """Retrieves a static resource.

        The response is a file.

        :param path: The path to the static file to retrieve.
        """
        self.res.path = list(reversed(list(self.res.path)))
        abspath = self.res.lookup(path)
        self.res.path = list(reversed(list(self.res.path)))
        if not abspath is None:
            return static_file(path, abspath[:-len(path)])
        else:
            return HTTPResponse(status = 404)
