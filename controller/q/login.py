import pyweb


class WebController(pyweb.Controller):
    def index(self, environ, start_response):
        registry = self.registry
        request = registry.request
        response = registry.response
        view = registry.view
        # Extended URL
        print('environ["REQUEST_METHOD"]: {}'.format(environ['REQUEST_METHOD']))
        print('environ["PATH_INFO"]: {}'.format(environ['PATH_INFO']))
        print('environ["_PATH_INFO_MATCHED"]: {}'.format(environ['_PATH_INFO_MATCHED']))
        print('environ["_PATH_INFO_EXTENDED"]: {}'.format(environ['_PATH_INFO_EXTENDED']))
        print('environ["QUERY_STRING"]: {}'.format(environ.get('QUERY_STRING', '')))
        print('post (raw): {}'.format(request.post_raw()))
        # Model
        # Data
        data = {
            'title': 'Welcome to pyweb!',
            'script_root': '..'
        }
        # Response
        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        body = view.view('view/login.view', data)
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]
