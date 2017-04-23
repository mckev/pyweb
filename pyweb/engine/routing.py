import importlib
import os
import re


class Routing:
    """
    URL Dispatch mechanism
    Every .py files in "controller" directory and its sub-directory is accessible and can be called directly by client.
    Note that only one routing object exists for all client connections!
    """

    def __init__(self):
        # Ref: http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/

        # Scan "controller" directory and its sub-directories and import all controller files
        print('Scanning controller directory:')

        # _controllers stores the information of all controller files. Each controller file has the following:
        #    - data['regex']: Path pattern
        #      It also accept the optional slash followed with any characters (/.*) to specify _PATH_INFO_EXTENDED,
        #      for example "controller/user.py" controller file will be responsible to process the following
        #      url: http://192.168.10.163:9090/user/johny/profile
        #      In this case:
        #         environ['_PATH_INFO_MATCHED']: /user
        #         environ['_PATH_INFO_EXTENDED']: /johny/profile
        #    - data['pymodule']: Compiled code of controller file
        self._controllers = []

        # Ref: https://docs.python.org/3/library/os.html#os.walk
        for (root, dirs, files) in os.walk('controller', topdown=True, followlinks=False):
            for file in files:
                if file[-3:] == '.py':
                    data = {}

                    # endpoint is the physical Python file
                    endpoint = root + os.sep + file

                    # weburl is the HTTP path accessible by all users
                    weburl = root[len('controller'):] + os.sep + file[:-3]
                    if os.sep != '/':
                        # Non-POSIX OS such as Windows
                        weburl = weburl.replace(os.sep, '/')
                    print('   {} => {}'.format(weburl, endpoint))

                    # regex is the compiled regular expression to match weburl
                    data['regex'] = re.compile(r'^({0})(/.*)?$'.format(re.escape(weburl)))

                    # pymodulename is a dot-separated python module name
                    pymodulename = endpoint[:-3].replace(os.sep, '.')
                    print('   import {}'.format(pymodulename))
                    data['pymodule'] = importlib.import_module(pymodulename)

                    # Each controller must have "WebController" class
                    assert hasattr(data['pymodule'], 'WebController') == True

                    # Store in _controllers list
                    self._controllers.append(data)

    def route(self, path, registry, environ, start_response):
        log = registry.log

        if path == '/' or path == '' or path is None:
            path = '/index'

        no = None
        for (i, data) in enumerate(self._controllers):
            m = data['regex'].match(path)
            if m:
                no = i
                environ['_PATH_INFO_MATCHED'] = m.group(1)
                environ['_PATH_INFO_EXTENDED'] = m.group(2)  # could be: None
                break

        if no is None:
            # Path was not found
            log.log('Unable to find path: {0}'.format(path), log.WARNING)
            return self.route('/errors/404', registry, environ, start_response)
        else:
            # Path found
            webcontroller = self._controllers[no]['pymodule'].WebController(registry)
            return webcontroller.index(environ, start_response)
