import psycopg2
import psycopg2.extensions
import psycopg2.extras
import time


class DB:
    """ Database connection """

    def __init__(self, log):
        self._log = log
        self._error_code = None
        self._error_desc = None

    def connect(self, database, user, password, host, port=5432):
        """
        Connect with a new database connection
        :param database: the database name
        :param user: username used to authenticate
        :param password: password used to authenticate
        :param host: database host address
        :param port: connection port number (defaults to 5432 if not provided)
        :return: true if operation is successful
        """
        # Ref: https://wiki.python.org/moin/UsingDbApiWithPostgres
        assert type(database) is str
        assert type(user) is str
        assert type(password) is str
        assert type(host) is str
        assert type(port) is int

        # Connect to database
        try:
            self._db = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
            self._db.autocommit = True
        except psycopg2.Error as e:
            # http://www.postgresql.org/docs/current/static/errcodes-appendix.html
            self._error_code = '08006'
            self._error_desc = str(e)
            self._log.log('DB connect error: {}'.format(e), self._log.WARNING)
            return False

        self._cursor = self._db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return True

    def connect_from_pool(self, dbpool):
        """
        Connect with a given database pool connection.
        :param dbpool: postgresql database pool
        """

        # Get one database connection from database pool
        self._db = dbpool.getconn()
        self._db.autocommit = True
        while self.verify_database() is False:
            # Connection failed. Probably due to postgresql database is restarted.
            # Put it back to the pool and request a new one. Magically psycopg2 will recover it.
            dbpool.putconn(self._db)
            time.sleep(0.1)
            self._db = dbpool.getconn()
            self._db.autocommit = True

        self._dbpool = dbpool
        self._cursor = self._db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return True

    def verify_database(self):
        """ Verify database connection """
        # Refs:
        #   https://code.djangoproject.com/attachment/ticket/11798/base.py
        #   http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html on "Disconnect Handling - Pessimistic"
        assert hasattr(self, '_db') is True
        with self._db.cursor() as cursor:
            try:
                cursor.execute('SELECT 1')
                return True
            except psycopg2.Error as e:
                # If database is restarted, then it gives the following error:
                # "DB Pool connect error: terminating connection due to administrator command. server closed
                # the connection unexpectedly. This probably means the server terminated abnormally before
                # or while processing the request."
                self._error_code = '08006'
                self._error_desc = str(e)
                self._log.log('DB verify_database error: {}'.format(e), self._log.WARNING)
                return False

    @staticmethod
    def escape(value):
        """
        Escape the SQL data so that it is safe to use in query string. Please use prepared statement instead.
        :param value: the string value to be quoted
        """
        assert type(value) is str
        # psycopg2.extensions.adapt returns <class 'psycopg2._psycopg.QuotedString'> type, so we need to convert it
        # back to normal string. It works by replacing ' with '', replacing \ with \\, and add leading and
        # trailing single quotes.
        return str(psycopg2.extensions.adapt(value))

    def query(self, sql, data=None):
        """
        Query to database and expecting a returned data, for example: SELECT
        :param sql: sql query string
        :param data: sequence of data that are bound to variables in the operation
        :return: query result
        """
        assert type(sql) is str
        assert data is None or type(data) is list or type(data) is tuple
        assert hasattr(self, '_cursor') is True
        try:
            result = {}
            # Important note: Use "data" or escape all input to prevent SQL injection!
            self._cursor.execute(sql, data)
            result['rows'] = self._cursor.fetchall()
            result['num_rows'] = len(result['rows'])
            result['row'] = result['rows'][0] if result['num_rows'] > 0 else {}
            return result
        except psycopg2.Error as e:
            self._error_code = e.pgcode
            self._error_desc = e.pgerror
            self._log.log('DB query error: {}'.format(e), self._log.WARNING, print_stack=True)
            return False

    def execute(self, sql, data=None):
        """
        Query to database but not expecting any returned data, for example: INSERT, UPDATE, DELETE
        :param sql: sql query string
        :param data: sequence of data that are bound to variables in the operation
        :return: true if operation is successful
        """
        assert type(sql) is str
        assert data is None or type(data) is list or type(data) is tuple
        assert hasattr(self, '_cursor') is True
        try:
            # Important note: Use "data" or escape all input to prevent SQL injection!
            self._cursor.execute(sql, data)
            return True
        except psycopg2.Error as e:
            self._error_code = e.pgcode
            self._error_desc = e.pgerror
            self._log.log('DB execute error: {}'.format(e), self._log.WARNING, print_stack=True)
            return False

    def count_affected(self):
        """ Count how many rows are affected by the last query """
        assert hasattr(self, '_cursor') is True
        return self._cursor.rowcount

    def error_code(self):
        """ Get the error code of the last error """
        return self._error_code

    def error_desc(self):
        """ Get the error description of the last error """
        return self._error_desc

    def __del__(self):
        """ Close cursor and database connection upon object destroy """
        if hasattr(self, '_cursor'):
            self._cursor.close()
        if hasattr(self, '_dbpool'):
            if hasattr(self, '_db'):
                # Release back database connection into database pool. Do not ever close() this database connection
                # since it belongs to the database pool
                self._dbpool.putconn(self._db)
        else:
            if hasattr(self, '_db'):
                self._db.close()
