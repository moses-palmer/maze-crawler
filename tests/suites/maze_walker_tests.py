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
