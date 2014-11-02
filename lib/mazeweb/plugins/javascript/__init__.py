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
import shutil

from bottle import HTTPResponse, static_file

from .. import Plugin, PLUGINS
from mazeweb.crawler.plugin import MazePlugin


@MazePlugin.router
class JavaScriptPlugin(Plugin):
    """Serves JavaScript.

    This plugin is separate from *static* to allow passing all *JavaScript*
    through a single point."""
    __plugin_name__ = 'javascript'

    @classmethod
    def initialize(self):
        super(JavaScriptPlugin, self).initialize()
        self.sources = [self]

    @classmethod
    def _javascript_from_partial_path(self, partial):
        """Locates a ``JavaScript`` file in one of the registered sources.

        :param str partial: The path to look up. This is a relative part without
            the extensions ``.js``.
        """
        for source in self.sources:
            value = source.javascript_from_partial_path(partial)
            if not value is None:
                return value
        return None

    @classmethod
    def _cache_path(self, partial):
        """Converts a partial path to a full path in the cache.

        This function ensures that the resulting path is a subpath in the cache
        directory.

        :param str partial: The path to complete. This is a relative part
            without the extensions ``.js``.

        :raises ValueError: if the path tries to escape the cache directory
        """
        full = os.path.realpath(os.path.join(self.cache_dir, partial + '.js'))
        if full.startswith(self.cache_dir + os.path.sep):
            return full
        else:
            raise ValueError('%s is outside of cache directory', partial)

    @classmethod
    def _cache_lookup(self, partial):
        """Looks up a file in the cache.

        :param str partial: The path to look up. This is a relative part without
            the extensions ``.js``.

        :return: an :func:`os.stat` result, or ``None``.
        """
        try:
            return os.stat(self._cache_path(partial))
        except OSError:
            return None

    @classmethod
    def _cache_add(self, partial, full):
        """Adds a file to the cache.

        :param str partial: The path to add. This is a relative part without
            the extensions ``.js``.

        :param str full: The full path of the file to add.
        """
        target = self._cache_path(partial)

        # Make sure the target directory exists
        try:
            os.makedirs(os.path.dirname(target))
        except OSError:
            pass

        shutil.copyfile(full, target)
        shutil.copystat(full, target)

    @MazePlugin.get('/<partial:path>.js')
    @classmethod
    def get_javascript(self, partial):
        """Retrieves a *JavaScript* file.

        :param str partial: The base path to the file to retrieve. The file
            extension ``.js`` is appended.

        :statuscode 200: the file was found

        :statusocde 404: the file does not exist

        :statuscode 500: an error occurred when trying to retrieve the file
        """
        cache_st = self._cache_lookup(partial)

        try:
            full = self._javascript_from_partial_path(partial)
            if full is None:
                return HTTPResponse(status = 404)
        except:
            return HTTPResponse(status = 500)

        source_st = os.stat(full)

        if cache_st is None or cache_st.st_mtime != source_st.st_mtime:
            self._cache_add(partial, full)

        return static_file(partial +'.js', self.cache_dir)

    @classmethod
    def javascript_from_partial_path(self, partial):
        """Retrieves the absolute path name for a partial path.

        :param str partial: The path to retrieve. This is a relative part
            without the extensions ``.js``.

        :return: an absolute path, or ``None``
        :rtype: str or None
        """
        full = os.path.join(os.path.dirname(__file__), partial + '.js')
        if os.access(full, os.R_OK):
            return full
        else:
            return None
