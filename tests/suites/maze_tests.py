from ._util import webtest, get, put, post, delete, maze_reset

@webtest
def maze_get0():
    """Test GET /maze with no maze initialised"""
    status, data = get('/maze')

    assert status == 204, \
        'GET /maze returned %d instead of 204' % status
    assert not data, \
        'GET /maze returned data (%s)' % str(data)


@webtest
def maze_get1():
    """Test GET /maze with a default maze initialised"""
    maze_reset()

    status, data = get('/maze')

    assert status == 200, \
        'GET /maze returned %d instead of 200 after update' % status

    assert not isinstance(data, str), \
        'GET /maze did not return valid data (%s)' % str(data)


@webtest
def maze_get2():
    """Test GET /maze to verify that start_room is set"""
    maze_reset()

    status, data = get('/maze')

    assert data.start_room, \
        'start_room was not set'


@webtest
def maze_reset0():
    """Test POST /maze with an empty body"""
    maze_reset()

    status, data = get('/maze')

    assert status == 200, \
        'GET /maze returned %d instead of 200 after update' % status

    assert not isinstance(data, str), \
        'GET /maze did not return valid data (%s)' % data


@webtest
def maze_reset1():
    """Test POST /maze with a maze description"""
    width = 55
    height = 13
    walls = 6
    maze_reset(
        width = width,
        height = height,
        walls = walls)

    status, data = get('/maze')

    assert status == 200, \
        'GET /maze returned %d instead of 200 after update' % status

    assert data.width == width \
            and data.height == height \
            and data.walls == walls, \
        'GET /maze returned %s' % str(data)


@webtest
def maze_reset2():
    """Test POST /maze with a maze description with invalid data"""
    status, data = post('/maze', dict(
        walls = 7))
    assert status == 400, \
        'POST /maze failed with status code %d' % status

    status, data = post('/maze', dict(
        width = 0))
    assert status == 400, \
        'POST /maze failed with status code %d' % status

    status, data = post('/maze', dict(
        height = -1))
    assert status == 400, \
        'POST /maze failed with status code %d' % status

    status, data = get('/maze')

    assert status == 204, \
        'GET /maze returned %d instead of 204' % status
