#!/usr/bin/python3

import json
import model.user
import os
import pyweb
import pyweb.util
import re


# Util tests
def test_util():
    assert pyweb.util.get_int(3) == 3
    assert pyweb.util.get_int(3, -1) == 3
    assert pyweb.util.get_int(3.99, -1) == 3
    assert pyweb.util.get_int([3], -1) == -1
    assert pyweb.util.get_int((3,)) is None
    assert pyweb.util.get_int({3}, -1) == -1
    assert pyweb.util.get_int({'three': 3}) is None
    assert pyweb.util.get_int(None, -1) == -1
    assert pyweb.util.get_int('a string', -1) == -1
    assert pyweb.util.get_int('a string') is None


test_util()


# Log tests
def read_log(log_filename):
    assert type(log_filename) is str
    contents = []
    # Ref: http://www.diveintopython3.net/files.html
    with open(log_filename, 'rt') as f:
        for line in f:
            # Convert "2014-10-25 20:01:27,455: DEBUG: This is debug" into "DEBUG: This is debug"
            line_trunc = line.rstrip()[line.find(': ') + len(': '):]
            contents.append(line_trunc)
    return contents


def test_log():
    log = pyweb.Log()
    log.log('This is console only log')
    log.shutdown()
    if os.path.isfile('test.log'):
        os.remove('test.log')
    log = pyweb.Log('test.log')
    log.log('This is debug', log.DEBUG)
    log.log('This is info')
    log.log('This is info too', log.INFO)
    log.set_level(log.ERROR)
    log.log("This shouldn't be printed!", log.DEBUG)
    log.log("This shouldn't be printed!")
    log.log("This shouldn't be printed!", log.INFO)
    log.log("This shouldn't be printed!", log.WARNING)
    log.log('This should be printed', log.ERROR)
    log.log('This should be printed too', log.CRITICAL)
    log.shutdown()
    log = pyweb.Log()
    log.log('This is console only log')
    log.shutdown()
    # Verify
    contents = read_log('test.log')
    os.remove('test.log')
    assert contents == ['DEBUG: This is debug', 'INFO: This is info', 'INFO: This is info too',
                        'ERROR: This should be printed', 'CRITICAL: This should be printed too']


test_log()


# Config tests
def test_config():
    with open('testconfig.cfg', 'wt') as f:
        # https://docs.python.org/3/library/os.html#os.linesep:
        # "Do not use os.linesep as a line terminator when writing files opened in text mode (the default);
        # use a single '\n' instead, on all platforms."
        f.write('[section_a]\n')
        f.write('mykey=myvalue1\n')
        f.write('[section_b]\n')
        f.write('   \t mykey \t = \t myvalue2 \t \n')
        f.write('[general]\n')
        f.write('mykey=myvalue0\n')
        f.write('mynumber=8888\n')
    config = pyweb.Config('testconfig.cfg')
    # Default is to go into 'general' section
    assert config.get('mykey') == 'myvalue0'
    # Number is considered as string
    assert config.get('mynumber') == '8888'
    # Section names are case sensitive but keys are not
    assert config.get('MYKEY', 'section_a') == 'myvalue1'
    assert config.get('MYKEY', 'section_A') is None
    # Leading and trailing white-space is removed from keys and values
    assert config.get('mykey', 'section_b') == 'myvalue2'
    # Unknown
    assert config.get('something') is None
    assert config.get('something', 'else') is None
    os.remove('testconfig.cfg')


test_config()


# Registry tests
def test_registry():
    registry = pyweb.Registry()
    user = model.user.User(registry)
    controller = pyweb.Controller(registry)
    registry.a = 'apple'
    assert user.registry.a == 'apple'
    assert controller.registry.a == 'apple'


test_registry()


