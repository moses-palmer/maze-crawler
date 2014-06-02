import math

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


@webtest
def maze_update0():
    """Test PUT /maze for an uninitialised maze"""
    status, data = put('/maze', {})

    assert status == 400, \
        'PUT /maze returned %d, not 400' % status


@webtest
def maze_update1():
    """Test PUT /maze for an initialised maze with no data"""
    maze_reset()

    original_data = {}
    status, data = put('/maze', original_data)

    assert status == 200, \
        'PUT /maze returned %d, not 200' % status


@webtest
def maze_update2():
    """Test PUT /maze for an initialised maze with request to move to current
    room"""
    maze_reset()

    status, data = get('/maze')

    original_data = dict(
        current_room = data.current_room.identifier)
    status, data = put('/maze', original_data)

    assert status == 200, \
        'PUT /maze returned %d, not 200' % status


@webtest
def maze_update3():
    """Test PUT /maze for an initialised maze with request to move to invalid
    room"""
    maze_reset()

    original_data = dict(
        current_room = '-1')
    status, data = put('/maze', original_data)

    assert status == 404, \
        'PUT /maze returned %d, not 200' % status


@webtest
def maze_update4():
    """Test PUT /maze with a request to move to an unreachable room"""
    maze_reset()

    status, data = get('/maze')

    start_room = data.current_room.identifier
    status, data = get('/maze/%d' % start_room)
    assert status == 200, \
        'GET /maze/%d returned %d instead of 200' % (start_room, status)

    for next_room in (wall.target.identifier
            for wall in data.walls
            if wall.target):
        status, data = get('/maze/%d' % next_room)
        assert status == 200, \
            'GET /maze/%d returned %d instead of 200' % (next_room, status)

        try:
            unreachable_room = next(wall.target.identifier
                for wall in data.walls
                if wall.target and wall.target.identifier != start_room)
        except StopIteration:
            continue
        original_data = dict(
            current_room = unreachable_room)
        status, data = put('/maze', original_data)

        assert status == 403, \
            'PUT /maze returned %d instead of 403' % status

        break


@webtest
def maze_update5():
    """Test PUT /maze for an initialised maze with request to move to neighbour
    room"""
    maze_reset()

    status, data = get('/maze')

    room_identifier = data.current_room.identifier
    status, data = get('/maze/%d' % room_identifier)

    next_room = next(wall.target.identifier
        for wall in data.walls
        if wall.target)

    original_data = dict(
        current_room = next_room)
    status, data = put('/maze', original_data)

    assert status == 200, \
        'PUT /maze returned %d, not 200' % status
    assert data.current_room.identifier == next_room, \
        'current_room is %s, not %s' % (data.current_room, next_room)


@webtest
def maze_delete0():
    """Test DELETE /maze for an uninitialised maze"""
    status, data = delete('/maze')

    assert status == 204, \
        'DELETE /maze returned %d, not 204' % status


@webtest
def maze_delete1():
    """Test DELETE /maze for an initialised maze"""
    maze_reset()

    status, data = delete('/maze')

    assert status == 204, \
        'DELETE /maze returned %d, not 204' % status

    status, data = get('/maze')

    assert status == 204, \
        'GET /maze returned %d instead of 204' % status


def maze_walk():
    """Walks the way from start_room to the top right corner of the maze and
    verifies all results along the way"""
    maze_reset()

    status, data = get('/maze')

    current_room = data.current_room
    direction = None
    previous_room = None
    target_position = dict(
        x = data.width - 1,
        y = data.height - 1)

    while True:
        status, data = get('/maze/%d' % current_room)
        assert status == 200, \
            'GET /maze/%d returned %d, not 200' % (current_room, status)
        assert data.identifier == current_room, \
            'current_room is %d, not %s' % (data.current_room, next_room)

        if data.position == target_position:
            break

        if not direction:
            direction, next_room = next((w.span.start, w.target)
                for w in data.walls
                if w.target)
        else:
            directions = sorted(
                ((w.span.start, w.target) for w in data.walls if w.target),
                key = lambda a:
                    a[0] - direction if a[0] > direction
                    else 2 * math.pi + a[0] - direction)
            direction, next_room = directions[
                0 if directions[0][1] != previous_room else -1]
            previous_room = current_room

        original_data = data
        status, data = put('/maze', dict(
            current_room = next_room))
        assert status == 200, \
            'PUT /maze returned %d for %d => %d, current room = %s' % (
                status, current_room, next_room, str(original_data))
        assert data.current_room == next_room, \
            'current_room is %d, not %d' % (data.current_room, next_room)
        current_room = next_room
