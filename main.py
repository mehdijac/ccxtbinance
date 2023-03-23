from config import *
from utils import *
from indicators import In_trend
from credentials import BINANCE_API_KEY,BINANCE_SECRET_KEY

import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')


import ccxt
import schedule


global in_position
global orders
global balance
global pnl
global binance_spot_api


in_position=False
balance=WALLET
pnl=[]
orders=[]

def init_bot():
    """
    This function creates a client to the Binance api
    """
    global binance_spot_api 
    binance_spot_api=ccxt.binance({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_SECRET_KEY
     })
    
    print("\N{seedling}"+' Initiating bot.......')




def is_buy_signal(df,symbol:str):
    """
    This function identify the period when it is suitable to buy
    """
    last_index=len(df)-1
    signal=(not df['in_uptrend'][last_index-1] and df['in_uptrend'][last_index])

    return signal


def is_sell_signal(df,symbol:str):
    """
    This function identify the period when it is suitable to sell
    """  
    last_index=len(df)-1
    signal=(df['in_uptrend'][last_index-1] and not df['in_uptrend'][last_index]) and df["close"][last_index]>(orders[-1]+10)

    return signal



def buy_sell_orders(df,symbol:str):
    """
    This function creates buy and sell orders if there is any signal and if there is no active order
    """

    global in_position
    global orders
    global balance
    global pnl
    global timeframe

    last_index=len(df)-1
    
    if not in_position:
        
        if is_buy_signal(df,symbol):
            #order = exchange.create_market_buy_order
            orders.append(df["close"][last_index])
            print("\N{blossom}"+ f" changed to uptrend, buy order executed at price { orders[-1]}")
            in_position = True
    
    else :
        
        if is_sell_signal(df,symbol) :
            orders.append(df["close"][last_index])
            pnl.append(profit_loss(orders,balance))
            #order = exchange.create_market_sell_order
            print("\N{money with wings}"+"\N{money with wings}"+"\N{money with wings}"+f' profit and loss : {pnl[-1]}')
            in_position = False
        
            


def run_bot(pair,timeframe,limit,last_period,weight_ma_margion):

    print("\N{spouting whale}"+f"  Fetching new bars for {datetime.now().isoformat()}")
    df = get_bars(binance_spot_api,pair,limit,timeframe)
    Intrend_data = In_trend(df,last_period,weight_ma_margion)

    
    buy_sell_orders(Intrend_data,pair)



if __name__=='__main__':

    pair=ACTIVE_TRADING_PAIRS[0]['symbol']
    timeframe='1s'
    limit=80
    last_period=5
    weight_ma_margion=2
    #since=

    init_bot()

    schedule.every(1).seconds.do(lambda: run_bot(pair,timeframe,limit,last_period,weight_ma_margion))

    start_time= get_local_timestamp()
    print("\N{alarm clock}"+f' start time  : {start_time}')



    while (get_local_timestamp()-start_time)<500:
        schedule.run_pending()
        time.sleep(1)
    print("\N{money with wings}"+"\N{money with wings}"+"\N{money with wings}"+f' profit and loss : {pnl[-1]}')
    print("\N{alarm clock}"+ f' end time  : {get_local_timestamp()}')

