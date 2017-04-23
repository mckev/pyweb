import pyweb


class WebController(pyweb.Controller):
    def index(self, environ, start_response):
        # How to test:
        #    - Open 3 browser windows:
        #         http://192.168.10.163:9090/q/tests/db_concurrent01
        #         http://192.168.10.163:9090/q/tests/db_concurrent02
        #         http://192.168.10.163:9090/q/tests/db_concurrent03
        #    - The output must be shown in 10 seconds, and not 30 seconds.
        registry = self.registry
        db = registry.db
        response = registry.response

        db.execute('SELECT pg_sleep (10)')
        db_version = db.query('SELECT version()')

        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        body = 'db version: {}'.format(db_version)
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]
