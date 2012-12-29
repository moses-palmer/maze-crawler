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
