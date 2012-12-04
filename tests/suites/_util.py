import os
import socket
import subprocess
import sys
import time

if sys.version_info.major < 3:
    from httplib import CannotSendRequest, HTTPConnection
else:
    from http.client import CannotSendRequest, HTTPConnection

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
    server = subprocess.Popen(args, env = env)

    # Wait for the socket to become available
    while True:
        assert server.poll() is None
        try:
            connection = HTTPConnection(_HOST, port)
            connection.request('GET', '/')
            connection.getresponse().close()
            break
        except (CannotSendRequest, socket.error):
            time.sleep(0.1)

    _servers.append((server, connection))

def _server_stop():
    """
    Kills the most currently started server.

    @raise AssertionError if the current server is not running
    @raise IndexError if no server is running
    """
    global _servers

    server, connection = _servers.pop()
    assert server.poll() is None, \
        'The current server is not running'
    connection.close()
    server.kill()


def _get_connection():
    """
    Returns a connection to the most currently started server.

    @return a connection to the most currently started server
    @raise AssertionError if the most currently started server is not running
    @raise IndexError if no server is running
    """
    global _servers

    server, connection = _servers[-1]
    assert server.poll() is None, \
        'The current server is not running'

    return connection