# Routing tests
def test_routing():
    routing = pyweb.Routing()
    # https://www.python.org/dev/peps/pep-0333/:
    #    REQUEST_METHOD: The HTTP request method, such as "GET" or "POST" .
    #                    This cannot ever be an empty string, and so is always required.
    #    PATH_INFO: This may be an empty string.
    #    QUERY_STRING: May be empty or absent.
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': ''}
    log = pyweb.Log()
    request = pyweb.Request(environ)
    response = pyweb.Response()
    registry = pyweb.Registry()
    registry.log = log
    registry.request = request
    registry.response = response

    # noinspection PyUnusedLocal
    def start_response(a, b):
        pass

    body = routing.route('/q/tests/url', registry, environ, start_response)
    assert body == [
        b'REQUEST_METHOD: GET. PATH_INFO: . _PATH_INFO_MATCHED: /q/tests/url.'
        b' _PATH_INFO_EXTENDED: None. QUERY_STRING: .']
    body = routing.route('/q/tests/url/', registry, environ, start_response)
    assert body == [
        b'REQUEST_METHOD: GET. PATH_INFO: . _PATH_INFO_MATCHED: /q/tests/url.'
        b' _PATH_INFO_EXTENDED: /. QUERY_STRING: .']
    body = routing.route('/q/tests/url/aaa/1/2/3', registry, environ, start_response)
    assert body == [
        b'REQUEST_METHOD: GET. PATH_INFO: . _PATH_INFO_MATCHED: /q/tests/url.'
        b' _PATH_INFO_EXTENDED: /aaa/1/2/3. QUERY_STRING: .']
    environ['QUERY_STRING'] = 'q=abc'
    body = routing.route('/q/tests/url/aaa/1/2/3', registry, environ, start_response)
    environ['QUERY_STRING'] = None
    assert body == [
        b'REQUEST_METHOD: GET. PATH_INFO: . _PATH_INFO_MATCHED: /q/tests/url.'
        b' _PATH_INFO_EXTENDED: /aaa/1/2/3. QUERY_STRING: q=abc.']
    body = routing.route('/non_existent', registry, environ, start_response)
    assert body == [b'Not Found']
    # body = routing.route ('/', registry, environ, start_response)
    # assert body != [b'Not Found']
    # body = routing.route ('', registry, environ, start_response)
    # assert body != [b'Not Found']
    # body = routing.route (None, registry, environ, start_response)
    # assert body != [b'Not Found']
    log.shutdown()


test_routing()


# View tests
def test_view():
    if not os.path.isdir('view/tests/_1/2/3'):
        os.makedirs('view/tests/_1/2/3')
    with open('view/tests/_1/2/3/template01.view', 'wt') as f:
        # https://docs.python.org/3/library/os.html#os.linesep:
        # "Do not use os.linesep as a line terminator when writing files opened in text mode (the default);
        # use a single '\n' instead, on all platforms."
        f.write('<html>\n')
        f.write('\tFrom Python: --- <?py print ("Hello, world!", end="") ?> ---\n')
        f.write('</html>\n')
    with open('view/tests/_1/2/3/template02.view', 'wt') as f:
        f.write('<?py\n')
        f.write('import html\n')
        f.write('?><html>\n')
        f.write('\tFrom Python: --- <?py print ("Simple variables: {} {}".format ('
                'html.escape (str (a)), html.escape (str (b))), end="") ?> ---\n')
        f.write('</html>\n')
    with open('view/tests/_1/2/3/template03.view', 'wt') as f:
        f.write('<html>\n')
        f.write('\tFrom Python: --- <?py print ("Test local variables: {}".format (str (locals())), end="") ?> ---\n')
        f.write('</html>\n')
    with open('view/tests/_1/2/3/template04.view', 'wt') as f:
        f.write('<?py\n')
        f.write('import html\n')
        f.write('?><html>\n')
        f.write('\tFrom Python: --- <?py print ("Complex variables: {} {} {}".format ('
                'html.escape (str (a)), html.escape (str (b)), html.escape (str (c[1]))), end="") ?> ---\n')
        f.write('</html>\n')
    with open('view/tests/_1/2/3/template05.view', 'wt') as f:
        f.write('<html>\n')
        f.write('<!-- Test backslashes: 1. \\n 2. f:\\SLB\\2012 - Pune\\ -->\n')
        f.write('</html>\n')
    view = pyweb.View()
    html01 = view.view('view/tests/_1/2/3/template01.view', {})
    assert html01 == '<html>\n\tFrom Python: --- Hello, world! ---\n</html>\n'
    html02 = view.view('view/tests/_1/2/3/template02.view', {'a': 'kevin', 'b': 1980})
    assert html02 == '<html>\n\tFrom Python: --- Simple variables: kevin 1980 ---\n</html>\n'
    html03 = view.view('view/tests/_1/2/3/template03.view', {'a': 'kevin'})
    assert html03 == "<html>\n\tFrom Python: --- Test local variables: {'a': 'kevin'} ---\n</html>\n"
    html04 = view.view('view/tests/_1/2/3/template04.view', {'a': '<?py &tag; ?>',
                                                             'b': 'unicode ' + chr(233) + chr(0x0bf2) + chr(3972) + chr(
                                                                 6000) + chr(13231) + ' rocks!',
                                                             'c': ['apple', 'banana', 'candy']})
    assert html04 == '<html>\n\tFrom Python: --- Complex variables: &lt;?py &amp;tag; ?&gt; unicode ' + chr(233) + chr(
        0x0bf2) + chr(3972) + chr(6000) + chr(13231) + ' rocks! banana ---\n</html>\n'
    html05 = view.view('view/tests/_1/2/3/template05.view', {})
    assert html05 == '<html>\n<!-- Test backslashes: 1. \\' + 'n 2. f:\\SLB\\' + '2012 - Pune\\ -->\n</html>\n'
    os.remove('view/tests/_1/2/3/template05.view')
    os.remove('view/tests/_1/2/3/template04.view')
    os.remove('view/tests/_1/2/3/template03.view')
    os.remove('view/tests/_1/2/3/template02.view')
    os.remove('view/tests/_1/2/3/template01.view')
    os.removedirs('view/tests/_1/2/3')


