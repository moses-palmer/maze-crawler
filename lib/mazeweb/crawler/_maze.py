import bottle
from .. import mazeutil

from app import app


@app.get('/maze')
def maze_get():
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
    return mazeutil.to_dict(mazeutil.load())


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
        maze, remaining = mazeutil.new(**bottle.request.json)
    except (KeyError, ValueError):
        raise bottle.HTTPError(status = 400)
    if remaining:
        print('Remaining arguments: ' + str(remaining))

    mazeutil.store(maze)
    return mazeutil.to_dict(maze)


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
        maze = mazeutil.load()
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
        next_room = mazeutil.get_adjacent(maze, next_room_identifier)
        maze.current_room = next_room_identifier
        store = True

    if store:
        mazeutil.store(maze)

    return mazeutil.to_dict(maze)
