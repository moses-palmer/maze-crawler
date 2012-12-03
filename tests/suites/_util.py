import os
import subprocess
import time

# The list of servers running
_servers = []

# The address on which the bottle server will listen; every time server_start is
# called the port number will be incremented and every time server_stop is
# called it will be decremented
_HOST = 'localhost'
_BASE_PORT = 8080

# The string that specifies the bottle descriptor for the server application
_SERVER_APPLICATION = None

def _server_start():
    """
    Starts a new server.

    @raise OSError if a python instance cannot be started
    """
    global _servers

    port = _BASE_PORT + len(_servers)
    args = ['python', '-m', 'bottle',
        '--bind=%s:%d' % (_HOST, port),
        '--debug',
        _SERVER_APPLICATION]
    env = {
        'PYTHONPATH': os.path.join(
            os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'lib')}

    # Start bottle
    _servers.append(subprocess.Popen(args, env = env))

def _server_stop():
    """
    Kills the most currently started server.

    @raise AssertionError if the current server is not running
    @raise IndexError if no server is running
    """
    global _servers

    server = _servers.pop()
    assert server.poll() is None, \
        'The current server is not running'
    server.kill()