test_view()


# Request GET and POST tests: http://unixpapa.com/js/querystring.
def test_get_and_post():
    request = pyweb.Request({'CONTENT_LENGTH': 'ERR13'})
    assert request.get_var('foo') is None
    assert request.get_var_as_list('foo') is None
    assert request.post_raw() is None
    assert request.post_var('foo') is None
    assert request.post_var_as_list('foo') is None

    f = open('post.txt', 'w')
    f.write('foo=qux&baz=bar')
    f.close()
    f = open('post.txt', 'r')
    request = pyweb.Request({'QUERY_STRING': 'foo=bar&baz=qux', 'wsgi.input': f, 'CONTENT_LENGTH': 15})
    assert request.get_var('foo') == 'bar'
    assert request.get_var('baz') == 'qux'
    assert request.get_var('bar') is None
    assert request.get_var_as_list('foo') == ['bar']
    assert request.get_var_as_list('baz') == ['qux']
    assert request.get_var_as_list('bar') is None
    assert request.post_raw() == 'foo=qux&baz=bar'
    assert request.post_var('foo') == 'qux'
    assert request.post_var('baz') == 'bar'
    assert request.post_var('bar') is None
    assert request.post_var_as_list('foo') == ['qux']
    assert request.post_var_as_list('baz') == ['bar']
    assert request.post_var_as_list('bar') is None
    f.close()

    f = open('post.txt', 'w')
    f.write('search=here+to+stay&rock%26roll=Rock+%26+Roll&birthdate=16&16=my+birthdate')
    f.close()
    postlen = os.stat('post.txt').st_size
    f = open('post.txt', 'r')
    request = pyweb.Request(
        {'QUERY_STRING': 'search=Rock+%26+Roll&rock%26roll=here+to+stay', 'wsgi.input': f, 'CONTENT_LENGTH': postlen})
    assert request.get_var('search') == 'Rock & Roll'
    assert request.get_var('rock&roll') == 'here to stay'
    assert request.get_var('foo') is None
    assert request.get_var_as_list('search') == ['Rock & Roll']
    assert request.get_var_as_list('rock&roll') == ['here to stay']
    assert request.get_var_as_list('foo') is None
    assert request.post_raw() == 'search=here+to+stay&rock%26roll=Rock+%26+Roll&birthdate=16&16=my+birthdate'
    assert request.post_var('search') == 'here to stay'
    assert request.post_var('rock&roll') == 'Rock & Roll'
    assert request.post_var('birthdate') == '16'
    assert request.post_var('16') == 'my birthdate'
    assert request.post_var('foo') is None
    assert request.post_var_as_list('search') == ['here to stay']
    assert request.post_var_as_list('rock&roll') == ['Rock & Roll']
    assert request.post_var_as_list('birthdate') == ['16']
    assert request.post_var_as_list('16') == ['my birthdate']
    assert request.post_var_as_list('foo') is None
    f.close()

    f = open('post.txt', 'w')
    f.write('key1=&key2=&&key3&key4&key=mouse&key=cat&key=dog')
    f.close()
    postlen = os.stat('post.txt').st_size
    f = open('post.txt', 'r')
    request = pyweb.Request({'QUERY_STRING': 'key1=&key2=&key=dog&key=cat&key=mouse&&key3&key4', 'wsgi.input': f,
                             'CONTENT_LENGTH': postlen})
    assert request.get_var('key') == 'mouse'  # here we only get the last value
    assert request.get_var('key1') is None
    assert request.get_var_as_list('key') == ['dog', 'cat', 'mouse']  # here we get all values
    assert request.get_var_as_list('key1') is None
    assert request.post_raw() == 'key1=&key2=&&key3&key4&key=mouse&key=cat&key=dog'
    assert request.post_var('key') == 'dog'  # here we only get the last value
    assert request.post_var('key1') is None
    assert request.post_var_as_list('key') == ['mouse', 'cat', 'dog']  # here we get all values
    assert request.post_var_as_list('key1') is None
    f.close()

    os.remove('post.txt')


