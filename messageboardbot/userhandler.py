import logging

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup

from .keyboards import keyboards

class MessageBoardBot(telepot.helper.UserHandler):
    def __init__(self, token, timeout, app):
        super(MessageBoardBot, self).__init__(token, timeout)
        self.app = app
        self.chosenchannel = 'none'
        self.posting = False

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if chat_type != 'private':
            return

        if content_type == 'text':
            if self.posting:
                if msg['text'] != '🤐 Cancel Posting 🤐':
                    channel = self.app.get_channel(self.chosenchannel)[0]
                    telepot.Bot('231888783:AAHdPC0NDScgqJV3YTGEtICfhbKi2CGZAqc').sendMessage('@'+channel[1], msg['text'])
                    self.sender.sendMessage('Your message was posted on the {} board'.format(channel[1]), reply_markup = keyboards['start'])
                    self.posting = False
                else:
                    self.sender.sendMessage('Posting cancelled', reply_markup = keyboards['start'])

            else:
                if msg['text'].startswith('@MessageBoardBot '):
                    handle_command(msg)

                elif msg['text'].startswith('/start'):
                    self.sender.sendMessage("Welcome", reply_markup=keyboards['start'])

                elif msg['text'] == 'List Channels':
                    keyboard = [['Channel: ' + row[1]] for row in self.app.get_channels()]
                    self.sender.sendMessage("Here's a list of channels, click on one to get more information.", reply_markup=ReplyKeyboardMarkup(keyboard=keyboard))

                elif msg['text'].startswith('Channel: '):
                    channel = self.app.get_channel(msg['text'][9:])[0]
                    if channel:
                        self.sender.sendMessage("The channel {} can be found here: {}".format(channel[1], channel[2]), reply_markup = keyboards['chosenchannel'])
                        self.chosenchannel = channel[1]

                    else:
                        self.sender.sendMessage("The requested channel was not found.")

                elif msg['text'] == '📝 Post 📝':
                    channel = self.app.get_channel(self.chosenchannel)[0]
                    self.sender.sendMessage('What would you like to send to {}?'.format(channel[1]), reply_markup = ReplyKeyboardMarkup(keyboard = [['🤐 Cancel Posting 🤐']]))
                    self.posting = True

    def handle_command(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if msg['text'][17:].startswith('reply'):
            pass
        else:
            self.sendMessage('Command not recognized')