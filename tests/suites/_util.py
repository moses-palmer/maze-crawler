import json
import os
import socket
import subprocess
import sys
import time

from .. import test
from mazeweb.util.data import JSONWrapper

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
_SERVER_APPLICATION = 'mazeweb:app'

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
            os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'lib'),
        'MAZEWEB_PLUGIN_PATH': os.getenv('MAZEWEB_PLUGIN_PATH'),
        'MAZEWEB_CONFIG_DIR': os.getenv('MAZEWEB_CONFIG_DIR'),
        'MAZEWEB_DATA_DIR': os.getenv('MAZEWEB_DATA_DIR')}

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
    inner.name = f.__name__
    inner.suite = f.suite if hasattr(f, 'suite') else f.__globals__['__name__']

    return test(inner)


def get(path):
    """
    Retrieves the data at path for the most currently started server with HTTP
    GET.

    If the response content type is application/json, a value parsed with
    json.loads is returned, otherwise a string is returned.

    @param path
        The path to the data to get.
    @return the tuple (response_code, data)
    @raise AssertionError if the most currently started server is not running
    """
    c, headers = _get_connection_data()

    # Parse the data
    c.request('GET', path, headers = headers)
    r = c.getresponse()
    data = _get_response_data(r)
    status = r.status

    return (r.status, data)


def put(path, data):
    """
    Uploads data to path for the most currently started server with HTTP PUT.

    If the response content type is application/json, a value parsed with
    json.loads is returned, otherwise a string is returned.

    @param path
        The path to the data to get.
    @param data
        The data to upload. If this is a str, it will be uploaded as text/plain,
        otherwise it will be passed to json.dumps and uploaded as
        application/json.
    @return the tuple (response_code, data)
    @raise AssertionError if the most currently started server is not running
    """
    c, headers = _get_connection_data()

    # Convert the data
    if not isinstance(data, str):
        data = json.dumps(data)
        headers['Content-Type'] = 'application/json'
    else:
        headers['Content-Type'] = 'text/plain'

    # Upload the data
    c.request('PUT', path, data, headers)
    r = c.getresponse()
    data = _get_response_data(r)
    status = r.status

    return (r.status, data)


def post(path, data):
    """
    Uploads data to path for the most currently started server with HTTP POST.

    If the response content type is application/json, a value parsed with
    json.loads is returned, otherwise a string is returned.

    @param path
        The path to the data to get.
    @param data
        The data to upload. If this is a str, it will be uploaded as text/plain,
        otherwise it will be passed to json.dumps and uploaded as
        application/json.
    @return the tuple (response_code, data)
    @raise AssertionError if the most currently started server is not running
    """
    c, headers = _get_connection_data()

    # Convert the data
    if not isinstance(data, str):
        data = json.dumps(data)
        headers['Content-Type'] = 'application/json'
    else:
        headers['Content-Type'] = 'text/plain'

    # Upload the data
    c.request('POST', path, data, headers)
    r = c.getresponse()
    data = _get_response_data(r)
    status = r.status

    return (r.status, data)


def delete(path):
    """
    Deletes the resource path for the most currently started server with HTTP
    DELETE.

    If the response content type is application/json, a value parsed with
    json.loads is returned, otherwise a string is returned.

    @param path
        The path to the data to get.
    @return the tuple (response_code, data)
    @raise AssertionError if the most currently started server is not running
    """
    c, headers = _get_connection_data()

    # Delete the resource
    c.request('DELETE', path, headers = headers)
    r = c.getresponse()
    data = _get_response_data(r)
    status = r.status

    return (r.status, data)


def maze_reset(**kwargs):
    """
    Resets the current maze by PUTing kwargs on /maze.

    The response is verified.

    @raise AssertionError if the maze was not created
    """
    status, data = post('/maze', kwargs)
    assert status == 200, \
        'POST /maze failed with status code %d' % status