test_get_and_post()


# Ref: http://pymotw.com/2/Cookie/
def test_cookie_request():
    # r'' will make sure \ character is part of the string
    request = pyweb.Request({
        'HTTP_COOKIE': r'integer=5; string_with_quotes="He said, \"Hello, World!\""'})
    assert request.cookie_var('integer') == '5'
    assert request.cookie_var('string_with_quotes') == 'He said, "Hello, World!"'
    assert request.cookie_var('xxx') is None


test_cookie_request()


# Response tests
def test_response():
    response = pyweb.Response()
    assert response.escape('<HTML>Rock & Roll \'get it\' "babe"</HTML>') == '&lt;HTML&gt;Rock &amp; ' \
                                                                            'Roll &#x27;get it&#x27; &quot;ba' \
                                                                            'be&quot;&lt;/HTML&gt;'
    response = pyweb.Response()
    assert response.get_status() == '200 OK'
    assert response.get_body() == b'Hello, world!'
    response.set_header('Date', 'Sun, 16 Feb 1980 08:00:00 GMT')
    assert response.get_header('Date') == 'Sun, 16 Feb 1980 08:00:00 GMT'
    assert response.get_headers() == [('Date', 'Sun, 16 Feb 1980 08:00:00 GMT')]
    response.set_header('Date', ('Sun, 16 Feb 1980 08:00:00 GMT', 'Mon, 17 Feb 1980 17:00:00 GMT'))
    assert response.get_header('Date') == ('Sun, 16 Feb 1980 08:00:00 GMT', 'Mon, 17 Feb 1980 17:00:00 GMT')
    assert response.get_headers() == [('Date', 'Sun, 16 Feb 1980 08:00:00 GMT'),
                                      ('Date', 'Mon, 17 Feb 1980 17:00:00 GMT')]
    response.set_header('Date', ['Sun, 16 Feb 1980 08:00:00 GMT', 'Mon, 17 Feb 1980 17:00:00 GMT'])
    assert response.get_header('Date') == ['Sun, 16 Feb 1980 08:00:00 GMT', 'Mon, 17 Feb 1980 17:00:00 GMT']
    assert response.get_headers() == [('Date', 'Sun, 16 Feb 1980 08:00:00 GMT'),
                                      ('Date', 'Mon, 17 Feb 1980 17:00:00 GMT')]
    response.set_status('404 Not Found')
    response.set_body('Hi, there!')
    assert response.get_status() == '404 Not Found'
    assert response.get_body() == b'Hi, there!'


test_response()


