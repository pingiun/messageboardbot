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
            admin = self._select("SELECT * FROM Admins WHERE User_ID = ?", (user_id,))
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
            channels = self._select("SELECT * FROM Channels")
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
            channel = self._select("SELECT * FROM Channels WHERE ChannelName = ?", (name,))
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
            channel = self._select("SELECT * FROM Channels WHERE ChannelURL = ?", (url,))
            self.cache.put('channelurl_'+url, channel)
            return channel

    def add_channel(self, name, url):
        """Adds a channel to the Channels table
        The caller of this function is supposed to check privileges.

        Args:
            name: The name of the channel
            url: The URL of the channel
        """
        self._execute("INSERT INTO Channels VALUES (NULL,?,?)", (name, url))

    def get_message(self, channel_id, message_id):
        """Returns a message with channel_id and message_id

        Returns:
            A list of size 1 with a message row including the channel row.
        """
        postid = self.cache.get('postid_{}_{}'.format(channel_id, message_id))
        if postid:
            return postid
        else:
            return self._select("SELECT * FROM Posts_per_Channel INNER JOIN Channels ON Posts_per_Channel.Channel_ID=Channels.Channel_ID WHERE Message_ID = ? AND Posts_per_Channel.Channel_ID = ?", (message_id, channel_id))

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
            chain = self._select("SELECT * FROM Posts_per_Channel WHERE Replyto_ID = ? LIMIT ?,?", (post_id, offset, offset+10))
            self.cache.put('chain_{}_{}'.format(post_id, offset), chain)
            return chain

    def store_post(self, post_id, channel_id, message_id, content_type, content_text, replyto_id=None, file_id=None):
        """Store a post"""
        self._execute("INSERT INTO Posts_per_Channel VALUES (?, ?, ?, ?, ?, ?, ?)", (post_id, replyto_id, channel_id, message_id, content_type, content_text, file_id))

    def get_post_id(self):
        """Get a new ID for a new post"""
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