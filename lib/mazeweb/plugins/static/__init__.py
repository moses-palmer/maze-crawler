import os

from .. import Plugin
from bottle import HTTPResponse, ResourceManager, static_file
from mazeweb.crawler.plugin import MazePlugin

@MazePlugin.router
class StaticPlugin(Plugin):
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
        """
        Retrieves a static resource.

        @param path
            The path to the static file to retrieve.
        """
        abspath = self.res.lookup(path)
        if not abspath is None:
            return static_file(path, abspath[:-len(path)])
        else:
            return HTTPResponse(status = 404)
