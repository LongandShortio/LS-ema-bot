#! /usr/bin/python3
# longandshort.io
# Sends a Telegram message to keep you updated of your position every n minutes
import logging
from time import sleep
n=15 # An update will be sent every 15 minutes

def update(bot):
    while True:
        try:
            bot.update_position()
            logging.info('update_position')
        except:
            logging.info('update_position failed')
        sleep(n*60)
