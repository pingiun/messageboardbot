import sqlite3
import time
import logging

import telepot
from telepot.delegate import per_from_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup

from keyboards import keyboards

class Cache(object):
    def __init__(self):
        self.cachedict = {}

    def get(self, key, time=600):
        value = self.cachedict.get(key, None)
        if value:
            if value[0] + 600 > time.time():
                return value[1]
        return None

    def put(self, key, value):
        self.cachedict[key] = [time.time(), value]

class App(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.cache = Cache()

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

class MessageBoardBot(telepot.helper.UserHandler):
    def __init__(self, token, timeout):
        super(MessageBoardBot, self).__init__(token, timeout)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if chat_type != 'private':
            return

        if content_type == 'text':
            if msg['text'].startswith('@MessageBoardBot '):
                handle_command(msg)
            elif msg['text'].startswith('/start'):
                bot.sendMessage(chat_id, "Welcome", reply_markup=keyboards['start'])
            elif msg['text'] == 'List Channels':
                keyboard = [['Channel: ' + row[1]] for row in app.get_channels()]
                bot.sendMessage(chat_id, "Here's a list of channels, click on one to get more information.", reply_markup=ReplyKeyboardMarkup(keyboard=keyboard))
            elif msg['text'].startswith('Channel: '):
                channel = app.get_channel(msg['text'][9:])[0]
                if channel:
                    bot.sendMessage(chat_id, "The channel {} can be found here: {}".format(channel[1], channel[2]))
                else:
                    bot.sendMessage(chat_id, "The requested channel was not found.")

    def handle_command(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if msg['text'][17:].startswith('reply'):
            pass
        else:
            bot.sendMessage(chat_id, 'Command not recognized')

TOKEN_TG = '216237136:AAGb8w2fpkDs2NyaznJ9VNKmBWzPMQWVf60'
logger = logging.getLogger(__name__)

app = App('database.db')
bot = telepot.DelegatorBot(TOKEN_TG, [
    (per_from_id(), create_open(MessageBoardBot, timeout=20)),
])
print("Listening...")
bot.message_loop(run_forever=True)