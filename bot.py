#!/usr/bin/env python3

import configparser

import telepot
from telepot.delegate import per_from_id, create_open

from messageboardbot.app import App
from messageboardbot.userhandler import MessageBoardBot

if __name__ == '__main__':
  configfile = configparser.ConfigParser()
  configfile.read('config.ini')
  config = configfile['bot']

  app = App(config['DatabaseFile'])
  bot = telepot.DelegatorBot(config['TelegramToken'], [
      (per_from_id(), create_open(MessageBoardBot, timeout=30, app=app)),
  ])
  print("Listening...")
  bot.message_loop(run_forever=True)