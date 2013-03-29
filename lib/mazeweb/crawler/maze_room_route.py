import bottle
from .. import app, util


@app.get('/maze/<room_identifier:int>')
def maze_get_room(room_identifier):
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
        target = identifier). If the wall does not have a wall, target is None.

    @return 204 if no maze has been initialised, 403 if the requested room is
        not immediately reachable, 404 if room_identifier is invalid and 200
        otherwise
    """
    maze = util.load()
    return util.room_to_dict(
        maze,
        util.get_adjacent(maze, room_identifier))


@app.get('/maze/<room_identifier:int>/details')
def maze_get_room_details(room_identifier):
    """
    Retrieves a thorough description of a room.

    This will behave exactly like GET /maze/<room_identifier> with the following
    exceptions:

    @response.walls
        A list containing dict(span = dict(start = ..., end = ...),
        target = room). If the wall does not have a wall, target is None. The
        target values will be on the same format as GET /maze/<room_identifier>.

    @see maze_get_room
    """
    maze = util.load()
    return util.room_to_dict(
        maze,
        util.get_adjacent(maze, room_identifier), True)
