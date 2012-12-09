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
