from .. import Plugin

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
