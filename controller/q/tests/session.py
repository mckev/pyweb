import pyweb
import re


class WebController(pyweb.Controller):
    def test_page_one(self):
        # Required behaviours:
        #    - Browser (client) doesn't send sessid cookie.
        #    - Server tells browser (client) to set a new sessid cookie. It always gives a unique session id.
        #    - Nothing is in session.
        registry = self.registry
        request = registry.request
        response = registry.response
        session = registry.session
        start_response = registry.start_response
        body = '<html><body>'
        body += 'Session Id: {}<br />'.format(session.get_id())
        # Verify that browser (client) doesn't send sessid cookie
        assert request.cookie_var('sessid') is None
        # Verify that server tells browser (client) to set a new sessid cookie
        session_cookie = response.get_cookie_output('sessid')
        print(session_cookie)
        assert re.match(r'^Set-Cookie: sessid=[0-9a-f]+;.* Path=/$', session_cookie) is not None
        # Verify that nothing is in session
        session_vars = session.get_vars()
        assert len(session_vars) == 0
        session.set_vars({
            'name': 'Kevin Haritmonds',
            'address': '5599 San Felipe'
        })
        body += 'Click <a href="/q/tests/session?page=two">here</a> to continue testing...'
        body += '</body></html>'
        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]

    def test_page_two(self):
        # Required behaviours:
        #    - Browser (client) sends sessid cookie.
        #    - Server doesn't send sessid cookie!!
        #    - Browser (client) cannot access document.cookie from javascript (httponly)
        registry = self.registry
        request = registry.request
        response = registry.response
        session = registry.session
        start_response = registry.start_response
        body = '<html><body>'
        # Verify that browser (client) sends sessid cookie
        assert request.cookie_var('sessid') is not None
        # Verify that server doesn't send any sessid cookie
        assert response.get_cookie_output('sessid') is None
        # Verify session
        session_vars = session.get_vars()
        body += 'Name: {}<br />'.format(session_vars.get('name', '(None)'))
        body += 'Address: {}<br />'.format(session_vars.get('address', '(None)'))
        assert len(session_vars) == 2
        assert session_vars['name'] == 'Kevin Haritmonds'
        assert session_vars['address'] == '5599 San Felipe'
        session.set_vars({
            'name': 'Kevin Haritmonds Cool',  # Test replacement of a session variable
            # Test deletion of a session variable
            'birthdate': 16,  # Test adding a session variable
            'is_correct': True  # Test adding another session variable
        })
        # Verify httponly
        body += 'Test httponly feature...<br />'
        body += '<script>if (document.cookie !== "") {'
        body += 'alert("Should not be able to display cookie information here: " + document.cookie);'
        body += '}</script>'
        body += 'Click <a href="/q/tests/session?page=three">here</a> to continue testing...'
        body += '</body></html>'
        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]

    def test_page_three(self):
        # Required behaviours:
        #    - Browser (client) sends sessid cookie.
        #    - Server sends sessid cookie: sessid=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Path=/
        registry = self.registry
        request = registry.request
        response = registry.response
        session = registry.session
        start_response = registry.start_response
        body = '<html><body>'
        # Verify that browser (client) sends sessid cookie
        assert request.cookie_var('sessid') is not None
        # Verify session
        session_vars = session.get_vars()
        body += 'Name: {}<br />'.format(session_vars['name'])
        body += 'Birthdate: {}<br />'.format(session_vars['birthdate'])
        body += 'Is_Correct: {}<br />'.format(session_vars['is_correct'])
        assert len(session_vars) == 3
        assert session_vars['name'] == 'Kevin Haritmonds Cool'
        assert session_vars['birthdate'] == 16
        assert session_vars['is_correct'] == True
        # Test destroying session
        session.invalidate()
        response.delete_cookie('sessid')
        # Verify that server sends sessid cookie to delete it
        assert response.get_cookie_output(
            'sessid') == 'Set-Cookie: sessid=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Path=/'
        body += 'Click <a href="/q/tests/session?page=one">here</a> to start from beginning...'
        body += '</body></html>'
        response.set_status('200 OK')
        response.set_header('Content-Type', 'text/html')
        response.set_body(body)
        start_response(response.get_status(), response.get_headers())
        return [response.get_body()]

    def index(self, environ, start_response):
        # How to test:
        #    1. Close your browser. This forces session cookie (if exists) to be cleared.
        #    2. Browse to: http://192.168.10.163:9090/q/tests/session
        registry = self.registry
        request = registry.request
        registry.environ = environ
        registry.start_response = start_response
        if request.get_var('page') == 'one':
            return self.test_page_one()
        elif request.get_var('page') == 'two':
            return self.test_page_two()
        elif request.get_var('page') == 'three':
            return self.test_page_three()
        else:
            return self.test_page_one()
