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


@test
@test.before(load)
@test.after(unload)
def plugin_dependencies0():
    """Asserts that a plugin with a dependency is loaded"""
    assert 'depends-1' in PLUGINS, \
        'DependsPlugin1 was not loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_dependencies1():
    """Asserts that a plugin with multiple dependencies is loaded"""
    assert 'depends-2' in PLUGINS, \
        'DependsPlugin2 was not loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_dependencies2():
    """Asserts that a plugin with multiple dependencies on plugins with
    dependencies is loaded"""
    assert 'depends-3' in PLUGINS, \
        'DependsPlugin3 was not loaded'
    assert 'depends-4' in PLUGINS, \
        'DependsPlugin4 was not loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_dependencies3():
    """Asserts that a plugin with dependencies on a disabled plugin is not
    loaded"""
    assert not 'depends-5' in PLUGINS, \
        'DependsPlugin5 was loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_conflicts0():
    """Asserts that a plugin that conflicts with a loaded plugin is not
    loaded"""
    assert not 'conflicts-1' in PLUGINS, \
        'ConflictsPlugin1 was loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_conflicts1():
    """Asserts that a plugin that conflicts with a plugin that is not loaded is
    loaded"""
    assert 'conflicts-2' in PLUGINS, \
        'ConflictsPlugin2 was loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_conflicts2():
    """Asserts that a plugins that depends on a plugin that conflicts with a
    loaded plugin is not loaded"""
    assert not 'conflicts-3' in PLUGINS, \
        'ConflictsPlugin3 was loaded'


@test
@test.before(load)
@test.after(unload)
def plugin_conflicts3():
    """Asserts that a plugins that depends on a plugin that is unloaded due to
    dependency on a plugin that conflicts with a loaded plugin is not loaded"""
    assert not 'conflicts-4' in PLUGINS, \
        'ConflictsPlugin4 was loaded'


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


@webtest
def plugins_get_room():
    """Tests that the get room callbacks are called"""
    maze_reset()

    status, data = get('/maze')
    room_position = data.current_room.position
    room_identifier = data.current_room.identifier

    expected = dict(
        room_pos = room_position,
        neighbor_details = False)
    status, data = get('/maze/%d' % room_identifier)
    assert data.get_room_plugin == expected, \
        'GetRoomPlugin set the room data to %s instead of %s' % (
            str(data.get_room_plugin), str(expected))

    expected = dict(
        room_pos = room_position,
        neighbor_details = True)
    status, data = get('/maze/%d/details' % room_identifier)
    assert data.get_room_plugin == expected, \
        'GetRoomPlugin set the room data to %s instead of %s' % (
            str(data.get_room_plugin), str(expected))
