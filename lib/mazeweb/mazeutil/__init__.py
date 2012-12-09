import bottle
import random

from maze.quad import Maze
from maze.tri import TriMaze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

from numeric import randuniq

MAZE_CLASSES = dict((len(mc.Wall.WALLS), mc) for mc in (
    TriMaze,
    Maze,
    HexMaze))


def new(width = 30, height = 20, walls = 4, seed = None, **kwargs):
    """
    Creates a new maze from keyword arguments.

    @param width, height
        The dimensions of the maze.
    @param walls
        The number of walls. Valid values are 3, 4 and 6.
    @return the tuple (a new maze instance, unused arguments)
    @raise KeyError if walls is invalid
    @raise ValueError if the dimensions are invalid
    """
    if width <= 0 or height <= 0:
        raise ValueError('invalid maze dimensions')
    maze = MAZE_CLASSES[walls](width, height)
    maze.random = randuniq(
        None,
        seed or random.randint(0, 1000000))
    initialize(maze, lambda max: maze.random.next() % max)

    maze.room_mapping = {}
    for room_pos in maze.room_positions:
        identifier = maze.random.next()
        maze[room_pos].identifier = identifier
        maze.room_mapping[identifier] = room_pos

    return (maze, kwargs)


def load():
    """
    Loads the maze from the current session.

    @return the current maze
    @raise bottle.HTTPResponse if no cached maze exists
    """
    session = bottle.request.environ.get('beaker.session')
    try:
        return session['maze']
    except KeyError:
        raise bottle.HTTPResponse(status = 204)


def store(maze):
    """
    Stores a maze to the current session.

    The session is saved.

    @param maze
        The new maze.
    """
    session = bottle.request.environ.get('beaker.session')
    session['maze'] = maze
    session.save()


def to_dict(maze):
    """
    Converts a maze instance to a dict that can be passed as return value for
    /maze.

    @param maze
        The maze to convert to a dict.
    @return a dict describing the maze
    """
    return dict(
        width = maze.width,
        height = maze.height,
        walls = len(maze.Wall.WALLS),
        start_room = maze[(0, 0)].identifier)


def room_to_dict(maze, room_pos):
    """
    Converts a room to a dict that can be passed as return value for
    /maze/<room_identifier>.

    @param maze
        The maze to which the room belongs.
    @param room_pos
        The position of the room.
    @return a dict describing the room
    """
    return dict(
        identifier = maze[room_pos].identifier,
        position = dict(
            x = room_pos[0],
            y = room_pos[1]),
        center = dict(
            x = maze.get_center(room_pos)[0],
            y = maze.get_center(room_pos)[1]),
        walls = [dict(
            target = maze[maze.walk(w)].identifier
                if w in maze[room_pos] else None,
            span = dict(
                start = w.span[0],
                end = w.span[1])) for w in maze.walls(room_pos)])