def test_cookie_response():
    response = pyweb.Response()
    response.add_cookie('mykey', 'myvalue', ttl=None)
    cookie_header = response.get_cookie_output('mykey')
    assert cookie_header == r'Set-Cookie: mykey=myvalue; Path=/'

    # Ref: https://docs.python.org/3/library/http.cookies.html
    response.add_cookie('keebler', 'E=everybody; L="Loves"; fudge=\n;', ttl=None, httponly=True)
    cookie_header = response.get_cookie_output('keebler')
    assert cookie_header == r'Set-Cookie: keebler="E=everybody\073 L=\"Loves\"\073 fudge=\012\073"; HttpOnly; Path=/'

    response.add_cookie('cookie_with_ttl', 'myvalue', ttl=3600)
    cookie_header = response.get_cookie_output('cookie_with_ttl')
    assert re.match(r'^Set-Cookie: cookie_with_ttl=myvalue; expires=.+ GMT; Path=/$', cookie_header) is not None

    response.delete_cookie('tobedeletedkey')
    cookie_header = response.get_cookie_output('tobedeletedkey')
    assert cookie_header == 'Set-Cookie: tobedeletedkey=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Path=/'

    headers = response.get_headers()
    assert len(headers) == 4
    for (key, value) in headers:
        assert key == 'Set-Cookie'

    # format_cookie_date tests
    assert response.format_cookie_date(0) == 'Thu, 01-Jan-1970 00:00:00 GMT'
    # Ref: http://unixtimesta.mp/319536963
    assert response.format_cookie_date(319536963.0) == 'Sat, 16-Feb-1980 08:16:03 GMT'
    assert response.format_cookie_date(2147483648) == 'Tue, 19-Jan-2038 03:14:08 GMT'


test_cookie_response()

# JSON tests
assert json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}]) == '["foo", {"bar": ["baz", null, 1.0, 2]}]'


