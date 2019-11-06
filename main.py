#! /usr/bin/python3
# longandshort.io
import os
os.chdir('') # Define your working directory
from trading_bot import *
import threading
import rest_api as api
from bot_update import *

# ------- Bybit session
api_key="" # Enter your Bybit API key
secret="" # Enter your Bybit secret key
leverage=2 # Select your leverage
url="https://api-testnet.bybit.com" # For the testnet, for the real trading environement url="https://api.bybit.com"
session=api.Account(api_key,secret,leverage,url) # Create your trading session

# ------- Telegram bot
token="" # Enter your Telegram Token
chat_id="" # Enter your Telegra chat ID
bot=TelegramBot(session,token,chat_id) # Create your Telegram bot

# ------- EMAs
n1=10 # Length of EMA1
n2=20 # Length of EMA2

if __name__ == '__main__':
    trade = threading.Thread(target=trading, args=(session, bot,n1,n2))
    telegram_update = threading.Thread(target=update, args=(bot,))
    trade.start()
    telegram_update.start()
