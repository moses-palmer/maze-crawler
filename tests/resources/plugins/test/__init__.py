from .. import Plugin

class TestPlugin1(Plugin):
    __plugin_name__ = 'test1'

class TestPlugin2(Plugin):
    __plugin_name__ = 'test2'

class DisabledPlugin(Plugin):
    __plugin_name__ = 'disabled'