# DB tests
def test_db():
    log = pyweb.Log('test.log')
    db = pyweb.DB(log)
    assert db.connect(database='mytest', user='myuser', password='wrong_password', host='localhost') is False
    log.shutdown()
    contents = read_log('test.log')
    os.remove('test.log')
    assert contents == ['WARNING: DB connect error: FATAL:  password authentication failed for user "myuser"', '']
    assert 'password authentication failed for user "myuser"' in db.error_desc()

    quoted = pyweb.DB.escape(r"Hello World'; DROP DATABASE World;")
    assert quoted == r"'Hello World''; DROP DATABASE World;'"
    quoted = pyweb.DB.escape(r'`1230-=qwep[]\asdl;' + r"'" + r'zxcm,./~!@#$%^&*()_+QWEP{}|ASDL:"ZXCM<>?')
    assert quoted == r"'" + r'`1230-=qwep[]\\asdl;' + r"''" + r'zxcm,./~!@#$%^&*()_+QWEP{}|ASDL:"ZXCM<>?' + r"'"

    log = pyweb.Log()
    db = pyweb.DB(log)
    assert db.connect(database='mytest', user='myuser', password='Password1', host='localhost') is True
    rows = db.query('SELECT version()')
    assert rows is not False
    assert rows['num_rows'] == 1
    # Silence the traceback (traceback is using INFO level)
    log.set_level(log.WARNING)
    rows = db.query('SELECT versions()')
    log.set_level(log.DEBUG)
    assert rows is False
    assert db.error_code() == '42883'  # undefined_function
    assert 'function versions() does not exist' in db.error_desc()
    log.shutdown()

    log = pyweb.Log()
    db = pyweb.DB(log)
    assert db.connect(database='mytest', user='myuser', password='Password1', host='localhost') is True
    assert db.execute('DROP TABLE IF EXISTS RKArticles') is True
    assert db.execute('CREATE TABLE RKArticles ('
                      '        Id BIGSERIAL NOT NULL PRIMARY KEY'
                      '        , Name TEXT NOT NULL'
                      '        , Description TEXT NOT NULL'
                      '        , Pages INTEGER NOT NULL'
                      '        , Email CHARACTER VARYING(20) NOT NULL'
                      '        , DateAdded TIMESTAMP DEFAULT NULL'
                      '    )') is True

    sql = 'INSERT INTO RKArticles (Name, Description, Pages, Email, DateAdded) VALUES ({}, {}, {}, {}, {})'.format(
        db.escape('Kevin Haritmonds'), db.escape('The creator of pyweb'), db.escape('23'),
        db.escape('haritmonds@yahoo.com'), db.escape('now'))
    assert sql == r"INSERT INTO RKArticles (Name, Description, Pages, Email, DateAdded)" \
                  " VALUES ('Kevin Haritmonds', 'The creator of pyweb', '23', 'haritmonds@yahoo.com', 'now')"
    assert db.execute(sql) is True
    assert db.count_affected() == 1

    sql = 'INSERT INTO RKArticles (Name, Description, Pages, Email, DateAdded)' \
          ' VALUES (%s, %s, %s, %s, %s) RETURNING Id, Name'
    data = ('Shilvanna Litania', 'The younger sister of Kevin Haritmonds', 42, 'foulu_4@yahoo.com', 'now')
    returned_sql_data = db.query(sql, data)
    # returned_sql_data == {'row': {'id': 2, 'name': 'Shilvanna Litania'},
    # 'rows': [{'id': 2, 'name': 'Shilvanna Litania'}], 'num_rows': 1}
    assert returned_sql_data is not False
    assert db.count_affected() == 1
    assert returned_sql_data['num_rows'] == 1
    assert returned_sql_data['row'] == {'id': 2, 'name': 'Shilvanna Litania'}
    assert returned_sql_data['rows'][0] == {'id': 2, 'name': 'Shilvanna Litania'}

    sql = 'INSERT INTO RKArticles (Name, Description, Pages, Email, DateAdded) VALUES (%s, %s, %s, %s, %s)'
    data = ('Amanda Litania',
            'The older sister of Kevin Haritmonds ' + chr(233) + chr(0x0bf2) + chr(3972) + chr(6000) + chr(
                13231) + ' unicode rocks!', 7, 'alitani4@yahoo.com', 'now')
    assert db.execute(sql, data) is True
    assert db.count_affected() == 1

    sql = 'UPDATE RKArticles SET DateAdded=%s WHERE Id >= %s'
    data = ('now', 2)
    assert db.execute(sql, data) is True
    # This update affects two rows (Id of 2 and 3)
    assert db.count_affected() == 2

    articles = db.query('SELECT * FROM RKArticles')
    assert articles is not False
    assert db.count_affected() == 3
    assert articles['num_rows'] == 3
    assert articles['row']['id'] == 1
    assert articles['row']['name'] == 'Kevin Haritmonds'
    assert articles['row']['description'] == 'The creator of pyweb'
    assert articles['row']['pages'] == 23
    assert articles['row']['email'] == 'haritmonds@yahoo.com'
    assert len(articles['row']) == 6
    assert articles['rows'][0]['id'] == 1
    assert articles['rows'][0]['name'] == 'Kevin Haritmonds'
    assert articles['rows'][0]['description'] == 'The creator of pyweb'
    assert articles['rows'][0]['pages'] == 23
    assert articles['rows'][0]['email'] == 'haritmonds@yahoo.com'
    assert articles['rows'][1]['id'] == 2
    assert articles['rows'][1]['name'] == 'Shilvanna Litania'
    assert articles['rows'][1]['description'] == 'The younger sister of Kevin Haritmonds'
    assert articles['rows'][1]['pages'] == 42
    assert articles['rows'][1]['email'] == 'foulu_4@yahoo.com'
    assert articles['rows'][2]['id'] == 3
    assert articles['rows'][2]['name'] == 'Amanda Litania'
    assert articles['rows'][2]['description'] == 'The older sister of Kevin Haritmonds ' + chr(233) + chr(0x0bf2) + chr(
        3972) + chr(6000) + chr(13231) + ' unicode rocks!'
    assert articles['rows'][2]['pages'] == 7
    assert articles['rows'][2]['email'] == 'alitani4@yahoo.com'

    articles = db.query('SELECT * FROM RKArticles WHERE Id=-1')
    assert articles is not False
    assert articles['num_rows'] == 0
    assert articles['row'] == {}
    assert articles['rows'] == []

    sql = 'INSERT INTO RKArticles (Name) VALUES (%s)'
    data = ('Kevin Haritmonds',)
    log.set_level(log.WARNING)
    assert db.execute(sql, data) is False
    log.set_level(log.DEBUG)
    assert db.error_code() == '23502'  # not_null_violation
    assert 'null value in column "description" violates not-null constraint' in db.error_desc()
    # Ref: https://www.python.org/dev/peps/pep-0249/#rowcount
    assert db.count_affected() == -1

    assert db.execute('DROP TABLE RKArticles') is True
    log.shutdown()


