import pyweb


class WebController(pyweb.Controller):
    def index(self, environ, start_response):
        registry = self.registry
        response = registry.response
        # Response
        response.set_status('404 Not Found')
        response.set_header('Content-Type', 'text/plain')
        response.set_body('Not Found')
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]
