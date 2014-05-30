# coding: utf-8
# mazeweb
# Copyright (C) 2012-2014 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import bottle

from beaker.middleware import SessionMiddleware


session_options = {
    'session.type': 'memory',
    'session.cookie_expires': 300,
    'session.auto': True}


app = bottle.Bottle()

@app.get('/')
def get_session_cookie():
    """
    Simply causes the beaker session cookie to be set.
    """
    session = bottle.request.environ.get('beaker.session')
    session.persist()


from . import crawler
from . import plugins


app = SessionMiddleware(app, session_options)
plugins.load()