test_db()


# Cache Tests
def test_cache():
    cache = pyweb.Cache(host='localhost')
    cache.set('test_key', 'test_value', 3600)
    assert cache.exists('test_key') is True
    assert cache.get('test_key') == 'test_value'
    assert 0 <= 3600 - cache.get_ttl('test_key') < 3
    cache.set('test_key', 'test_new_value', 14400)
    assert cache.get('test_key') == 'test_new_value'
    assert cache.rename('test_invalid_key', 'test_new_key') is False
    assert cache.rename('test_key', 'test_new_key') is True
    assert cache.get('test_key') is None
    assert cache.get('test_new_key') == 'test_new_value'
    assert cache.rename('test_new_key', 'test_key') is True
    assert cache.get('test_key') == 'test_new_value'
    assert cache.get('test_new_key') is None
    assert 0 <= 14400 - cache.get_ttl('test_key') < 3
    cache.set_ttl('test_key', 28800)
    assert 0 <= 28800 - cache.get_ttl('test_key') < 3
    # https://docs.python.org/3/howto/unicode.html
    unicode_str = 'these are unicode chars: ' + chr(233) + chr(0x0bf2) + chr(3972) + chr(6000) + chr(13231) + '!'
    cache.set('test_key', unicode_str, 14400)
    assert cache.get('test_key') == 'these are unicode chars: ' + chr(233) + chr(0x0bf2) + chr(3972) + chr(6000) + chr(
        13231) + '!'
    cache.set('test_key', 1980, 14400)
    assert cache.get('test_key') == 1980
    cache.set('test_key', 16.02, 14400)
    assert cache.get('test_key') == 16.02
    cache.set('test_key', True, 14400)
    assert cache.get('test_key') is True
    cache.set('test_key', False, 14400)
    assert cache.get('test_key') is False
    cache.set('test_key', None, 14400)
    assert cache.get('test_key') is None
    cache.set('test_key', (2, 3, 5, 7, 11, 13, 17), 14400)
    # Note that json encoding will transform tuple into list
    assert type(cache.get('test_key')) is list
    assert len(cache.get('test_key')) == 7
    assert cache.get('test_key') == [2, 3, 5, 7, 11, 13, 17]
    cache.set('test_key', {'Name': 'Kevin Haritmonds', 'Address': 'Pune, India'}, 14400)
    assert type(cache.get('test_key')) is dict
    assert len(cache.get('test_key')) == 2
    assert cache.get('test_key') == {'Address': 'Pune, India', 'Name': 'Kevin Haritmonds'}
    # Note that json encoding does not support "bytes" type
    cache.set('test_key',
              {'a': None, 'b': True, 'c': False, 'd': 1980, 'e': 16.02, 'f': 'this is string', 'g': [1, 2, 3],
               'h': (1, 2, 3, 4), 'i': {'Address': 'Pune, India', 'Name': 'Kevin Haritmonds'}}, 14400)
    assert type(cache.get('test_key')) is dict
    assert len(cache.get('test_key')) == 9
    assert cache.get('test_key') == {'a': None, 'b': True, 'c': False, 'd': 1980, 'e': 16.02, 'f': 'this is string',
                                     'g': [1, 2, 3], 'h': [1, 2, 3, 4],
                                     'i': {'Address': 'Pune, India', 'Name': 'Kevin Haritmonds'}}
    cache.delete('test_key')
    assert cache.get('test_key') is None
    assert cache.exists('test_key') is False


