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
from .. import app, util


@app.get('/maze')
def maze_get(maze):
    """Retrieves a description of the current maze.

    The response is a :term:`maze dict` describing the new maze.

    :statuscode 200: the maze description was retrieved

    :statuscode 204: no maze has been initialised
    """
    return util.to_dict(maze)


@app.post('/maze')
def maze_reset():
    """Resets the current maze and reinitialises it.

    The response is a :term:`maze dict` describing the new maze.

    :jsonparam int width: The width of the maze. This must be a value greater
        than ``0``. This value is optional with a default value of ``30``.

    :jsonparam int height: The height of the maze. This must be a value greater
        than ``0``. This value is optional with a default value of ``20``.

    :jsonparam int walls: The number of walls for every room of the maze. This
        value is optional with a default value of ``4``. Supported values are
        ``3``, ``4`` and ``6``.

    :statuscode 200: the maze was successfully reset

    :statuscode 400: a parameter is invalid
    """
    try:
        maze, remaining = util.new(**bottle.request.json)
    except (KeyError, ValueError):
        raise bottle.HTTPError(status = 400)
    if remaining:
        print('Remaining arguments: ' + str(remaining))

    util.store(maze)
    return util.to_dict(maze)


@app.put('/maze')
def maze_update():
    """Updates the maze.

    The response is a :term:`maze dict` describing the new maze.

    :jsonparam int current_room: The :term:`room identifier` of the room to
        which to move. This room must be immediately reachable from the current
        room. This parameter is optional.

    :statuscode 200: the maze was successfully updated

    :statuscode 400: no maze has been initialised

    :statuscode 403: the requested room is not immediately reachable

    :statuscode 404: the requested room does not exist
    """
    try:
        maze = util.load()
    except bottle.HTTPResponse as e:
        if e.status_code == 204:
            e.status = 400
        raise

    # Do not store the session by default
    store = False

    # Check for a request to change the current room
    try:
        next_room_identifier = int(bottle.request.json.get(
            'current_room',
            maze.current_room))
    except:
        return bottle.HTTPResponse(status = 400)
    if next_room_identifier != maze.current_room:
        next_room = util.get_adjacent(maze, next_room_identifier)
        maze.current_room = next_room_identifier
        store = True

    if store:
        util.store(maze)

    result = util.to_dict(maze)

    for plugin in maze.plugins.values():
        plugin.update_maze(maze, bottle.request.json, result)

    return result


@app.delete('/maze')
def maze_delete():
    """Deletes the current maze.

    :statuscode 204: the maze was deleted
    """
    bottle.request.environ.get('beaker.session').delete()
    return bottle.HTTPResponse(status = 204)
