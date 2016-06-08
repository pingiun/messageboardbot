import sqlite3

from .utils import cache

class App(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.cache = cache.Cache()

    def _select(self, query, values=None):
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        if values:
            c.execute(query, values)
        else:
            c.execute(query)
        result = c.fetchall()
        conn.close()
        return result

    def get_channels(self):
        channels = self.cache.get('channels')
        if channels:
            return channels
        else:
            channels = self._select("SELECT * FROM Channels")
            self.cache.put('channels', channels)
            return channels

    def get_channel(self, name):
        channel = self.cache.get('channel_'+name)
        if channel:
            return channel
        else:
            return self._select("SELECT * FROM Channels WHERE ChannelName=?", (name,))