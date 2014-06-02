from .. import Plugin
from mazeweb.crawler.plugin import MazePlugin

class TestPlugin1(Plugin):
    __plugin_name__ = 'test1'

class TestPlugin2(Plugin):
    __plugin_name__ = 'test2'

class DisabledPlugin(Plugin):
    __plugin_name__ = 'disabled'

class InitializePlugin(Plugin):
    __plugin_name__ = 'initialize'

    def pre_initialize(self, maze):
        for wall in maze.walls((0, 0)):
            maze[wall.room_pos][wall] = True

    def post_initialize(self, maze):
        maze.current_room = maze[(1, 1)].identifier

class GetMazePlugin(Plugin):
    __plugin_name__ = 'get_maze'

    def get_maze(self, maze, result):
        result['get_maze_plugin'] = 'was here'

class UpdateMazePlugin(Plugin):
    __plugin_name__ = 'update_maze'

    def update_maze(self, maze, value, result):
        result['update_maze_plugin'] = value.get('update_maze_plugin', None)

class GetRoomPlugin(Plugin):
    __plugin_name__ = 'get_room'

    def get_room(self, maze, room_pos, neighbor_details, result):
        result['get_room_plugin'] = dict(
            room_pos = dict((c, rp) for c, rp in zip('xy', room_pos)),
            neighbor_details = neighbor_details)

class DependsPlugin1(Plugin):
    __plugin_name__ = 'depends-1'
    __plugin_dependencies__ = ['test1']

class DependsPlugin2(Plugin):
    __plugin_name__ = 'depends-2'
    __plugin_dependencies__ = ['test1', 'test2']

class DependsPlugin3(Plugin):
    __plugin_name__ = 'depends-3'
    __plugin_dependencies__ = ['test1', 'depends-2']

class DependsPlugin4(Plugin):
    __plugin_name__ = 'depends-4'
    __plugin_dependencies__ = ['test1', 'depends-2', 'depends-3']

class DependsPlugin5(Plugin):
    __plugin_name__ = 'depends-5'
    __plugin_dependencies__ = ['disabled', 'depends-2', 'depends-3']

class ConflictsPlugin1(Plugin):
    __plugin_name__ = 'conflicts-1'
    __plugin_conflicts__ = ['test1']

class ConflictsPlugin2(Plugin):
    __plugin_name__ = 'conflicts-2'
    __plugin_conflicts__ = ['disabled']

class ConflictsPlugin3(Plugin):
    __plugin_name__ = 'conflicts-3'
    __plugin_dependencies__ = ['conflicts-1']

class ConflictsPlugin4(Plugin):
    __plugin_name__ = 'conflicts-4'
    __plugin_dependencies__ = ['conflicts-3']

@MazePlugin.router
class RouterPlugin1(Plugin):
    __plugin_name__ = 'router-1'

    @MazePlugin.get('/router-echo/<value>')
    def get_test(self, value):
        print self.__class__.__name__
        return {'value': value}

@MazePlugin.router
class RouterPlugin2(Plugin):
    __plugin_name__ = 'router-2'
    __plugin_conflicts__ = ['router-3']

    @MazePlugin.get('/router-silent/<value>')
    def get_test(self, value):
        print self.__class__.__name__
        return {'value': value}

@MazePlugin.router
class RouterPlugin3(Plugin):
    __plugin_name__ = 'router-3'

    @MazePlugin.get('/router-blocker/<value>')
    def get_test(self, value):
        print self.__class__.__name__
        return {'value': value}
