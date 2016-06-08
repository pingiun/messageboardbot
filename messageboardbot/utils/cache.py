import time

class Cache(object):
    def __init__(self):
        self.cachedict = {}

    def get(self, key, timeout=600):
        value = self.cachedict.get(key, None)
        if value:
            if value[0] + timeout > time.time():
                return value[1]
        return None

    def put(self, key, value):
        self.cachedict[key] = [time.time(), value]