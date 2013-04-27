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
        coffee_file_rel = path + '.coffee'

        for path in self.configuration.paths:
            # Construct the filename of the CoffeeScript file
            coffee_file = os.path.join(path, coffee_file_rel)

            # Make sure the coffee_file is absolute
            if not os.path.isabs(coffee_file):
                coffee_file = os.path.abspath(
                    os.path.join(
                        self.data_dir,
                        os.path.pardir,
                        coffee_file))

            if os.path.isfile(coffee_file):
                return static_file(
                    os.path.basename(coffee_file),
                    os.path.dirname(coffee_file))

        return HttpError(status = 404)
