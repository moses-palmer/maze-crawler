from ._util import webtest

from .. import assert_exception

from cursedmaze import MazeWalker

@webtest
def MazeWalker_init0():
    """MazeWalker creation with invalid arguments"""
    with assert_exception(ValueError):
        MazeWalker(width = -1)


@webtest
def MazeWalker_init1():
    """MazeWalker creation with valid arguments"""
    mw = MazeWalker(width = 5, height = 5)

    assert mw.width == 5 and mw.height == 5, \
        'Failed to create a maze with dimensions %S: it was %s' % (
            str((width, height)), str((mw.width, mw.height)))


@webtest
def MazeWalker_getitem0():
    """MazeWalker[int] for invalid room identifier"""
    mw = MazeWalker()

    with assert_exception(KeyError):
        mw[-1]


@webtest
def MazeWalker_getitem1():
    """MazeWalker[tuple] for invalid room position"""
    mw = MazeWalker()

    with assert_exception(IndexError):
        mw[(-1, -1)]


@webtest
def MazeWalker_getitem2():
    """MazeWalker[tuple] for valid room identifier"""
    mw = MazeWalker()

    assert not mw[mw.current_room] is None, \
        'The current room is not cached'

    for neighbor, direction in mw[mw.current_room][1]:
        assert not mw[neighbor] is None, \
            'A neigbour of the current room is not cached'


@webtest
def MazeWalker_current_room0():
    """Setting MazeWalker.current_room to an invalid room identifier"""
    mw = MazeWalker()

    with assert_exception(AssertionError):
        mw.current_room = -1


@webtest
def MazeWalker_current_room1():
    """Setting MazeWalker.current_room to an immediately reachable room
    identifier"""
    mw = MazeWalker()

    start_room = mw.current_room
    mw.current_room = mw[mw.current_room][1][0][0]


@webtest
def MazeWalker_current_room2():
    """Setting MazeWalker.current_room to an unreachable room identifier"""
    mw = MazeWalker()

    start_room = mw.current_room
    mw.current_room = mw[mw.current_room][1][0][0]
    for unreachable_room in (w[0] for w in mw[mw.current_room][1]
            if w[0] != start_room):
        mw.current_room = start_room

        with assert_exception(AssertionError):
            mw.current_room = unreachable_room
