import os

from .. import Plugin
from bottle import ResourceManager, static_file
from mazeweb.crawler.plugin import MazePlugin

@MazePlugin.router
class EspressoPlugin(Plugin):
    __plugin_name__ = 'espresso'


    @MazePlugin.get('/espresso/<path:path>.js')
    def get_js(self, path):
        """
        Retrieves a coffee script and, if necessary, compiles it.

        @param path
            The base path to the file to retrieve. The file extensions '.coffee'
            and '.js' are appended.
        @return a bottle static_file
        """
        raise NotImplementedError()

    @MazePlugin.get('/espresso/<path:path>.coffee')
    def get_coffee(self, path):
        """
        Retrieves a coffee script without compiling it.

        @param path
            The base path to the file to retrieve. The file extension '.coffee'
            is appended.
        @return a bottle static_file
        """
        raise NotImplementedError()
