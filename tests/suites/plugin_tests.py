from mazeweb.plugins import load, unload, PLUGINS

from .. import test
from ._util import webtest, get, put, post, delete, maze_reset

@test
@test.before(load)
@test.after(unload)
def PLUGINS_initialised():
    """Asserts that the plugins from the test resources are loaded"""
    assert 'test1' in PLUGINS, \
        'Test1Plugin was not loaded'
    assert 'test2' in PLUGINS, \
        'Test2Plugin was not loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_enabled():
    """Asserts that a disabled plugin is not loaded"""
    assert not 'disabled' in PLUGINS, \
        'DisabledPlugin was loaded'


@webtest
def plugins_loaded():
    """Tests that the plugins are loaded when mazeweb is started and that they
    are passed with the maze description"""
    maze_reset()

    status, data = get('/maze')

    assert 'test1' in data.plugins, \
        'Test1Plugin was not loaded'
    assert 'test2' in data.plugins, \
        'Test2Plugin was not loaded'


@webtest
def plugins_initialized():
    """Tests that the initialized callbacks are called"""
    maze_reset()

    status, data = get('/maze')

    assert 'initialize' in data.plugins, \
        'InitializePlugin was not loaded'
    assert data.current_room.position == dict(x = 1, y = 1), \
        'InitializePlugin did not set the current room'


@webtest
def plugins_get_maze():
    """Tests that the get maze callbacks are called"""
    maze_reset()

    status, data = get('/maze')

    assert data.get_maze_plugin == 'was here', \
        'GetMazePlugin did not update the maze'


@webtest
def plugins_update_maze():
    """Tests that the update maze callbacks are called"""
    maze_reset()

    status, data = put('/maze', dict(
        update_maze_plugin = 'activated'))

    assert data.update_maze_plugin == 'activated', \
        'GetMazePlugin did not update the maze'
