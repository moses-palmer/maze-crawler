import json
import math
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

        # Create a cache for rooms, and a mapping from ID to position
        self.rooms = [list(None for i in range(self.width))
            for j in range(self.height)]
        self.mapping = {}

        # Retrieve the current room
        self.current_room = data.current_room

    @property
    def current_room(self):
        """The identifier of the current room"""
        return self._current_room

    @current_room.setter
    def current_room(self, value):
        """Sets the current room identifier"""
        self._put('/maze', dict(
            current_room = value))
        self._current_room = value
        self._update_cache(self._current_room)

    @property
    def position(self):
        """The position of the current room"""
        return self.mapping[self.current_room]

    @position.setter
    def position(self, value):
        """Sets the current room position"""
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError('%s is not a valid position' % str(value))

        room = self.rooms[value[1]][value[0]]
        if room is None:
            raise ValueError('Room at %s is unknown' % str(value))
        self.current_room, walls = room

    def is_reachable(self, room_position):
        """
        Returns whether a room is immediately reachable from the current room.

        @param room_position
            The position opf the room.
        @return whether the room is reachable
        """
        if room_position == self.position:
            # The current room is reachable
            return True
        else:
            return any(room_position == tuple(p + d
                    for p, d in zip(self.position, w[1]))
                for w in self[self.position][1])

    def __del__(self):
        # Delete the session on the server
        if hasattr(self, 'connection') and hasattr(self, 'cookies'):
            try:
                self._delete('/maze')
            except:
                pass

    def __getitem__(self, i):
        if i in self.mapping:
            return self[self.mapping[i]]

        if isinstance(i, tuple) and len(i) == 2:
            x, y = i
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                raise IndexError()
            return self.rooms[i[1]][i[0]]

        raise KeyError(i)

    def _update_cache(self, identifier, add_neighbors = True):
        """
        Retrieves the specified room from the server and updates the cache.

        @param identifier
            The identifier of the room.
        @param add_neighbors
            Whether to also request neighbouring rooms. If this is True, every
            immediately reachable neighbour is also retrieved.
        """
        def span_to_direction(span):
            """
            Transforms a span expressed as an angle pair to a direction vector.
            """
            x = math.cos(span.start) + math.cos(span.end)
            y = math.sin(span.start) + math.sin(span.end)
            h = math.sqrt(x**2 + y**2)
            ix, iy = int(x / h), int(y / h)
            if abs(ix) == abs(iy):
                raise ValueError('Angles %d, %d yield invalid direction %s' % (
                    int(span.start * 360), int(span.end * 360), str((ix, iy))))
            return (ix, iy)

        # Get the current room
        data = self._get('/maze/%s' % identifier)
        self.mapping[identifier] = (
            int(data.position.x),
            int(data.position.y))
        self.rooms[data.position.y][data.position.x] = (
            (
                int(identifier),
                tuple((int(w.target), span_to_direction(w.span))
                    for w in data.walls if w.target)))

        # Update the neighbour rooms
        if add_neighbors:
            for w in data.walls:
                if w.target:
                    self._update_cache(int(w.target), add_neighbors = False)

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
