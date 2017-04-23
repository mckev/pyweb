import html
import http.cookies
import time


class Response:
    """ Handle HTTP output """

    def __init__(self):
        # Ref: http://legacy.python.org/dev/peps/pep-3333/
        # HTTP status code: http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        self._status = '200 OK'
        self._headers = {}
        self._body = 'Hello, world!'
        self._cookie = http.cookies.SimpleCookie()

    @staticmethod
    def escape(s):
        assert type(s) is str
        return html.escape(s, True)

    def set_status(self, status):
        assert type(status) is str
        self._status = status

    def get_status(self):
        return self._status

    def set_header(self, key, value):
        # Note that "value" could also be a list or a tuple
        assert type(key) is str
        assert type(value) is str or type(value) is list or type(value) is tuple
        self._headers[key] = value

    def get_header(self, key):
        assert type(key) is str
        return self._headers.get(key, None)

    def get_headers(self):
        headers = []
        # Output headers
        for (key, vals) in self._headers.items():
            if type(vals) is list or type(vals) is tuple:
                # Case where "vals" is a list or a tuple
                for val in vals:
                    headers.append((key, val))
            else:
                headers.append((key, vals))
        # Output cookies
        for key in self._cookie:
            headers.append(('Set-Cookie', self._cookie[key].output(header='')))
        return headers

    def set_body(self, body):
        self._body = body

    def get_body(self, encoding='utf-8'):
        assert type(encoding) is str
        return bytes(self._body, encoding)

    @staticmethod
    def format_cookie_date(epoch):
        """
        Format the time to ensure compatibility with cookie.
        :param epoch: seconds since the epoch. All times in UTC.
        """
        # Ref:
        #    http://pymotw.com/2/Cookie/
        #    Werkzeug-0.9.6/werkzeug/http.py
        # Format: 'Wdy, DD-Mon-YYYY HH:MM:SS GMT'.
        assert type(epoch) is int or type(epoch) is float
        d = time.gmtime(epoch)
        return time.strftime('%a, %d-%b-%Y %H:%M:%S GMT', d)

    def add_cookie(self, key, value, ttl, path='/', httponly=False):
        """
        Add a cookie which expires in "ttl" seconds
        :param key: the name of the cookie
        :param value: the value of the cookie
        :param ttl: cookie expiration time in seconds. Set ttl to None to set the cookie valid until the browser closes.
        :param path: tell the browser what path the cookie belongs to
        :param httponly: boolean which specifies that the cookie is only transferred in http requests,
                         and is not accessible through javascript
        """
        # Output sample: Set-Cookie: mykey=myvalue; expires=Tue, 30-Dec-2014 15:22:31 GMT; httponly; Path=/
        assert type(key) is str
        assert type(value) is str
        assert ttl is None or type(ttl) is int
        assert type(path) is str
        assert type(httponly) is bool
        self._cookie[key] = value
        if ttl is not None:
            # Ref: http://mrcoles.com/blog/cookies-max-age-vs-expires/
            # "If you care about your cookies functioning properly for a huge percentage of web users (65.66%),
            # don’t persist your cookies "the right way" according to spec (max-age),
            # persist them the way that works (expires)."
            self._cookie[key]['expires'] = Response.format_cookie_date(time.time() + ttl)
        self._cookie[key]['path'] = path
        if httponly:
            self._cookie[key]['httponly'] = True

    def delete_cookie(self, key, path='/'):
        # Output sample: Set-Cookie: mykey=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Path=/
        assert type(key) is str
        assert type(path) is str
        self._cookie[key] = 'deleted'
        self._cookie[key]['expires'] = Response.format_cookie_date(1)
        self._cookie[key]['path'] = path

    def get_cookie_output(self, key):
        assert type(key) is str
        if key in self._cookie:
            return self._cookie[key].output()
        else:
            return None
