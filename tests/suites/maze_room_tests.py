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
    start_position = data.current_room.position

    room_identifier = data.current_room.identifier
    status, data = get('/maze/%d' % room_identifier)

    assert status == 200, \
        'GET /maze/%d returned %d instead of 200' % (room_identifier, status)

    assert data.identifier == room_identifier, \
        'The identifier for the start room was %s, not %d' % (
            str(data.identifier), room_identifier)

    assert data.position == start_position, \
        'The position of the start room was %s, not %s' % (
            str(data.position), str(start_position))


@webtest
def maze_room_get2():
    """Test GET /maze/<start_room> with a default maze initialised for an
    invalid room"""
    maze_reset()

    room_identifier = -1
    status, data = get('/maze/%d' % room_identifier)

    assert status == 404, \
        'GET /maze/%d returned %d instead of 404' % (room_identifier, status)


@webtest
def maze_room_get3():
    """Test GET /maze/<start_room> with a default maze initialised for an
    unreachable room"""
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
            continue;
        status, data = get('/maze/%d' % unreachable_room)
        assert status == 403, \
            'GET /maze/%d returned %d instead of 403' % (
                unreachable_room, status)

        break
