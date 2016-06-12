#!/usr/bin/env python3

import configparser
import sys

import telepot
from telepot.delegate import per_from_id, create_open

from messageboardbot.app import App
from messageboardbot.userhandler import MessageBoardBot

if __name__ == '__main__':
  configfile = configparser.ConfigParser()
  configfile.read('config.ini')
  if not 'bot' in configfile:
    sys.exit("You need to supply a config file such as in config.sample")
  config = configfile['bot']

  if 'DatabaseURL' in config:
    app = App(config['DatabaseURL'])
  elif 'DatabaseFile' in config:
    app = App(config['DatabaseFile'])
  else:
    sys.exit("You need to add a DatabaseURL or DatabaseFile in the config.")

  bot = telepot.DelegatorBot(config['TelegramToken'], [
      (per_from_id(), create_open(MessageBoardBot, timeout=5*60, app=app)),
  ])
  print("Listening...")
  bot.message_loop(run_forever=True)