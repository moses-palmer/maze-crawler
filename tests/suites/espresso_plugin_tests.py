import os
import subprocess
import tempfile

from mazeweb.plugins import load, unload, PLUGINS

from ._util import webtest, get, put, post, delete, maze_reset, webtest
from ._script_util import run_coffee, run_js


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


@webtest
def espresso_get2():
    """GET resource and verify compatibility with CoffeScript for empty
    output"""
    maze_reset()

    status, js_script = get('/espresso/empty.js')
    js_data = run_js(js_script)
    status, coffee_script = get('/espresso/empty.coffee')
    coffee_data = run_coffee(coffee_script)

    assert js_data == coffee_data, \
        'JavaScript did not produce same as CoffeeScript: %s != %s' % (
            js_data, coffee_data)


@webtest
def espresso_get3():
    """GET resource and verify compatibility with CoffeScript for non-empty
    output"""
    maze_reset()

    status, js_script = get('/espresso/hello_world.js')
    js_data = run_js(js_script)
    status, coffee_script = get('/espresso/hello_world.coffee')
    coffee_data = run_coffee(coffee_script)

    assert js_data == coffee_data, \
        'JavaScript did not produce same as CoffeeScript: %s != %s' % (
            js_data, coffee_data)
