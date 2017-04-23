def get_int(val, default=None):
    assert default is None or type(default) is int
    try:
        return int(val)
    except ValueError:
        return default
    except TypeError:
        # When val is None, list, tuple, set, dict, etc.
        return default
