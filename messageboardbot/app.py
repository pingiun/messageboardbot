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

    def _execute(self, query, values=None):
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        if values:
            c.execute(query, values)
        else:
            c.execute(query)
        conn.commit()
        conn.close()

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
            return self._select("SELECT * FROM Channels WHERE ChannelName = ?", (name,))

    def get_message(self, post_id):
        postid = self.cache.get('postid_'+postid)
        if postid:
            return postid
        else:
            return self._select("SELECT * FROM Posts_per_Channel INNER JOIN Channels ON Posts_per_Channel.Channel_ID=Channels.Channel_ID WHERE Post_ID = ?", (postid,))

    def get_comment_chain(self, post_id, offset=0):
        chain = self.cache.get('chain_{}_{}'.format(postid, offset))
        if chain:
            return chain
        else:
            return self._select("SELECT * FROM Post_per_Channel WHERE Replyto_ID = ? LIMIT ?,?", (post_id, offset, offset+10))

    def store_post(self, post_id, channel_id, message_id, content_type, content_text, replyto_id=None, file_id=None):
        self._execute("INSERT INTO Posts_per_Channel VALUES (?, ?, ?, ?, ?, ?, ?)", (post_id, replyto_id, channel_id, message_id, content_type, content_text, file_id))

    def get_post_id(self):
        postid = self.cache.get('postid')
        if postid:
            self.cache.put('postid', postid+1)
            return postid + 1
        else:
            try:
                postid = self._select("SELECT Post_ID FROM Posts_per_Channel ORDER BY Post_ID DESC LIMIT 1;")[0][0]
            except IndexError:
                postid = 0
            self.cache.put('postid', postid + 1)
            return postid + 1