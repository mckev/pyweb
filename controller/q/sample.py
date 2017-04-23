import model.user
import pyweb


class WebController(pyweb.Controller):
    def index(self, environ, start_response):
        registry = self.registry
        request = registry.request
        response = registry.response
        view = registry.view
        # Extended URL
        # Example:
        # http://192.168.10.163:9090/q/tests/url/johny?q=abc
        #    REQUEST_METHOD: GET
        #    PATH_INFO: /q/tests/url/johny
        #    _PATH_INFO_MATCHED: /q/tests/url
        #    _PATH_INFO_EXTENDED: /johny
        #    QUERY_STRING: q=abc
        print('environ["REQUEST_METHOD"]: {}'.format(environ['REQUEST_METHOD']))
        print('environ["PATH_INFO"]: {}'.format(environ['PATH_INFO']))
        print('environ["_PATH_INFO_MATCHED"]: {}'.format(environ['_PATH_INFO_MATCHED']))
        print('environ["_PATH_INFO_EXTENDED"]: {}'.format(environ['_PATH_INFO_EXTENDED']))
        print('environ["QUERY_STRING"]: {}'.format(environ.get('QUERY_STRING', '')))
        print('post (raw): {}'.format(request.post_raw()))
        # Model
        user = model.user.User(registry)
        # Data
        data = {
            'title': 'Welcome to pyweb!'
        }
        # Response
        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        body = view.view('view/sample.view', data)
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]
