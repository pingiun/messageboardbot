try:
    import psycopg2 as db
    dbtype = 'postgres'
except ImportError:
    import sqlite3 as db
    dbtype = 'sqlite'

from .utils import cache

queries = {
    'is_admin':          "SELECT * FROM admins WHERE user_id = ?;",
    'get_channels':      "SELECT * FROM channels;",
    'get_channel':       "SELECT * FROM channels WHERE channelname = ?;",
    'get_channel_byurl': "SELECT * FROM channels WHERE ChannelURL = ?;",
    'add_channel':       "INSERT INTO channels (channelname, channelurl) VALUES (?, ?);",
    'get_message':       "SELECT * FROM posts_per_channel INNER JOIN channels ON posts_per_channel.channel_id=channels.channel_id WHERE message_id = ? AND posts_per_channel.channel_id = ?;",
    'get_comment_chain': "SELECT * FROM posts_per_channel WHERE replyto_id = ? LIMIT ?,?;",
    'count_comments':    "SELECT COUNT(post_id) FROM posts_per_channel WHERE replyto_id = ?;",
    'store_post':        "INSERT INTO posts_per_channel VALUES (?, ?, ?, ?, ?, ?, ?);",
    'get_post_id':       "SELECT post_ID FROM posts_per_channel ORDER BY post_id DESC LIMIT 1;",
}

if dbtype == 'postgres':
    for key, value in queries.items():
        queries[key] = value.replace('?', '%s')

class App(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.cache = cache.Cache()

    def _select(self, query, values=None):
        conn = db.connect(self.dbname)
        c = conn.cursor()
        if values:
            c.execute(query, values)
        else:
            c.execute(query)
        result = c.fetchall()
        conn.close()
        return result

    def _execute(self, query, values=None):
        conn = db.connect(self.dbname)
        c = conn.cursor()
        if values:
            c.execute(query, values)
        else:
            c.execute(query)
        conn.commit()
        conn.close()

    def is_admin(self, user_id):
        """Return the admin level of a user_id
        
        Args:
            user_id: A Telegram User ID
        Returns:
            The admin level or 0 for not admin
        Raises:
            ValueError: If there's an error in the database
        """
        admin = self.cache.get('admin_{}'.format(user_id))
        if admin:
            return True
        else:
            admin = self._select(queries['is_admin'], (user_id,))
            if len(admin) == 1:
                self.cache.put('admin_{}'.format(user_id), admin[0][2])
                return admin[0][2]
            elif len(admin) > 1:
                raise ValueError("More than one entry in Admin table with the same User_ID")
            else:
                self.cache.put('admin_{}'.format(user_id), 0)
                return 0
        
    def get_channels(self):
        """Returns a list of channels"""
        channels = self.cache.get('channels')
        if channels:
            return channels
        else:
            channels = self._select(queries['get_channels'])
            self.cache.put('channels', channels)
            return channels

    def get_channel(self, name):
        """Returns information about a channel
        
        Args:
            name: The name of a channel
        Returns:
            A list of size 1 with a channel database row.
        """
        channel = self.cache.get('channel_'+name)
        if channel:
            return channel
        else:
            channel = self._select(queries['get_channel'], (name,))
            self.cache.put('channel_'+name, channel)
            return channel

    def get_channel_byurl(self, url):
        """Returns information about a channel when given an url
        
        Args:
            url: A channel url like @MBrandom
        Returns:
            A list of size 1 with a channel database row.
        """
        channel = self.cache.get('chanelurl_'+url)
        if channel:
            return channel
        else:
            channel = self._select(queries['get_channel_byurl'], (url,))
            self.cache.put('channelurl_'+url, channel)
            return channel

    def add_channel(self, name, url):
        """Adds a channel to the Channels table
        The caller of this function is supposed to check privileges.

        Args:
            name: The name of the channel
            url: The URL of the channel
        """
        self._execute(queries['add_channel'], (name, url))

    def get_message(self, channel_id, message_id):
        """Returns a message with channel_id and message_id

        Returns:
            A list of size 1 with a message row including the channel row.
        """
        postid = self.cache.get('postid_{}_{}'.format(channel_id, message_id))
        if postid:
            return postid
        else:
            return self._select(queries['get_message'], (message_id, channel_id))

    def get_comment_chain(self, post_id, offset=0):
        """Returns a comment chain based on a OP post_id
        
        Args:
            post_id: The post the comment chain should be retrieved from
            offset: Increment offset by 10 to get the next 10 comments
        Returns:
            The first 10 comments from an offset of `offset`
        """
        chain = self.cache.get('chain_{}_{}'.format(post_id, offset), timeout=5)
        if chain:
            return chain
        else:
            chain = self._select(queries['get_comment_chain'], (post_id, offset, offset+10))
            self.cache.put('chain_{}_{}'.format(post_id, offset), chain)
            return chain

    def count_comments(self, post_id):
        """Counts the amount of comments in a thread"""
        count = self.cache.get('count_{}'.format(post_id))
        if count:
            return count
        else:
            count = self._select(queries['count_comments'], (postid, ))
            self.cache.put('count_{}'.format(post_id), count)
            return count

    def store_post(self, post_id, channel_id, message_id, content_type, content_text, replyto_id=None, file_id=None):
        """Store a post"""
        self._execute(queries['store_post'], (post_id, replyto_id, channel_id, message_id, content_type, content_text, file_id))

    def get_post_id(self):
        """Get a new ID for a new post"""
        postid = self.cache.get('postid')
        if postid:
            self.cache.put('postid', postid+1)
            return postid + 1
        else:
            try:
                postid = self._select(queries['get_post_id'])[0][0]
            except IndexError:
                postid = 0
            self.cache.put('postid', postid + 1)
            return postid + 1