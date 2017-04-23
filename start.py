import psycopg2.pool
import pyweb

log = pyweb.Log()
log.log('Starting up WSGI application...', log.INFO)

# Controller
routing = pyweb.Routing()

# View
view = pyweb.View()

# Database Pool
# Ref: http://www.slideshare.net/petereisentraut/programming-with-python-and-postgresql page 62
# Note: maxconn (configured here) must >= the number of uwsgi threads (configured in start.sh).
# Otherwise PoolError("connection pool exausted") might be raised while executing "dbpool.getconn()".
try:
    dbpool = psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=20, database='mytest', user='myuser',
                                                  password='Password1', host='localhost', port=5432)
except psycopg2.Error as e:
    log.log('DB ThreadedConnectionPool error: {}'.format(e), log.CRITICAL)
    assert False


def application(environ, start_response):
    request = pyweb.Request(environ)
    response = pyweb.Response()
    db = pyweb.DB(log)
    db.connect_from_pool(dbpool)

    # Cache
    cache = pyweb.Cache(host='localhost', port=6379)

    # Session management
    sessid = request.cookie_var('sessid')
    if sessid is not None and pyweb.Session.is_id_valid(sessid) and cache.exists(pyweb.Session.get_storagename(sessid)):
        # User already has a session
        session = pyweb.Session(cache, sessid, ttl=14400)
    else:
        # Create a new session for this user
        session = pyweb.Session(cache, None, ttl=14400)
        sessid = session.get_id()
        # Set the cookie to expire until the browser is closed
        response.add_cookie('sessid', sessid, ttl=None, httponly=True)

    # Registry
    registry = pyweb.Registry()
    registry.cache = cache
    registry.db = db
    registry.log = log
    registry.request = request
    registry.response = response
    registry.session = session
    registry.view = view

    # Execute the requested controller
    path = environ['PATH_INFO']
    response_body = routing.route(path, registry, environ, start_response)

    return response_body


def shutdown():
    # Currently nobody calls this function
    log.log('Shutting down WSGI application...', log.INFO)
    dbpool.closeall()
    log.shutdown()
