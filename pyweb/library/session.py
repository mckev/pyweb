import hashlib
import os
import string
import time


class Session:
    """ Manage user session """

    # Tips:
    #    - Protecting cookie should be taken as the same priority as protecting password.
    #      Knowing a user's cookie would make you able to log in as that user.
    #    - Do not pass session id through URL. It's not good because user might send the url that contains his
    #      session id by mistake, and it's bad for search engine optimization (SEO).
    #    - Prevent accessing document.cookie from JavaScript by sending "httponly" cookie.
    #      Ref: http://www.codinghorror.com/blog/2008/08/protecting-your-cookies-httponly.html
    #    - Prevent XSRF (cross-site request forgery) by putting something else other than session id required to do
    #      sensitive transactions. XSRF works by a malicious website constructs request to make the user
    #      perform actions (unknowingly) on our website.
    #      Ref: http://www.codinghorror.com/blog/2008/10/preventing-csrf-and-xsrf-attacks.html
    #    - Prevent sniffing of cookie message in the network by always using HTTPS protocol.
    #      Ref: http://www.codinghorror.com/blog/2012/02/should-all-web-traffic-be-encrypted.html

    @staticmethod
    def is_id_valid(session_id):
        """
        Verify if the syntax of session id is valid
        :param session_id: session id
        :return: true if the format of the session id is valid
        """
        # Make sure it's a string
        if type(session_id) is not str:
            return False

        # Make sure the session id is 256 bits = 32 bytes = 64 bytes (in hexadecimal)
        if len(session_id) != 64:
            return False

        # Make sure session id only contains valid characters 0-9, A-f, a-f
        # Ref: http://stackoverflow.com/questions/11592261/check-if-string-is-hexadecimal
        hexdigits = set(string.hexdigits)
        return all(c in hexdigits for c in session_id)

    @staticmethod
    def get_storagename(session_id):
        # Example: 'sessid:83c16eb0df39da917ac280e8a275c0cbe7c415efb14082b8ca2c0d775d1b35b4'
        assert Session.is_id_valid(session_id) is True
        return 'sessid:{}'.format(session_id)

    def __init__(self, cache, session_id, ttl):
        """ Initialize user session. Will generate a new session id if session id is None. """
        # session id is in hexadecimal
        assert session_id is None or type(session_id) is str
        assert type(ttl) is int
        self._cache = cache
        self._ttl = ttl
        if session_id is None:
            # Generate a new session
            self._id = Session._generate_id()
        else:
            # Load existing session
            self._id = session_id
        assert Session.is_id_valid(self._id) is True

    def get_id(self):
        """ Return the session id """
        assert Session.is_id_valid(self._id) is True
        return self._id

    def regenerate_id(self):
        """ Regenerate (and rename) the current session id. Returns the new id """
        assert Session.is_id_valid(self._id) is True
        old_id = self._id
        new_id = Session._generate_id()
        assert self._cache.rename(Session.get_storagename(old_id), Session.get_storagename(new_id)) is True
        self._id = new_id
        assert Session.is_id_valid(self._id) is True
        return new_id

    def get_vars(self):
        """ Retrieve user's session data """
        data = self._read_session()
        assert type(data) is dict
        return data

    def set_vars(self, data):
        """
        Overwrite user's session data with a new one
        :param data: session data
        """
        assert type(data) is dict
        self._write_session(data)

    def invalidate(self):
        """ Delete existing user session """
        self._delete_session()

    @staticmethod
    def _generate_id():
        """ Private method to generate 256-bit random hexadecimal """
        # Ref: Werkzeug-0.9.6/werkzeug/contrib/sessions.py
        randombytes = b''.join([str(time.perf_counter()).encode('ascii'), os.urandom(32)])
        return hashlib.sha256(randombytes).hexdigest()

    def _read_session(self):
        """ Private method to return a dictionary containing user's session data. """
        # Uses cache mechanism in the back-end
        assert type(self._ttl) is int
        storagename = Session.get_storagename(self.get_id())
        data = self._cache.get(storagename)
        if data is None:
            # There is a possibility that the session has expired or does not exist
            data = {}
        else:
            # Refresh the ttl
            self._cache.set_ttl(storagename, self._ttl)
        assert type(data) is dict
        return data

    def _write_session(self, data):
        """ Private method to write user's session data. Uses cache mechanism in the back-end. """
        assert type(self._ttl) is int
        assert type(data) is dict
        storagename = Session.get_storagename(self.get_id())
        self._cache.set(storagename, data, self._ttl)

    def _delete_session(self):
        """ Private method to delete user's session data. Uses cache mechanism in the back-end. """
        storagename = Session.get_storagename(self.get_id())
        self._cache.delete(storagename)
