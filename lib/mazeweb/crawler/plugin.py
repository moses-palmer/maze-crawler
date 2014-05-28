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

import inspect
from bottle import abort, install, HTTPResponse, HTTPError

from .. import app, plugins, util
from mazeweb import app


class MazePlugin(object):
    """
    A bottle plugin that replaces the keyword argument 'maze' with an actual
    Maze instance stored in the session.
    """

    name = 'maze'

    def __init__(self):
        pass

    def apply(self, callback, context):
        # Check whether the route accepts the 'maze' keyword argument; ignore it
        # if it does not and is not a decorated plugin method
        try:
            argspec = inspect.getargspec(context['callback'])[0]
        except TypeError:
            argspec = inspect.getargspec(context['callback'].callback)[0]
        if not 'maze' in argspec and not isinstance(callback, self.routed):
            return callback

        def wrapper(*args, **kwargs):
            try:
                argspec = inspect.getargspec(context['callback'])[0]
            except TypeError:
                argspec = inspect.getargspec(context['callback'].callback)[0]

            # If the route is a plugin route, make sure to pass the plugin as
            # the self parameter
            if isinstance(callback, self.routed):
                try:
                    maze = util.load()
                    args = (maze.plugins[callback.plugin_name],) + args
                except (HTTPResponse, KeyError):
                    abort(404)
            else:
                maze = util.load()

            # Add the maze to the parameter list if required
            if 'maze' in argspec:
                kwargs['maze'] = maze

            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper

    class routed(object):
        def __init__(self, callback, method, *args, **kwargs):
            self.__name__ = callback.__name__
            self.callback = callback
            self.method = method
            self.args = args
            self.kwargs = kwargs
            self.plugin_name = None

        def __call__(self, *args, **kwargs):
            return self.callback(*args, **kwargs)

    @classmethod
    def route(self, method, *args, **kwargs):
        """
        A decorator to mark an instance method of a ..plugins.Plugin a route.

        When invoked, the instance is located by finding the plugin with the
        name of the __plugin_name__ attribute of the defining class.

        @param method
            The HTTP method this method routes.
        """
        def inner(callback):
            return self.routed(callback, method, *args, **kwargs)
        return inner

    @classmethod
    def get(self, *args, **kwargs):
        return self.route('GET', *args, **kwargs)

    @classmethod
    def put(self, *args, **kwargs):
        return self.route('PUT', *args, **kwargs)

    @classmethod
    def post(self, *args, **kwargs):
        return self.route('POST', *args, **kwargs)

    @classmethod
    def delete(self, *args, **kwargs):
        return self.route('DELETE', *args, **kwargs)

    @classmethod
    def router(self, router_class):
        """
        """
        for attribute_name in dir(router_class):
            try:
                # Get the attribute value; make sure it is a a plugin route
                item = getattr(router_class, attribute_name)
                if not isinstance(item, self.routed):
                    continue

                # Set the plugin name
                item.plugin_name = router_class.__plugin_name__

                # Add the attribute as a bottle route
                app.route(method = item.method, *item.args, **item.kwargs)(item)

            except (AttributeError, TypeError):
                print item
                import traceback
                traceback.print_exc()

            except:
                print item
                raise

        return router_class


app.install(MazePlugin())
