from ._util import webtest, get, put, post, delete, maze_reset

@webtest
def maze_room_get0():
    """Test GET /maze/1 with no maze initialised"""
    status, data = get('/maze/1')

    assert status == 204, \
        'GET /maze/1 returned %d instead of 204' % status
    assert not data, \
        'GET /maze/1 returned data (%s)' % str(data)


@webtest
def maze_room_get1():
    """Test GET /maze/<start_room> with a default maze initialised"""
    maze_reset()

    status, data = get('/maze')

    room_identifier = data.start_room
    status, data = get('/maze/%d' % room_identifier)

    assert status == 200, \
        'GET /maze/%d returned %d instead of 200' % (room_identifier, status)

    assert data.identifier == room_identifier, \
        'The identifier for the start room was %s, not %d' % (
            str(data.identifier), room_identifier)

    assert data.position == dict(
        x = 0,
        y = 0), \
        'The position of the start room was %s, not {"x": 0, "y": 0}' % (
            str(data.position))


@webtest
def maze_room_get2():
    """Test GET /maze/<start_room> with a default maze initialised for an
    invalid room"""
    maze_reset()

    room_identifier = -1
    status, data = get('/maze/%d' % room_identifier)

    assert status == 404, \
        'GET /maze/%d returned %d instead of 404' % (room_identifier, status)
