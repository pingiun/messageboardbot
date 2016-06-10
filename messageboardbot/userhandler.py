import logging

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup
from .keyboards import keyboards

from .router import KeyboardRouter

class MessageBoardBot(telepot.helper.UserHandler):
    def __init__(self, token, timeout, app):
        super(MessageBoardBot, self).__init__(token, timeout)
        self.app = app

        self.helptext = "I don't get it mate, press /start to start over."

        self.chosenchannel = 'none'
        self.status = 'start'
        self.captiontype = 'none'
        layout  = [
              (r'\/start|Main Menu', ("Welcome", [['List Channels'],['About']])),
              (r'About', ("The bot is made by..", [['Main Menu']])),
              (r'List Channels', self.list_channels),
              (r'Channel: (\S.*)', self.channel_info),
              (r'📝 Post 📝', self.post),
              (r'.+', self.catchall)
            ]
        self._router = KeyboardRouter(self.bot, layout, self.on_nontext)

        self.on_message = self._router.on_message
    
    def on_nontext(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if self.status == 'posting' or self.status == 'replying':
            if content_type == 'photo':
                if msg.get('caption'):
                    self.post_to_channel(msg, 'photo', file_id=msg['photo'][-1]['file_id'])
                else:
                    self.sender.sendMessage("Now choose a caption to go with your photo.", reply_markup=keyboards['nocaption'])
                    self.captiontype = 'choosecaption_photo'
                    self.file_id = msg['photo'][-1]['file_id']
            elif content_type == 'document':
                if msg.get('caption'):
                    self.post_to_channel(msg, 'document', file_id=msg['document']['file_id'])
                else:
                    self.sender.sendMessage("Now choose a caption to go with your gif.", reply_markup=keyboards['nocaption'])
                    self.captiontype = 'choosecaption_document'
                    self.file_id = msg['document']['file_id']
        elif msg.get('forward_from_chat'):
            self.replytoid = msg['caption'].split('\n', 1)[0]
            self.replytochat = '@'+msg['forward_from_chat']['username']
            self.sender.sendMessage('Now send the reply',reply_markup=ReplyKeyboardMarkup(keyboard = [['🤐 Cancel Posting 🤐', 'Main Menu']]))
            self.status = 'replying'
        else:
            self.sender.sendMessage(self.helptext)

    def list_channels(self, msg):
        keyboard = [['Channel: ' + row[1]] for row in self.app.get_channels()]
        self.sender.sendMessage("Here's a list of channels, click on one to get more information.", reply_markup=ReplyKeyboardMarkup(keyboard=keyboard))

    def channel_info(self, msg, channelg):
        channel = self.app.get_channel(channelg)[0]
        if channel:
            self.sender.sendMessage("The channel {} can be found here: {}".format(channel[1], channel[2]), reply_markup=keyboards['chosenchannel'])
            self.chosenchannel = channel

        else:
            self.sender.sendMessage("The requested channel was not found.")

    def post(self, msg):
        self.sender.sendMessage('What would you like to send to {}?'.format(self.chosenchannel[1]), reply_markup = ReplyKeyboardMarkup(keyboard = [['🤐 Cancel Posting 🤐', 'Main Menu']]))
        self.status = 'posting'

    def post_to_channel(self, msg, content_type='text', file_id=None):
        postid = self.app.get_post_id()
        if self.status == 'posting':
            if content_type == 'text':
                msgtext = msg['text']
                self.bot.sendMessage(self.chosenchannel[2], "#p{}\n{}".format(postid, msgtext))
            elif content_type == 'photo':
                if msg.get('caption'):
                    msgtext = msg['caption']
                else:
                    msgtext = msg['text']
                self.bot.sendPhoto(self.chosenchannel[2], file_id, "#p{}\n{}".format(postid, msgtext))
            elif content_type == 'document':
                if msg.get('caption'):
                    msgtext = msg['caption']
                else:
                    msgtext = msg['text']
                self.bot.sendDocument(self.chosenchannel[2], file_id, "#p{}\n{}".format(postid, msgtext))
            self.replytoid = None
        
        elif self.status == 'replying':
            if content_type == 'text':
                msgtext = '>>> {}\n{}'.format(self.replytoid, msg['text'])
                self.bot.sendMessage(self.replytochat,"#p{}\n{}".format(postid, msgtext))
            elif content_type == 'photo':
                if msg.get('caption'):
                    msgtext = '>>> {}\n{}'.format(self.replytoid, msg['caption'])
                else:
                    msgtext = '>>>> {}\n{}'.format(self.replytoid, msg['text'])
                self.bot.sendPhoto(self.replytochat, file_id, "#p{}\n{}".format(postid, msgtext))
            elif content_type == 'document':
                if msg.get('caption'):
                    msgtext = '>>> {}\n{}'.format(self.replytoid, msg['caption'])
                else:
                    msgtext = '>>> {}\n{}'.format(self.replytoid, msg['text'])
                self.bot.sendDocument(self.replytochat, file_id, "#p{}\n{}".format(postid, msgtext))

        sendmsg = self.sender.sendMessage('Your message was posted on the {} board'.format(self.chosenchannel[1]), reply_markup=keyboards['start'])
        self.app.store_post(postid, self.chosenchannel[0], sendmsg['message_id'], content_type, msgtext, replyto_id=self.replytoid[2:], file_id=file_id)
        self.status = 'start'

    def catchall(self, msg):
        if msg['text'].startswith('@MessageBoardBot '):
            self.handle_command(msg)
            return
        if msg.get('forward_from_chat'):
            self.replytoid = msg['text'].split('\n', 1)[0]
            self.replytochat = '@'+msg['forward_from_chat']['username']
            print(self.replytoid)
            print(self.replytochat)
            self.sender.sendMessage('Now send the reply', reply_markup=ReplyKeyboardMarkup(keyboard = [['🤐 Cancel Posting 🤐', 'Main Menu']]))
            self.status = 'replying'
        elif self.captiontype.startswith('choosecaption'):
            self.post_to_channel(msg, self.status[14:], self.file_id)
        elif self.status == 'posting':
            if msg['text'] == '🤐 Cancel Posting 🤐':
                self.sender.sendMessage('Posting cancelled', reply_markup = keyboards['start'])
            else:
                self.post_to_channel(msg)
        elif self.status == 'replying':
            if msg['text'] == '🤐 Cancel Posting 🤐':
                self.sender.sendMessage('Posting cancelled', reply_markup = keyboards['start'])
            else:
                self.post_to_channel(msg)
        else:
            self.sender.sendMessage(self.helptext)

    def handle_command(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if msg['text'][17:].startswith('reply'):
            pass
        else:
            self.sendMessage('Command not recognized')