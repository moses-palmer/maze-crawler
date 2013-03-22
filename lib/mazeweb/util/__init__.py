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

import bottle
import random

from maze.quad import Maze
from maze.tri import TriMaze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

from .numeric import randuniq
from ..plugins import PLUGINS


MAZE_CLASSES = dict((len(mc.Wall.WALLS), mc) for mc in (
    TriMaze,
    Maze,
    HexMaze))


def new(width = 30, height = 20, walls = 4, seed = None, **kwargs):
    """Creates a new maze from keyword arguments.

    :param int width: The width of the maze.

    :param int height: The height of the maze.

    :param int walls: The number of walls. Valid values are 3, 4 and 6.

    :return: the tuple (a new maze instance, unused arguments)

    :raises KeyError: if walls is invalid

    :raises ValueError: if the dimensions are invalid
    """
    if width <= 0 or height <= 0:
        raise ValueError('invalid maze dimensions')
    maze = MAZE_CLASSES[walls](width, height)
    maze.plugins = dict((name, plugin()) for name, plugin in PLUGINS.items())
    maze.random = randuniq(
        None,
        seed or random.randint(0, 1000000))

    for plugin in maze.plugins.values():
        plugin.pre_initialize(maze)
    initialize(maze, lambda max: next(maze.random) % max)

    maze.room_mapping = {}
    for room_pos in maze.room_positions:
        identifier = next(maze.random)
        maze[room_pos].identifier = identifier
        maze.room_mapping[identifier] = room_pos

    maze.current_room = maze[(0, 0)].identifier

    for plugin in maze.plugins.values():
        plugin.post_initialize(maze)

    return (maze, kwargs)


def load():
    """Loads the maze from the current session.

    :return: the current maze
    :rtype: maze.BaseMaze

    :raises bottle.HTTPResponse: if no cached maze exists
    """
    session = bottle.request.environ.get('beaker.session')
    try:
        return session['maze']
    except KeyError:
        raise bottle.HTTPResponse(status = 204)


def store(maze):
    """Stores a maze to the current session.

    The session is saved.

    :param maze.BaseMaze: maze The new maze.
    """
    session = bottle.request.environ.get('beaker.session')
    session['maze'] = maze
    session.save()


def to_dict(maze):
    """Converts a :class:`maze.BaseMaze` instance to a dict.

    The result is a :term:`maze dict`.

    :param maze.BaseMaze maze: The maze to convert to a dict.

    :return: a dict describing the maze
    :rtype: dict
    """
    result = dict(
        width = maze.width,
        height = maze.height,
        walls = len(maze.Wall.WALLS),
        plugins = list(maze.plugins.keys()),
        start_room = maze[(0, 0)].identifier,
        current_room = room_to_dict(maze, maze.room_mapping[maze.current_room],
            neighbor_details = True))

    for plugin in maze.plugins.values():
        plugin.get_maze(maze, result)

    return result


def room_to_dict(maze, room_pos, neighbor_details = False):
    """Converts a room to a ``dict``.

    The result is a :term:`recursive room dict` if ``neighbor_details`` is
    ``True`` and a :term:`non-recursive room dict` otherwise.

    :param maze.BaseMaze maze: The maze to which the room belongs.

    :param room_pos: The position of the room.
    :type room_pos: (int, int)

    :param bool neighbor_details: Whether to include adjacent rooms recursively.
        If this is ``True``, the ``target`` values in ``walls`` will be
        populated with ``room_to_dict(maze, neighbor_pos, False)``, otherwise it
        will be set to the identifier of the neighbour room.

    :return: a dict describing the room
    :rtype: dict
    """
    result = dict(
        identifier = maze[room_pos].identifier,
        position = dict(
            x = room_pos[0],
            y = room_pos[1]),
        center = dict(
            x = maze.get_center(room_pos)[0],
            y = maze.get_center(room_pos)[1]),
        walls = [dict(
            target = (maze[maze.walk(w)].identifier if not neighbor_details
                    else room_to_dict(maze, maze.walk(w)))
                if w in maze[room_pos] else None,
            span = dict(
                start = w.span[0],
                end = w.span[1])) for w in maze.walls(room_pos)
            if not maze.edge(w)])

    for plugin in maze.plugins.values():
        plugin.get_room(maze, room_pos, neighbor_details, result)

    return result


def get_adjacent(maze, room_identifier):
    """Returns the coordinates of an adjacent room.

    :param maze.BaseMaze maze: The maze whose room coordinates to retrieve.

    :param int room_identifier: The identifier of the adjacent room.

    :return: the coordinates of the adjacent room
    :rtype: (int, int)

    :raises bottle.HTTPResponse: if the room is not immediately reachable
        (``403``) or if ``room_identifier`` is invalid (``404``)
    """
    try:
        room_pos = maze.room_mapping[room_identifier]
    except KeyError:
        raise bottle.HTTPError(status = 404)

    # Check whether the rooms are connected
    current_room_pos = maze.room_mapping[maze.current_room]
    if room_pos == current_room_pos \
            or maze.adjacent(room_pos, current_room_pos):
        return room_pos
    else:
        raise bottle.HTTPError(status = 403)
