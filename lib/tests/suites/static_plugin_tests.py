from mazeweb.plugins import load, unload, PLUGINS

from ._util import webtest, get, put, post, delete, maze_reset, webtest

@webtest
def static_get0():
    """GET static resource that does not exist"""
    maze_reset()

    status, data = get('/static/__unused__')
    assert status == 404, \
        'GET /static/__unused__ returned %d, not 404' % status


@webtest
def static_get1():
    """GET static resource that exists"""
    maze_reset()

    status, data = get('/static/hello.json')
    assert status == 200, \
        'GET /static/hello.json returned %d, not 200' % status

    assert data.hello == 'world', \
        'GET /static/hello.json returned %s' % str(data)


@webtest
def static_get2():
    """GET resource and verify that later specified source directory takes
    precedence"""
    maze_reset()

    status, data = get('/static/shadowed.txt')

    assert data.strip() == 'Valid data', \
        'Shadowing file did not take precedence: %s' % (
            data)


@webtest
def static_get3():
    """GET resource and verify that later specified source directory takes
    precedence"""
    status, data = get('/static/hello.json')
    assert status == 200, \
        'GET /static/hello.json returned %d, not 200' % status

    assert data.hello == 'world', \
        'GET /static/hello.json returned %s' % str(data)