test_cache()


def test_session():
    # is_id_valid() static method
    assert pyweb.Session.is_id_valid(None) is False
    assert pyweb.Session.is_id_valid(True) is False
    assert pyweb.Session.is_id_valid('') is False
    assert pyweb.Session.is_id_valid('03c16eb0df39da917ac280e8a275c0cbe7c415efb14082b8ca2c0d775d1b35b4') is True
    assert pyweb.Session.is_id_valid(' 3c16eb0df39da917ac280e8a275c0cbe7c415efb14082b8ca2c0d775d1b35b4') is False
    assert pyweb.Session.is_id_valid('03c16eb0df39da917ac280e8a275c0cbe7c415egb14082b8ca2c0d775d1b35b4') is False
    assert pyweb.Session.is_id_valid('03c16eb0df39da917ac280e8a275c0cbe7c415efb14082b8ca2c0d775d1b35b40') is False
    assert pyweb.Session.is_id_valid('03c16eb0df39da917ac280e8a275c0cbe7c415efb14082b8ca2c0d775d1b35b') is False

    cache = pyweb.Cache(host='localhost')
    session1 = pyweb.Session(cache, None, ttl=14400)
    session2 = pyweb.Session(cache, None, ttl=14400)

    session_id1 = session1.get_id()
    session_id2 = session2.get_id()
    assert pyweb.Session.is_id_valid(session_id1) is True
    assert pyweb.Session.is_id_valid(session_id2) is True
    assert session_id1 != session_id2

    # Each session has its own data
    assert session1.get_vars() == {}
    assert session2.get_vars() == {}
    session1.set_vars({'Name': 'Kevin Haritmonds', 'Address': 'Pune, India'})
    session2.set_vars({'Name': 'Apple', 'Color': 'Red', 'Traits': ['Round', 'Has seed', 'Sweet'], 'Qty': 3})
    assert session1.get_vars() == {'Name': 'Kevin Haritmonds', 'Address': 'Pune, India'}
    assert session2.get_vars() == {'Name': 'Apple', 'Color': 'Red', 'Traits': ['Round', 'Has seed', 'Sweet'], 'Qty': 3}
    session1.set_vars({'Name': 'Tifa Litania'})
    session2.set_vars({'Name': 'Banana', 'Traits': ['Long', 'Seedless', 'Sweet'], 'Qty': 7})
    assert session1.get_vars() == {'Name': 'Tifa Litania'}
    assert session2.get_vars() == {'Name': 'Banana', 'Traits': ['Long', 'Seedless', 'Sweet'], 'Qty': 7}

    # Regenerate session id
    new_session_id1 = session1.regenerate_id()
    assert pyweb.Session.is_id_valid(new_session_id1) is True
    assert session1.get_id() == new_session_id1
    assert session_id1 != new_session_id1
    assert session1.get_vars() == {'Name': 'Tifa Litania'}
    session_id1 = new_session_id1

    # Load previous session
    session3 = pyweb.Session(cache, session_id2, ttl=14400)
    assert session3.get_vars() == {'Name': 'Banana', 'Traits': ['Long', 'Seedless', 'Sweet'], 'Qty': 7}

    # Creating a new session should not store anything. Storing into session must be explicit using session.set_vars().
    session4 = pyweb.Session(cache, None, ttl=14400)
    session4_storage_name = pyweb.Session.get_storagename(session4.get_id())
    print("Session's stored name: {}".format(session4_storage_name))
    assert cache.exists(session4_storage_name) is False

    # Invalidate a session that has never been used should not give error
    session5 = pyweb.Session(cache, None, ttl=14400)
    session5.invalidate()
    session5.invalidate()

    # Remove sessions
    session1.invalidate()
    session2.invalidate()
    session3.invalidate()
    session4.invalidate()
    removed_session = pyweb.Session(cache, session_id1, ttl=14400)
    assert removed_session.get_vars() == {}
    removed_session.invalidate()
    removed_session = pyweb.Session(cache, session_id2, ttl=14400)
    assert removed_session.get_vars() == {}
    removed_session.invalidate()


test_session()

print('All tests passed.')
