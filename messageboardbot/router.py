import re

from telepot.namedtuple import ReplyKeyboardMarkup

class KeyboardRouter(object):
  def __init__(self, bot, layout, nontext):
    super(KeyboardRouter, self).__init__()
    self._router = Router(flavor, {'chat': lambda msg: self.on_chat_message(msg),
                                   'edited_chat': lambda msg: self.on_edited_chat_message(msg),
                                   'callback_query': lambda msg: self.on_callback_query(msg),
                                   'inline_query': lambda msg: self.on_inline_query(msg),
                                   'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg)})
                                   # use lambda to delay evaluation of self.on_ZZZ to runtime because
                                   # I don't want to require defining all methods right here.
    self.bot = bot
    self._layout = layout
    self._nontext = nontext

    # Example layout
    {
      r'\/start|Main Menu': ("Welcome", [['List Channels'],['About']]),
      r'About': ("The bot is made by..", [['Main Menu']]),
      r'List Channels': jefunctie(msg),
      r'Channel: (\S.*)': jefunctie(msg, group1, group2),
      r'📝 Post 📝': jefunctie(msg),
      '.+': jefunctie
    }

    @property
    def router(self):
      return self._router

    def on_message(self, msg):
      self._router.route(msg)

    def on_chat_message(self, msg):
      content_type, chat_type, chat_id = telepot.glance(msg)
      if content_type != 'text':
        self._nontext(msg)
        return

      for key, value in layout:
        match = re.match(key, msg[text])
        if match:
          if type(value) is function:
            if match.groups():
              value(msg, *match.groups())
              return
            else:
              value(msg)
              return
          else:
            bot.sendMessage(chat_id, value[1], reply_markup=ReplyKeyboardMarkup(keyboard=value[2]))
            return

      raise LookupError("Could not found a match for message text {}, please include a catch all match.".format(msg[text]))