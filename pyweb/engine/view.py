import contextlib
import io
import os
import re


class View:
    """
    Class to generate dynamic view
    We are using PHP-style <?py ... ?> to insert Python codes in between HTML.
    Note that this object lives for a long time because it stores the view templates that have been compiled.
    """

    def __init__(self):
        # Scan "view" directory and its sub-directories, and compile all view files into Python code
        print('Scanning view directory:')

        # _objects stores the compiled code of all view files.
        self._objects = {}

        for (root, dirs, files) in os.walk('view', topdown=True, followlinks=False):
            for file in files:
                if file[-5:] == '.view':
                    path = root + os.sep + file
                    print('   {}'.format(path))
                    # Convert the dynamic view template into Python code
                    code = View._convert_template_into_py(path)
                    # Compile the code
                    obj = compile(code, '<string>', 'exec')
                    # Store in _objects dict
                    self._objects[path] = obj

    @staticmethod
    def _convert_template_into_py(path):
        """ Convert a view template into Python code """
        assert type(path) is str

        # Read the view template
        with open(path, 'rt') as in_file:
            template = in_file.read()

        # Detect the start and end of Python code: <?py ... ?>
        chunks = re.split(r'<\?py\s+(.*?)\s*\?>', template, flags=re.DOTALL)
        # print ('Chunks: ' + str (chunks))

        # Replace the non-code portion into: print (r''' <non-code portion> ''', end='')
        # Non-code portion is at element 0, 2, 4, 6, 8, ...
        for i in range(0, len(chunks), 2):
            chunks[i] = "print (r'''" + chunks[i] + "''', end='')\n"

        # Add newline to the code portion
        # Code portion is at element 1, 3, 5, 7, 9, ...
        for i in range(1, len(chunks), 2):
            chunks[i] += '\n'

        code = ''.join(chunks)
        assert type(code) is str
        return code

    def view(self, path, data):
        """
        Return HTML string from a view template given data as input
        :param path: path to the .view file
        :param data: variables that are accessible from the .view file
        :return: stdout of the .view file execution
        """
        assert type(path) is str
        assert type(data) is dict

        # Verify that we have previously had this view template compiled
        assert path in self._objects
        obj = self._objects[path]

        # Execute the object with data as input. Redirect all STDOUT into buf.
        # Ref: https://docs.python.org/3.4/library/contextlib.html#contextlib.redirect_stdout
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(obj, None, data)
        html = buf.getvalue()

        assert type(html) is str
        return html
