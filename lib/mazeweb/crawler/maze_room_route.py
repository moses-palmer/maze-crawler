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