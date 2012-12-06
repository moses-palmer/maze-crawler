import bottle

from app import app


from beaker.middleware import SessionMiddleware

session_options = {
    'session.type': 'memory',
    'session.cookie_expires': 300,
    'session.auto': True}


@app.get('/')
def get_session_cookie():
    """
    Simply causes the beaker session cookie to be set.
    """
    session = bottle.request.environ.get('beaker.session')
    session.persist()


app = SessionMiddleware(app, session_options)
