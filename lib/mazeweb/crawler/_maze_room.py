import bottle
from .. import mazeutil

from app import app


@app.get('/maze/<room_identifier:int>')
def maze_get_room(room_identifier):
    """
    Retrieves a description of a room.

    @response.identifier
        The identifier of the room.
    @response.position
        The position of the room in the maze matrix expressed as
        dict(x = ..., y = ...).
    @response.center
        The physical centre of the room expressed as dict(x = ..., y = ...).
    @response.walls
        A list containing dict(span = dict(start = ..., end = ...),
        target = identifier). If the wall does not have a wall, target is None.

    @return 204 if no maze has been initialised, 403 if the requested room is
        not immediately reachable, 404 if room_identifier is invalid and 200
        otherwise
    """
    maze = mazeutil.load()

    try:
        room_pos = maze.room_mapping[room_identifier]
    except KeyError:
        raise bottle.HTTPError(status = 404)

    return mazeutil.room_to_dict(maze, room_pos)
