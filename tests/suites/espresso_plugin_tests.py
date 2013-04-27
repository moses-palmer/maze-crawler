import os
import subprocess
import tempfile

from mazeweb.plugins import load, unload, PLUGINS

from ._util import webtest, get, put, post, delete, maze_reset, webtest


@webtest
def espresso_get0():
    """GET resource that does not exist"""
    maze_reset()

    status, data = get('/espresso/__unused__')
    assert status == 404, \
        'GET /espresso/__unused__ returned %d, not 404' % status


@webtest
def espresso_get1():
    """GET CoffeeScript resource that exists"""
    maze_reset()

    status, data = get('/espresso/hello_world.coffee')
    assert status == 200, \
        'GET /espresso/hello_world.js returned %d, not 200' % status

    assert len(data) > 0, \
        'data was empty'
