#!/usr/bin/env python3

import telepot
from telepot.delegate import per_from_id, create_open

from messageboardbot.app import App
from messageboardbot.userhandler import MessageBoardBot

if __name__ == '__main__':
  TOKEN_TG = '216237136:AAGb8w2fpkDs2NyaznJ9VNKmBWzPMQWVf60'

  app = App('database.db')
  bot = telepot.DelegatorBot(TOKEN_TG, [
      (per_from_id(), create_open(MessageBoardBot, timeout=20, app=app)),
  ])
  print("Listening...")
  bot.message_loop(run_forever=True)