Plugins for mazeweb
===================

The mazeweb server supports plugins.

Plugins are called when HTTP actions are performed. see
:class:`~mazeweb.plugins.Plugin` for a listing of all events.

Plugins are sub-packages of :mod:`mazeweb.plugins`. The are loaded from all
directories specified in :data:`mazeweb.plugins.__path__` when
:func:`mazeweb.plugins.load` is called.

:data:`mazeweb.plugins.__path__` is initialised when :mod:`mazeweb.plugins` is
imported. Its value is set from the environment variable
``$MAZEWEB_PLUGIN_PATH``, which is split on :data:``os.pathsep``. The package
directory for :mod:`mazeweb.plugins` is always included.


The plugin interface
--------------------

.. autoclass:: mazeweb.plugins.Plugin
    :members:


Module interface
----------------

.. automodule:: mazeweb.plugins
    :members:
    :exclude-members: Plugin


Standard plugins
----------------

.. autoclass:: mazeweb.plugins.static.StaticPlugin
    :members:

.. autoclass:: mazeweb.plugins.espresso.EspressoPlugin
    :members:
