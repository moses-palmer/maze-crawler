import inspect
from bottle import install, HTTPResponse, HTTPError

from .. import app, util


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
        # otherwise
        args = inspect.getargspec(context['callback'])[0]
        if not 'maze' in args:
            return callback

        def wrapper(*args, **kwargs):
            # Get the maze instance
            kwargs['maze'] = util.load()

            return callback(*args, **kwargs)

        # Replace the route callback with the wrapped one.
        return wrapper

app.install(MazePlugin())
