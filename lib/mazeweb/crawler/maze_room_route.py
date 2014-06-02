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
    """Retrieves a description of a room.

    Only immediately reachable rooms will be returned.

    An immediately reachable room is the current room and any connected rooms.

    The response is a :term:`recursive room dict`.

    :param room_identifier: The room identifier.

    :statuscode 200: the room was successfully retrieved

    :statuscode 204: no maze has been initialised

    :statuscode 403: the room is not immediately reachable

    :statuscode 404: ``room_identifier`` is invalid
    """
    return util.room_to_dict(
        maze,
        util.get_adjacent(maze, room_identifier), True)
