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

    assert mw.maze.width == 5 and mw.maze.height == 5, \
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

    for w in mw.maze.doors(mw.position):
        assert not getattr(mw[w.room_pos], 'identifier', False) is False, \
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
    mw.current_room = mw[
        next(
            mw.maze.doors(
                mw.mapping[start_room]))
            .room_pos].identifier


@webtest
def MazeWalker_current_room2():
    """Setting MazeWalker.current_room to an unreachable room identifier"""
    mw = MazeWalker()

    start_room = mw.current_room
    mw.current_room = mw[
        next(
            mw.maze.doors(
                mw.mapping[start_room]))
            .room_pos].identifier
    for unreachable_room in (mw[w.room_pos].identifier
            for w in mw.maze.doors(mw.mapping[mw.current_room])
            if mw[w.room_pos].identifier != start_room):
        mw.current_room = start_room

        with assert_exception(AssertionError):
            mw.current_room = unreachable_room


@webtest
def MazeWalker_position0():
    """Setting MazeWalker.position to an invalid value"""
    mw = MazeWalker()

    with assert_exception(ValueError):
        mw.position = (-1, -1)


@webtest
def MazeWalker_position1():
    """Setting MazeWalker.position to an immediately reachable room"""
    mw = MazeWalker()

    start_room = mw.current_room
    next_room = next(
        mw.maze.doors(
            mw.mapping[start_room])).room_pos
    mw.position = next_room


@webtest
def MazeWalker_position2():
    """Setting MazeWalker.position to an unknown room"""
    mw = MazeWalker()

    start_position = mw.position

    with assert_exception(ValueError):
        mw.position = (start_position[0], start_position[1] + 2)


@webtest
def MazeWalker_position3():
    """Setting MazeWalker.position to an unreachable room"""
    mw = MazeWalker()

    start_room = mw.current_room
    mw.current_room = mw[
        next(
            mw.maze.doors(
                mw.mapping[start_room]))
            .room_pos].identifier
    for unreachable_room_id in (mw[w.room_pos].identifier
            for w in mw.maze.doors(mw.position)
            if mw[w.room_pos].identifier != start_room):
        unreachable_room = mw.mapping[unreachable_room_id]
        mw.current_room = start_room

        with assert_exception(AssertionError):
            mw.position = unreachable_room


@webtest
def MazeWalker_is_reachable0():
    """MazeWalker.is_reachable for the current room"""
    mw = MazeWalker()

    assert mw.is_reachable(mw.position), \
        'The current room is not reachable'


@webtest
def MazeWalker_is_reachable1():
    """MazeWalker.is_reachable for neighbouring rooms"""
    mw = MazeWalker()

    start_room = mw.current_room
    mw.current_room = mw[
        next(
            mw.maze.doors(
                mw.mapping[start_room]))
            .room_pos].identifier

    for w in mw.maze.walls(mw.position):
        old_pos = mw.position
        next_pos = mw.maze.walk(w)
        try:
            mw.position = next_pos
            is_reachable = True
            mw.position = old_pos
        except (AssertionError, ValueError):
            is_reachable = False

        assert mw.is_reachable(next_pos) == is_reachable, \
            'MazeWalker.is_reachable returned %s, but the room could %s ' \
            'moved to' % (not is_reachable, 'be' if is_reachable else 'not be')
