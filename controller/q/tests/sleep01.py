import pyweb
import time


class WebController(pyweb.Controller):
    def index(self, environ, start_response):
        # How to test:
        #    - Open 3 browser windows:
        #         http://192.168.10.163:9090/q/tests/sleep01
        #         http://192.168.10.163:9090/q/tests/sleep02
        #         http://192.168.10.163:9090/q/tests/sleep03
        #    - The output must be shown in 10 seconds, and not 30 seconds.
        registry = self.registry
        response = registry.response

        time.sleep(10)

        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        body = 'Has just slept for 10 seconds'
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]
