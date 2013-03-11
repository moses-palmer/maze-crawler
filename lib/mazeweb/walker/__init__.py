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

import json
import math
import sys

from mazeweb.util.data import JSONWrapper

from maze.hex import HexMaze
from maze.quad import Maze
from maze.tri import TriMaze

if sys.version_info.major < 3:
    from httplib import CannotSendRequest, HTTPConnection
else:
    from http.client import CannotSendRequest, HTTPConnection


class MazeWalker(object):
    def __init__(self, host = 'localhost', port = 8080, width = 20,
            height = 15):
        """Initialises a new maze walker.

        :param str host: The maze crawler host.

        :param int port: The post.

        :param int width: The width of the maze

        :param int height: The height of the maze.

        :raises AssertionError: if no cookies were retrieved from the server

        :raises ValueError: if the size of the maze created on the server was
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
                if h.lower() == 'set-cookie':
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

        self.maze = {
            3: TriMaze,
            4: Maze,
            6: HexMaze}[data.walls](data.width, data.height)

        # Create a mapping from ID to position
        self.mapping = {}

        # Retrieve the current room
        self.current_room = data.current_room.identifier

    @property
    def current_room(self):
        """The identifier of the current room"""
        return self._current_room

    @current_room.setter
    def current_room(self, value):
        """Sets the current room identifier"""
        maze = self._put('/maze', dict(
            current_room = value))
        self._current_room = value
        self._update_cache(self._current_room, maze.current_room)

    @property
    def position(self):
        """The position of the current room"""
        return self.mapping[self.current_room]

    @position.setter
    def position(self, value):
        """Sets the current room position"""
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError('%s is not a valid position' % str(value))

        try:
            room = self.maze[value]
        except IndexError:
            raise ValueError('%s is outside of the maze' % str(value))

        try:
            self.current_room = room.identifier
        except AttributeError:
            raise ValueError('%s is not a known room from %s' % (
                str(value), str(self.position)))

    def is_reachable(self, room_position):
        """Returns whether a room is immediately reachable from the current
        room.

        :param room_position:
            The position of the room.
        :type room_position: (int, int)

        :return: whether the room is reachable
        :rtype: bool
        """
        if room_position == self.position:
            # The current room is reachable
            return True
        else:
            return self.maze.connected(self.position, room_position)

    def __del__(self):
        # Delete the session on the server
        if hasattr(self, 'connection') and hasattr(self, 'cookies'):
            try:
                self._delete('/maze')
            except:
                pass

    def __getitem__(self, i):
        try:
            return self[self.mapping[i]]

        except KeyError:
            if isinstance(i, tuple) and len(i) == 2:
                x, y = i
                if False \
                        or x < 0 or x >= self.maze.width \
                        or y < 0 or y >= self.maze.height:
                    raise IndexError()
                return self.maze[i]

        raise KeyError(i)


    def _update_cache(self, identifier, add_neighbors = True,
            current_room = None):
        """Retrieves the specified room from the server and updates the cache.

        :param str identifier: The identifier of the room.

        :param bool add_neighbors: Whether to also request neighbouring rooms.
            If this is ``True``, every immediately reachable neighbour is also
            retrieved.

        :param dict current_room:
            A value to use as the current room instead of querying the server.
            This must be a :term:`recursive room dict` or a
            :term:`non-recursive room dict`. If this is ``None``, the server
            will be queried.
        """
        # Get the current room
        data = current_room or self._get('/maze/%s' % identifier)
        room_pos = (int(data.position.x), int(data.position.y))
        room = self.maze[room_pos]

        # Make sure that the room is what we expect
        if (data.center.x, data.center.y) != self.maze.get_center(room_pos):
            raise ValueError('Unexpecter center for room %s: %s' % (
                str(room_pos), str(data.center)))

        # Update the room
        room.identifier = identifier
        self.mapping[room.identifier] = room_pos

        # Update the doors
        for wall in self.maze.walls(room_pos):
            try:
                if not self.maze.edge(wall):
                    self.maze[room_pos][wall] = next(not w.target is None
                        for w in data.walls
                        if w.span.start == wall.span[0])
            except StopIteration:
                raise ValueError('Wall %s not found for room %s' % (
                    wall.NAMES[int(wall)], str(room_pos)))

        # Update the neighbour rooms
        if add_neighbors:
            for w in data.walls:
                if w.target:
                    self._update_cache(w.target.identifier, False, w.target)


    def _req(self, method, path, data = None):
        """Performs an HTTP request to the server for path.

        :param str method: The HTTP method to use.

        :param str path: The path.

        :param data: The data to send.
        :type data: dict or None

        :return: the JSON decoded response, or None for HTTP status 204
        :rtype: dict or None
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
            data = response.read().decode('ascii')
            assert (response.getheader('Content-Type') == 'application/json'
                    or not data), \
                'The server did not respond with JSON data'

            return JSONWrapper(json.loads(data)) \
                if response.status == 200 else None
        finally:
            response.close()

    def _get(self, path):
        """
        See :meth:`_req`
        """
        return self._req('GET', path)

    def _put(self, path, data):
        """
        See :meth:`_req`
        """
        return self._req('PUT', path, data)

    def _post(self, path, data):
        """
        See :meth:`_req`
        """
        return self._req('POST', path, data)

    def _delete(self, path):
        """
        See :meth:`_req`
        """
        return self._req('DELETE', path)
