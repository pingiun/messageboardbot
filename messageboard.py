import telepot
from telepot.delegate import per_from_id, create_open

from keyboards import keyboards

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
            else:
                pass
                
    def handle_command(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if msg['text'][17:].startswith('reply'):
            pass
        else:
            bot.sendMessage(chat_id, 'Command not recognized')

TOKEN_TG = '216237136:AAGb8w2fpkDs2NyaznJ9VNKmBWzPMQWVf60' 

bot = telepot.DelegatorBot(TOKEN_TG, [
    (per_from_id(), create_open(MessageBoardBot, timeout=20)),
])
bot.message_loop(run_forever=True)