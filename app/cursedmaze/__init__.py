import sys

if sys.version_info.major < 3:
    from httplib import CannotSendRequest, HTTPConnection
else:
    from http.client import CannotSendRequest, HTTPConnection


class MazeWalker(object):
    def __init__(self, host = 'localhost', port = 8080):
        """
        Initialises a new maze walker.

        @param host, port
            The host and port for the maze crawler server.
        @raise AssertionError if no cookies were retrieved from the server
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
