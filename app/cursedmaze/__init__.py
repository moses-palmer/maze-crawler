import json
import sys

if sys.version_info.major < 3:
    from httplib import CannotSendRequest, HTTPConnection
else:
    from http.client import CannotSendRequest, HTTPConnection


class MazeWalker(object):
    class JSONWrapper(object):
        def __init__(self, d):
            self._d = d
            for aname in dir(d):
                # Copy all magic methods from the value except those we define
                if True and (\
                        aname.startswith('__') and aname.endswith('__')
                        and callable(getattr(d, aname))
                        and not aname in (
                            '__class__', # This is callable
                            '__getattr__',
                            '__getitem__',
                            '__int__')):
                    setattr(self, aname,
                        lambda s, *args, **kwargs:
                            getattr(s._d, aname)(s._d, *args, **kwargs))

        def __getattr__(self, key):
            v = self._d[key]
            if hasattr(v, '__getitem__'):
                return self.__class__(v)
            else:
                return v
        __getitem__ = __getattr__
        def __int__(self):
            return int(self._d)

    def __init__(self, host = 'localhost', port = 8080, width = 20,
            height = 15):
        """
        Initialises a new maze walker.

        @param host, port
            The host and port for the maze crawler server.
        @param width, height
            The dimensions of the maze.
        @raise AssertionError if no cookies were retrieved from the server
        @raise ValueError if the size of the maze created on the server was
            different from the requested size
        """
        self.host, self.port = host, port

        # Make an initial connection to get the session ID
        self.connection = HTTPConnection(self.host, self.port)
        self.connection.request('GET', '/')
        r = self.connection.getresponse()
        self.cookies = None
        try:
            for h, v in r.getheaders():
                if h == 'set-cookie':
                    self.cookies = v
                    break
        finally:
            r.close()

        assert self.cookies, \
            'No session ID was saved'

        # Initialise a new maze and get its properties
        data = self._post('/maze', dict(
            width = width,
            height = height))
        if data.width != width or data.height != height:
            raise ValueError('Failed to create a maze with dimensions %s' % (
                str((width, height))))
        self.width = data.width
        self.height = data.height

    def _req(self, method, path, data = None):
        """
        Performs a HTTP request to the server for path.

        @param method
            The HTTP method to use.
        @param path
            The path.
        @param data
            The data to send, or None.
        @return the JSON decoded response, or None for HTTP status 204
        """
        headers = {
            'Cookie': self.cookies}
        if data:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data)

        self.connection.request(method, path, data, headers = headers)
        response = self.connection.getresponse()

        try:
            # Map HTTP status 400 to ValueError
            if response.status == 400:
                raise ValueError('The server responded "%s" for %s %s' % (
                    response.read(), method, path))

            # Make sure the response is one we allow
            assert response.status in (200, 204), \
                'The server responded %d for %s %s' % (
                    response.status, method, path)

            # Make sure the data, if received, is application/json
            data = response.read()
            assert (response.getheader('Content-Type') == 'application/json'
                    or not data), \
                'The server did not respond with JSON data'

            return self.JSONWrapper(json.loads(data)) \
                if response.status == 200 else None
        finally:
            response.close()

    def _get(self, path):
        """
        @see _req
        """
        return self._req('GET', path)

    def _put(self, path, data):
        """
        @see _req
        """
        return self._req('PUT', path, data)

    def _post(self, path, data):
        """
        @see _req
        """
        return self._req('POST', path, data)

    def _delete(self, path):
        """
        @see _req
        """
        return self._req('DELETE', path)
