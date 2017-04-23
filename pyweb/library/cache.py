import json
import redis


class Cache:
    """ Cache mechanism that is able to store a value for a particular key for a given period of time """

    def __init__(self, host, port=6379):
        self._redis = redis.Redis(host=host, port=port)

    def set(self, key, value, ttl):
        """
        Set the value of a key that expires in "ttl" seconds
        :param key: the name of the cache
        :param value: the value of the cache
        :param ttl: the lifetime of the cache (in seconds)
        """
        # Ref: https://redis-py.readthedocs.org/en/latest/
        assert type(key) is str
        assert type(ttl) is int
        assert value is None or isinstance(value, (bool, int, float, str, list, tuple, dict))

        # Notes about json encoding:
        #    - It will transform tuple into list
        #    - It does not support "bytes" type
        #    - Unicode will be converted as ascii (example: \u00e9)
        value_in_json = json.dumps(value)

        # Redis will store the data as "bytes" type
        self._redis.setex(key, value_in_json, ttl)

    def get(self, key):
        """
        Return the value of a key
        :param key: the name of the cache
        :return: the value of cache, or None if the key doesn't exist
        """
        assert type(key) is str
        value_in_json_bytes = self._redis.get(key)
        if value_in_json_bytes is None:
            return None
        value_in_json = value_in_json_bytes.decode('ascii')
        value = json.loads(value_in_json)
        return value

    def rename(self, old_key, new_key):
        """
        Rename the cache
        :param old_key: old name
        :param new_key: new name
        :return: false if the old name doesn't exist
        """
        assert type(old_key) is str
        assert type(new_key) is str
        try:
            self._redis.rename(old_key, new_key)
            return True
        except redis.exceptions.ResponseError:
            return False

    def exists(self, key):
        """
        Returns a boolean indicating whether a key exists
        :param key: the name of the cache
        :return: true of the cache exists
        """
        assert type(key) is str
        return self._redis.exists(key)

    def set_ttl(self, key, ttl):
        """
        Set an expire flag on a key for "ttl" seconds
        :param key: the name of the cache
        :param ttl: the lifetime of the cache (in seconds)
        """
        assert type(key) is str
        assert type(ttl) is int
        self._redis.expire(key, ttl)

    def get_ttl(self, key):
        """
        Returns the number of seconds until the key will expire (ttl)
        :param key: the name of the cache
        :return: the lifetime of the cache (in seconds)
        """
        return self._redis.ttl(key)

    def delete(self, key):
        """
        Delete a key
        :param key: the name of the cache
        """
        assert type(key) is str
        self._redis.delete(key)
