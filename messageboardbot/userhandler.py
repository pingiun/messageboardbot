import logging

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup
from pprint import pprint
from .keyboards import keyboards

class MessageBoardBot(telepot.helper.UserHandler):
    def __init__(self, token, timeout, app):
        super(MessageBoardBot, self).__init__(token, timeout)
        self.app = app
        self.chosenchannel = 'none'
        self.status = 'start'

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if chat_type != 'private':
            return

        if self.status == 'posting':
            if content_type == 'text':
                if msg['text'] != '🤐 Cancel Posting 🤐':
                    postid = self.app.get_post_id()
                    self.bot.sendMessage(self.chosenchannel[2], '#p'+str(postid)+'\n'+msg['text'])
                    sendmsg = self.sender.sendMessage('Your message was posted on the {} board'.format(self.chosenchannel[1]), reply_markup = keyboards['start'])
                    self.app.store_post(postid, self.chosenchannel[0], sendmsg['message_id'], content_type, msg['text'])
                    self.status = 'start'
                else:
                    self.sender.sendMessage('Posting cancelled', reply_markup = keyboards['start'])
            elif content_type == 'photo':
                postid = self.app.get_post_id()
                self.bot.sendPhoto(self.chosenchannel[2],msg['photo'][-1]['file_id'], caption = '#p'+str(postid)+'\n'+msg['caption'])
                sendmsg = self.sender.sendMessage('Your message was posted on the {} board'.format(self.chosenchannel[1]), reply_markup = keyboards['start'])
                self.app.store_post(postid, self.chosenchannel[0], sendmsg['message_id'], content_type, msg['caption'],file_id = msg['photo'][-1]['file_id'])
                self.status = 'start'
            elif content_type == 'document':
                postid = self.app.get_post_id()
                self.bot.sendDocument(self.chosenchannel[2],msg['document']['file_id'], caption = '#p'+str(postid)+'\n'+msg['caption'])
                sendmsg = self.sender.sendMessage('Your message was posted on the {} board'.format(self.chosenchannel[1]), reply_markup = keyboards['start'])
                self.app.store_post(postid, self.chosenchannel[0], sendmsg['message_id'], content_type, msg['caption'],file_id = msg['document']['file_id'])
                self.status = 'start'
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
                    self.chosenchannel = channel

                else:
                    self.sender.sendMessage("The requested channel was not found.")

            elif msg['text'] == '📝 Post 📝':
                self.sender.sendMessage('What would you like to send to {}?'.format(self.chosenchannel[1]), reply_markup = ReplyKeyboardMarkup(keyboard = [['🤐 Cancel Posting 🤐', '/start']]))
                self.status = 'posting'

    def handle_command(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if msg['text'][17:].startswith('reply'):
            pass
        else:
            self.sendMessage('Command not recognized')