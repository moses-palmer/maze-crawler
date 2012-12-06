import bottle
import random

from maze.quad import Maze
from maze.tri import TriMaze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

MAZE_CLASSES = dict((len(mc.Wall.WALLS), mc) for mc in (
    TriMaze,
    Maze,
    HexMaze))


def new(width = 30, height = 20, walls = 4, **kwargs):
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
    initialize(maze, lambda max: random.randint(0, max - 1))
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
        walls = len(maze.Wall.WALLS))
