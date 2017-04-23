import http.cookies
import urllib.parse


class Request:
    """ Handle HTTP input """

    def __init__(self, environ):
        self._environ = environ

    def get_var(self, key):
        """
        Return GET value as string
        :param key: the name of the get variable
        :return: the value of the get variable, or None if the variable doesn't exist
        """
        # Ref:
        #    http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/webob.html :
        #       Sometimes returning a string, and sometimes returning a list, is the cause of frequent exceptions.
        #    http://unixpapa.com/js/querystring.html :
        #       A query string can contain multiple values for the same key. This is the normal result from
        #       form elements like multiple selects.
        assert type(key) is str
        if not hasattr(self, '_get_vars'):
            self._get_vars = {key: value for (key, value) in
                              urllib.parse.parse_qsl(self._environ.get('QUERY_STRING', ''))}
        # Note: If a query string contains multiple values for the same key (e.g. in the case of multiple selects),
        #       you'll only get the last one. Use "get_var_as_list ()" in the case of the key contains multiple values.
        return self._get_vars.get(key, None)

    def get_var_as_list(self, key):
        """
        Return GET value as list
        :param key: the name of the get variable
        :return: the value of the get variable as list, or None if the variable doesn't exist
        """
        assert type(key) is str
        if not hasattr(self, '_get_vars_as_list'):
            self._get_vars_as_list = urllib.parse.parse_qs(self._environ.get('QUERY_STRING', ''))
        return self._get_vars_as_list.get(key, None)

    def _read_content_data(self):
        """ Read all POST variables """
        # Ref:
        #    http://webpython.codepoint.net/wsgi_request_parsing_post
        #    http://stackoverflow.com/questions/1783383/how-do-i-copy-wsgi-input-if-i-want-to-process-post-data-more-than-once
        if hasattr(self, '_content_data'):
            return
        try:
            content_length = int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            content_length = 0
        if content_length == 0:
            self._content_data = None
        else:
            self._content_data = self._environ['wsgi.input'].read(content_length)

    def post_raw(self):
        """
        Return POST data as raw (binary)
        :return: raw post data
        """
        if not hasattr(self, '_content_data'):
            self._read_content_data()
        return self._content_data

    def post_var(self, key):
        """
        Return POST value as string
        :param key: the name of the post variable
        :return: the value of the post variable, or None if the variable doesn't exist
        """
        assert type(key) is str
        if not hasattr(self, '_post_vars'):
            if not hasattr(self, '_content_data'):
                self._read_content_data()
            self._post_vars = {key: value for (key, value) in urllib.parse.parse_qsl(self._content_data)}
        # Note: If a query string contains multiple values for the same key (e.g. in the case of multiple selects),
        # you'll only get the last one.
        return self._post_vars.get(key, None)

    def post_var_as_list(self, key):
        """
        Return POST value as list
        :param key: the name of the post variable
        :return: the value of the post variable as list, or None if the variable doesn't exist
        """
        assert type(key) is str
        if not hasattr(self, '_post_vars_as_list'):
            if not hasattr(self, '_content_data'):
                self._read_content_data()
            self._post_vars_as_list = urllib.parse.parse_qs(self._content_data)
        return self._post_vars_as_list.get(key, None)

    def cookie_var(self, key):
        """
        Return COOKIE value as string
        :param key: the name of the cookie variable
        :return: the value of the cookie variable, or None if the variable doesn't exist
        """
        assert type(key) is str
        if not hasattr(self, '_cookie_vars'):
            # Parse Cookies variables
            self._cookie_vars = http.cookies.SimpleCookie()
            self._cookie_vars.load(self._environ.get('HTTP_COOKIE', ''))
        if key in self._cookie_vars:
            return self._cookie_vars[key].value
        else:
            return None
