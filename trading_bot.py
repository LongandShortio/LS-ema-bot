#! /usr/bin/python3
# longandshort.io
import os
os.chdir('') # Define your working directory
import rest_api as api
from time import sleep
from math import floor
import pandas as pd
from telegram_bot import * # If you have created a Telegram bot to stay updated
import logging
logger=logging.getLogger()
logger.handlers = []
logging.basicConfig(filename=f"{os.getcwd()}/trading_bot.log",format='%(asctime)s - %(process)d-%(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

# --------------------------



def long(ema1, ema2):
    """
    The function which decides to go long or not
    """
    if ema1.iloc[-1]>ema2.iloc[-1] and ema1.iloc[-2]<ema2.iloc[-2]: return True # A cross just happened
    return False

def short(ema1, ema2):
    """
    The function which decides to go short or not
    """
    if ema1.iloc[-1]<ema2.iloc[-1] and ema1.iloc[-2]>ema2.iloc[-2]: return True # A cross just happened
    return False



def trading(session, bot,n1,n2):
    """
    The function which does the trading part.
    It takes your Bybit session, a telegram bot and the length of the two EMAs
    """
    logging.info('+++++++++++++++ Start trading +++++++++++++++')

    while True:

        logging.info('+++++++++++++++ Get data +++++++++++++++')

        kline=session.get_kline(interval=240) # Define your timeframe in minutes: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720
        data={'close': [float(x["close"]) for x in kline["result"]],
              'open': [float(x["open"]) for x in kline["result"]],
              'high':[float(x["high"]) for x in kline["result"]] ,
              'low': [float(x["low"]) for x in kline["result"]],
              }
        df=pd.DataFrame(data=data)
        del data
        price=(df['close']+df['open']+df['low']+df['high'])/4 # Using Heikin Ashi candlesticks, replace by price=df['close'] for regular candlesticks
        del df

        ema1=price.ewm(span=n1, min_periods=n1).mean().dropna() # Compute the first EMA
        ema2=price.ewm(span=n2, min_periods=n2).mean().dropna() # Compute the second EMA
        go_long, go_short=long(ema1, ema2), short(ema1, ema2) # Decide whether to go long or short
        del ema1, ema2

        my_position= session.my_position()['result'][0]['side'] # Get your current position

        if my_position=="None" and go_long:
            logging.info('+++++++++++++++ my_position==None and go_long +++++++++++++++')
            session.cancel_all_pending_order() # Cancel all unfulfilled orders
            price=floor(float(session.get_orderbook()['result'][0]['ask_price'])-10)
            stop_loss=floor(float(price*0.90)) # SL @ 10%
            take_profit=floor(float(price*1.5)) # TP @ 50 %
            size=1000 # Define the size of your position
            session.place_active_order("Buy", size, price, stop_loss, take_profit)
            bot.send_message("Had no position and placed long order")
            message=f"Price = {price}, Size = {size}, Leverage = {leverage}, Stop Loss = {stop_loss}, Take Profit = {take_profit}" # Send a telegram message
            bot.send_message(message)
            sleep(10*60)
            logging.info('+++++++++++++++ Sleep 10*60s for the order to get filled +++++++++++++++')

        elif my_position=="None" and go_short:
            logging.info('+++++++++++++++ my_position==None and go_short +++++++++++++++')
            session.cancel_all_pending_order() # Cancel all unfulfilled orders
            price=floor(float(session.get_orderbook()['result'][0]['bid_price'])+10)
            stop_loss=floor(float(price*1.10)) # SL @ 10%
            take_profit=floor(float(price*0.50)) # TP @ 50 %
            size=1000 # Define the size of your position
            session.place_active_order("Sell", size, price, stop_loss, take_profit)
            bot.send_message("Had no position and placed short order")
            message=f"Price = {price}, Size = {size}, Leverage = {leverage}, Stop Loss = {stop_loss}, Take Profit = {take_profit}" # Send a telegram message
            bot.send_message(message)
            sleep(10*60)
            logging.info('+++++++++++++++ Sleep 10*60s for the order to get filled +++++++++++++++')

        elif my_position=="Sell" and go_long:
            logging.info('+++++++++++++++ my_position==Sell and go_long +++++++++++++++')
            session.cancel_all_pending_order()
            size=session.my_position()['result'][0]['size'] # Get current size position
            session.market_close("Buy", size) # Close current position @ market

            price=floor(float(session.get_orderbook()['result'][0]['ask_price'])-10) #2
            stop_loss=floor(float(price*0.90)) # SL @ 10%
            take_profit=floor(float(price*1.50)) # TP @ 50 %
            size=1000 # Define the size of your position
            session.place_active_order("Buy", size, price, stop_loss, take_profit)
            bot.send_message("Just closed a short and placed long order")
            message=f"Price = {price}, Size = {size}, Leverage = {leverage}, Stop Loss = {stop_loss}, Take Profit = {take_profit}" # Send a telegram message
            bot.send_message(message)
            sleep(10*60)
            logging.info('+++++++++++++++ Sleep 10*60s for the order to get filled +++++++++++++++')

        elif my_position=="Buy" and go_short:
            logging.info('+++++++++++++++ my_position==Buy and go_short +++++++++++++++')
            session.cancel_all_pending_order()
            size=session.my_position()['result'][0]['size'] # Get current size position
            session.market_close("Sell", size) # Close current position @ market

            price=floor(float(session.get_orderbook()['result'][0]['bid_price'])+10) #2
            stop_loss=floor(float(price*1.10)) # SL @ 10%
            take_profit=floor(float(price*0.50)) # TP @ 50 %
            size=1000 # Define the size of your position
            session.place_active_order("Sell", size, price, stop_loss, take_profit)
            bot.send_message("Just closed a long and placed short order")
            message=f"Price = {price}, Size = {size}, Leverage = {leverage}, Stop Loss = {stop_loss}, Take Profit = {take_profit}" # Send a telegram message
            bot.send_message(message)
            sleep(10*60)
            logging.info('+++++++++++++++ Sleep 10*60s for the order to get filled +++++++++++++++')



        logging.info('+++++++++++++++ Sleep 5min +++++++++++++++')
        sleep(5*60)
        logging.info('+++++++++++++++ Starts again +++++++++++++++')
