The HTTP Interface to mazeweb
=============================

This is a description of the HTTP interface to mazeweb.

.. autobottle:: mazeweb:app


Glossary
--------

.. glossary::

    room identifier
        An ``int``.

    room position
        A two dimensional room position in the actual room matrix used by the
        maze. It looks like this:

        .. sourcecode:: javascript

            {
                "x": 12,
                "y": 23
            }

        ``x`` and ``y`` are always integers.

    physical room position
        The actual *physical* position of a room when the rooms are rendered on
        a canvas. It looks like this:

        .. sourcecode:: javascript

            {
                "x": 0.7071067811865475,
                "y": 0.7071067811865475
            }

    wall span
        The span of a wall expressed with a start and end angle in radians. It
        looks like this:

        .. sourcecode:: javascript

            {
                "start": 2.356194490192345,
                "end": 0.7853981633974483
            }

        Degrees are expressed clock-wise.

    non-recursive room dict
        The JSON representation of a room in a maze. It looks like this:

        .. sourcecode:: javascript

            {
                "identifier": 3541243473, // A room identifier
                "position": {
                    // A room position
                },
                "center": {
                    // A physical room position
                },
                "walls": [
                    {
                        "span": {
                            // A wall span
                        },
                        "target": 2740848712 // A room identifier
                    },
                    ... // An entry for every wall
                ]
            }

        .. seealso:: :term:`room identifier`, :term:`room position`,
            :term:`physical room position`, :term:`wall span`,
            :term:`room identifier`

    recursive room dict
        The JSON representation of a room in a maze. It looks like this:

        .. sourcecode:: javascript

            {
                "identifier": 3541243473, // A room identifier
                "position": {
                    // A room position
                },
                "center": {
                    // A physical room position
                },
                "walls": [
                    {
                        "span": {
                            // A wall span
                        },
                        "target": {
                            // A non-recursive room dict
                        }
                    },
                    ... // An entry for every wall
                ]
            }

        .. seealso:: :term:`room identifier`, :term:`room position`,
            :term:`physical room position`,  :term:`wall span`,
            :term:`non-recursive room dict`

    maze dict
        The JSON representation of :class:`maze.BaseMaze` meta data. It looks
        like this:

        .. sourcecode:: javascript

            {
                "height": 20,
                "width": 20,
                "walls": 4,
                "plugins": [],
                "start_room": 1411380071,
                "current_room": {
                    // A recursive room dict
                }
            }

        `plugins` contains a list of plugin names.

        .. seealso:: :term:`recursive room dict`
