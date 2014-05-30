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
    """
    Retrieves a description of the current maze.

    @response.width
        The width of the current maze.
    @response.height
        The height of the current maze.
    @response.walls
        The number of walls for the current maze.
    @response.start_room
        The identifier of the room at (0, 0).
    @response.current_room
        The identifier of the current room.

    @return 204 if no maze has been initialised and 200 otherwise
    """
    return util.to_dict(maze)


@app.post('/maze')
def maze_reset():
    """
    Resets the current maze and reinitialises it.

    @request.width
        The width of the maze. This must be a value greater than 0. This value
        is optional with a default value of 30.
    @request.height
        The height of the maze. This must be a value greater than 0. This value
        is optional with a default value of 20.
    @request.walls
        The number of walls for every room of the maze. This value is optional
        with a default value of 4.

    @return 400 if a parameter is invalid and 200 otherwise
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
    """
    Updates the maze.

    @request.current_room
        The room to which to move. This room must be immediately reachable from
        the current room. This parameter is optional.

    @response.width
        The width of the current maze.
    @response.height
        The height of the current maze.
    @response.walls
        The number of walls for the current maze.
    @response.start_room
        The identifier of the room at (0, 0).
    @response.current_room
        The identifier of the current room.

    @return 400 if no maze has been initialised, 403 if the requested room is
        not immediately reachable, 404 if the requested room does not exist and
        200 otherwise
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
    """
    Deletes the current session.

    @return 204
    """
    bottle.request.environ.get('beaker.session').delete()
    return bottle.HTTPResponse(status = 204)
