import pyweb


class WebController(pyweb.Controller):
    def index(self, environ, start_response):
        registry = self.registry
        response = registry.response
        # Extended URL
        # Example:
        # http://192.168.10.163:9090/q/tests/url/johny?q=abc
        #    REQUEST_METHOD: GET
        #    PATH_INFO: /q/tests/url/johny
        #    _PATH_INFO_MATCHED: /q/tests/url
        #    _PATH_INFO_EXTENDED: /johny
        #    QUERY_STRING: q=abc
        # Response
        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        body = 'REQUEST_METHOD: {}. PATH_INFO: {}. _PATH_INFO_MATCHED: {}. _PATH_INFO_EXTENDED: {}. QUERY_STRING: {}.' \
            .format(environ['REQUEST_METHOD'], environ['PATH_INFO'], environ['_PATH_INFO_MATCHED'],
                    environ['_PATH_INFO_EXTENDED'], environ.get('QUERY_STRING', ''))
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]
