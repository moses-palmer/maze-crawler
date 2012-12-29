from mazeweb.plugins import load, unload, PLUGINS

from .. import test

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
