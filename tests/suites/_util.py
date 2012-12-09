import json
import os
import socket
import subprocess
import sys
import time

from .. import test

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
    cookies = ''
    while True:
        assert server.poll() is None
        try:
            connection = HTTPConnection(_HOST, port)
            connection.request('GET', '/')
            r = connection.getresponse()
            for h, v in r.getheaders():
                if h == 'set-cookie':
                    cookies = v
                    break
            r.close()
            break
        except (CannotSendRequest, socket.error):
            time.sleep(0.1)

    _servers.append((server, connection, cookies))

def _server_stop():
    """
    Kills the most currently started server.

    @raise AssertionError if the current server is not running
    @raise IndexError if no server is running
    """
    global _servers

    server, connection, cookies = _servers.pop()
    assert server.poll() is None, \
        'The current server is not running'
    connection.close()
    server.kill()


def _get_connection_data():
    """
    Returns a connection to the most currently started server, and the headers
    that should be sent along.

    The headers include cookies set by the first request to the server.

    @return the tuple (connection, headers)
    @raise AssertionError if the most currently started server is not running
    """
    server, connection, cookies = _servers[-1]
    assert server.poll() is None, \
        'The current server is not running'

    return connection, {
        'Cookie': cookies}


def _get_response_data(response):
    """
    Returns the data of the response.

    If the content type is application/json, an object indexable as a JavaScript
    object will be returned, otherwise a string will be returned.

    @param response
        The HTTP response as returned by HTTPConnection.getresponse().
    @return the response data
    """
    class JSONWrapper(object):
        def __init__(self, d):
            self._d = d
            for aname in dir(d):
                # Copy all magic methods from the value except those we define
                value = getattr(d, aname)
                if callable(value) \
                        and not aname in (
                            '__class__',
                            '__cmp__',
                            '__getattr__',
                            '__getitem__') \
                        and aname.startswith('__') and aname.endswith('__'):
                    setattr(self, aname,
                        lambda *args, **kwargs:
                            value(*args, **kwargs))

        def __get__(self, instance, owner):
            value = self._d
            if isinstance(value, (dict, list)):
                return self
            else:
                return value
        def __cmp__(self, other):
            print 'compared', self
            return cmp(self._d, other)
        def __getattr__(self, key):
            value = self._d[key]
            if isinstance(value, (dict, list)):
                return JSONWrapper(value)
            else:
                return value
        __getitem__ = __getattr__

    if response.getheader('Content-Type') == 'application/json':
        return JSONWrapper(json.loads(response.read()))
    else:
        return response.read()


def webtest(f):
    """
    A decorator to make a function a test for the server.

    This decorator will return a @test decorated function that starts the
    server, makes sure a connection can be made, then calls the test function
    and finally shuts down the server.
    """
    def inner():
        _server_start()
        try:
            f()
        finally:
            _server_stop()

    inner.__doc__ = f.__doc__
    inner.func_name = f.func_name
    inner.suite = f.suite if hasattr(f, 'suite') else f.__globals__['__name__']

    return test(inner)
