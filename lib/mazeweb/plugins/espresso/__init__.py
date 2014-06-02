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

import os
import subprocess

from .. import Plugin
from bottle import HTTPError, ResourceManager, static_file
from mazeweb.crawler.plugin import MazePlugin


@MazePlugin.router
class EspressoPlugin(Plugin):
    __plugin_name__ = 'espresso'

    def _compile(self, source, destination_dir):
        """
        Compiles a Coffee script file source into a JavaScript file destination.

        The compilation is performed by the coffe compiler installed on the
        system.

        @param source
            The source CoffeScript file.
        @param destination_dir
            The destinataion directory for the JavaScript file.
        @raise ValueError if the source file cannot be compiled
        """
        code = subprocess.call([
            'coffee',
            '--output', destination_dir,
            source])
        if code:
            raise ValueError(source)

    @MazePlugin.get('/espresso/<path:path>.js')
    def get_js(self, path):
        """
        Retrieves a coffee script and, if necessary, compiles it.

        @param path
            The base path to the file to retrieve. The file extensions '.coffee'
            and '.js' are appended.
        @return a bottle static_file
        """
        target = os.path.join(self.cache_dir, path + '.js')
        coffee_file_rel = path + '.coffee'

        if not os.path.isfile(target) or self.configuration('compile.always'):
            for path in reversed(list(self.configuration.paths)):
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
                    try:
                        self._compile(coffee_file, os.path.dirname(target))
                        break
                    except ValueError:
                        raise HTTPError(status = 500)

        return static_file(os.path.basename(target), os.path.dirname(target))

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

        for path in reversed(list(self.configuration.paths)):
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
