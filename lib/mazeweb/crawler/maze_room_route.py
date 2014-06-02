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


@app.get('/maze/<room_identifier:int>')
def maze_get_room(maze, room_identifier):
    """
    Retrieves a description of a room.

    Only immediately reachable rooms will be returned.

    An immediately reachable room is the current room and any connected rooms.

    @response.identifier
        The identifier of the room.
    @response.position
        The position of the room in the maze matrix expressed as
        dict(x = ..., y = ...).
    @response.center
        The physical centre of the room expressed as dict(x = ..., y = ...).
    @response.walls
        A list containing dict(span = dict(start = ..., end = ...),
        target = room). If the wall does not have a wall, target is None. The
        target values will be on the same format as this object, except that the
        target values of their walls list will be only room identifiers.

    @return 204 if no maze has been initialised, 403 if the requested room is
        not immediately reachable, 404 if room_identifier is invalid and 200
        otherwise
    """
    return util.room_to_dict(
        maze,
        util.get_adjacent(maze, room_identifier), True)
